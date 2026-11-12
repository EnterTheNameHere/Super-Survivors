# File guide for the Build 42 port

Snapshot: 10 November 2026. Companion to [the prioritized review](CODEBASE_PORT_REVIEW_2026-11-10.md). Every runtime Lua file has an individual entry below. Descriptions identify responsibility and the next port boundary; they are not compatibility certifications. Line counts include comments/blank lines.

## Runtime Lua


### `42/media/lua/client/0_Utilities`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [SuperSurvivorContextUtilities.lua](../42/media/lua/client/0_Utilities/SuperSurvivorContextUtilities.lua) · 673 | Square, distance, area, flee, door, window and building-search helpers used by tasks and UI. | Core spatial adapter. Nil distance returns -1, so callers can accidentally interpret a missing target as nearby; audit floors, loaded squares and bounds. |
| [SuperSurvivorLootUtilities.lua](../42/media/lua/client/0_Utilities/SuperSurvivorLootUtilities.lua) · 443 | Finds/scorers weapons, food and water in inventories and on floors; defines category predicates. | R08: several zero-based Java lists skip index 0. Recheck B42 fluid content and edible-item scoring beyond method names. |
| [SuperSurvivorSpiralSearchUtilities.lua](../42/media/lua/client/0_Utilities/SuperSurvivorSpiralSearchUtilities.lua) · 50 | Stateful outward spiral iterator for nearby-square scans. | Keep as a pure helper; verify search coverage/radius and bound work per simulation tick. |
| [SuperSurvivorSuitsList.lua](../42/media/lua/client/0_Utilities/SuperSurvivorSuitsList.lua) · 374 | Outfit catalog, rarity groups and preset clothing lists. | Data port: current item IDs and typed body slots, gender filtering and third-party outfits. Not engine outfit metadata. |
| [SuperSurvivorSuitsRegistry.lua](../42/media/lua/client/0_Utilities/SuperSurvivorSuitsRegistry.lua) · 13 | Initializes the global outfit-category tables if absent. | Load-order support, not a separate outfit system. Explicitly initialize before catalog extensions. |
| [SuperSurvivorSuitsUtilities.lua](../42/media/lua/client/0_Utilities/SuperSurvivorSuitsUtilities.lua) · 98 | Chooses a rarity/outfit, filters gender, equips catalog entries. | R19 random selection; unbounded retry if no compatible outfit. Make item failures and optional content explicit. |
| [SuperSurvivorTablesUtilities.lua](../42/media/lua/client/0_Utilities/SuperSurvivorTablesUtilities.lua) · 206 | Text table/KV save readers/writers, file checks, random table key helper and save-directory helper. | R02–R04, R19. Highest-risk persistence boundary; shared global table extensions and duplicate getSaveDir definition. |
| [SuperSurvivorTextUtilities.lua](../42/media/lua/client/0_Utilities/SuperSurvivorTextUtilities.lua) · 23 | Global translation-prefix helpers for dialogue, names, UI, actions, challenges and options. | Presentation adapter. Avoid translated text as saved role/order identity; global getName can collide. |
| [SuperSurvivorUtilities.lua](../42/media/lua/client/0_Utilities/SuperSurvivorUtilities.lua) · 226 | Order names, colors, perk choices, generic table helpers and mouse/world-coordinate conversion. | R19 grey typo. Distinguish its unusual size() contract from ordinary #table; player-0 coordinate assumptions. |
| [SuperSurvivorWeaponsList.lua](../42/media/lua/client/0_Utilities/SuperSurvivorWeaponsList.lua) · 209 | Weapon rarity/category catalogs and configuration-dependent item choices. | Validate item IDs and optional weapon mods; source of randomized equipment rather than engine weapon ownership. |
| [SuperSurvivorWeaponsRegistry.lua](../42/media/lua/client/0_Utilities/SuperSurvivorWeaponsRegistry.lua) · 6 | Legacy EnabledTranslations registry/buffer despite its filename. | Misleading name: not a weapon registry. Declaring EN/JP does not load translation resources. |
| [SuperSuvivorsCombatUtilities.lua](../42/media/lua/client/0_Utilities/SuperSuvivorsCombatUtilities.lua) · 218 | Ammo-box mapping/counts, ammo-type helpers and the global PvP toggle. | R19 qualification bug; hard-coded ammo counts/ORGM integration. PvP is global player behavior, not NPC-private. |

### `42/media/lua/client/1_Dialogue`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [SuperSurvivorDialogue.lua](../42/media/lua/client/1_Dialogue/SuperSurvivorDialogue.lua) · 1137 | Speech/dialogue tables and selection logic for NPC situations. | Preserve translation keys and named speakers; separate content from probability/relationship logic. |
| [SuperSurvivorNames.lua](../42/media/lua/client/1_Dialogue/SuperSurvivorNames.lua) · 46 | Random survivor name data/selection. | Audit random bounds and empty/missing translated names; display names must not become durable actor IDs. |
| [SuperSurvivorOrders.lua](../42/media/lua/client/1_Dialogue/SuperSurvivorOrders.lua) · 61 | Order/dialogue-related data and helpers. | Keep canonical command identifiers separate from translated labels and Task.Name strings. |

### `42/media/lua/client/2_Group`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [SuperSurvivorGroup.lua](../42/media/lua/client/2_Group/SuperSurvivorGroup.lua) · 567 | Membership, leader/roles, enemies, bounds, named work/storage areas, warnings and group serialization. | R04, R12. Central group model; persist named fields and resolve unloaded member IDs explicitly. |
| [SuperSurvivorGroupManager.lua](../42/media/lua/client/2_Group/SuperSurvivorGroupManager.lua) · 122 | Creates, looks up and saves/loads groups; creates fixed scenario groups at file load. | R04 sequential-file discovery. Distinguish actual group count from ID high-water mark; avoid scenario state as import side effect. |

