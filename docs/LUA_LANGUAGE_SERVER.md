# VS Code Lua Language Server

Open the repository root in VS Code with the `sumneko.lua` extension enabled.
The workspace settings in `.vscode/settings.json` index the installed game's
`media/lua/shared`, `client`, and `server` directories as external libraries.
This enables completion and navigation for vanilla Lua globals and required
modules without copying or shipping game source. Mod require paths are included
and the runtime is set to Lua 5.1, the closest language setting to PZ's Kahlua.

The installation path currently points to
`G:/Steam/steamapps/common/ProjectZomboid`. Change the three library paths if
Steam moves the installation. After changing them, run **Lua: Restart Language
Server** from the VS Code command palette (or reload the window).

Library diagnostics are disabled to avoid reporting problems in vanilla source;
diagnostics remain enabled for mod code. Generated save data, historical data,
Python tools, and build output are excluded from Lua workspace analysis.

## Java API definitions

`editor/pz-api/library.lua` provides editor-only definitions for the requested
native globals, selected methods of their return types, and engine event names.
It uses `---@meta` and is registered as a LuaLS library. Never require it from
runtime Lua. The release builder only packages `42/` and `common/media/`, so the
definitions cannot enter the release.

Regenerate after updating the game:

```powershell
.\.venv\Scripts\python.exe tools/generate_editor_api.py 'G:\Steam\steamapps\common\ProjectZomboid\projectzomboid.jar'
```

The generator reads Java signatures and records the JAR's SHA-256. Overloads and
constant names come from the installed game; selected globals have handwritten
descriptions and meaningful parameter names. Other parameter names are placeholders.
This is a partial API, not a complete model of every class. Referenced types
without supplied methods are explicitly opaque. Java signatures do not describe
nullability or guarantee Lua exposure. `getPlayer` and `getSpecificPlayer` are
explicitly nullable. `instanceof` is the Lua binding for Java `isType`.

`IsoGridSquare` includes all public fields and method signatures declared in the
installed game class, so returned squares support member completion and argument
checking. This reflects Java visibility; it does not independently prove that
every member is exposed to Lua. Types returned by square methods can still be
opaque until their own definitions are added.

`Events` lists engine registry names with `Add` and `Remove`, but callback
parameters are currently unspecified. Custom mod events need their own
definitions. Undefined-global diagnostics remain enabled. LuaLS sees client and
server libraries together; completion does not prove availability in a context.

See [the undefined-name review](UNDEFINED_NAMES_REVIEW_2026-11-12.md) for the
expanded API coverage, actual scope bugs fixed, and external/obsolete names
deliberately left unresolved.

The [undefined-field review](UNDEFINED_FIELDS_REVIEW_2026-11-12.md) records
inherited/interface API coverage and the remaining base/subclass mismatches.
Selected core types now include verified public signatures whose names appear
in mod call sites; the generated header records a hash of that Lua source as
well as the JAR. Regenerate after introducing calls to further native methods.

The [nil-safety review](NIL_SAFETY_REVIEW_2026-11-12.md) records the
`need-check-nil` pass, fixes for unavailable actors/UI data, and validation limits.

The [duplicate-field review](DUPLICATE_FIELDS_REVIEW_2026-11-12.md) distinguishes
the fixed heading assignment, narrowly annotated chained overrides, and the
remaining full vanilla action replacements whose warnings stay enabled.

The names `MyHeadArmor`, `MyBodyArmor`, `MyArmArmor`, `MyHandArmor`,
`MyShieldArmor`, `MyLegArmor`, and `MyFeetArmor` occur only as reads in the two
legacy survivor info panels. No definitions were found in current mod or vanilla
Lua. They are not declared by these stubs: warnings should continue to flag that
unresolved legacy dependency rather than present it as a supported game API.
