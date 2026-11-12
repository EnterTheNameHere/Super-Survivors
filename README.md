# Superb Survivors — Build 42 port

The `B42` branch is a port in progress. The versioned folder layout does not
establish gameplay or API compatibility with Build 42.

## Layout

- `42/mod.info` and `42/poster.png`: Build 42 mod metadata.
- `42/media/`: Lua, item scripts, maps, and animation overrides.
- `common/media/`: shared textures and sounds.
- `42/zombie/`: preserved legacy Java bytecode; compatibility and loading still
  need investigation before release.
- `reference/`: historical save and options files, preserved for investigation.
  These are not runtime defaults and must not be included in release packages.

This checkout represents a single mod folder. For local development, place it
under `Zomboid/mods/SuperbSurvivors/`. For Workshop packaging, use
`python tools/build_mod.py` to create a local ZIP with
`Contents/mods/SuperbSurvivors/` layout, excluding debug helpers and generated
save data. Avoid loading a Workshop copy with the same
mod ID alongside the development copy.

The game mounts versioned and common content under the normal mod paths, so Lua
asset references such as `media/textures/PVPOn.png` stay unchanged.

See [Build 42 port status](docs/B42_PORT.md) for validation commands, the debug
spawn probe, and the remaining compatibility work.

The [whole-codebase review](docs/CODEBASE_PORT_REVIEW_2026-11-10.md) and
[file-by-file porting guide](docs/FILE_GUIDE_2026-11-10.md) describe the current
architecture, prioritized defects, subsystem risks and verification limits.
The [focused vanilla replacement review](docs/VANILLA_OVERRIDES_REVIEW_2026-11-10.md)
compares copied actions/UI and method hooks with the installed game.

See [development scenarios](docs/DEVELOPMENT_SCENARIOS.md) for the debug station
runner and the release packaging boundary.

See [Lua Language Server setup](docs/LUA_LANGUAGE_SERVER.md) for VS Code completion
and navigation using the installed game's Lua source.

The [Lua duplication review](docs/LUA_DUPLICATION_REVIEW_2026-11-10.md) records
clone candidates within the mod and against installed vanilla, with a repeatable scanner.