### `42/media/lua/client/3_Other`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [SuperSurvivor.lua](../42/media/lua/client/3_Other/SuperSurvivor.lua) · 4866 | Main actor wrapper: constructors/load/spawn, identity, perception, pathing, task helpers, update, combat, health, equipment, ammo, saving and hygiene. | R01, R03, R06, R17, R20. Main port boundary; split responsibilities after contracts are stable. See method map below. |
| [SuperSurvivorDoctor.lua](../42/media/lua/client/3_Other/SuperSurvivorDoctor.lua) · 72 | Body-part treatment predicates and treatment-priority selection. | Used by doctor tasks; tie decisions to current action capabilities and distinguish a treated injury from a healed one. |
| [SuperSurvivorManager.lua](../42/media/lua/client/3_Other/SuperSurvivorManager.lua) · 424 | Global actor registry, main-player wrapper, spawn/load/update, death reactions and spatial-index text serialization. | R01–R03, R12. setPlayer writes metadata through index 0 even when passed another ID; switchPlayer changes native local-player ownership. |
| [SuperSurvivorPresetSpawns.lua](../42/media/lua/client/3_Other/SuperSurvivorPresetSpawns.lua) · 658 | Named/scenario NPC construction, clothing, loadouts and stockpiles at fixed coordinates. | R09-adjacent data port; missing WoodenLance/WaterPot. Validate against current map and make optional scenarios explicit. |
| [SuperSurvivorRender.lua](../42/media/lua/client/3_Other/SuperSurvivorRender.lua) · 50 | Submits standalone NPC IsoPlayers to B42 opaque world rendering and restores observer opacity. | R01: SP bridge, not full native actor registration/cutaway policy. Guard timing and observer ownership remain material risks. |
| [SuperSurvivorSettings.lua](../42/media/lua/client/3_Other/SuperSurvivorSettings.lua) · 14 | Small global settings bridge: follow distance, debug speech, speech and PvP defaults. | Reads globals during load; actual options are elsewhere. Do not mistake comments for a validated config schema. |
| [SuperSurvivorSpeakConditions.lua](../42/media/lua/client/3_Other/SuperSurvivorSpeakConditions.lua) · 228 | LMSConditions moodle/speech tables. | Data and thresholds for conditional chatter; review typed moodle mapping, empty entries and update cadence. |
| [SuperSurvivorUndressing.lua](../42/media/lua/client/3_Other/SuperSurvivorUndressing.lua) · 152 | Defines custom ISUnequipClothingAction and equipment/animation cleanup behavior. | Action calls perform from update; rebase lifecycle and use normal unequip ownership rather than repeated immediate completion. |
| [SuperSurvivorUpdate.lua](../42/media/lua/client/3_Other/SuperSurvivorUpdate.lua) · 513 | Player initialization/update, death callback, cover/injury helper and weapon-hit handling. | R06, R17. Global event callbacks can affect the real player; separate native health/damage from NPC reactions. |
| [SuperSurvivorsMod.lua](../42/media/lua/client/3_Other/SuperSurvivorsMod.lua) · 1266 | Main event orchestration, startup, grid loading/spawning, keyboard orders, equipment hooks, random spawns and raids. | R20. Large global controller; split simulation, presentation, spawning and save scheduling. Debug code and normal gameplay are interleaved. |

### `42/media/lua/client/4_AI`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [AI-Manager.lua](../42/media/lua/client/4_AI/AI-Manager.lua) · 1154 | Primary priority/rule engine deciding follow, combat, fear, supplies, treatment, loot and base work. | Runs from TaskManager.update and can replace the queue during update. Make priorities, interruptibility and no-target states explicit. |
| [AI-Manager_Companions.lua](../42/media/lua/client/4_AI/AI-Manager_Companions.lua) · 220 | Extracted companion decision logic with pursuit, combat, healing, following and reload rules. | Explicitly marked unconnected/incomplete in source. Do not assume changes here affect active companion AI; contains stale target/global assumptions. |
| [AI-Manager_GroupsBaseJobs.lua](../42/media/lua/client/4_AI/AI-Manager_GroupsBaseJobs.lua) · 2 | Placeholder for future group/base-job AI split. | No functional subsystem to port yet; main manager owns these decisions. |
| [AI-Manager_Hostile.lua](../42/media/lua/client/4_AI/AI-Manager_Hostile.lua) · 3 | Placeholder for future hostile AI split. | No functional subsystem to port yet; main manager owns these decisions. |
| [AI-Manager_RandomSurvivor.lua](../42/media/lua/client/4_AI/AI-Manager_RandomSurvivor.lua) · 3 | Placeholder for future random-survivor AI split. | No functional subsystem to port yet; main manager owns these decisions. |

