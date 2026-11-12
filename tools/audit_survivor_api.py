"""Conservative name audit of known Java receiver chains in SuperSurvivor.lua.

Checks public inherited method names/arity and selected literal argument types,
not Lua exposure, full argument typing, behavior, overload selection, or arbitrary
local-variable types. Unresolved chains stop.
"""
import argparse
import json
import re
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile
from inspect_game_api import members


def audit(jar_path, lua_path, inventory=False):
    with ZipFile(jar_path) as jar:
        @lru_cache(None)
        def methods(classname):
            try:
                metadata = {}
                declared = list(members(jar.read(classname + '.class'), metadata))
            except KeyError:
                return {}
            found = {n: set(d) for n, d in methods(metadata['superclass']).items()} if metadata['superclass'] else {}
            for interface in metadata['interfaces']:
                for name, descriptors in methods(interface).items():
                    found.setdefault(name, set()).update(descriptors)
            for kind, flags, name, descriptor in declared:
                if kind == 'method' and flags & 1:
                    found.setdefault(name, set()).add(descriptor)
            return found

        source = Path(lua_path).read_text(encoding='utf-8')
        # Blank strings/comments but retain offsets and line numbers.
        tokens = r'--\[(=*)\[[\s\S]*?\]\1\]|--[^\n]*|\[(=*)\[[\s\S]*?\]\2\]|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27'
        code = re.sub(tokens, lambda m: re.sub(r'[^\n]', ' ', m[0]), source)
        roots = {
            r'\b(?:self\.player|o\.player|Buddy)\b': 'zombie/characters/IsoPlayer',
            r'\bself:Get\(\)': 'zombie/characters/IsoPlayer',
            r'\bgetSpecificPlayer\([^()]*\)': 'zombie/characters/IsoPlayer',
            r'\bgetPlayer\(\)': 'zombie/characters/IsoPlayer',
            r'\bgetCell\(\)': 'zombie/iso/IsoCell',
            r'\bgetWorld\(\)': 'zombie/iso/IsoWorld',
            r'\bgetGameTime\(\)': 'zombie/GameTime',
            r'\b(?:o\.userName|o\.Bikuri|self\.userName|self\.Bikuri)\b': 'zombie/ui/TextDrawObject',
        }
        checked, missing, arity = [], [], []
        for pattern, initial_class in roots.items():
            for root in re.finditer(pattern, code):
                pos, classname = root.end(), initial_class
                while True:
                    call = re.match(r'\s*:\s*(\w+)\s*\(', code[pos:])
                    if not call:
                        break
                    name = call[1]
                    line = code.count('\n', 0, pos + call.start(1)) + 1
                    entry = {'line': line, 'class': classname, 'method': name}
                    descriptors = methods(classname).get(name)
                    if not descriptors:
                        missing.append(entry)
                        break
                    checked.append(entry)
                    pos += call.end()
                    args_start = pos
                    depth, commas = 1, 0
                    while pos < len(code) and depth:
                        if code[pos] == ',' and depth == 1:
                            commas += 1
                        depth += (code[pos] == '(') - (code[pos] == ')')
                        pos += 1
                    count = commas + 1 if source[args_start:pos-1].strip() else 0
                    counts = {len(re.findall(r'\[*L[^;]+;|\[*[BCDFIJSZ]', d[1:d.index(')')])) for d in descriptors}
                    if count not in counts:
                        arity.append(dict(entry, arguments=count, signatures=sorted(descriptors)))
                    returns = {d.split(')')[1] for d in descriptors}
                    if len(returns) != 1:
                        break
                    returned = returns.pop()
                    if not returned.startswith('L'):
                        break
                    classname = returned[1:-1]
        result = {'scope': __doc__, 'checked_calls': len(checked),
                'checked': sorted(checked, key=lambda x: x['line']),
                'missing': sorted(missing, key=lambda x: x['line']),
                'arity_mismatches': sorted(arity, key=lambda x: x['line'])}
        # A verified B42 signature change that name/arity checks cannot catch.
        result['typed_literal_mismatches'] = []
        for call in re.finditer(r':(getWornItem|setWornItem)\s*\(\s*([\x22\x27])(.*?)\2', source):
            if code[call.start()] == ':':
                result['typed_literal_mismatches'].append({
                    'line': code.count('\n', 0, call.start()) + 1,
                    'method': call[1], 'literal': call[3],
                    'expected': 'ItemBodyLocation, not a string'})
        for binding in re.finditer(r'\blocal\s+(\w+)\s*=\s*[^\n]*?:getWornItems\(\)', code):
            alias = binding[1]
            following = code[binding.end():]
            boundary = re.search(r'(?m)^function\s', following)
            end = binding.end() + boundary.start() if boundary else len(code)
            scope = source[binding.end():end]
            for use in re.finditer(r'\b' + re.escape(alias) + r'\s*:(getItem|setItem)\s*\(\s*([\x22\x27])(.*?)\2', scope):
                offset = binding.end() + use.start()
                if code[offset:offset + len(alias)] == alias:
                    result['typed_literal_mismatches'].append({
                        'line': code.count('\n', 0, offset) + 1,
                        'method': 'WornItems.' + use[1], 'literal': use[3],
                        'expected': 'ItemBodyLocation, not a string'})
        result['indexed_set_mismatches'] = []
        for binding in re.finditer(r'\blocal\s+(\w+)\s*=\s*[^\n]*?getCell\(\)\s*:\s*(get(?:Object|Add|Remove)List)\(\)', code):
            alias, getter = binding[1], binding[2]
            if not any(d.endswith(')Ljava/util/Set;') for d in methods('zombie/iso/IsoCell').get(getter, ())):
                continue
            # Simple local binding within its containing top-level function.
            following = code[binding.end():]
            boundary = re.search(r'(?m)^function\s', following)
            scope = following[:boundary.start()] if boundary else following
            for use in re.finditer(r'\b' + re.escape(alias) + r'\s*:\s*get\s*\(', scope):
                result['indexed_set_mismatches'].append({
                    'line': code.count('\n', 0, binding.end() + use.start()) + 1,
                    'alias': alias, 'getter': getter,
                    'expected': 'Set has no indexed get; use the Lua snapshot or an iterator'})
        classnames = {}
        for path in jar.namelist():
            if path.startswith('zombie/') and path.endswith('.class'):
                simple = path[:-6].split('/')[-1].split('$')[-1]
                classnames.setdefault(simple, []).append(path[:-6])
        result['static_missing'] = []
        for call in re.finditer(r'\b([A-Z]\w*)\.(\w+)\s*\(', code):
            candidates = classnames.get(call[1], [])
            if len(candidates) == 1:
                name = '<init>' if call[2] == 'new' else call[2]
                if name not in methods(candidates[0]):
                    result['static_missing'].append({'line': code.count('\n', 0, call.start()) + 1,
                                                     'class': candidates[0], 'method': call[2]})
        if inventory:
            public_names = set()
            for path in jar.namelist():
                if path.startswith('zombie/') and path.endswith('.class'):
                    public_names.update(n for k, f, n, d in members(jar.read(path))
                                        if k == 'method' and f & 1)
            lua_names = set()
            for path in Path(lua_path).parents[2].rglob('*.lua'):
                lua_names.update(re.findall(r'function\s+[\w.:]+[:.](\w+)\s*\(', path.read_text(encoding='utf-8-sig')))
            absent = {}
            for call in re.finditer(r':(\w+)\s*\(', code):
                name = call[1]
                if name not in public_names and name not in lua_names:
                    absent.setdefault(name, []).append(code.count('\n', 0, call.start()) + 1)
            result['names_absent_from_game_and_mod_definitions'] = absent
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar')
    parser.add_argument('lua')
    parser.add_argument('--inventory', action='store_true')
    args = parser.parse_args()
    print(json.dumps(audit(args.jar, args.lua, args.inventory), indent=2))
