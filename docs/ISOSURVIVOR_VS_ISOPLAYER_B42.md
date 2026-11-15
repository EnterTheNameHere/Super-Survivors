# IsoSurvivor versus IsoPlayer in installed B42

15 November 2026. SSR-ANALYSIS-01. **Decision: reject switching SSR actors to
IsoSurvivor for this port.** User explicitly asked to finish the proposal as
rejected after the source findings. The analysis is delivered; the rejected
item is the actor migration, not the existing IsoPlayer implementation.

Keep IsoPlayer. No production changes, tests, game experiment or Java modification
were made for this assignment. SSR-TEST-02 remains pending separately, including
its cell-only constructor experiment and factory supplement.

## Why the switch is rejected

The installed classes share a base, but do not initialize equivalent actors.
IsoSurvivor has no concrete modern visual implementation, receives null primary
body-damage, moodle and XP objects, and lacks the player control/persistence
extensions that SSR uses. These are source-level incompatibilities, not merely
missing Lua annotations or an assumption based on the name Survivor.

Most decisively, IsoSurvivor inherits IsoGameCharacter.getVisual(), which throws
RuntimeException("subclasses must implement this"). Its inherited character
save/load calls getVisual().save/load directly. It cannot use that native
roundtrip unchanged. IsoLivingCharacter.DoAttack() also transitions into
SwipeStatePlayer, whose enter(IsoGameCharacter) casts the owner to IsoPlayer.
Even preceding attack logic reads moodles, which are null for IsoSurvivor.

IsoSurvivor is final. A Lua wrapper cannot turn it into an IsoPlayer, initialize
its final native bodyDamage/moodles fields through an ordinary setter, implement
IHumanVisual for it, or replace Java virtual dispatch by renaming Lua methods.
A different Lua actor backend would have to replace major engine-dependent
functionality; an equivalent Java subclass/engine change is outside the user's
constraints. The small removal-rule benefit does not justify that loss.

## Evidence and limits

Primary evidence: installed G:/Steam/steamapps/common/ProjectZomboid JAR and
bundled media/lua. Build 42.22.2, revision 3d39148846; JAR SHA256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only CFR output plus declared JVM members/bytecode were inspected.
Decompiled evidence remains ignored under .venv/actor-decompiled,
.venv/persistence-decompiled, .venv/test-decompiled and .venv/camera-decompiled.
References below name exact installed classes/methods; decompiled line numbers
are tool-dependent, so they are not presented as original game source lines.

The JAR scan covered all 23,692 .class entries, filtering constant-pool method
references and invocation-byte patterns for both constructors and
SurvivorFactory.InstansiateInCell. It yielded 23 candidate caller methods,
with zero parse failures. Important paths were followed in decompiled methods.
This is a static inventory, not execution tracing or proof that every remaining
path runs. Byte-pattern matching is not a general bytecode control-flow analysis.
Vanilla Lua was searched recursively for IsoSurvivor, InstansiateInCell,
IsoPlayer.new and OnCreateSurvivor. Text hits were checked for comments.
SSR migration sites were searched in committed runtime Lua at 6234ff6 (same
runtime tree as 090f424); unrelated uncommitted edits were not incorporated.

No new runtime observations exist for IsoSurvivor. Prior native IsoPlayer probe
results remain separate evidence: X/Y and marker restored after restart while
currentSquare stayed at the deliberately different constructor square. That
probe does not prove an SSR loader defect, validate IsoSurvivor, or independently
vary Z. See [NATIVE_POSITION_R1.md](NATIVE_POSITION_R1.md).

## Comparison matrix

