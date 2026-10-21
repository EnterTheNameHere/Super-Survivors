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
under `Zomboid/mods/SuperbSurvivors/`. For Workshop packaging, copy only `42/`
and `common/` into `Contents/mods/SuperbSurvivors/`. Keep the repository metadata
and `reference/` out of that package. Avoid loading a Workshop copy with the same
mod ID alongside the development copy.

The game mounts versioned and common content under the normal mod paths, so Lua
asset references such as `media/textures/PVPOn.png` stay unchanged.

See [Build 42 port status](docs/B42_PORT.md) for validation commands, the debug
spawn probe, and the remaining compatibility work.