### `42/media/lua/client/5_UI`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [DDebugUI.lua](../42/media/lua/client/5_UI/DDebugUI.lua) · 265 | Developer-facing debug UI controls and callbacks. | Keep diagnostics separate from released gameplay; validate callback actors/targets and stale debug assumptions. |
| [SSQuestManagerDialogue.lua](../42/media/lua/client/5_UI/SSQuestManagerDialogue.lua) · 210 | Dialogue window, question/continue handling and quest response dispatch. | Coordinate task cancellation with window closure; prevent double answers/reward dispatch and handle missing speakers. |
| [SSQuestManagerWindow.lua](../42/media/lua/client/5_UI/SSQuestManagerWindow.lua) · 52 | Quest information window and its creation/lifetime. | Quest persistence is absent (R15); UI lifetime must survive player/world transitions without stale globals. |
| [SuperSurvivorBasePanel.lua](../42/media/lua/client/5_UI/SuperSurvivorBasePanel.lua) · 349 | Group/base-area controls and visual presentation of designated work/storage areas. | Validate rectangle/floor selection, translations and current group; separate display from mutating saved group state. |
| [SuperSurvivorInfoPanel.lua](../42/media/lua/client/5_UI/SuperSurvivorInfoPanel.lua) · 247 | Group member information panel. | R12: loaded/dead/missing members need one stable view model rather than mixed wrappers/IDs. |
| [SuperSurvivorInventory.lua](../42/media/lua/client/5_UI/SuperSurvivorInventory.lua) · 389 | Two-way inventory transfer UI with item rows/tooltips. | R13 immediate transfer after queued unequip; normal range, capacity, reservation and cancellation contracts bypassed. |
| [SuperSurvivorLoadout.lua](../42/media/lua/client/5_UI/SuperSurvivorLoadout.lua) · 409 | Equipment management UI and item equip/unequip controls. | Shares inventory-row patterns; sequence actual equipment actions and update UI after completion. |
| [SuperSurvivorMyGroupWindow.lua](../42/media/lua/client/5_UI/SuperSurvivorMyGroupWindow.lua) · 194 | Group-management window composing member panels and commands. | R12 and player-0 globals; coordinate multiple UI implementations rather than treating each as a separate actor model. |
| [SuperSurvivorOptions.lua](../42/media/lua/client/5_UI/SuperSurvivorOptions.lua) · 684 | Options registration/UI, saved option read/write and keybinding configuration. | Validate saved indices/ranges and current mod identity. Global defaults/load order and per-user/per-world scope need documentation. |
| [SuperSurvivorPVPButton.lua](../42/media/lua/client/5_UI/SuperSurvivorPVPButton.lua) · 59 | HUD PvP button, images and toggle wiring. | Changes global coop PvP. Test current game PvP settings, death/reload and conflicts with other HUD mods. |
| [SuperSurvivorWindow.lua](../42/media/lua/client/5_UI/SuperSurvivorWindow.lua) · 692 | Survivor interaction/group-command window and selection controls. | Task and role string coupling; review selected-member lifetime and consistency with newer panels. |
| [SuperSurvivorsContextMenu.lua](../42/media/lua/client/5_UI/SuperSurvivorsContextMenu.lua) · 1173 | World/inventory context menus and order-to-task dispatch; recruitment, gifts and debug commands. | Large command gateway; R18 animator call. Validate actor/target lifetime, unloaded members, command capability and authority. |
| [SurvivorInfoWindow.lua](../42/media/lua/client/5_UI/SurvivorInfoWindow.lua) · 165 | Older survivor status/details window and call/order controls. | Overlapping UI with InfoPanel; do not delete until references are mapped. Some comments use old build-detection heuristics. |
| [SurvivorLocator.lua](../42/media/lua/client/5_UI/SurvivorLocator.lua) · 60 | World-map survivor markers plus Show/Hide button; wraps ISWorldMap.render globally. | R12 mixed unloaded member representation; assumes array member 1 is player. Global hook needs lifecycle/idempotence review. |
| [UIUtils.lua](../42/media/lua/client/5_UI/UIUtils.lua) · 138 | Colors, group/member view helpers and UI order dispatch; deliberate debug-break helper. | R12: number/nil indexing, coords typo, wrong task key. get_group/get_member_info can mutate group membership during display. |

### `42/media/lua/client/6_Options`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [SuperSurvivorsOptionsLoad.lua](../42/media/lua/client/6_Options/SuperSurvivorsOptionsLoad.lua) · 49 | Converts saved option selections to global gameplay configuration and immediately refreshes them. | Explicit initialization dependency, validation and game-mode scope required; no server synchronization contract. |

