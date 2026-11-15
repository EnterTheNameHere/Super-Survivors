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

**At initial delivery, engine observations were NOT RUN; see the subsequent
in-game evidence below.** Mock tests deliberately emulate the
inspected native coordinate/square distinction and verify guardrails/UI control
flow. Installed-JAR tests verify coordinate read/write call sites. Neither is a
substitute for the user's disposable-world results, which must be reported as
new evidence before deciding persistence corrections or acceptance.


## Actual engine observations (15 November 2026)

User reports successful same-session test, staging, full game restart, world
reload and successful resume. Archived session log independently contains two
same-session PASSED results, successful staging, and next-session PASSED resume.
Filtered evidence: [NATIVE_POSITION_2026-11-15.log](evidence/NATIVE_POSITION_2026-11-15.log).
Runtime code includes offset fix a7222eb; engine remains 42.22.2, zero offsets.

| Run | Saved XYZ | Constructor XYZ | Immediately after raw native load |
| --- | --- | --- | --- |
| Same session, first | 9885.5, 12812.5, 0 | 9883.5, 12814.5, 0 | 9885.5, 12812.5, 0 |
| Same session, repeated | 9877.5, 12805.5, 0 | 9875.5, 12807.5, 0 | 9877.5, 12805.5, 0 |
| After restart | 9870.5, 12799.5, 0 | 9868.5, 12801.5, 0 | 9870.5, 12799.5, 0 |

In all loads currentSquare remained the constructor square, its moving-object
collection still contained the actor, and the cell object list contained it;
add/remove lists were empty. This establishes the coordinate/square-registration
split in actual execution. Snapshot marker restored, missing-file load returned
without exception/change, and human identity/position/singleton/save filename
checks passed. Cleanup detached owned actors from world/add/remove lists and
cleared currentSquare. Snapshot files intentionally remain.

Staged source session was 1794747913356_802487; resume session was
1794748044287_495694. User confirms restarting the game; session tokens alone
would establish only a new Lua session. Z stayed zero in every phase: this
experiment independently demonstrates X/Y restoration, not distinct-Z restoration.

This validates the focused native snapshot probe, not complete SSR persistence,
streaming, death handling, prolonged AI behavior or all UI interactions. No
persistence scan/unload/loader rewrite or acceptance follows automatically.
Review actual loader square reconciliation next; manual XYZ setters alone do
not establish or repair square membership. No restart required for these records.


## SSR-TEST-02 installed-source findings and proposed runtime measurement

15 November 2026. User explicitly resumed this assignment after source-only
IsoSurvivor analysis. IsoSurvivor migration remains rejected; actors remain
IsoPlayer. No production SSR loader/scan/unload code changes in this assignment.

Verified public constructor: `IsoPlayer(IsoCell)` delegates to
`IsoPlayer(IsoCell, SurvivorDesc, int, int, int)` with null descriptor and 0/0/0.
The main constructor supplies a new descriptor if null, health/visual/XP/clothing,
player state/action setup and creation hooks. It does not assign local slots or
the singleton. LuaManager.Exposer includes IsoPlayer and public constructor
exposure; the one-argument Lua invocation remains to be measured in-game.

In IsoGameCharacter(IsoCell,float,float,float), object-list registration occurs
only when an input coordinate is nonzero. Coordinates become centered X/Y=0.5,
Z=0. If cell is supplied it queries getGridSquare(0,0,0) and calls
setMovingSquareNow; currentSquare may therefore be nil or an origin tile even
without cell object-list membership. This is why the test captures both square
and cell lists, not just whether an actor object was returned.

Raw native load has the previously established coordinate/square split. The
inspected registration primitives are public and exposed through the normal
Java methods:

| Installed method | Contract used in this test |
| --- | --- |
| IsoMovingObject.setCurrentSquare(IsoGridSquare) | Calls setCurrent, which assigns current only; does not change coordinates or movingSq. |
| IsoMovingObject.setMovingSquareNow() | Calls setMovingSquare(current), removes membership from old movingSq when different, and adds to the new square if absent. |
| IsoCell.addMovingObject(IsoMovingObject) | Adds to objectList if safeToAdd; otherwise addList. The probe requires and rechecks safeToAdd. |
| IsoMovingObject.removeFromWorld/removeFromSquare | Detaches from cell/square structures; use only returned owned nonlocal actors and verify cleanup. |

