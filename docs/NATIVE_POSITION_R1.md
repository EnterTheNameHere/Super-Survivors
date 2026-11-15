# PERSIST-01 R1: native position and lifecycle investigation

15 November 2026. Authoritative request: the R1 clarification and SSR-TEST-01 on
canonical B42, acknowledged from source head d585676 on codex/persistence-b42.
The earlier mandatory optimization request is superseded. **No persistence
scan/unload rewrite was made.** Findings below are source evidence and proposed
follow-up, not actual gameplay observations or acceptance of SSR-PERSIST-01.

## Inspected build and method

Installed `G:\Steam\steamapps\common\ProjectZomboid`, version **42.22.2**, revision
3d39148846. projectzomboid.jar SHA-256:
`3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287`.

Version API follow-up: Core.getGameVersion() omits the build suffix (42.22);
Core.getGameAndBuildVersion() supplies 42.22.2 and is used by the probe gate.

Read-only CFR inspection and bytecode/member inspection of the installed classes.
Decompiled files are ignored under .venv/persistence-decompiled,
.venv/test-decompiled and .venv/camera-decompiled; none are shipped or committed.
Legacy mod code is evidence of its attempted usage, not the engine contract.

## Established source facts: native save/load

| Installed method | Relevant behavior |
|---|---|
| IsoPlayer.save(String) | Validates the path, sets that actor's saveFileName, writes native world version 251 and delegates ByteBuffer encoding to the character. No call to the no-argument player/database save is needed. |
| IsoPlayer.save(ByteBuffer, boolean) | Temporarily makes this actor IsoPlayer.instance while delegating, restoring the previous instance in finally. Also saves worn/hand-item indices and other player state. |
| IsoMovingObject.save(ByteBuffer, boolean) | Writes offsets, **world X/Y/Z**, facing and its ModData table. It does not call IsoObject.save for this actor representation. |
| IsoMovingObject.load(ByteBuffer, int, boolean) | Reads X/Y plus saveoffsetx/y times 256, assigns X/lastX/nextX and Y/lastY/nextY, assigns Z/lastZ, restores direction and ModData. |
| IsoMovingObject.setX/setY/setZ | Change coordinates/next or last position; do not assign currentSquare. Z has native clamping. |
| IsoGameCharacter.load | Delegates to the moving-object loader, then restores descriptor/visual/inventory/stats/body damage/XP and other character state. |
| IsoPlayer.load(ByteBuffer, int, boolean) | Delegates, restores worn/hand items and player fields. A saved vehicle flag may set Z to zero. No general current-square or moving-square repair is performed in this path. |
| IsoPlayer.load(String) | Returns silently if the file is absent; otherwise reads the version/header and calls native load. A successful method return alone does not prove a snapshot loaded. |

Therefore native position persistence is real; seeing manual setX/Y/Z in the old
mod was not evidence that B42 requires them. The prior PERSISTENCE_B42.md wording
about base IsoObject saving character ModData is imprecise: the relevant actor
path encodes it in IsoMovingObject itself. Native serialization is still used.

Coordinates and world association are separate. A raw load at a different
constructor location can restore position while retaining constructor-associated
square state. The probe records this immediately, without a world update or
manual coordinate/square correction. This source finding does **not** establish
a bug in the current SSR loader: it constructs at the registry's saved tile.
Its explicit setX/Y/Z may be redundant for fresh zero-offset worlds, but removing
them is a separate reviewed change, not part of this delivery.

## Established source facts: construction and registration

- IsoGameCharacter's constructor registers a nonzero-location actor through
  IsoCell.addMovingObject, centers X/Y at tile + 0.5, sets current from
  getGridSquare and calls setMovingSquareNow. These are constructor effects,
  not an inference from the mod's spawn code.
- IsoCell.addMovingObject inserts into objectList when safeToAdd is true,
  otherwise into addList. Object-list absence alone is not failed creation.
- setMovingSquare removes the actor from the previous square's moving-object
  collection and adds it to the new one. setCurrent only assigns the current
  reference; coordinate setters do not perform either operation.
- The five-argument IsoPlayer constructor uses its supplied fresh descriptor,
  emits OnCreateLivingCharacter and initializes normal player components. It
  does not assign the actor into human player slots. Human creation in IsoWorld
  explicitly assigns players[0]/instance separately. isLocalPlayer tests actual
  identity in the local-player array, not merely playerNum zero.
- setNpc(true) adds AIComponent; it does not imply a separate local viewport.
- Native moveUnmodded calls setCurrentSquareFromPosition, but that is a movement
  operation, not part of raw load. It is intentionally not used by the probe.