### `42/media/lua/client/7_Tasks`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [AttackTask.lua](../42/media/lua/client/7_Tasks/AttackTask.lua) · 116 | Combat task that steers toward enemies and requests actor attacks. | R06/R05 context; references undefined self.Target for distance and undeclared weapon in readiness branch. Validate current target before completion checks. |
| [AttemptEntryIntoBuildingTask.lua](../42/media/lua/client/7_Tasks/AttemptEntryIntoBuildingTask.lua) · 270 | Finds and navigates doors/windows to enter a target building, handling obstructions. | Current world object/path APIs, floor/load state and claims; coordinate with actor's parallel locked-door recovery logic. |
| [BarricadeBuildingTask.lua](../42/media/lua/client/7_Tasks/BarricadeBuildingTask.lua) · 129 | Selects windows and acquires/uses materials to barricade a building. | R07 copied barricade action. Recheck tool/material reservation and cancellation when building/window disappears. |
| [ChopWoodTask.lua](../42/media/lua/client/7_Tasks/ChopWoodTask.lua) · 186 | Moves to a designated area, finds an axe/tree, rests and queues chopping. | Group may become absent after constructor; validate tools and current chopping actions; bounded search and explicit resource policy. |
| [CleanInvTask.lua](../42/media/lua/client/7_Tasks/CleanInvTask.lua) · 207 | Drops/transfers inventory into a selected destination, optionally including hand items. | R08 skips first item; removal/movement/equipment state must use current action lifecycle. |
| [DialogueTask.lua](../42/media/lua/client/7_Tasks/DialogueTask.lua) · 98 | NPC direct dialogue/question task, waiting for UI/answers and dispatching resulting quest actions. | Task/UI lifetime and R05 cancellation; prevent repeated trigger execution or orphaned dialogue windows. |
| [DoctorTask.lua](../42/media/lua/client/7_Tasks/DoctorTask.lua) · 163 | Searches for patients, approaches them and queues prioritized medical treatments. | R14 nearest-patient bug and manufactured supplies; current treatment constructors, reservations and patient lifetime. |
| [EatFoodTask.lua](../42/media/lua/client/7_Tasks/EatFoodTask.lua) · 139 | Acquires selected food, opens canned food through item-name substitution, and queues eating. | Current food/open-can definitions and R07 eating override; avoid synthesizing replacement foods or losing original contents on failure. |
| [EquipWeaponTask.lua](../42/media/lua/client/7_Tasks/EquipWeaponTask.lua) · 47 | Selects and equips a usable weapon from NPC inventory/bag. | Current equipment and inventory ownership; distinguish melee/firearm capabilities and asynchronous transfers. |
| [FarmingTask.lua](../42/media/lua/client/7_Tasks/FarmingTask.lua) · 429 | Area-based crop search, watering, plowing, seed creation, planting, harvesting and storage. | R09: coherent farming port required; old seed action and water item, nil count return, generated resources. |
| [FindBuilding.lua](../42/media/lua/client/7_Tasks/FindBuilding.lua) · 75 | FindBuildingTask: chooses and approaches a building. | File/class names differ. Audit floor-0 searches, loaded squares and cancellation of sneaking/path state. |
| [FindThisTask.lua](../42/media/lua/client/7_Tasks/FindThisTask.lua) · 211 | Finds/acquires requested item/category quantities, including direct ground pickup and container transfers. | R08/R13 live-list mutation and premature success counting. Count successful transfer completion, not queued attempts. |
| [FindUnLootedBuildingTask.lua](../42/media/lua/client/7_Tasks/FindUnLootedBuildingTask.lua) · 168 | FindUnlootedBuildingTask: scans for unexplored buildings and wanders/retries entry. | R16 loses Square scope; random direction bounds, floor assumptions and duplicated attempted-building state. |
| [FirstAideTask.lua](../42/media/lua/client/7_Tasks/FirstAideTask.lua) · 84 | Self-bandaging task with a timed fallback. | R14: forced treatment, wrong item field and lifecycle bypass; replace fallback with explicit failure handling. |
| [FleeAwayFromHereTask.lua](../42/media/lua/client/7_Tasks/FleeAwayFromHereTask.lua) · 44 | FleeFromHereTask: flees a specified position rather than the current enemy. | File/class names differ. Validate source/destination and restore movement state on cancellation (R05). |
| [FleeTask.lua](../42/media/lua/client/7_Tasks/FleeTask.lua) · 44 | Runs away from last enemy until danger/follow conditions end it. | Cleanup currently lives in isComplete, making a query mutate movement. Cancellation must restore running/sneaking explicitly. |
| [FollowRouteTask.lua](../42/media/lua/client/7_Tasks/FollowRouteTask.lua) · 84 | Finds nearest waypoint in a saved route and traverses route points. | Empty route leaves CurrentRoutePoint unset; streamed-out targets and resume/save semantics require explicit handling. |
| [FollowTask.lua](../42/media/lua/client/7_Tasks/FollowTask.lua) · 263 | Follows a target, mirrors sneaking, manages doors, ropes and vehicle passenger entry. | Complex path/action integration; R05 claims, R07 duplicated vehicle action, player-0 assumptions and target unload/death. |
| [ForageTask.lua](../42/media/lua/client/7_Tasks/ForageTask.lua) · 80 | Alternates short movement and forest scavenging, then stops after a count. | Uses old ISNPCScavengeAction rather than current foraging system; only legacy zone types and gameplay/cost model. |
| [GatherWoodTask.lua](../42/media/lua/client/7_Tasks/GatherWoodTask.lua) · 143 | Collects logs/planks and carries them to a destination/storage area. | Current ground/container transfers, loaded destination, bag capacity and cancellation safety. |
| [GiveRewardToPlayerTask.lua](../42/media/lua/client/7_Tasks/GiveRewardToPlayerTask.lua) · 80 | Creates configured reward items, approaches a destination/player and drops them. | Creation is not a durable reward commit. Guard invalid item IDs/nil, cancelled drops and repeated quest execution (R15). |
| [GoCheckItOutTask.lua](../42/media/lua/client/7_Tasks/GoCheckItOutTask.lua) · 56 | Approaches a suspicious location, such as a heard shot. | Use the actual source actor/location rather than implicit player 0; completion/path failure/streaming must be bounded. |
| [GuardTask.lua](../42/media/lua/client/7_Tasks/GuardTask.lua) · 40 | Holds/returns to a guard square while AI can react to threats. | Explicit interrupt/resume and loaded-square policy; do not confuse a stationary task with disabled native actor updates. |
| [HoldStillTask.lua](../42/media/lua/client/7_Tasks/HoldStillTask.lua) · 68 | Holds an actor in place, including while another actor treats them. | Pair doctor/patient lifetime and R05 cancellation; always release held state if doctor fails or disappears. |
| [ListenTask.lua](../42/media/lua/client/7_Tasks/ListenTask.lua) · 80 | Faces/listens to another actor and handles interaction waiting. | Bound wait and actor lifetime; avoid leaving repeated listener tasks in a queue after UI/order changes. |
| [LockDoorsTask.lua](../42/media/lua/client/7_Tasks/LockDoorsTask.lua) · 79 | Walks building doors and locks/unlocks them. | Current door/key semantics, claims and interaction completion; check both sides/load state and task cleanup. |
| [LootTask.lua](../42/media/lua/client/7_Tasks/LootTask.lua) · 279 | LootCategoryTask: explores rooms/squares and gathers a selected item category. | File/class differ. Search filters depend on loot helpers (R08), category/fluid assumptions and action completion. |
| [PatrolTask.lua](../42/media/lua/client/7_Tasks/PatrolTask.lua) · 60 | Patrols between two persisted squares. | R11 missing active-endpoint state; current code can turn back midway. Validate both points after streaming/reload. |
| [PileCorpsesTask.lua](../42/media/lua/client/7_Tasks/PileCorpsesTask.lua) · 147 | Finds corpse bodies, picks them up, carries and drops at a pile square. | R05 ForceFinish differs from expected cleanup hook. Old corpse item/action representations and large scans require a subsystem check. |
| [PursueTask.lua](../42/media/lua/client/7_Tasks/PursueTask.lua) · 125 | Tracks/chases a last-seen enemy and transitions back to combat/search. | Target validity, path throttling, floor/LOS transitions and lost-target completion semantics. |
| [ReturnToBase.lua](../42/media/lua/client/7_Tasks/ReturnToBase.lua) · 60 | ReturnToBaseTask: navigates toward group base. | File/class differ. Missing/moved base, unloaded center square and role-resume behavior. |
| [SortLootTask.lua](../42/media/lua/client/7_Tasks/SortLootTask.lua) · 232 | Chooses group storage areas by item and deposits inventory/bag contents. | R08 first item skipped; stale TheDropContainer can survive when next destination is a square. Guard missing group/destination. |
| [SpeakDialogueTask.lua](../42/media/lua/client/7_Tasks/SpeakDialogueTask.lua) · 57 | Speaks a configured sequence/dialogue while managing task completion. | Use elapsed time and translation-safe content; avoid presentation-driven task timing (R20). |
| [SurenderTask.lua](../42/media/lua/client/7_Tasks/SurenderTask.lua) · 64 | Surrender behavior and relationship to a threatening actor. | Historical misspelling is part of current task keys. R06 execution damage; cancellation must restore state without implicit lethal effects. |
| [TakeGiftTask.lua](../42/media/lua/client/7_Tasks/TakeGiftTask.lua) · 129 | Approaches and takes offered items, then may equip weapons/clothes/bags. | R13 direct ground ownership mutations; container transfer uses getBag instead of chosen DestContainer for water. Revalidate gifting/ownership. |
| [TaskManager.lua](../42/media/lua/client/7_Tasks/TaskManager.lua) · 166 | Zero-based interruptible task queue, AI invocation, update limits and task lookup/removal. | R05 central lifecycle defects. Fix the contract before individually compensating in every job. |
| [ThreatenTask.lua](../42/media/lua/client/7_Tasks/ThreatenTask.lua) · 169 | Threat negotiation, countdown, aiming and escalation/flee dispatch. | R10 wrong global, forced demands, wrong task parent and undeclared weapon. Pure logic repairs plus actor-lifetime checks. |
| [WanderInAreaTask.lua](../42/media/lua/client/7_Tasks/WanderInAreaTask.lua) · 49 | Random idle movement inside a given area rectangle. | Validate rectangle, floor and free/reachable square; bounded retry and explicit timing. |
| [WanderInBaseTask.lua](../42/media/lua/client/7_Tasks/WanderInBaseTask.lua) · 52 | Idle wandering inside group base bounds. | Handle absent/moved group and streaming; current native walking/path behavior. |
| [WanderInBuildingTask.lua](../42/media/lua/client/7_Tasks/WanderInBuildingTask.lua) · 47 | Idle movement within a building. | Building/square validity, floors and reachability rather than only random coordinate selection. |
| [WanderTask.lua](../42/media/lua/client/7_Tasks/WanderTask.lua) · 39 | Short random movement around current position. | Bound retries and native path requests; no hidden FPS-based duration assumptions. |
| [WashSelfTask.lua](../42/media/lua/client/7_Tasks/WashSelfTask.lua) · 147 | Selects a water source and queues current vanilla self/clothing washing with resource budgeting. | Already partly ported. Validate real water/soap consumption and cancellation/native actor identity; mocked reservation tests are not integration proof. |

