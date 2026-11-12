"""Find Lua clone candidates without changing source files.

Exact tokens ignore comments, whitespace and optional semicolons. Structural
tokens additionally mask bare identifiers (not fields/methods or function calls).
Strings/numbers stay significant. Structural matches are NOT semantic equality.
"""
import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

LEXER = re.compile(
    r'(?P<comment>--\[(?P<ceq>=*)\[[\s\S]*?\](?P=ceq)\]|--[^\n]*)'
    r'|(?P<long>\[(?P<seq>=*)\[[\s\S]*?\](?P=seq)\])'
    r'|(?P<string>"(?:\\[\s\S]|[^"\\])*"|\x27(?:\\[\s\S]|[^\x27\\])*\x27)'
    r'|(?P<space>\s+)|(?P<id>[A-Za-z_][A-Za-z_0-9]*)'
    r'|(?P<number>0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'
    r'|(?P<symbol>\.\.\.|\.\.|==|~=|<=|>=|.)')
KEYWORDS = set('and break do else elseif end false for function if in local nil not or repeat return then true until while'.split())
MASK = (1 << 64) - 1


@dataclass
class Source:
    path: str
    values: list
    structural: list
    lines: list
    functions: list
    digest: str


def tokenize(text):
    values, kinds, lines = [], [], []
    line = 1
    for match in LEXER.finditer(text):
        kind, value = match.lastgroup, match.group()
        if kind not in ('comment', 'space') and value != ';':
            values.append(sys.intern(value))
            kinds.append(kind)
            lines.append(line)
        line += value.count('\n')
    structural = []
    for i, (value, kind) in enumerate(zip(values, kinds)):
        previous = values[i - 1] if i else ''
        following = values[i + 1] if i + 1 < len(values) else ''
        structural.append('$identifier' if kind == 'id' and value not in KEYWORDS
                          and previous not in ('.', ':') and following != '(' else value)
    return values, structural, lines


def function_spans(values):
    # Small block-stack recognizer, not a type/binding parser. Only the token
    # block scan supplies the large-clone results; this finds short helpers too.
    stack, spans = [], []
    for i, value in enumerate(values):
        if value in ('function', 'if', 'for', 'while', 'repeat'):
            stack.append([value, i, value in ('for', 'while')])
        elif value == 'do':
            if stack and stack[-1][2]:
                stack[-1][2] = False
            else:
                stack.append(['do', i, False])
        elif value == 'until':
            if stack and stack[-1][0] == 'repeat': stack.pop()
        elif value == 'end' and stack:
            kind, start, _ = stack.pop()
            if kind == 'function':
                opening = next((j for j in range(start + 1, i) if values[j] == '('), None)
                if opening is not None: spans.append((start, opening, i + 1))
    return spans


def read_source(path, base):
    raw = path.read_bytes()
    values, structural, lines = tokenize(raw.decode('utf-8-sig', errors='replace'))
    return Source(path.relative_to(base).as_posix(), values, structural, lines,
                  function_spans(values), hashlib.sha256(raw).hexdigest())


def fingerprints(values, width, ids):
    numbers = []
    for token in values:
        if token not in ids: ids[token] = len(ids) + 1
        numbers.append(ids[token])
    if len(numbers) < width: return
    power = pow(257, width - 1, 1 << 64)
    digest = 0
    for number in numbers[:width]: digest = ((digest * 257) + number) & MASK
    yield 0, digest
    for i in range(width, len(numbers)):
        digest = (((digest - numbers[i - width] * power) * 257) + numbers[i]) & MASK
        yield i - width + 1, digest


def location(doc, start, end):
    return {'file': doc.path, 'start': doc.lines[start], 'end': doc.lines[end - 1]}


