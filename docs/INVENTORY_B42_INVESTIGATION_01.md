# SSR-INVENTORY-01: native B42 inventory compatibility investigation

Date: 2026-11-17. Status: investigation delivered for review; no UI/action implementation or engine experiment.

## Recommendation

Build a separate survivor-owned window with native presentation pieces and SSR actor-aware commands. Do not instantiate an unrestricted stock inventory page against an NPC container and treat its player index as NPC ownership. The displayed ItemContainer and the acting local player are separate bindings in vanilla. A page constructor does not itself replace the human inventory, but normal page refresh, input handlers and context actions repeatedly resolve the human through getSpecificPlayer.

First prove an independent, read-only window, with explicit stable survivor identity and no stock action/drag paths. Then prove individual commands using native timed actions plus NPC UI isolation. Add human-side Give To as a separate additive event subscriber afterward. Retain existing interfaces until their replacement covers their semantics.

## Evidence and limits

- Installed game: G:/Steam/steamapps/common/ProjectZomboid, B42.22.2 revision 3d39148846. Installed zombie.jar SHA256: 3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
- Implementation checkout: codex/persistence-b42, exclusive existing local implementer. Starting source HEAD def8c128bf9f0d1f9c841c22ddb72329525b4c5d; assignment ACK 5c12e37dd76661c8e10cdcbad9b32788df494929. Source reviewed includes pre-existing uncommitted user changes; none changed by this audit.
- Native references below are relative to the installed media/lua directory. Line numbers refer to that installed copy, not an online B41 API. Java was inspected from the installed classes using CFR; decompiler line numbers are navigation aids, not original source lines.
- High confidence: inspected Lua call signatures, local-player dependencies, SSR callbacks and Java container membership. Inference/proposal: a safe reuse boundary and future command policy. Not proved: a running standalone NPC page, every item-specific tooltip/action, multiplayer, controller behavior, other-mod interactions or future engine builds.
- No runtime mutation, new UI, menu hook, transfer implementation, or production edits. No new tests or in-game checks were run for this documentation-only assignment. Existing runtime combat evidence and persistence milestones remain separate.

## Native ownership and presentation

| Evidence | Contract and implication |
| --- | --- |
| client/ISUI/ISInventoryPage.lua:1940, :68 | new(x,y,width,height,inventory,onCharacter,zoom) accepts a displayed container, not an arbitrary actor. Child inventoryPane receives page.player. onCharacter describes human inventory versus loot behavior; false is not NPC mode. |
| client/ISUI/PlayerData/ISPlayerDataObject.lua:27–63 | Human UI creation assigns page.player, registers playerInventory/lootInventory and calls UIManager.setPlayerInventory. A separate SSR window must never replace these registrations or reparent the human pages. |
| client/ISUI/ISInventoryPage.lua:1537–1581 | refreshBackpacks resolves getSpecificPlayer(self.player), rebuilds human main/bag/keyring entries, and consults floor/vehicle/world containers. It also marks shared crafting/build UI dirty. Merely assigning NPC.inventory cannot supply NPC bag hierarchy. |
| client/ISUI/ISInventoryPage.lua:482, :636 | update/facing and weight presentation use the local actor. Actor-dependent headers must be supplied explicitly. |
| client/ISUI/ISInventoryPane.lua:2834 | new(x,y,width,height,inventory,zoom) binds a container and creates selection/drag state. It has no NPC actor parameter. Pass a valid numeric zoom; this constructor uses it arithmetically. |
| client/ISUI/ISInventoryPane.lua:2039–2197 | refreshContainer consults local actor/hotbar for worn/held/attached state, groups items, rebuilds selection and clears container drawDirty. This is not a completely inert read. |
| client/ISUI/ISInventoryPane.lua:557–575 | Sorting operates on a Lua presentation list using item names, weights and container ordering. Reuse/copy this presentation logic without sorting or changing the actual container ArrayList. |
| client/ISUI/ISInventoryPane.lua:866, :960, :1598 | Tooltips default to local actor; double-click and context-menu paths invoke local-player actions. Disabling right-click alone does not make a pane read-only. |
| client/ISUI/ISInventoryPane.lua:1803, :1836, :1890, :2776 | Rendering/update also touch drag state, tooltip/controller behavior and world highlight. Default handlers can finish a drag using shared ISMouseDrag. A passive proof must constrain all input and these active paths. |
| client/ISUI/InventoryWindow/ISInventoryWindowContainerControls.lua:39–56, :108 | Bulk-transfer handlers bind playerObj=getSpecificPlayer(window.player), inspect getPlayerLoot and share registered handler classes. They need actor-aware replacements, not automatic inclusion. |
| client/ISUI/ISEquippedItem.lua:602–610, :536 | Although new takes chr, it caches human inventory/loot/info UI by chr:getPlayerNum(), and tooltip/action paths resolve the human. Not an arbitrary-NPC equipment panel. |
| client/XpSystem/ISUI/ISCharacterScreen.lua:736 | Character screen is player-number based. ISClothingInsPanel is an insulation display, not a ready-made arbitrary-owner equipment slot interface. No general-purpose standalone NPC equipment window was established. |