### `42/media/lua/client/8_QuestManager`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [QuestManager.lua](../42/media/lua/client/8_QuestManager/QuestManager.lua) · 555 | Global trigger/action interpreter, quest banner/info/answer handling, key and timed event callbacks. | R15 quantity/floor bugs and unimplemented persistence; many player-0/name references and string-dispatched actions. |

### `42/media/lua/client/9_QuestData`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [ExampleQuest.lua](../42/media/lua/client/9_QuestData/ExampleQuest.lua) · 119 | Example trigger/action/dialogue data demonstrating the quest interpreter. | Treat as executable scenario configuration: validate keys, one-shot flags, spawn coordinates and rewards before enabling. |
| [HilltopRescueQuest.lua](../42/media/lua/client/9_QuestData/HilltopRescueQuest.lua) · 99 | Hilltop rescue scenario triggers/dialogue/rewards using named NPCs and fixed world positions. | Separate scenario milestone; current map/NPC names, durable progress and reward idempotence (R15). |

### `42/media/lua/client/Debug`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [SuperbSurvivorsDebug.lua](../42/media/lua/client/Debug/SuperbSurvivorsDebug.lua) · 244 | Debug spawn/inspection/model comparison commands and actor diagnostics used during porting. | Useful isolated observation, not a sandbox for the whole mod. Random spawns/AI/save callbacks can still run; no new probes added in this audit. |