| Area | IsoPlayer | IsoSurvivor | Implication |
| --- | --- | --- | --- |
| Inheritance | IsoLivingCharacter -> IsoGameCharacter -> IsoMovingObject -> IsoObject | Same chain | Shared method names do not imply equivalent initialized state. |
| Interfaces | Declares IAnimalVisual, IHumanVisual, IPositional | Declares none; common inherited interfaces remain | Modern human visual path differs materially. |
| Constructors | cell; cell/desc/x/y/z; cell/desc/x/y/z/isAnimal | cell; desc/cell/x/y/z; desc/cell/x/y/z/bSetInstance | Argument order and overload effects differ. |
| Visual | Allocates HumanVisual, overrides getVisual/getHumanVisual | Inherits throwing getVisual; no equivalent override in IsoLivingCharacter | Native serialization and modern visual consumers cannot be assumed usable. |
| Health, moodles, skills | Common constructor allocates BodyDamage, Moodles, XP for nonanimal IsoPlayer | Common constructor assigns null to those objects | Existing medical, need, skill and combat code is incompatible. |
| Stats and inventory | Shared Stats, ItemContainer and common character APIs | Same common fields/APIs | These shared pieces do not compensate for null health/XP/moodles. |
| Equipment | Initializes worn/attached groups and restores worn indices in player payload | Constructors differ in when/if Human groups are initialized; no player worn-payload override | Not equivalent native clothing roundtrip. |
| Nutrition/fitness/wetness | Allocates player-specific objects, exposes methods and persists nutrition/fitness | No corresponding constructor allocation or player APIs | SSR currently uses nutrition. |
| Sound | CharacterSoundEmitter or DummyCharacterSoundEmitter | Common constructor explicitly assigns emitter=null | Shared sound methods do not promise safe actor sound/update. |
| Native byte-buffer persistence | Adds player payload to common serializer | Inherits common serializer, with the visual/null-field blockers above | There is no unchanged equivalent working roundtrip established for Survivor. |
| Filename persistence | save(String), load(String), save(), save-file handling | No equivalent filename overloads in class or ancestors | Current SSR native snapshot path cannot be reused unchanged. |
| NPC control | setNpc toggles AIComponent; player update consumes control vars | No setNpc; inherited isNpc tests presence of component | IsoSurvivor name does not supply autonomous AI. |
| World removal | Some cell paths protect living IsoPlayers | Those specific player guards do not match Survivor | Easier passage through one removal path is not a lifecycle solution. |
| Death | Common OnCharacterDeath plus player override; OnPlayerDeath only when local | Common event and some old survivor corpse branches | Class swap changes hooks, inventory/visual death handling and save cleanup. |

## Constructors, exposure and factories

Verified public constructors (IsoCell=cell, SurvivorDesc=desc):

- IsoPlayer(IsoCell).
- IsoPlayer(IsoCell, SurvivorDesc, int, int, int).
- IsoPlayer(IsoCell, SurvivorDesc, int, int, int, boolean isAnimal).
- IsoSurvivor(IsoCell).
- IsoSurvivor(SurvivorDesc, IsoCell, int, int, int).
- IsoSurvivor(SurvivorDesc, IsoCell, int, int, int, boolean bSetInstance).

LuaManager.Exposer.exposeAll explicitly includes IsoPlayer, IsoSurvivor and
SurvivorFactory; LuaJavaClassExposer exposes public constructors/methods.
That establishes exposure machinery, not successful construction/update/save in
a world. No constructor was invoked during this analysis.

IsoPlayer(cell) delegates to its full five-argument constructor with null desc
and zero coordinates; it is not an empty deserialization shell. Full construction
allocates visual, health-related player objects, clothing systems, callbacks,
a player action group/state initialization, descriptor linkage and creation
events. It does not itself claim players[]/singleton, as distinct from human
initialization paths. Testing an alternate construction route is SSR-TEST-02;
no new probe or safety approval is implied by documenting this overload.

IsoSurvivor(cell) calls the common zero-coordinate constructor, adds itself to
cell.getSurvivorList(), emits OnCreateSurvivor and initializes worn/attached
Human groups. Descriptor-bearing five-argument construction sets descriptor
instance, sprite parts, pathfinder range, speech color and Dressup; it emits
OnCreateSurvivor and OnCreateLivingCharacter and initializes Human groups after
those events. The boolean overload optionally links desc.instance, emits only
OnCreateSurvivor here, and does not perform the same ending group initialization.
The descriptor-bearing overloads do not explicitly add to survivorList as the
cell-only overload does. Shared constructor registration still applies.

SurvivorFactory.CreateSurvivor overloads return SurvivorDesc. CreateFamily and
CreateSurvivorGroup return descriptor arrays, not living actors. The descriptor
factory also registers a descriptor in IsoGameCharacter's survivor map.
SurvivorFactory.InstansiateInCell(desc,cell,x,y,z) constructs and returns
IsoSurvivor, links desc.instance, and does not return an IsoPlayer.

IsoObject.initFactory registers class ID 1 / Player -> new IsoPlayer(cell), and
ID 2 / Survivor -> new IsoSurvivor(cell). factoryFromFileInput and its _OLD path
are generic serialized-object factories, not evidence of a fully initialized
modern Survivor NPC or automatic player/group persistence. A factory record is
not a repair for inherited throwing methods.

## What the engine actually uses