Use independent window, selection, scroll, tooltip and container navigation state. Keep human UI identities, visibility, selected bags, geometry, hotbar, drag state and player slots intact. A local index may describe the viewer's viewport/input, but must not implicitly choose the inventory actor. Do not swap IsoPlayer singleton/players entries or camera slots to make stock actions work.

### Icons, tooltips, worn/held and bags

InventoryItem:getTex() exists in the installed Java and delegates getTexture. Existing SSR rows already use it. ISToolTipInv:setCharacter(chr) at client/ISUI/ISToolTipInv.lua:173 delegates to ObjectTooltip:setCharacter(IsoGameCharacter); the installed Java stores that explicit character. Independent tooltip instances can therefore present an NPC actor without replacing a human UI instance. Native tooltip rendering also checks shared ISContextMenu.instance and viewport positioning, so isolated lifetime/position tests remain necessary.

Do not promise zero object changes from all presentation APIs: installed InventoryItem:getVisual() lazily creates/picks uninitialized ItemVisual values. Prefer existing textures and already initialized visuals, and distinguish harmless UI/cache updates from item ownership, gameplay or appearance mutation. The full set of modded item DoTooltip implementations was not audited.

Read worn items, primary/secondary hands and bag ItemContainers from the exact NPC, with explicit hidden-item filtering. Preserve the current exclusion of hidden worn bandage internals from Equipment. Display worn versus held versus attached distinctly; a held bag is both an item and a container. Traverse only container ownership rooted in that NPC, with visited identities and a depth bound; handle moving/removing an open bag by invalidating its view. Do not borrow refreshBackpacks to populate NPC bags.

## Native actions and queues

| Native contract | Reuse boundary |
| --- | --- |
| client/TimedActions/ISInventoryTransferAction.lua:764, :11 | new(character,item,srcContainer,destContainer,time) takes an explicit actor and exact containers. Native validation/timing/capacity are useful. Source disappearance sets dontAdd and may finish without a move; completion is not proof of transfer success. |
| Same file :129, :477, :632, :693 | update/perform may select getPlayerLoot(character:getPlayerNum()) via selectedContainer. transferItem delegates actual movement to ISTransferAction; favorite items moving outside actor inventory can be skipped. setOnComplete exists. Native action batches can merge queued transfers. Verify actual source/destination postconditions per item. |
| shared/TimedActions/ISTransferAction.lua:96 onward | This is Lua, not a Java global. Core movement handles bag containment cycles, world-floor/radio/animal-zone details and container/network bookkeeping. Do not replace it with manual Remove/Add or call its mutation method as a UI shortcut. |
| shared/TimedActions/ISInventoryTransferUtil.lua:14–60 | Factory can choose corpse-grab behavior. Its corpse branch resolves the local player inventory from actor.playerNum, even though the factory accepts character. Do not blindly route arbitrary NPC corpse transfers through this utility. |
| shared/TimedActions/ISWearClothing.lua:5, :92, :108 | Explicit actor, native validity, duration/animation/job progress and interruption. perform can refresh human inventory backpacks by actor.playerNum; complete mutates worn/held state. NPC adapter must isolate the former while preserving native latter. |
| shared/TimedActions/ISUnequipAction.lua:5, :66, :94, :111 | Explicit actor but hotbar/backpack UI access by playerNum. Preserve ownership checks and real timing; suppress only proven NPC-to-human UI callbacks. |
| shared/TimedActions/ISEquipWeaponAction.lua:113, :138, :253 | Explicit actor, primary/twoHands/alwaysTurnOn parameters. Constructor/hotbar and bag-refresh branches still target local UI. Not safe merely because new accepts an NPC. |
| shared/TimedActions/ISDropWorldItemAction.lua:5, :49, :157 | Explicit actor/item/square/offsets/rotation/isMultiple. Candidate for an actor-aware drop command after source/unequip validation. Complete handles lit-item replacement and radios; floor/placement validation matters. No guarantee every modded item survives as the identical object. |
| client/TimedActions/ISTimedActionQueue.lua:9, :60, :138, :278 | Queues are keyed by character object, not local player index. add begins the first action, completion advances, OnTick services all queues. Thus NPC queue ownership is supported independently of UI ownership. Local-only speed-reset logic is separate. |
| shared/TimedActions/ISBaseTimedAction.lua:60–110 | stop resets actor queue; perform advances it. Timing incorporates unhappiness, drunkenness, hand pain and temperature. Preserve native start/update/stop/perform/complete lifecycle; do not emulate it by instant mutations or manually calling complete. |