Other mods' constructor callbacks can run before Lua receives the returned
actor. A constructor exception after internal registration can leave no handle
for selective cleanup. The probe reports that uncertainty, blocks further runs
and instructs a restart. It does not search for/delete arbitrary world actors.

## Streaming, references and callback ordering

IsoCell.getGridSquare(int,int,int), in single-player, checks active non-ignored
player chunk maps and their loaded bounds (including Z -32 through 31), then
returns the cached grid-square reference or null. It does not construct a new
grid square or force loading a chunk. Each query has bounded map lookup work;
that does not quantify Lua/Java boundary cost or the current full-index workload.

IsoChunk.doLoadGridsquare emits **LoadGridsquare** for available squares and
**LoadChunk** after chunk integration. Chunk disposal emits **ReuseGridsquare**
before discard. removeFromWorld clears/soft-clears square links and detaches
moving objects; discard clears chunk and other associations. A saved reference
is not an authoritative promise that the same tile remains loaded. Cache
invalidation would need to follow these lifetimes, not retain raw references
indefinitely.

GlobalModData.init resets/loads and emits OnInitGlobalModData before IsoWorld
constructs the current cell through CellLoader. Normal IsoWorld initialization
creates/loads the human before IngameState.enter flushes pending grid-square
loads; enter subsequently emits OnGameStart/OnLoad. Lua human-wrapper
initialization is a separate condition (OnCreatePlayer is emitted by the exposed
initUISystem path). These facts do not establish every possible callback ordering
for custom startup/mods. Do not assume all initial squares necessarily precede
the human, or that all are observed after the SSR wrapper is ready.

An event-driven alternative is **plausible**, not implemented: index saved IDs
by coordinates/chunk, enqueue relevant IDs on load events, perform one catch-up
when both registry and human wrapper become ready, and drain a bounded queue in
a suitable main-thread phase. Consider explicit unload/save operations, missed
initial events and newly indexed positions as well. It would need measured
workload and regression/live evidence before replacing the current scan.

The current P.tick loop is demonstrably O(total index buckets) each tick,
including unloaded locations and possibly loaded actors' indexed positions.
That is a scaling property, **not a measured bottleneck**. No timing benchmark
or runtime population cost has been measured in this work.

## Unload investigation: facts versus remaining concern

In the ordinary inspected update path:

1. IngameState updates IsoWorld; IsoWorld updates the current cell.
2. IsoCell sets safeToAdd false around moving-object processing, then true,
   performs static updaters and drains ObjectDeletionAddition.
3. Later in the same IngameState update, onTick emits OnTick.

ObjectDeletionAddition deliberately skips removing living IsoPlayers from the
remove-list loop, then clears the list and appends pending additions. IsoCell.Remove
also refuses to queue a living IsoPlayer. IsoMovingObject.removeFromWorld has a
different path: immediate object-list removal when safe, otherwise removal
queuing; it also removes pending additions and scheduler ownership.

IsoChunk.removeFromWorld itself calls moving actors' removeFromWorld and
removeFromSquare and clears their square association. Thus the current SSR
unload path can encounter an actor that native streaming already detached and
can repeat those calls. Queue membership is transitional and does not by itself
mean terminal removal. No generic guarantee that repeating every removal side
effect is harmless was established. Other mods can also affect callback state.

**No unload-policy correction is proposed as proven yet.** A bounded future
proposal could distinguish queued transitions from confirmed unloaded squares,
defer destructive handling until an appropriate phase, and avoid duplicate
native detach when already complete. That must be reviewed against actual
streaming observations. The raw position probe only exercises its own controlled
safe-phase construction/removal; it does not validate the SSR unload policy.

## Runnable evidence and what remains unobserved

See [TESTS_UI.md](TESTS_UI.md) for exact UI entry, consent and run instructions.
There are explicit same-session, stage and resume definitions for this one
native diagnostic. Native actor snapshots use SSR_Test_NativePosition_* names;
restart evidence uses a separate world ModData key. Neither is an SSR survivor
registry entry. No raw test actor is intentionally left alive for a world update.

The test logs actor strings, actual square-reference equality within the load
operation, position/square coordinates, square containment, object/add/remove
membership, safeToAdd, missing-file behavior, human guards and cleanup outcomes.
Constructor axes that differ from the snapshot are reported individually. The
default same-floor experiment does not independently test Z restoration if Z
was unchanged; the installed source/bytecode establishes Z encoding separately.

**Actual engine observations: NOT RUN.** Mock tests deliberately emulate the
inspected native coordinate/square distinction and verify guardrails/UI control
flow. Installed-JAR tests verify coordinate read/write call sites. Neither is a
substitute for the user's disposable-world results, which must be reported as
new evidence before deciding persistence corrections or acceptance.