### `42/media/lua/client/ISUI/PlayerStats`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [ISPlayerStatsUI.lua](../42/media/lua/client/ISUI/PlayerStats/ISPlayerStatsUI.lua) · 794 | Large copied vanilla admin/player-stats UI, with attribute/profession/skill controls. | R18 known stale profession/access methods; globally shadows admin UI. Rebase to installed panel or isolate NPC-specific UI. |

### `42/media/lua/client/TimedActions`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [ISApplyBandage.lua](../42/media/lua/client/TimedActions/ISApplyBandage.lua) · 192 | Global vanilla-class replacement for bandaging, recently rebased to installed B42. | R07: verify real player and NPC complete/consume behavior after every target update; prefer narrow NPC adaptation. |
| [ISBarricadeAction.lua](../42/media/lua/client/TimedActions/ISBarricadeAction.lua) · 165 | Global vanilla-class replacement for barricading. | R07 old action lifecycle; review tools/materials, authority, duration, result and animation against installed vanilla. |
| [ISDisinfect.lua](../42/media/lua/client/TimedActions/ISDisinfect.lua) · 128 | Global vanilla-class replacement for disinfecting body parts. | R07 effects remain in perform; current vanilla separates complete. Rebase fluid/item consumption and patient/doctor behavior together. |
| [ISDropItemAction.lua](../42/media/lua/client/TimedActions/ISDropItemAction.lua) · 60 | Custom item-dropping helper; no matching current installed vanilla class found. | Namespace and port to current transfer/drop lifecycle; review world-item placement, corpse handling, inventory sync and cancellation. |
| [ISEatFoodAction.lua](../42/media/lua/client/TimedActions/ISEatFoodAction.lua) · 184 | Global vanilla-class replacement for eating. | R07 food consumption/on-eat effects/complete lifecycle; stale Cigarettes predicate is not itself a missing-item creation failure. |
| [ISEnterVehicle.lua](../42/media/lua/client/TimedActions/ISEnterVehicle.lua) · 75 | Replacement passenger entry action with animation completion bypass. | R07 duplicate of Vehicles/TimedActions version; one owner and current seat/door/position/network contract needed. |
| [ISGetHitFromBehindAction.lua](../42/media/lua/client/TimedActions/ISGetHitFromBehindAction.lua) · 48 | Custom forced hit/stagger response for a victim. | Match current animation variables/sets and queue cancellation; avoid allowing a visual reaction to own damage. |
| [ISGetHitFromFrontAction.lua](../42/media/lua/client/TimedActions/ISGetHitFromFrontAction.lua) · 51 | Custom front hit/stagger response for a victim. | Same animation/damage separation; shared player animation XML overrides require separate validation. |
| [ISNPCScavengeAction.lua](../42/media/lua/client/TimedActions/ISNPCScavengeAction.lua) · 410 | Legacy NPC scavenging implementation: loot choice, zone depletion/refill, XP and repeated action chaining. | R18 optional old UI methods. This is old foraging logic, not just a renamed current action; port to current foraging metadata/authority. |
| [ISRemoveBrokenGlass.lua](../42/media/lua/client/TimedActions/ISRemoveBrokenGlass.lua) · 60 | Global ISRemoveBrokenGlass replacement for removing broken glass from a window; recently rebased. | Follow-up comparison found only formatting differences from vanilla: redundant copy. Medical ISRemoveGlass is a separate installed action. |
| [ISSurenderAction.lua](../42/media/lua/client/TimedActions/ISSurenderAction.lua) · 49 | Custom surrender timed action/animation. | State cleanup and interruption must match SurenderTask; distinguish actor posture from health/attack permission. |
| [ZOverrides.lua](../42/media/lua/client/TimedActions/ZOverrides.lua) · 51 | Monkeypatches transfer/grab perform callbacks for group theft alerts. | R07 global, pre-success and reload-sensitive. Observe authoritative completed transfer rather than attempted action. |

### `42/media/lua/client/Vehicles/TimedActions`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [ISEnterVehicle.lua](../42/media/lua/client/Vehicles/TimedActions/ISEnterVehicle.lua) · 75 | Second copy of the same global vehicle-entry replacement. | R07 duplicate global/file ownership; remove ambiguity only after current constructor/lifecycle references are mapped. |

### `42/media/lua/server`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [SuperSurvivorsLoading.lua](../42/media/lua/server/SuperSurvivorsLoading.lua) · 26 | OnGameBoot sprite preload and activated-mod helper. | Not a server simulation implementation. Check texture resource paths; unused distribution require adds load coupling. |

### `42/media/lua/shared`

| File / lines | Responsibility | Port notes |
|---|---|---|
| [Utilities.lua](../42/media/lua/shared/Utilities.lua) · 28 | Global activated-mod detection, save-directory construction and item-source-square helper. | Duplicate getSaveDir with client utilities and broad global names. Explicit shared adapter boundary and nil/source type handling. |


## Main actor method map

`3_Other/SuperSurvivor.lua` is the largest concentration of responsibilities (4,866 lines). Suggested split points, preserving behavior first:

