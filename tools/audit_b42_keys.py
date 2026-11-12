"""Read-only inventory of fixed item IDs, typed constants and old recipe blocks.

Uses installed scripts/JAR, not an online list. Does not infer dynamic strings,
receiver types, imported mod catalogs, action behavior or crafting compatibility.
"""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from inspect_game_api import members


LUA_TOKENS = r'--\[(=*)\[[\s\S]*?\]\1\]|--[^\n]*|\[(=*)\[[\s\S]*?\]\2\]|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27'


def without_comments(source):
    return re.sub(LUA_TOKENS, lambda m: re.sub(r'[^\n]', ' ', m[0])
                  if m[0].startswith('--') else m[0], source)


def item_catalog(directory):
    result = {}
    for path in directory.rglob('*.txt'):
        source = path.read_text(encoding='utf-8-sig', errors='replace')
        source = re.sub(r'/\*[\s\S]*?\*/|//[^\n]*', '', source)
        # Assign each declaration to its preceding module. Generated item files
        # have one module; sequential multi-module files are supported too.
        module = None
        for match in re.finditer(r'\b(module|item)\s+(\w+)\s*\{', source):
            if match[1] == 'module':
                module = match[2]
            elif module:
                result[module + '.' + match[2]] = str(path)
    return result


def audit(game, root):
    catalog = item_catalog(game / 'media/scripts') | item_catalog(root / 'scripts')
    classes = {'Perks': 'zombie/characters/skills/PerkFactory$Perks'}
    names = ['CharacterStat', 'CharacterTrait', 'MoodleType', 'ItemTag', 'ItemBodyLocation']
    with ZipFile(game / 'projectzomboid.jar') as jar:
        for name in names:
            matches = [path[:-6] for path in jar.namelist() if path.endswith('/' + name + '.class')]
            if len(matches) == 1:
                classes[name] = matches[0]
        fields = {name: {n for k, f, n, d in members(jar.read(cls + '.class'))
                         if k == 'field' and f & 1 and f & 8}
                  for name, cls in classes.items()}
    missing_items, missing_constants, missing_perks = [], [], []
    paths = list((root / 'lua').rglob('*.lua'))
    for path in paths:
        source = without_comments(path.read_text(encoding='utf-8-sig'))
        def entry(match, key):
            return {'file': path.as_posix(), 'line': source.count('\n', 0, match.start()) + 1, 'key': key}
        for match in re.finditer(r'[\x22\x27]((?:Base|farming|Survivors)\.[A-Za-z0-9_]+)[\x22\x27]', source):
            if match[1] not in catalog:
                missing_items.append(entry(match, match[1]))
        # Selected item-only tables also contain unqualified Base item names.
        table_pattern = (r'\b(?:MeleeWeapons|RangeWeapons|SuperSurvivorsAmmoBoxes|CannedFoods'
                         r'|SurvivorRandomSuits(?:\[[^\]\n]+\])+)' + r'\s*=\s*\{([^}]+)\}')
        for table in re.finditer(table_pattern, source):
            for match in re.finditer(r'[\x22\x27](\w+)[\x22\x27]', table[1]):
                key = 'Base.' + match[1]
                if key not in catalog:
                    offset = table.start(1) + match.start()
                    missing_items.append({'file': path.as_posix(), 'line': source.count('\n', 0, offset) + 1,
                                          'key': key, 'unqualified': True})
        # Mask strings as well for actual constant references.
        code = re.sub(LUA_TOKENS, lambda m: re.sub(r'[^\n]', ' ', m[0]), source)
        for match in re.finditer(r'\b(' + '|'.join(fields) + r')\.(\w+)\b(?!\s*\()', code):
            if match[2] not in fields[match[1]]:
                missing_constants.append(entry(match, match[1] + '.' + match[2]))
        for match in re.finditer(r'Perks\.FromString\(\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]\s*\)', source):
            if match[1] not in fields['Perks']:
                missing_perks.append(entry(match, match[1]))
        table = re.search(r'\bSurvivorPerks\s*=\s*\{([^}]+)\}', source)
        if table:
            for match in re.finditer(r'[\x22\x27](\w+)[\x22\x27]', table[1]):
                if match[1] not in fields['Perks']:
                    missing_perks.append({'file': path.as_posix(), 'key': match[1], 'table': 'SurvivorPerks'})
    recipes = []
    for path in (root / 'scripts').rglob('*.txt'):
        for match in re.finditer(r'\brecipe\s+([^\r\n{]+)\s*\{', path.read_text(encoding='utf-8-sig')):
            recipes.append({'file': path.as_posix(), 'recipe': match[1].strip()})
    return {'scope': __doc__, 'lua_files': len(paths), 'missing_item_ids': missing_items,
            'missing_typed_constants': missing_constants, 'missing_perk_names': missing_perks,
            'legacy_recipe_blocks': recipes}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', type=Path)
    parser.add_argument('--root', type=Path, default=Path('42/media'))
    args = parser.parse_args()
    print(json.dumps(audit(args.game, args.root), indent=2))
