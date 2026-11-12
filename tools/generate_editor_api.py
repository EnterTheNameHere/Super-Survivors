"""Generate a deliberately limited LuaLS API library from the installed PZ JAR.

Only curated classes/methods are included. Java descriptors supply types and
overloads, not parameter names, nullability, Lua exposure, or documentation.
"""
import argparse
import hashlib
import re
from pathlib import Path
from zipfile import ZipFile

from inspect_game_api import members
from audit_lua_names import code_only

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = 'zombie/Lua/LuaManager$GlobalObject'
FUNCTIONS = {
    'getGameTime': ('Returns the game clock.', []),
    'getNumActivePlayers': ('Returns the number of active local player slots.', []),
    'ZombRand': ('Returns a random integer-valued number; the upper bound is exclusive.', ['minOrMax', 'max']),
    'getCell': ('Returns the loaded world cell.', []),
    'getPlayer': ('Returns the current local player, if present.', []),
    'getSpecificPlayer': ('Returns a local player by zero-based split-screen index.', ['playerIndex']),
    'getTextManager': ('Returns the text rendering and measurement manager.', []),
    'getText': ('Looks up a translation key and substitutes optional arguments.', ['key']),
    'checkSaveFileExists': ('Checks whether the named file exists in the current save.', ['filename']),
    'getTimestampMs': ('Returns the system timestamp in milliseconds.', []),
    'setGameSpeed': ('Sets the game speed code.', ['speed']),
    'getCore': ('Returns the core game settings and display manager.', []),
    'getMouseX': ('Returns the mouse X coordinate.', []),
    'getMouseY': ('Returns the mouse Y coordinate.', []),
    'getActivatedMods': ('Returns the active mod ID list.', []),
    'getWorld': ('Returns the world manager.', []),
    'instanceItem': ('Creates an inventory item from a script item, full type, or item key.', ['itemOrType', 'condition']),
    'triggerEvent': ('Triggers a named Lua event with optional arguments.', ['eventName']),
    'getGameSpeed': ('Returns the current game speed code.', []),
    'getModFileWriter': ('Opens a mod data file for writing.', ['modId', 'filename', 'createIfNull', 'append']),
    'getModFileReader': ('Opens a mod data file for reading.', ['modId', 'filename', 'createIfNull']),
    'getFileReader': ('Opens a file in the Lua cache directory, or returns nil.', ['filename', 'createIfNull']),
    'getFileWriter': ('Opens an allowed data-file extension in the Lua cache directory, or returns nil.', ['filename', 'createIfNull', 'append']),
    'getFileSeparator': ('Returns the platform file separator.', []),
    'isClient': ('Returns whether this process is a multiplayer client.', []),
    'isServer': ('Returns whether this process is a multiplayer server.', []),
    'getTexture': ('Looks up a texture by path.', ['path']),
    'getSoundManager': ('Returns the sound manager.', []),
    'getDebug': ('Returns whether debug mode is enabled.', []),
    'getNumClassFields': ('Returns the number of reflected fields for an object.', ['object']),
    'getClassFieldVal': ('Reads a reflected field on an object.', ['object', 'field']),
    'getClassField': ('Gets a reflected field by index.', ['object', 'index']),
    'addSound': ('Adds a world sound for AI hearing.', ['source', 'x', 'y', 'z', 'radius', 'volume']),
    'sendClientCommand': ('Sends a named command and argument table to the server.', []),
    'moduleDotType': ('Combines a module name and item type.', ['module', 'itemType']),
    'getGametimeTimestamp': ('Returns the game-time timestamp; distinct from the system timestamp.', []),
}
# Empty sets mean constants only; '*' includes public fields and methods.
# Java visibility alone does not establish Lua exposure; see the generated header.
CLASSES = {
    'zombie/iso/IsoGridSquare': {'*'},
    'zombie/iso/areas/IsoRoom': {'*'},
    'zombie/core/GameMode': {'toString'},
    'zombie/Lua/LuaEventManager': {'AddEvent', 'triggerEvent'},
    'zombie/scripting/objects/MoodleType': {'get', 'getTranslationName'},
    'zombie/characters/CharacterStat': {'getById', 'getId', 'getMinimumValue', 'getMaximumValue', 'getDefaultValue'},
    'zombie/characters/skills/PerkFactory$Perks': {'FromString', 'fromIndex', 'getMaxIndex'},
    'zombie/iso/objects/RainManager': {'isRaining', 'getRainIntensity', 'startRaining', 'stopRaining'},
    'zombie/characters/IsoPlayer': {'getInstance', 'getPlayerNum', 'isLocalPlayer', 'getUsername', 'getInventory', 'getStats', 'getBodyDamage', 'getCurrentSquare', 'getX', 'getY', 'getZ', 'isDead', 'isFemale', 'getDisplayName', 'getPerkLevel', 'getModData', 'getDir', 'setDir'},
    'zombie/ui/UIFont': {'FromString'},
    'zombie/iso/IsoDirections': {'fromString', 'fromIndex', 'RotLeft', 'RotRight', 'Rot180', 'dx', 'dy'},
    'zombie/GameTime': {'getInstance', 'getWorldAgeHours', 'getMultiplier', 'getTimeOfDay', 'getHour', 'getMinutes', 'getDay', 'getMonth', 'getYear', 'getNightsSurvived'},
    'zombie/iso/IsoCell': {'getGridSquare', 'getObjectList', 'getZombieList', 'getSurvivorList'},
    'zombie/ui/TextManager': {'getFontHeight', 'MeasureStringX', 'MeasureStringY', 'DrawString', 'DrawStringCentre', 'DrawStringRight'},
    'zombie/core/Core': {'getInstance', 'getScreenWidth', 'getScreenHeight', 'isIngame', 'getDebug', 'getVersionNumber', 'getMyDocumentFolder'},
    'zombie/ui/TextDrawObject': {'new', 'ReadString', 'Draw', 'DrawRaw', 'setDefaultColors', 'setOutlineColors', 'setAllowAnyImage', 'setAllowImages', 'setAllowFonts', 'setAllowBBcode', 'setMaxCharsPerLine', 'getWidth', 'getHeight'},
    'zombie/iso/IsoUtils': {'XToScreen', 'YToScreen', 'XToIso', 'YToIso', 'DistanceTo', 'DistanceToSquared'},
    'zombie/iso/IsoCamera': {'getOffX', 'getOffY', 'getLastOffX', 'getLastOffY', 'getCameraCharacterZ', 'getCameraCharacter', 'setCameraCharacter', 'clearCameraCharacter', 'update'},
    'zombie/characters/SurvivorFactory': {'CreateSurvivor', 'CreateSurvivorGroup', 'getRandomForename', 'getRandomSurname'},
    'zombie/scripting/objects/CharacterTrait': {'get', 'register', 'getName'},
    'zombie/characters/BodyDamage/BodyPartType': {'FromIndex', 'ToIndex', 'FromString', 'ToString', 'getDisplayName'},
    'zombie/scripting/objects/ItemBodyLocation': {'get', 'register'},
    'zombie/pathfind/PathFindBehavior2$BehaviorResult': set(),
    'zombie/characters/skills/PerkFactory': {'getPerkName', 'getPerk', 'getPerkFromName'},
    'zombie/ai/states/SwipeStatePlayer': {'instance', 'ConnectSwing'},
    'zombie/characterTextures/BloodBodyPartType': {'FromIndex', 'ToIndex', 'getDisplayName'},
    'zombie/characterTextures/BloodClothingType': {'fromString', 'getCoveredParts'},
    'zombie/core/ImmutableColor': {'new', 'getRed', 'getGreen', 'getBlue', 'getAlpha', 'getRedFloat', 'getGreenFloat', 'getBlueFloat', 'getAlphaFloat'},
    'zombie/input/Mouse': {'getX', 'getY', 'isLeftDown', 'isRightDown', 'isMiddleDown', 'isButtonDown'},
    'zombie/characters/BodyDamage/Metabolics': {'getMet', 'getBtuHr', 'getWm2', 'getW'},
    'zombie/iso/objects/IsoBarricade': {'GetBarricadeForCharacter', 'GetBarricadeOppositeCharacter', 'AddBarricadeToObject', 'addPlank', 'addMetal', 'getNumPlanks'},
    'zombie/characters/CharacterActionAnims': set(),
    'zombie/iso/IsoWorld': {'getCell', 'getWorld', 'getGameMode', 'getWorldAgeDays'},
    'zombie/Lua/LuaManager$GlobalObject$LuaFileWriter': {'write', 'writeln', 'close'},
}