The constructor inventory finds three direct Survivor caller methods:
SurvivorFactory.InstansiateInCell, IsoObject$3.InstantiateObject (the ID-2 factory),
and IsoObject.factoryFromFileInput_OLD. No additional direct compiled Survivor
constructor call was found in that scan. No direct compiled invocation of
InstansiateInCell was found by the same search. Dynamic/reflection/mod usage is
outside that conclusion; this does not prove universal absence of NPC behavior.

Player callers include IsoWorld.init, IsoCell.LoadPlayer, LuaManager.GlobalObject
setPlayerJoypad/setPlayerMouse, generic object factories, PlayerDB/ClientPlayerDB/
ServerPlayerDB, player/network connection packets and IsoAnimal constructors.
These are different use cases, not interchangeable NPC factory alternatives.
IsoCell.LoadPlayer and IsoWorld.init explicitly wire singleton/local slots and
world loading. The LuaManager helpers assign controls/usernames and call
addPlayerToWorld. They are human/coop integration paths; not safe arbitrary-NPC
creation shortcuts. Database routines load player records, not SSR registry actors.
No dedicated Lua-exposed fully prepared arbitrary-NPC IsoPlayer factory was
identified in these scanned constructor paths. Private/dynamic mechanisms beyond
that scope are not ruled out. Full factory/test work remains separate.

Vanilla Lua text has three IsoSurvivor.new occurrences. The two in
client/XpSystem/ISUI/ISCharacterScreen.lua (drawAvatar and new) are inside long
comments, so they are legacy examples, not active calls. The other is the body
of client/OptionScreens/CharacterCreationMain.lua:createAvatar; modern
setAvatarFromUI passes a descriptor to the avatar panel. A function body in
source is not proof its actor is spawned/updated in gameplay. A debug map window
also recognizes Survivor instances, and shared/NPCs/MainCreationMethods.lua
registers OnCreateSurvivor -> CreateCharacterInstance. That handler adds a
baseball bat; it does not allocate the missing health/visual/XP systems.

Inference: the available evidence fits a retained partial legacy actor much
better than a supported alternative modern NPC implementation. This inference
is supported by the missing concrete systems and stale attack state path; it
is not a claim about the game's future NPC plans or historical intent.

## Persistence: shared state and failed equivalence

Exact chain: IsoPlayer.save/load(ByteBuffer,...) -> IsoGameCharacter.save/load
-> IsoMovingObject.save/load. IsoSurvivor inherits the latter two through
IsoLivingCharacter, with no save/load override of its own.

IsoMovingObject serializes XYZ, direction and actor ModData. Its load restores
coordinates (XY include world save offsets), not currentSquare/moving-square
membership. This shared source fact also applies to the inherited method, but
it does not establish a complete Survivor character roundtrip.

IsoGameCharacter persists descriptor, visual, inventory, sleep, stats, body
wounds/health, XP, equipped hand indices, recipes and other common data. It
unconditionally calls getVisual().save/load and, for a non-zombie, bodyDamage
and XP serialization. A normally constructed Survivor hits the throwing visual
method and lacks the primary BodyDamage/XP objects. Inherited method signatures
are therefore not sufficient evidence of supported serialization.

IsoPlayer adds hours/kills, worn-item mappings, hand indices, nutrition, fitness,
vehicle state, books/media, voice and other player metadata. Its filename wrappers
handle a version/header and save path; save(ByteBuffer,...) temporarily changes
the singleton around common save and restores it in finally. Survivor has no
matching filename wrapper or player-specific extension. A new custom Lua writer
would require a schema and actual serialization for absent systems; it is not a
rename of the existing native snapshot operation. Copying player bytes into a
Survivor would not be a compatible deserializer.

## World lifecycle and gameplay contracts

IsoGameCharacter(cell,x,y,z) registers a nonzero-position actor through
cell.addMovingObject, sets centered coordinates and initializes current/moving
square when cell is supplied. Both subclasses share this base behavior. Zero
coordinates and descriptor/event ordering have different side effects; none
is a general proof of safe null-square construction.

IsoCell.ObjectDeletionAddition and Remove skip living IsoPlayers. IsoMovingObject
removeFromWorld follows safeToAdd immediate/deferred lists, and removeFromSquare
clears square membership. IsoMovingObject.ensureOnTile specifically removes a
Survivor with null current square from the cell and survivor list. IsoSurvivor
Despawn merely clears desc.instance; it does not detach the actor. Its list
membership and the special null-tile path need explicit lifecycle accounting.