Timed action acceptance does not freeze either participant or guarantee eventual success. Validate stable actors/world, live item/container, reach and capacity again when execution starts and during the action as appropriate. Respect cancellation, already queued work and AI danger interruptions. A batch is not atomic: report skipped/cancelled/transferred items honestly and never roll back by duplicating items.

## SSR inventory and equipment audit

### Current UI and identity

- SuperSurvivorWindow.lua:45–46 and :584 opens Inventory/Equipment; SuperSurvivorPanelUtilities.open resolves survivor ID for panel switching. Preserve both entry points and the quick Inventory/Equipment footer switch.
- SuperSurvivorInventory.lua:64–88 transfers one row item. Human -> NPC is acted by the human; NPC -> human is acted by the NPC. Both require living current member, distance <=2 and same Z; the helper adds wall/reach validation. Transfer failure results are currently ignored by the row, allowing silent rejection.
- Concrete source mismatch: SuperSurvivorInventory.lua:230 displays getPlayerInventory(0).inventory:getItems(), which can be a selected bag. Its transfer callback chooses human:getInventory() as source. Installed ItemContainer.contains(InventoryItem) checks direct list membership, so displayed nested-bag items fail helper source validation. Use actual item:getContainer() after proving its root owner, not a guessed root source.
- Rows resolve a mutable group member index; member_index is also assigned on shared row/panel objects around :318. A group reorder/removal can retarget a human-owned item to the new occupant of the old index. Bind survivor ID + wrapper + exact actor + world and revalidate; never use displayed name or group position as authority.
- NPC list shows main inventory only. It does not provide nested bag navigation. Headers around :301–307 combine getCapacityWeight/getContentsWeight; installed Java shows both are measures of current load, not current/max capacity. Correct capacity wording/calculation in a later implementation.
- SuperSurvivorLoadout.lua:60–96 selects current group member; a row caches its wrapper, shows pending native clothing progress/cancel, and changes weapons immediately through setGunWep/reEquipGun or setMeleeWep/reEquipMelee. Weapon choices also update remembered AI loadout, not just the hand slot. A native Equip command must preserve or deliberately revise this preference behavior.
- Loadout available items (:219) are nonhidden, unequipped Clothing/InventoryContainer/Weapon from main inventory; equipped list (:273) uses nonhidden isEquipped, including worn and held. Keep hidden bandage exclusion. Existing clothing self-management is remotely commandable; do not accidentally add human proximity rules to every NPC self-wear command while designing nearby Give To.

### Existing helpers to retain and extend

SuperSurvivorTransferUtilities.lua:15–40 validates direct source membership and capacity, checks same-floor two-tile unblocked actor reach through outermost container ownership, queues owner unequip before transfer, and rechecks reach through the native action isValid wrapper. It retains native transfer validation/timing and completion callbacks. It does not itself bind a stable survivor registry identity or reject all actor-death/replacement cases. Noncharacter world-container reach remains native validation territory; this helper is not blanket permission for arbitrary world transfers.

Its class hooks (:44–81) detach selectedContainer for nonlocal NPC update/perform, preventing the known human loot-panel selection through shared playerNum. They preserve base calls and apply to legacy direct native callers too. Retain this behavior; audit other UI callbacks separately. Hook chaining/reload with other mods remains a regression case, not a solved compatibility guarantee.

SuperSurvivorClothingUtilities.lua:14–38 requires a live actor, direct main-inventory ownership, valid wearable body location and at most one clothing action. It queues native wear/remove and disables remove-action hotbar binding for NPCs. :40 cancellation clears the entire actor queue, not just that row's command. Loadout calls StopWalk before starting clothing. SuperSurvivor:StopWalk (:3268) clears Lua/native queues and resets movement/combat state. A new UI needs explicit command ownership/interruption policy; calling StopWalk indiscriminately can cancel unrelated work.

### Callers, roles and survival behavior

