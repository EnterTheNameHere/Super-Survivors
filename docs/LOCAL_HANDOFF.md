# Local Codex handoff

Repository: `EnterTheNameHere/Super-Survivors`, branch `B42`.

## Current state

This branch began as a copy of the B41 mod. The cloud work has:

- Moved version-specific content into `42/`, textures and sounds into
  `common/media/`, and old save/options artifacts into `reference/`.
- Changed `42/mod.info` to `versionMin=42.0`; this is metadata, not proof of
  compatibility. The mod ID remains `SuperbSurvivors`.
- Fixed stale require paths and explicit dialogue/translation/name dependencies.
- Removed an unused require for the absent `CharacterSave_SaveLoad` module.
- Added `SuperbSurvivorsDebug.spawn()` for a manual, debug-only single-player
  spawn check. It spawns nothing automatically and preserves constructor errors.
- Added seven isolated regression checks in `tests/test_startup.py`.

All 109 Lua files passed Lua 5.1 syntax checks and all seven tests passed in the
cloud. The tests mock game services. No game client was available; no in-game
loading, NPC creation, combat, persistence or multiplayer claim has been verified.

## Set up on Windows

Clone the branch and open its folder in VS Code:

```bat
git clone --branch B42 https://github.com/EnterTheNameHere/Super-Survivors.git
cd Super-Survivors
code .
```

For an existing checkout, preserve local work, fetch, switch to `B42`, and pull
with `--ff-only` instead of cloning another copy.

Install the official OpenAI Codex extension, sign in, and select local execution.
The local session has its own permissions; it does not inherit this chat's tool
access or conversation. The native x64 command prompt is suitable. A Python 3
installation is needed only for the isolated checks:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install lupa==2.6
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools\check_lua.py
```

## First local task

1. Locate the installed game and record the exact version. The agreed initial
   target is 42.21; verify that against the actual installation. Inspect its Lua
   files and Java API instead of relying on the older 42.20.2 community mirror.
2. Copy only `42/` and `common/` into
   `%USERPROFILE%\Zomboid\mods\SuperbSurvivors\`. These are copies: recopy changed
   files after edits, removing obsolete files from this development copy as needed.
   Do not copy `reference/`, `.git/`, tests or tools. Disable other copies of this
   mod, including Workshop copies with the same ID.
3. Follow `B42_PORT.md`: use a fresh disposable single-player world, launch with
   `-debug`, fix the first startup exception, then run
   `SuperbSurvivorsDebug.spawn()` in the debug Lua console.
4. Inspect `%USERPROFILE%\Zomboid\console.txt` (or the configured game cache
   directory), preserving the full first relevant stack and the game version.
   Continue until one survivor can spawn and remain present without recurring
   errors, then work on following/navigation and combat.

The game can use a custom cache path; confirm paths before copying or reading
logs. Do not overwrite an existing mod installation or valuable save blindly.

## Decisions to preserve

- Port incrementally, initially single-player, while designing server-owned state.
- Do not mask API failures with broad error suppression or disable meaningful
  behavior merely to make loading appear successful.
- Replace old group/location text files with versioned global mod data under a
  `SuperbSurvivors` namespace: named areas, stable survivor IDs, rebuilt location
  indexes, and explicit multiplayer synchronization. This is not implemented yet.
- Full NPC serialization (inventory, appearance, health, skills) is separate from
  registry metadata; `ModData` does not automatically serialize live NPC objects.
- Keep historical save artifacts for reference and exclude them from releases.

Known work includes old moodle/trait/API references, `loadstring` moodle lookups,
copied vanilla timed actions and UI, fluids, farming, and Java/animation overrides.
The bundled `42/zombie/.../Attack.class` is preserved, not validated. Existing
random/preset spawning and legacy saving still run; the debug command does not
isolate the entire mod or guarantee save compatibility.

## Prompt for the local Codex session

> Read README.md, docs/LOCAL_HANDOFF.md and docs/B42_PORT.md. Continue the B42 port
> from the startup/spawn milestone. Inspect the local Project Zomboid installation
> and console.txt, confirm the actual game version, and fix the first reproducible
> loading or spawn failure. Preserve the agreed persistence design and distinguish
> isolated tests from real in-game validation. Ask me to launch/test the game when
> needed, then inspect the resulting logs.
