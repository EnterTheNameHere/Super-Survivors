# SSR-PERSIST-01 — clean native B42 persistence

FROM: Orchestrator
TO: Local Codex implementer
STATUS: REQUESTED / not acknowledged
CANONICAL COORDINATION REF: B42
SOURCE: EnterTheNameHere/Super-Survivors
WORK BRANCH: implement on exclusively owned branch based on B42; report chosen branch and parent.
SCOPE: B42 single-player, clean newly created worlds, persistence + stable registry only.

## Objective
Replace legacy mod-directory survivor/group metadata save files with native **per-world persistence**. There are no public B42 users or B42 save compatibility requirements. Do not write migration code or legacy loading, retain old reference files only as history. A new world should start with correct fresh data and later save/reload the same records correctly.

## Investigate installed B42 first
- Verify actual installed game version and inspect installed Lua + Java APIs.
- Verify Global ModData support: `ModData.getOrCreate`, `ModData.get`, `Events.OnInitGlobalModData` (newGame), `Events.OnSave`; decide correct ownership/lifecycle based on installed implementation.
- Review https://projectzomboid.com/modding/zombie/world/moddata/GlobalModData.html and https://demiurgequantified.github.io/ProjectZomboidLuaDocs/md_Events.html as *references*, not substitutes for installed version evidence.
- Verify current `IsoPlayer:save` / `load` behavior for mod-created NPCs, actual path, fields restored (health, inventory, skills, equipment, appearance), and safe unload/reload hooks. Do not reimplement native character serializer without reason. No Java-side modifications.

## Required behavior
- Persistent world-owned global registry with explicit schema version, stable never-accidentally-reused survivor IDs, group IDs, dynamic survivors/groups, named group areas, location records, loaded/unloaded/dead lifecycle.
- Do not instantiate six default groups just because manager loads; scenario-owned groups may be created by their scenario.
- No fixed group slots, contiguous file scanning, positional areas, old SurvivorLocX/Y/Z text-file storage, mod-dir world save writer, or on-render-count/Escape saving for registry.
- Separate live NPC runtime objects from persistent serializable data; unloaded survivor has record without forcing live IsoPlayer.
- Keep persisted vs last-observed state distinguishable. Reconcile registry with character save records on reload; report inconsistencies; do not silently invent survivors.
- Use supported engine save lifecycle; world copy/delete should carry the complete mod state.
- Account for consistency between world registry and separately serialized characters. No artificial guarantees of atomic saving if engine doesn't offer them.
- Do not implement new AI manager, inspector or test UI within this scope.

## Validation
Run automated checks, but distinguish them from in-game tests. Provide specific manual test instructions for disposable new PZ world:
1. Create two groups (including empty group), several survivors.
2. Save / exit / restart / reload; check IDs/group membership and character state (health, inventory, equipment, skills, positions).
3. Unload/reload survivors; kill one and reload; verify dead isn't respawned.
4. Repeat saves; check no duplicate IDs.
5. Copy full world-save folder to another save slot; verify independence and absence of old mod-directory dependencies.

## Delivery
Send addressed completion/blocker message to `ai-workflow/mail/orchestrator/inbox/` including branch/commit/parent, changed files, verified API evidence from installed B42, tests run + results, in-game validations actually performed (if any), shortcomings and needed decisions. Update state. Do not claim acceptance or merge to B42 without orchestrator review.