The two panels use these helpers; Debug/SuperbSurvivorsTests.lua also calls the transfer helper. Legacy AI callers still construct native ISInventoryTransferAction directly: FindThisTask:191, CleanInvTask:138/:183, ChopWoodTask:71–83, LootTask:208, SortLootTask:148/:207 and TakeGiftTask:102. Their environmental destinations, actor choice and durations must survive UI replacement. Do not globally force these through a human Give To policy.

getBag() (SuperSurvivor.lua:1539) chooses equipped back bag, then secondary bag, then primary bag, then main inventory. This differs from both current panel main-inventory display and human selected bag. LootTask chooses items/categories and compares weapons; CleanInvTask/SortLootTask protect held/remembered weapons and ammo except explicit cleanup choices, and use group storage-area routing. Preserve AI tasks and group roles rather than replacing their behavior with native UI actions.

TakeGiftTask:74–114 still manually moves ground gifts and immediately wears gifts, while container gifts use a timed transfer then WearThis. This is live gameplay, not only spawn setup: it needs separate unification with validated commands to avoid bypassing timing/ownership. WearThis in suits/spawn/load appearance setup is legitimate immediate initialization and should remain separate. Installed IsoGameCharacter still has getClothingItem_Back/setClothingItem_Back and typed setWornItem: these names are valid B42, not obsolete just because they look old.

Native Eat/Fill/other use menus make actor-specific survival decisions. Current SSR AI and its preferences/needs must remain independent of the new inventory view. This audit does not establish safe generic NPC Eat/Drink/medication/crafting/recipe/fluid commands or replace survival AI. Keep them unavailable in the proof until each action family is inspected. UI replacement alone does not improve autonomous survival.

## Additive human inventory Give To proposal

Installed client/ISUI/ISInventoryPaneContextMenu.lua:27 builds the normal menu; :935 calls triggerEvent("OnFillInventoryObjectContextMenu", player, context, items), then returns context. The subscriber signature is exactly (playerNum, context, items), with no test flag, actor or isInPlayerInventory argument. Empty-selection uses a separate createMenuNoItems path. Vanilla paused/tutorial availability applies; do not promise this menu works while paused.

1. Subscribe through the event and append one submenu. Do not replace createMenu, clear existing entries, consume the event, or rebuild Eat/Fill. Native submenu pattern: context:addOption followed by ISContextMenu:getNew(context) and context:addSubMenu(option, submenu). Namespace callbacks and avoid duplicate event registration on reload.
2. Normalize selection with ISInventoryPane.getActualItems(items) (:915): single InventoryItems and grouped .items entries; group .items[1] is a dummy duplicate and must be skipped. It deduplicates identity when both group and child are selected. getActualUniqueItems is representative-per-group and wrong for transferring all selected items.
3. Resolve the actual human using playerNum, verify local/living/current-world actor. The event lacks origin ownership: prove each item's actual containing chain is rooted in this human inventory (ItemContainer:isInCharacterInventory plus bounded root checks), with item:getContainer() as exact source. Exclude world loot and other actors even if the same event fires there.
4. List only loaded, live, currently eligible SSR recipients by name; capture ID, wrapper, exact actor and world, not index/name alone. Recommended first milestone: current group companions only, same Z, <=2 tiles and unblocked reach, matching existing transfer interaction. Permission for non-group/friendly gifts is a design decision; do not silently expose hostile/remote recipients.
5. At click and action start, re-resolve and compare identities, group/eligibility, loaded/dead state, world, source membership/root, range/Z/walls, destination policy and hasRoomFor(actor,item). Recheck while queued; a valid menu is not durable authorization. Native source disappearance/completion skipping must be reported as a skip, not success.
6. Human-owned equipped items: queue owner unequip then transfer, with actual source verified again afterward. Preserve favorite/locked/hidden/special-item restrictions or show an explicit reason. Initially exclude corpse-grab, world devices and other special transfers until tested. Human is the acting donor for Give To; do not ask NPC to unequip a human item.
7. Handle nested selection and multiple items serially. If an ancestor bag and a child item are both selected, choose and explain one deterministic policy (initially reject overlap or transfer bag subtree once), beyond native object deduplication. Prevent destination-inside-source cycles, re-evaluate capacity after preceding transfers, and track per-item results. Do not automatically split stacks, relocate children or aggregate capacity as a transaction.
8. Return focus/refresh through independent UI state and existing human APIs only as normal human actions do. Never register the NPC window as getPlayerInventory/getPlayerLoot. Compatible additive menu hooks preserve other mods' entries; item-specific and hook-order interoperability still needs testing.

Installed ItemContainer.contains(item) is direct membership; getOutermostContainer and isInCharacterInventory follow containing bags with bounded traversal. hasRoomFor(actor,item) includes item acceptance, effective capacity and nested/character load rules. Plain weight addition is not an equivalent validation.