# Verified additions from the undefined-field review. Keep these explicit rather
# than accepting arbitrary members on native objects.
for path, names in {
    'zombie/core/Core': 'getZoom getKey getGameVersion isDisplayPlayerModel',
    'zombie/characters/IsoPlayer': (
        'new getCoopPVP setCoopPVP Say setInstance setLocalPlayer initSpritePartsEmpty '
        'getPrimaryHandItem getSecondaryHandItem setPrimaryHandItem setSecondaryHandItem '
        'isOutside isAiming CanSee getDescriptor getBuilding getBeenMovingFor isAsleep '
        'forceAwake hasTrait removeFromHands setWornItem isInvisible isSpriteInvisible '
        'getDoRender setAlphaAndTarget getMoodles setSceneCulled'),
    'zombie/characters/BodyDamage/BodyPartType': 'index getPainModifyer',
    'zombie/ui/TextDrawObject': 'setDefaultFont',
    'zombie/characters/SurvivorFactory': 'randomName',
    'zombie/inventory/InventoryItem': 'getCount',
    'zombie/inventory/ItemContainer': 'AddItem DoRemoveItem Remove getItemFromTypeRecurse',
    'zombie/iso/IsoObject': 'setHighlightColor setHighlighted',
    'zombie/iso/objects/IsoDeadBody': 'getModData',
    'zombie/iso/IsoWorld': 'registerZone getMetaGrid',
    'zombie/input/Mouse': 'isLeftPressed',
    'zombie/BaseSoundManager': 'PlaySound',
}.items():
    CLASSES.setdefault(path, set()).update(names.split())

