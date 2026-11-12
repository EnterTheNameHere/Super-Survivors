"""Inventory colon-call names across mod Lua against game Java and Lua definitions.

Candidates require review: this does not infer receivers, argument types, Lua
exposure, dynamic Lua assignments, lifecycle compatibility, or global functions.
"""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from inspect_game_api import members


def code_only(source):
    tokens = r'--\[(=*)\[[\s\S]*?\]\1\]|--[^\n]*|\[(=*)\[[\s\S]*?\]\2\]|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27'
    return re.sub(tokens, lambda m: re.sub(r'[^\n]', ' ', m[0]), source)


def inventory(game, root):
    public, lua_names = set(), set()
    with ZipFile(game / 'projectzomboid.jar') as jar:
        for path in jar.namelist():
            if path.startswith('zombie/') and path.endswith('.class'):
                public.update(n for k, f, n, d in members(jar.read(path))
                              if k == 'method' and f & 1)
    sources = {}
    for directory in (game / 'media/lua', root):
        for path in directory.rglob('*.lua'):
            code = code_only(path.read_text(encoding='utf-8-sig', errors='replace'))
            lua_names.update(re.findall(r'function\s+[\w.:]+[:.](\w+)\s*\(', code))
            # Vanilla also defines methods with Table.method = function(...).
            lua_names.update(re.findall(r'[\w.]+\.(\w+)\s*=\s*function\s*\(', code))
            if directory == root:
                sources[path] = code
    candidates = []
    for path, code in sorted(sources.items()):
        for call in re.finditer(r':(\w+)\s*\(', code):
            if call[1] not in public | lua_names | {'gmatch', 'gsub', 'match'}:
                candidates.append({'file': path.as_posix(),
                                   'line': code.count('\n', 0, call.start()) + 1,
                                   'method': call[1]})
    return {'scope': __doc__, 'files': len(sources), 'candidates': candidates}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('root', type=Path, nargs='?', default=Path('42/media/lua'))
    args = parser.parse_args()
    print(json.dumps(inventory(args.game, args.root), indent=2))
