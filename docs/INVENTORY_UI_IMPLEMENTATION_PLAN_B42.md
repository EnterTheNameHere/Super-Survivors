# SSR B42 Survivor Inventory and Give To — implementation plan

Status: AGREED DIRECTION / NOT IMPLEMENTED
Date: 2026-11-17
Basis: SSR-INVENTORY-01 source/native investigation, report docs/INVENTORY_B42_INVESTIGATION_01.md on codex/persistence-b42, source commit e76e662c11ad8a2af8b2e2c92515b7b6cf2c8b71.

## Objective and invariants

Replace SSR's separate bespoke player-versus-survivor transfer rows and equipment/wear UI, where there is evidence of safe native reuse, with an **independently instantiated survivor-owned inventory window** that offers familiar PZ item representation, bags, equipment, and actor-aware interactions. Extend the **existing human inventory right-click menu additively** with Give To -> Survivor Name. Do not replace, reparent, register as, or modify the human's existing vanilla inventory panes, hotbar, context menu behavior, UIManager player inventory registrations or player slots. No local-slot/singleton swap to fake NPC actions.

Preserve existing SSR transfer and clothing behavior until replacements reach functional parity, including native timed actions, interaction range/walls/Z, item identity, cancellation/progress, hidden bandage exclusions, and NPC remembered weapon preferences. Avoid speculative native Eat/Fill/Use on nonlocal actors.

## Evidence-led reuse boundary

Installed B42.22.2 native ISInventoryPage accepts display ItemContainer but its normal refresh/input/bag/context/bulk handlers resolve a local human player. ISInventoryPane likewise has actor assumptions and shared drag/UI state. ISEquippedItem is not turnkey arbitrary-NPC equipment UI. Thus **reuse native UI primitives, item textures, sorting/list/scroll and isolated tooltips**, while providing SSR-controlled owner binding and actions, rather than enabling a full stock NPC page unmodified. Existing actor-keyed timed action queues make individual owner-aware commands plausible, but some vanilla action callbacks still refresh human UI using playerNum and require narrow adapters. Proof in game is required; the source audit did not create a window.

## Phases (in order)

### 1. Independent read-only survivor window proof
- Explicit stable SSR ID + wrapper + exact actor and world; revalidate open/update/close, unloaded/dead/replaced/group reorder.
- Item icon, name, details/tooltip, sorting, human-like scroll; main and nested bags with bounded traversal and selected-container invalidation, distinct equipped/held/worn items. No vanilla context menu, drag, transfer, destructive actions or native player-ui registration.
- Verify with installed B42 in-game, preserving all human UI references, current selected bags, positioning/hotbar/drag state, human character singleton and slots, actor inventory/AI state. No changes to item ownership.
- Keep existing Inventory and Equipment windows accessible in parallel until acceptance.

### 2. Actor-aware item commands, individually accepted
- One operation at a time: item transfer (human -> survivor and survivor -> human), wear, remove/unequip, weapon equip, drop. Preserve native action timing, validation, interruption/progress/cancellation, and SSR's remembered AI gun/melee preference behavior.
- Centralize explicit actor/container/item ownership and range/Z/walls/capacity validation on click, start and completion as appropriate; check results rather than assuming native action completion equals item transfer. Avoid duplication/loss or accidentally affecting human hotbar/loot UI; don't cancel unrelated NPC queues.
- Correct discovered legacy UI defects in tightly scoped work: displayed human selected-bag item but callback passes main inventory source; mutable group member index can retarget recipient; inaccurate capacity header; ignored transfer errors. Validate use of actual item:getContainer() with root owner and stable NPC ID/ref.
- Reuse SSR transfer/clothing utilities and documented native callbacks rather than rewrite the physical item move as Remove/Add.

### 3. Additive human inventory context menu: Give To
- Extend OnFillInventoryObjectContextMenu(playerNum,context,items), preserving vanilla Eat/Fill/Equip and other mods. Show Give To -> eligible nearby survivor names; first milestone restrict to same-group companions pending explicit social/policy design.
- Selected item(s): normalize native grouped selection with getActualItems, skip group dummy and deduplicate item identities; handle selected bags and nested contents, prevent ancestor+child duplicate transfer and cycles, treat worn/favorite/locked items deliberately, preserve native item restrictions.
- At menu build, click, queued start and action completion validate actual local human source/root/container/item ownership, exact NPC ID/wrapper/actor/world, recipient eligibility, range <=2 tiles, same floor, unobstructed reach, destination capacity. A visible menu is not permanent permission. Batch partial success and skipped/cancelled items reported honestly; no atomic guarantee.
- Route through same vetted transfer service as survivor inventory window; do not touch vanilla inventory panel implementations.

### 4. Expand only from verified action families
- Evaluate additional survivor right-click actions (Eat, Fill, use/medical/crafting/repair), drag/drop, controller, bulk operations and mod-extensible context actions individually. Never blindly run human context-menu handlers against NPCs; each action has an explicit acting character. Keep NPC autonomy and goals separate from UI commands.

## Acceptance and risk checklist
- Exact source/recipient actor and item container at execution; no wrong survivor after group reorder/reload/unload.
- Human inventory pages/loot UI/hotbar/selected bag, player0-3 slots and singleton unchanged by merely opening/closing NPC window.
- No item loss/duplication with nested bags, worn/equipped items, dropped/transformed items, cancellation/partial batch, distance/walls/Z/capacity changes and interruption.
- Existing transfer and clothing progress/AI loadout preference semantics are not silently discarded.
- Test in disposable world; do not migrate source or delete old panels until approved acceptance. One stage per separately reviewed implementation assignment.
- Native B42 changes can affect UI action assumptions; source findings are scoped to installed 42.22.2.
- This is a **saved plan**, not approval to implement every phase or change the live game. Immediate gameplay priority remains fixing NPC combat.

## Source of truth and next action
Native audit on source implementation branch: docs/INVENTORY_B42_INVESTIGATION_01.md.
Only Phase 1 is the next inventory implementation candidate, after a separate bounded assignment. Do not begin while combat correction on the same exclusive source branch is in progress.
