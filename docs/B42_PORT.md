# Build 42 port status

Target: Project Zomboid 42.21, initially single-player. This is still B41 gameplay
code in B42 packaging. No game client is installed in the cloud environment.

## First increment: dependencies and a spawn probe

Fixed the survivor -> preset -> group-manager -> group require paths, made the
translation/dialogue/name prerequisites explicit, and removed the unused
`CharacterSave_SaveLoad` require from the context menu. Character saving still
uses the existing `SuperSurvivor:SaveSurvivor` path; persistence has not migrated.

Seven isolated Lua tests cover the real survivor dependency chain, context-menu
registration, and the debug probe's preconditions/delegation/error propagation.
Game-provided services are mocked. These tests do not exercise the NPC constructor
or establish that all mod files load inside Kahlua.

Run from the checkout with Python and `lupa==2.6`:

```sh
python -m unittest discover -s tests -v
```

## In-game check

1. Use a fresh disposable 42.21 single-player world with only this mod enabled.
   Start the game with `-debug`. Avoid a second Workshop copy of the same mod.
2. Record any loading/initialization errors from `Zomboid/console.txt` first.
   Stop and investigate the first relevant stack trace if initialization fails.
3. Once the player is in the world, run in the debug Lua console:

   ```lua
   SuperbSurvivorsDebug.spawn()
   ```

   This requests one survivor two tiles east, on the player's floor, only if the
   tile is loaded, free and has a floor. To choose a tile explicitly:

   ```lua
   SuperbSurvivorsDebug.spawn(x, y, z)
   ```

4. A successful call returns the survivor wrapper and logs its ID and position.
   Confirm that the character is visible and remains present without recurring
   errors. The command uses the existing constructor, so it is not an isolated
   AI mode and can trigger legacy initialization behavior.
5. Record the exact game version, command, observed behavior, and first full
   relevant error stack. Constructor exceptions deliberately propagate.

Nothing spawns automatically from the new debug module. Existing random/preset
spawning remains unchanged. Repeated calls deliberately create additional NPCs;
the probe does not provide cleanup or save-migration guarantees.

## Remaining work

- Validate startup events and replace obsolete moodle/trait/API references.
  `SuperSurvivorSpeakConditions.lua` still builds old moodle lookups with
  `loadstring`; this has not been ported.
- Verify the survivor constructor, NPC flags and registration against 42.21.
- Verify movement, combat, animations and the bundled Java bytecode.
- Rebase copied vanilla actions and UI onto the target game's implementations;
  inventory and action authority need particular attention.
- Implement versioned, server-owned global mod data for groups and the survivor
  registry. Full character serialization is a separate requirement.
- Port fluids, farming, jobs and multiplayer synchronization after the core.

The historical files under `reference/` are not runtime defaults and must stay
out of release packages. See [the local handoff](LOCAL_HANDOFF.md) for continuing
in VS Code with a local Codex session.