The chosen explicit experiment sets current to the exact loaded saved tile,
reconciles moving-square membership, then adds cell membership only if missing.
It does not call an actor update or setX/Y/Z, nor rely on
setCurrentSquareFromPosition's fallback-to-lower-floor behavior. Snapshot load
and all registrations/cleanup occur in the same safe callback. The normal
automatic AI/update path never sees an intentionally unplaced probe actor.

### Factory / engine-managed loading supplement

A 23,692-class JAR constructor/factory-reference scan from SSR-ANALYSIS-01, plus
method-body follow-up here, identified the following distinct mechanisms. The
same JAR SHA256 is in the report header; this is not a search of every possible
reflective/plugin creation mechanism.

| Exact entry point | Return/exposure | Meaning and side effects |
| --- | --- | --- |
| SurvivorFactory.CreateSurvivor overloads | SurvivorDesc; public static, exposed class | Descriptor factory, no IsoPlayer actor. |
| SurvivorFactory.InstansiateInCell(desc,cell,x,y,z) | IsoSurvivor; public static | Wrong actor class for SSR; invokes Survivor constructor/descriptor linkage. |
| IsoObject.factoryFromFileInput(IsoCell,byte) / (IsoCell,ByteBuffer) | IsoObject; public static; exposed class | Serialized-object selector. ID 1 instantiates IsoPlayer(cell); ByteBuffer overload consumes header/class bytes, does not perform complete actor load/placement. Not a fully registered NPC factory. |
| IsoCell.LoadPlayer(int worldVersion) | boolean; public | Human save import: map_p data, singleton/slot 0 creation if absent, chunk-map coordinates, player DB save/upload and file deletion. Never called by probe. |
| IsoWorld.init() | void; engine world initialization | Human player constructor followed by players[0], singleton and camera wiring, then traits/world startup. Not an isolated actor helper. |
| LuaManager.GlobalObject.setPlayerJoypad(int,int,IsoPlayer,String,boolean) / setPlayerMouse(IsoPlayer) | void; Lua-facing globals | May construct a player then assign usernames/control/world integration via private addPlayerToWorld(int,IsoPlayer,boolean); not a separate NPC-returning API. Never called by probe. |
| PlayerDB.loadLocalPlayer(int), ClientPlayerDB.loadNetworkPlayer(), packet/server player-loading paths | Player-record workflows | Constructor consumers for human/local/network records; not SSR registry/native snapshot factories. |

Relevant inspected callers also include PlayerDB.uploadLocalPlayers2DB,
getAllLocalPlayers lambda, ClientPlayerDB.getAllNetworkPlayers,
ServerPlayerDB.serverLoadNetworkCharacter, CreatePlayerPacket.parse/processServer,
ConnectedPacket.parse and IsoAnimal constructors. Static constructor references
were inventoried; not all networking/database workflows were executed or fully
reconstructed. No dedicated fully prepared arbitrary-NPC IsoPlayer factory was
found in this scope. Generic construction/serialized-object factories exist,
so the conclusion is not that the game has no factories at all.

Direct cell-only construction remains the most bounded measurement of the
requested question: it bypasses human loading/control paths while exposing
constructor versus load versus explicit placement effects. Native PlayerDB and
IsoCell use this constructor, supporting its role as an initialization route;
this is evidence for designing the experiment, not proof of arbitrary NPC
safety over time. Native events/other mods and a throw before a handle returns
remain limits, handled by best-effort owned cleanup, inconclusive outcome and
blocking subsequent runs when unverifiable.

Six focused mock cases cover nil-square cell-only success, implicit constructor
membership, failed position restore, registration failure/missing moving-square
membership, constructor handle gaps, and nonzero local-slot changes. Installed
JAR tests verify constructor/primitives' public signatures/delegation. Tests:
185 passed, 112 Lua syntax checks; LuaLS 88 legacy diagnostics, none test modules.
**USER IN-GAME NOT RUN for SSR-TEST-02.** User steps and exact new selector title
are in [TESTS_UI.md](TESTS_UI.md). No restart roundtrip is added for this test.