| Area | Entry points | Ownership to establish |
|---|---|---|
| Lifecycle | `new`, `newLoad`, `newSet`, `loadPlayer`, `spawnPlayer`, `delete`, `OnDeath` | Native actor versus wrapper; loaded versus durable state; player identity |
| Identity/group | ID/name, group/role/mode setters, relationship helpers | Stable canonical data keys and validation |
| Presentation | `renderName`, `Speak`, `RoleplaySpeak`, debug speech | Observer/player index and UI lifecycle |
| Perception | `RealCanSee`, `DoVision`, `DoHumanEntityScan`, companion scan | Native LOS versus AI perception, target lifetime |
| Navigation | `walkTo`, `WalkToPoint`, `StopWalk`, building/door/window helpers | Path request, action queue, claims and failure/retry |
| Decisions | `Task_Is*`, `NPCTask_*`, pursue scores | Avoid competing decisions spread across actor and AI manager |
| Update | `updateTime`, `update`, `PlayerUpdate`, `WalkToUpdate` | One simulation clock and bounded work |
| Combat | `requestCombatAttack`, `Attack`, `NPC_Attack`, readiness/reload | Native hit authority; no recursive engine update |
| Supplies | `getBag`, `FindThisNearBy`, food/water/weapon/ammo helpers | Qualified item IDs, fluid content and completed transfers |
| Persistence | `SaveSurvivor`, `SaveSurvivorOnMap` | Full native snapshot versus versioned registry metadata |
| Hygiene/health | injury speed helpers, `getFilth`, `CleanUp` | Current visuals, equipment, stats and timed actions |

## Maps and asset files

The four `spawnpoints.lua` files are separate scenario entry points, not part of the runtime Lua directory checked by `check_lua.py`. Each defines a global `SpawnPoints()` function with profession-specific entries. Keep them in their separate map scopes.

- [42/media/maps/Hilltop Survivor Camp/spawnpoints.lua](../42/media/maps/Hilltop%20Survivor%20Camp/spawnpoints.lua) (22 lines): scenario player-start coordinates; validate current map cell/world offsets and profession coverage.
- [42/media/maps/Military Blockade/spawnpoints.lua](../42/media/maps/Military%20Blockade/spawnpoints.lua) (22 lines): scenario player-start coordinates; validate current map cell/world offsets and profession coverage.
- [42/media/maps/Prison Escape/spawnpoints.lua](../42/media/maps/Prison%20Escape/spawnpoints.lua) (22 lines): scenario player-start coordinates; validate current map cell/world offsets and profession coverage.
- [42/media/maps/Woobury/spawnpoints.lua](../42/media/maps/Woobury/spawnpoints.lua) (22 lines): scenario player-start coordinates; validate current map cell/world offsets and profession coverage.

| Resource | Description and port work |
|---|---|
| `42/mod.info`, `42/poster.png` | Mod ID, name, minimum-version declaration and selection artwork. ID must match persistence/config lookups; minimum is not a tested range. |
| `42/media/maps/Hilltop Survivor Camp/map.info`, `description.txt`, `thumb.png` | Scenario/map selection metadata and artwork; fixed scenario coordinates also exist in Lua. |
| Same three files in `Military Blockade`, `Prison Escape`, `Woobury` | Other scenario selection metadata. Preserve spelling/path identity during migration; review translated display text separately. |
| Hilltop `39_26.lotheader`, `chunkdata_39_26.bin`, `world_39_26.lotpack` | Actual binary map cell content. Requires B42 map/asset validation; Lua syntax checks cannot establish compatibility. |
| `42/media/scripts/SuperSurvivors.txt` | `Survivors` module items (cigarettes, tea, bleach, grave/cross) and three legacy recipe blocks. Review current item types, callbacks, fluid/crafting definitions and unintended player access. |
| `42/media/AnimSets/player/actions/StaggerForward.xml`, `StaggerBackward.xml` | Player animation action-node additions used with custom hit reactions; no matching exact installed paths found. Shared action set, not NPC-only resources; validate current animation/schema/loading. |
| `42/zombie/scripting/commands/Character/Attack.class` | Legacy Java bytecode, no source/build integration. Establish whether/how it is loaded and compare exact target class semantics before relying on it or distributing it. |
| Six `42/media/lua/shared/Translate/EN/*.json` | Current English translation migration: challenge, context menu, dialogue/game sound, IGUI, moodles/names, and options/UI. Parse/schema/key coverage are separate checks from Lua/API validity. Other languages are currently absent. |
| `common/media/textures/MakingFriends.png`, `PVPOff.png`, `PVPOn.png` | Shared interaction/PvP artwork. The grave/cross icons referenced by scripts and the server preload are not supplied in this directory; check whether another mounted asset supplies them. Use exact disk names when packaging. |
| `common/media/sound/*.ogg` | Two shared sound assets. Check event/script references, playback API and volume/loop behavior against target. |
| `common/2026-11-06_04-21-12/*` | Live generated world metadata, 33 line-oriented Lua files plus three coordinate KV files at review time. These are not executable mod source; R02 explains why they are in the repository. Do not ship as defaults. |
| Root `media/` | Empty directory at review time; active content is in `42/media` and `common/media`. |

## Audit and development tools

| File | Purpose | Limits / port use |
|---|---|---|
| [inspect_game_api.py](../tools/inspect_game_api.py) | Reads class metadata/bytecode and member references directly from the installed JAR. | Static public existence is not Lua exposure or correct runtime behavior; use actual superclass/argument types and caller context. |
| [audit_survivor_api.py](../tools/audit_survivor_api.py) | Conservative known-receiver chain/arity/literal checks on main actor class. | Subclass return types and unresolved locals limit inference; not a whole-game type checker. |
| [audit_lua_names.py](../tools/audit_lua_names.py) | Whole runtime colon-method-name inventory against Java and Lua definitions. | No receiver/constructor/global-function/authority/lifecycle proof; review candidates manually. |
| [audit_b42_keys.py](../tools/audit_b42_keys.py) | Selected literal item IDs, perks, typed fields and legacy recipe inventory. | Dynamic IDs, optional catalogs and full script/crafting schemas are outside scope. |
| [check_lua.py](../tools/check_lua.py) | Compiles runtime Lua with Lua 5.1 through Lupa. | Does not execute methods or check map spawnpoint scripts, native actor behavior or assets. |