# These core types use public signatures whose names occur in mod call sites.
# This expands useful coverage without emitting every Java method or treating
# arbitrary member names as valid. Return types remain the real Java types.
for path in (
    'zombie/characters/IsoPlayer', 'zombie/inventory/InventoryItem',
    'zombie/inventory/ItemContainer', 'zombie/iso/IsoObject',
    'zombie/iso/objects/IsoDeadBody', 'zombie/characters/Stats',
    'zombie/characters/BodyDamage/BodyDamage', 'zombie/characters/Moodles/Moodles',
    'zombie/pathfind/PathFindBehavior2', 'zombie/iso/objects/IsoDoor',
    'zombie/iso/objects/IsoWindow', 'zombie/characters/SurvivorDesc',
    'zombie/core/GameVersion', 'zombie/iso/areas/IsoBuilding',
    'zombie/iso/BuildingDef', 'zombie/iso/IsoMetaGrid', 'zombie/iso/zones/Zone',
    'zombie/characters/traits/CharacterTraits', 'zombie/inventory/types/HandWeapon',
    'zombie/inventory/types/InventoryContainer', 'zombie/inventory/types/Key',
    'zombie/core/Core', 'zombie/iso/objects/IsoBarricade',
    'zombie/iso/IsoCell', 'zombie/characterTextures/BloodBodyPartType',
    'zombie/characters/WornItems/WornItems',
    'zombie/characters/BodyDamage/Thermoregulator',
    'zombie/characters/BodyDamage/Nutrition', 'zombie/iso/objects/IsoTree',
    'zombie/characters/IsoGameCharacter$XP',
    'zombie/core/skinnedmodel/visual/BaseVisual',
    'zombie/core/skinnedmodel/visual/HumanVisual', 'zombie/iso/objects/IsoThumpable',
):
    CLASSES.setdefault(path, set()).add('@used')