Chunk teardown detaches moving objects and clears square references. Shared
base teardown does not guarantee both actor classes persist/reload identically.
No Survivor streaming or safe cleanup sequence was executed here. A generic
factory and a survivor list are not an automatic save/repopulation registry.

Both share pathToLocation/getPathFindBehavior2, common stats/inventory/state and
animation variables. However IsoPlayer adds human action context/state setup,
modern visuals, movement/input/endurance/nutrition integrations and controls.
The class comparison proves common APIs exist, not full movement/animation
correctness on an untested Survivor actor.

IsoLivingCharacter.DoAttack transitions to SwipeStatePlayer; its enter casts
owner to IsoPlayer. AttemptAttack's attack-var/hook preparation is conditional
on IsoPlayer. AIComponent.update is empty in this build; its control-application
methods take IsoPlayer and getPlayer obtains an IsoPlayer owner. IsoPlayer.setNpc
installs that component; it is a control bridge, not a survival planner.
IsoSurvivor has no autonomous planning/update override in its declared class.

Common OnDeath emits OnCharacterDeath. Player.OnDeath adds action cleanup,
local-only OnPlayerDeath and save-file cleanup. IsoDeadBody's constructor has
old Survivor statistics/Despawn branches, but modern human visual/inventory
transfer is conditional on IHumanVisual, which Survivor does not implement.
Those legacy branches do not establish equivalent corpse appearance/loot or
reanimation; these remain untested and are not reasons to migrate.

## SSR migration surface

These are representative committed call sites, not an exhaustive Lua dataflow
audit. The receiver-name/member inventory includes inherited methods and was
manually checked against the source; arbitrary aliases may add more sites.

| SSR area | Current contract | Consequence of switching |
| --- | --- | --- |
| SuperSurvivor.lua:loadPlayer / createPlayer | IsoPlayer.new(cell,desc,x,y,z), setNpc, block movement, display name, player native load | Construction/control/serialization redesign. |
| SuperSurvivorPersistence.lua:saveSurvivor | isLocalPlayer guard, native actor:save(filename) | Neither contract is available unchanged on Survivor. |
| SuperSurvivorUpdate.lua event registrations | OnPlayerUpdate and OnCharacterDeath | Survivor does not emit Player's update event; update scheduling must change. |
| SuperSurvivor.lua movement/attack | setJustMoved, setPathfindRunning, setBlockMovement, pressedAttack, initiate/attack-started, performing-action fields | Player-only methods need replacement; inherited attack path also casts to Player. |
| SuperSurvivor.lua hunger/medical/skills | getNutrition, getBodyDamage, getXp, getMoodles | First is player-only; latter inherited accessors return absent objects on Survivor. |
| Context menu / DoctorTask / threat AI / combat hooks | instanceof(...,"IsoPlayer") identifies human actors and SSR targets | Targeting, medical selection, hostility, damage/UI hooks must be revisited. |
| CleanInvTask / SortLootTask | actor:getPlayerNum plus player-oriented item UI/actions | Interface changes extend into task/UI integration. |
| Rendering, equipment, corpse paths | HumanVisual and player body systems | Lua wrapper cannot provide missing native virtual methods/interfaces. |

A backend abstraction can isolate identity, capabilities, registry queries and
actor commands while retaining IsoPlayer underneath. It would be future design
work with real capability checks, not merely changing instanceof to a base class.
It cannot make unsafe native methods work for Survivor. No such abstraction was
implemented or assigned by this report.

## Options and disposition

| Option | Assessment | Confidence / cost |
| --- | --- | --- |
| Keep IsoPlayer | Recommended current backend; continue evidence-based lifecycle review | High confidence in compatibility advantage; viewport/streaming concerns remain. |
| Switch to IsoSurvivor | **Rejected** by user; direct swap has verified structural blockers | High confidence in blockers; equivalent gameplay would be a major backend/engine replacement, not this port. |
| Abstract shared type | Possible future organization while still using Player | Moderate confidence as design direction; does not resolve native differences and adds migration/testing work. |

No further experiment is needed to establish that a direct class replacement is
incompatible. If future engine changes supply the missing visual/health/combat
contracts, re-inspect those exact members before considering an isolated minimal
runtime experiment. No such experiment is implemented, requested of the user,
or executed now. The separately requested cell-only IsoPlayer experiment is
neither approved nor rejected by this actor comparison; it remains pending the
user/orchestrator's next sequencing decision.