def scan(sources, vanilla, mode, minimum=100, min_lines=8, width=40):
    index, ids, covered, results = defaultdict(list), {}, {}, []
    attribute = 'values' if mode == 'exact' else 'structural'

    def visit(doc, number, add):
        values = getattr(doc, attribute)
        for start, digest in fingerprints(values, width, ids):
            for other_number, other_start in index.get(digest, ()):
                other = sources[other_number]
                theirs = getattr(other, attribute)
                if number == other_number and start - other_start < width: continue
                key = (other_number, number, start - other_start)
                if covered.get(key, -1) >= start + width: continue
                if values[start:start + width] != theirs[other_start:other_start + width]: continue
                left, right = 0, width
                while start - left > 0 and other_start - left > 0 and values[start-left-1] == theirs[other_start-left-1]:
                    left += 1
                while start+right < len(values) and other_start+right < len(theirs) and values[start+right] == theirs[other_start+right]:
                    if number == other_number and other_start + right >= start - left: break
                    right += 1
                covered[key] = start + right
                length = right + left
                if number == other_number and other_start+right > start-left: continue
                a, b = location(other, other_start-left, other_start+right), location(doc, start-left, start+right)
                if length >= minimum and min(a['end']-a['start']+1, b['end']-b['start']+1) >= min_lines:
                    results.append({'mode': mode, 'tokens': length, 'a': a, 'b': b})
            if add:
                # Skip very repetitive seed patterns rather than explode pair counts.
                entries = index[digest]
                if len(entries) < 30: entries.append((number, start))

    for i, doc in enumerate(sources): visit(doc, i, True)
    internal = list(results)
    results.clear()
    for i, (path, base) in enumerate(vanilla):
        doc = read_source(path, base)
        visit(doc, len(sources) + i, False)
    return internal, results


def short_functions(sources, minimum=16):
    groups = defaultdict(list)
    for doc in sources:
        for start, opening, end in doc.functions:
            body = tuple(doc.values[opening:end])
            if len(body) >= minimum:
                groups[body].append(location(doc, start, end))
    return sorted([{'tokens': len(key), 'locations': locations} for key, locations in groups.items()
                   if len(locations) > 1], key=lambda row: -row['tokens'])


def prune(rows):
    # Drop duplicate/contained ranges, including structural matches already exact.
    kept = []
    for row in sorted(rows, key=lambda r: (-r['tokens'], r['mode'] != 'exact')):
        a,b = row['a'],row['b']
        if any(not (row['mode']=='exact' and k['mode']=='structural')
               and a['file']==k['a']['file'] and b['file']==k['b']['file']
               and k['a']['start']<=a['start'] and k['a']['end']>=a['end']
               and k['b']['start']<=b['start'] and k['b']['end']>=b['end'] for k in kept): continue
        kept.append(row)
    return kept


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('42/media'))
    parser.add_argument('--game', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources = [read_source(p, args.root) for p in sorted(args.root.rglob('*.lua'))]
    vanilla = []
    if args.game:
        base = args.game / 'media/lua'
        vanilla = [(p, base) for p in sorted(base.rglob('*.lua'))]
    internal, external = [], []
    for mode in ('exact', 'structural'):
        a,b = scan(sources, vanilla, mode)
        internal.extend(a);external.extend(b)
        print(f'{mode}: {len(a)} internal, {len(b)} vanilla candidates', file=sys.stderr)
    file_groups = defaultdict(list)
    for source in sources: file_groups[source.digest].append(source.path)
    result = {'scope': __doc__, 'mod_root': args.root.as_posix(), 'mod_files': len(sources),
              'vanilla_files': len(vanilla), 'minimum_tokens':100, 'minimum_lines':8,
              'limitations':'Heuristic seeds capped at 30 occurrences; no binding/type inference; no semantic proof.',
              'identical_files':[g for g in file_groups.values() if len(g)>1],
              'source_hashes':{source.path:source.digest for source in sources},
              'internal':prune(internal), 'vanilla':prune(external),
              'identical_functions':short_functions(sources)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f'Wrote {args.output}: {len(result["internal"])} internal / {len(result["vanilla"])} vanilla ranges')


if __name__ == '__main__': main()