## Compatibility matrix

| Feature | Classification | Initial boundary |
| --- | --- | --- |
| Separate window/frame/scroll UI | Native reusable independent primitives | Own lifecycle and SSR stable actor binding; no pdata/UIManager inventory registration. |
| Item icons and basic labels | Native reusable presentation | getTex and copied list metadata; do not invoke gameplay actions. |
| Tooltip | Presentation + SSR binding | Independent ISToolTipInv, setCharacter(NPC), isolated lifetime/position; modded tooltip side effects unproven. |
| Sorting and grouped stacks | Presentation reuse | Sort UI copy; native getActualItems for selected items; retain identity and skip group dummy. |
| Full ISInventoryPage/ISInventoryPane | Presentation only after adaptation | Default update/input/render/control paths are not proven passive or actor independent. |
| Worn/held/attached display | Presentation + SSR binding | Read exact NPC state; no stock ISEquippedItem as turnkey owner. Keep hidden bandages excluded. |
| Nested containers/bag tabs | Presentation + SSR hierarchy | Explicit NPC root, bounded traversal, stale bag invalidation; no human refreshBackpacks. |
| Wear/remove | Retain SSR + native actions | Preserve timing/progress/cancel; isolate hotbar/backpack callbacks; nested source staging later. |
| Equip weapon | Retain SSR preferences + future timed adapter | Preserve LastGunUsed/LastMeleeUsed and mode; audit native equip callbacks. Immediate UI equip needs replacement, not removed Java names. |
| Actor-to-actor transfer | Retain SSR native-action adapter | Fix exact source/stable identity/silent failure later; preserve reach, owner unequip, timing and NPC loot-UI hook. |
| Drop | Native action candidate + SSR adapter | Native placement/special-item handling, ownership and interrupt tests first. |
| Eat/fill/use/medicine/crafting | Unknown/unproven per family | Do not enable entire local-human native context menu on NPC pane. |
| Human Give To | Additive native event + SSR transfer | Keep original menu; normalize selection and revalidate actual donor/recipient. |
| Multi-selection/batch transfer | Presentation + SSR command policy | Per-item result/capacity/ancestor handling; no atomic guarantee. |
| Drag/drop and bulk controls | Defer; replace actor-routing assumptions | Shared drag state, human hotbar/loot endpoints and controller routes need full proof. |
| Current bespoke panels | Retain until parity | Keep entry points, panel switch, equipment filtering, preferences and progress/cancel. |
| Manual live ground-gift move/instant wear | Replace unsafe bypass in later assignment | Existing methods valid; path bypasses native ownership/timing pipeline. |

## Ordered future experiments and acceptance

1. Read-only survivor window: exact ID/wrapper/actor/world binding, independent list/tooltips, NPC main/bag navigation and worn/held display; no native input actions, drag, bulk controls or actor queues. Safer first option is generic native list/frame primitives rather than a stock pane with only right-click disabled. Test human UI identity/geometry/selected container/visibility/hotbar/drag/player-slot/singleton invariants before/after opening, switching and closing two survivor views; validate no item/equipment/AI mutation. Include unload, death, group reorder, world reload and actor replacement. Lazy caches/drawDirty must be distinguished from gameplay mutation.
2. Actor-aware command proof: one item/command at a time, starting with existing transfer and clothing, then weapon equip/drop. Preserve native queue lifecycle and SSR preferences; narrowly isolate NPC UI callbacks. Test exact ownership counts and destination identity before/after, insufficient capacity, wall/Z/range changes before and during action, source moved/deleted, favorite/hidden/worn/held/two-handed/nested bag, interruption, closing window and actor replacement. Check progress/cancel behavior and unrelated human/AI queues. Special drop transformations require semantic conservation, not an unconditional same-object assertion.
3. Give To proof: additive event only, companion eligibility initially, stable bindings and real source containers. Test Eat/Fill/other-mod entries unchanged, raw/group/mixed selection, duplicate child/group, selected-bag items, ancestor bag+child overlap, capacity exhausted mid-batch, stale menu/recipient, two humans where supported, and no remote/world-item transfer. Confirm no duplicate/lost items across cancelled/partially completed batches and truthful results.
4. Only after these pass: broader use actions and optional drag/controller routes, each as its own inspected action family. Test installed build first; no future-B42 or multiplayer compatibility claim from this audit.

No restart or user test is required for this report. Implementation authorization and review of these boundaries are the next step. Combat03 further fixes await their separate review; Test04 R1 restart proof remains pending; Test03 early observer remains deferred.