## Existing tests

These 12 Python files run mocked Lua or static contracts. They provide useful regressions but are not a replacement for engine integration.

| File | What it covers / practical limit |
|---|---|
| [test_api_inventory.py](../tests/test_api_inventory.py) | API audit inventory behavior; does not prove every candidate is a bug or every call is valid. |
| [test_bandaging.py](../tests/test_bandaging.py) | Bandage action's ported lifecycle/typed API contracts under mocks. Real actor animation/action identity still needs game testing. |
| [test_combat_water.py](../tests/test_combat_water.py) | Attack request, water and washing port contracts. Does not cover the remaining old hit-event damage override or full fluid/action execution. |
| [test_legacy_save_io.py](../tests/test_legacy_save_io.py) | Reader/writer helper behavior and mod identity/path contracts. Does not validate a crash-consistent whole-world save or location-index correctness. |
| [test_movement.py](../tests/test_movement.py) | Selected path/movement port behavior. Does not exercise streaming, multi-floor pathfinding, vehicle seats or patrol state over time. |
| [test_outfits.py](../tests/test_outfits.py) | Clothing/equipment port behavior with mocked items/body slots. Does not validate every preset/catalog combination or gender/random selection. |
| [test_render_bridge.py](../tests/test_render_bridge.py) | Render bridge filtering/submission and opacity calls. Cannot prove when native player rendering happens relative to the callback. |
| [test_render_debug.py](../tests/test_render_debug.py) | Debug inspection/model-report helpers. Does not establish visual correctness. |
| [test_startup.py](../tests/test_startup.py) | Selected startup/global/mock API contracts. Does not run full Lua boot in the native game. |
| [test_ui_parenting.py](../tests/test_ui_parenting.py) | Fixed parent/child UI-manager registration patterns. Does not cover member disappearance or transfer lifecycle. |
| [test_vision.py](../tests/test_vision.py) | Selected engine collection/visibility API contract. Native LOS viewport ownership remains separate. |
| [test_windows.py](../tests/test_windows.py) | Window interaction and broken-glass action contracts. Native path/animation and streaming remain untested. |

## Documentation and historical data

| File/category | How to use it |
|---|---|
| [README.md](../README.md) | Repository purpose/layout/packaging entry point. Packaging needs to exclude generated save output now present under common. |
| [B42_PORT.md](B42_PORT.md) | Original milestone/port approach and validation commands. Historical status is not an up-to-date compatibility guarantee. |
| [LOCAL_HANDOFF.md](LOCAL_HANDOFF.md) | Local installation, launch/debug workflow and chronological fixes. Later native/render/save findings in focused documents supersede earlier hypotheses. |
| [LOCAL_STARTUP_ERRORS_2026-10-21.md](LOCAL_STARTUP_ERRORS_2026-10-21.md) | Original loading/spawn failures and fixes; useful regression context. |
| [LONG_RUN_REVIEW_2026-11-08.md](LONG_RUN_REVIEW_2026-11-08.md) | Prior longer-run error/API/data findings; reconcile fixed items with current source. |
| [PLAYER_VISIBILITY_REVIEW_2026-10-21.md](PLAYER_VISIBILITY_REVIEW_2026-10-21.md) | Static/native follow-up on player visibility and ownership; important context for R01. |
| [REMAINING_API_NAMES_2026-10-21.md](REMAINING_API_NAMES_2026-10-21.md) | Earlier whole-runtime name inventory. Current review reruns tools against the current installation. |
| [RENDER_DIAGNOSTICS_2026-10-21.md](RENDER_DIAGNOSTICS_2026-10-21.md) | Detailed model/alpha/render investigations; observations and evolving hypotheses, not a stable engine abstraction. |
| [SAVE_IO_ERROR_2026-11-10.md](SAVE_IO_ERROR_2026-11-10.md) | Mod-ID/path save failure and latest crash/death context; distinguish error aftermath from cause. |
| [SUPER_SURVIVOR_API_AUDIT.md](SUPER_SURVIVOR_API_AUDIT.md) | Earlier main-class Java API review; rerun against each installed version before applying recommendations. |
| `reference/legacy-config/SurvivorOptions.lua` | Historical line-oriented option values; despite extension, not normal executable Lua defaults. Use as migration input only. |
| `reference/legacy-saves/05-02-2023_08-29-38/SurvivorGroup{0..5}{,Areas,Bounds,metaData}.lua` | 24 historical files: member arrays, flattened areas, bounds, count/leader metadata. Useful for decoding the old format; not runtime scripts. |
| Same historical directory `SurvivorManagerInfo.lua` | Historical survivor-count/high-water metadata. No full live actor snapshot included here. |
| `.gitignore` | Ignores Python bytecode and .venv; generated world output is not ignored. Fix the persistence root before treating ignore patterns as the solution. |
| `.venv/`, `__pycache__/`, `.git/` | Local environment, generated diagnostics/caches and repository internals; not mod content. |

## Coverage record

The review inventories 110 runtime Lua files and four map Lua files, totaling 27,938 lines including comments/blank lines at the initial snapshot. Every runtime filename is accounted for above. Selected high-risk execution paths were read in detail, all runtime files were included in the static inventories, and identified pure logic failures were probed separately. This is not a claim that every gameplay branch or binary resource has been tested. The main review lists the reproducible checks and integration gaps.