def generate(jar_path):
    references = set()
    parents = {}
    source_hash = hashlib.sha256()
    used_methods = set()
    for path in sorted((ROOT / '42/media/lua').rglob('*.lua')):
        source = path.read_bytes()
        source_hash.update(path.relative_to(ROOT).as_posix().encode() + b'\0' + source + b'\0')
        used_methods.update(re.findall(r'[:.]\s*([A-Za-z_]\w*)\s*\(', code_only(source.decode('utf-8-sig'))))

    def name(path):
        if path == 'zombie/characters/skills/PerkFactory$Perks':
            return 'Perks'
        if path == 'zombie/pathfind/PathFindBehavior2$BehaviorResult':
            return 'BehaviorResult'
        return path.rsplit('/', 1)[-1].replace('$', '_')

    def type_of(descriptor):
        if descriptor.startswith('['):
            return type_of(descriptor[1:]) + '[]'
        if descriptor.startswith('L'):
            path = descriptor[1:-1]
            known = {'java/lang/String': 'string', 'java/lang/Object': 'any',
                     'java/lang/Boolean': 'boolean', 'se/krka/kahlua/vm/KahluaTable': 'table'}
            if path in known:
                return known[path]
            references.add(path)
            return name(path)
        return {'V': 'nil', 'Z': 'boolean', 'F': 'number', 'D': 'number'}.get(descriptor, 'integer')

    def signature(descriptor):
        args, result = descriptor[1:].split(')')
        return [type_of(t) for t in re.findall(r'\[*L[^;]+;|\[*[ZBCSIJFD]', args)], type_of(result)

    def emit_method(owner, method, overloads, doc='', labels=()):
        out = [f'---{doc}'] if doc else []
        # The primary declaration and overloads preserve Java arity/types.
        def params(entry):
            flags, descriptor = entry
            types, result = signature(descriptor)
            names = [labels[i] if i < len(labels) else f'arg{i + 1}' for i in range(len(types))]
            if flags & 0x80 and types:
                names[-1], types[-1] = '...', types[-1].removesuffix('[]')
            return names, types, result
        for entry in overloads[1:]:
            names, types, result = params(entry)
            self_arg = [f'self: {owner}'] if owner and not entry[0] & 8 else []
            args = self_arg + [f'{n}: {t}' for n, t in zip(names, types)]
            out.append(f'---@overload fun({", ".join(args)}): {result}')
        names, types, result = params(overloads[0])
        out += [f'---@param {n} {t}' for n, t in zip(names, types)]
        if method in ('getPlayer', 'getSpecificPlayer', 'getFileReader', 'getFileWriter') or (owner == 'IsoCamera' and method == 'getCameraCharacter'):
            result += '|nil'
        if result != 'nil':
            out.append(f'---@return {result}')
        prefix = owner + ('.' if overloads[0][0] & 8 else ':') if owner else ''
        out.append(f'function {prefix}{method}({", ".join(names)}) end\n')
        return out

    with ZipFile(jar_path) as jar:
        def read(path):
            metadata = {}
            entries = list(members(jar.read(path + '.class'), metadata))
            return entries, metadata

        lines = ['---@meta', '-- Generated by tools/generate_editor_api.py; EDITOR ONLY. Do not require this file.',
                 '-- Partial API. Java signatures do not guarantee Lua exposure or non-nil returns.',
                 '-- JAR SHA-256: ' + hashlib.sha256(jar_path.read_bytes()).hexdigest(),
                 '-- Mod Lua SHA-256 (call-name selection): ' + source_hash.hexdigest(), '']
        entries, _ = read(GLOBAL)
        for method, (doc, labels) in FUNCTIONS.items():
            overloads = [(f, d) for k, f, n, d in entries if k == 'method' and n == method and f & 1]
            if not overloads:
                raise ValueError(f'Missing requested global: {method}')
            lines += emit_method(None, method, overloads, doc, labels)

        lines += ['---Tests whether a Java object is an instance of the named exposed class.',
                  '---Lua binding name for GlobalObject.isType(Object, String).',
                  '---@param object any', '---@param className string', '---@return boolean',
                  'function instanceof(object, className) end', '']
        # Confirm the underlying binding target still exists.
        assert any(n == 'isType' and d == '(Ljava/lang/Object;Ljava/lang/String;)Z' for _, _, n, d in entries)

        for path, allowed in CLASSES.items():
            owner = name(path)
            entries, metadata = read(path)
            coverage = 'Public Java API' if '*' in allowed else 'Partial definition'
            parent = metadata['superclass']
            suffix = ''
            if parent and parent.startswith('zombie/'):
                references.add(parent)
                suffix = ': ' + name(parent)
            lines += [f'---{coverage} of {path.replace("/", ".")}.', f'---@class {owner}{suffix}']
            for kind, flags, field, descriptor in entries:
                if kind == 'field' and flags & 1 and (flags & 8 or '*' in allowed) and re.fullmatch(r'[A-Za-z_]\w*', field):
                    lines.append(f'---@field {field} {type_of(descriptor)}')
            lines += [f'{owner} = {{}}', '']
            found = {}
            parent_path = path
            interfaces = []
            # Include inherited signatures for the explicitly selected method names.
            while True:
                interfaces.extend(metadata['interfaces'])
                for kind, flags, method, descriptor in entries:
                    if kind == 'method' and flags & 1 and method == '<init>' and 'new' in allowed and parent_path == path:
                        found.setdefault('new', []).append((flags | 8, descriptor[:-1] + 'L' + path + ';'))
                    if (kind == 'method' and flags & 1 and not flags & 0x1040
                            and (method in allowed or ('@used' in allowed and method in used_methods)
                                 or ('*' in allowed and re.fullmatch(r'[A-Za-z_]\w*', method)))):
                        overload = (flags, descriptor)
                        if overload not in found.setdefault(method, []):
                            found[method].append(overload)
                parent = metadata['superclass']
                if not parent or parent.startswith('java/'):
                    break
                parents[parent_path] = parent
                references.add(parent)
                parent_path = parent
                entries, metadata = read(parent)
            # Java default/interface methods may not be declared on the class.
            visited = set()
            while interfaces:
                interface = interfaces.pop()
                if interface in visited or interface + '.class' not in jar.namelist():
                    continue
                visited.add(interface)
                entries, metadata = read(interface)
                interfaces.extend(metadata['interfaces'])
                for kind, flags, method, descriptor in entries:
                    if (kind == 'method' and flags & 1 and not flags & (8 | 0x1040)
                            and (method in allowed or ('@used' in allowed and method in used_methods)
                                 or ('*' in allowed and re.fullmatch(r'[A-Za-z_]\w*', method)))):
                        overload = (flags, descriptor)
                        if overload not in found.setdefault(method, []):
                            found[method].append(overload)
            for method, overloads in sorted(found.items()):
                lines += emit_method(owner, method, overloads)

        # Event names in the engine's registry; callback argument types are not encoded here.
        _, metadata = read('zombie/Lua/LuaEventManager')
        events = sorted({s for s in metadata['pool'] if isinstance(s, str)
                         and re.fullmatch(r'(?:On|Every)[A-Z]\w*|LoadGridsquare|RenderOpaqueObjectsInWorld', s)})
        lines += ['---@class PZEvent', '---@field Add fun(callback: fun(...: any))',
                  '---@field Remove fun(callback: fun(...: any))', '',
                  '---Built-in engine events. Callback signatures are currently unspecified.',
                  '---@class PZEvents']
        lines += [f'---@field {event} PZEvent' for event in events]
        lines += ['Events = {}', '']
        # Standard Java types live in the JRE, not in the game JAR. These small
        # hand-maintained contracts are distinct from the extracted game API.
        lines += ['---Standard java.util.List contract (element type unspecified).',
                  '---@class List', '---@field size fun(self: List): integer',
                  '---@field get fun(self: List, index: integer): any',
                  '---@field contains fun(self: List, value: any): boolean',
                  '---@field isEmpty fun(self: List): boolean',
                  '---@field add fun(self: List, valueOrIndex: any, value?: any): boolean|nil # add(value) or add(zeroBasedIndex, value).',
                  '---@field set fun(self: List, index: integer, value: any): any # Replaces an element; returns the previous value.',
                  '---@field remove fun(self: List, indexOrValue: any): any # Java overloads remove(index) and remove(object) have different results.',
                  '---@field clear fun(self: List)',
                  '---@field indexOf fun(self: List, value: any): integer # Zero-based index, or -1 when absent.',
                  '---@field lastIndexOf fun(self: List, value: any): integer # Zero-based index, or -1 when absent.', '',
                  '---Standard java.util.ArrayList contract. Indices start at zero; element types are unspecified.',
                  '---@class ArrayList: List',
                  '---@field ensureCapacity fun(self: ArrayList, minCapacity: integer)',
                  '---@field trimToSize fun(self: ArrayList)', '',
                  '---Standard java.util.Set contract (element type unspecified).',
                  '---@class Set', '---@field contains fun(self: Set, value: any): boolean',
                  '---@field size fun(self: Set): integer',
                  '---@field isEmpty fun(self: Set): boolean', '',
                  '---Standard java.lang.reflect.Field name accessor.',
                  '---@class Field', '---@field getName fun(self: Field): string', '',
                  '---Standard java.io.BufferedReader contract.',
                  '---@class BufferedReader',
                  '---@field readLine fun(self: BufferedReader): string|nil',
                  '---@field close fun(self: BufferedReader)', '']
        # Opaque return/argument types, deliberately without fabricated members.
        for path in sorted(references - CLASSES.keys() - {
                'java/util/List', 'java/util/ArrayList', 'java/util/Set',
                'java/lang/reflect/Field', 'java/io/BufferedReader'}):
            suffix = ': ' + name(parents[path]) if path in parents else ''
            lines += [f'---Opaque Java type: {path.replace("/", ".")}.', f'---@class {name(path)}{suffix}', '']
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jar', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'editor/pz-api/library.lua')
    args = parser.parse_args()
    result = generate(args.jar)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding='utf-8')
    print(f'Wrote {len(result.splitlines())} lines to {args.output}')


if __name__ == '__main__':
    main()
