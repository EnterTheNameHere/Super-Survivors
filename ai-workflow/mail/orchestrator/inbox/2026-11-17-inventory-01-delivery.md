FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: INVESTIGATION DELIVERED FOR REVIEW / NO IMPLEMENTATION
SUBJECT: Inventory01 native presentation reusable; local actor routing requires adapters

Exclusive existing codex/persistence-b42 checkout; no other implementer or parallel
combat edits. Research followed Combat03 runtime evidence delivery. Source/report
commit e76e662c11ad8a2af8b2e2c92515b7b6cf2c8b71; parent
5c12e37dd76661c8e10cdcbad9b32788df494929. Modified paths:
docs/INVENTORY_B42_INVESTIGATION_01.md and docs/LOCAL_HANDOFF.md only.
Canonical ACK 5cc196af3aca617a0134d39bc1043049606d4367.

Installed B42.22.2 revision 3d39148846 Lua and installed Java classes inspected.
Report records JAR SHA256, exact source paths/line anchors, API contracts,
confidence/unknowns, current SSR callers, compatibility matrix and ordered proofs.

MAIN FINDING: stock inventory page binds displayed ItemContainer separately from
acting local player index. Creating a separate page does not inherently replace
the human UI, but refresh/input/context/bulk controls repeatedly resolve human
through getSpecificPlayer/getPlayerInventory/getPlayerLoot. ISEquippedItem also
has local UI dependencies despite accepting chr. Never swap slots/singleton or
replace/reparent/register human inventory UI to reuse NPC presentation.

Reusable: native frame/list/icon/sorting pieces and independently bound tooltip.
Not turnkey: full page/pane, worn/bag navigation, context actions, drag/controller
and bulk transfer. Explicit-actor native timed actions are useful but several
refresh human hotbar/backpack/loot UI by NPC playerNum. Preserve existing NPC
transfer selectedContainer isolation; audit each action family separately.

CONCRETE SSR ISSUES (documented, NOT FIXED):
- Human list can show selected bag but callback passes main inventory source;
  ItemContainer.contains(item) is direct, so legitimate bag item transfer rejects.
- Inventory row recipient uses mutable group index; reorder can retarget.
- Header compares two current-weight measures; not current/max capacity.
- Row ignores helper rejection; no visible error.
- Equipment weapon choices immediately equip AND set remembered AI preference;
  native equip replacement must preserve this semantics intentionally.
- Live TakeGift manually moves ground items/instant wears, unlike timed UI flow.
Old Back clothing accessor methods still exist: not classified obsolete.

Give To event confirmed exactly (playerNum,context,items), no test/origin flag.
Append submenu using native event, preserve Eat/Fill/other mods. Flatten through
getActualItems (skip dummy group[1], deduplicate); verify actual source and human
root, stable recipient ID/wrapper/actor/world, same floor/reach/walls/capacity at
execution. Handle nested ancestor selections, worn owner unequip, favorites and
partial batches. Initial recipient group restriction recommended pending design.

PHASES PROPOSED, NOT IMPLEMENTED:
1 Independent read-only presentation proof with human UI/player-slot invariants.
2 Individual actor-aware transfer/clothing/equip/drop proofs, native timing/cancel,
  SSR AI loadout preferences, no loss/duplication and stale actor handling.
3 Additive human Give To, then separately audited use/drag/controller features.
No generic NPC native Eat/Fill/crafting compatibility claim.

VALIDATION: source audit only, git diff --check passed on report/handoff. No new
tests or engine proof run; no production/UI/menu/action/transfer code changed,
runtime mutation, restart request or Java modification. User source/settings and
common saves untouched. Report branch contains prior source deliveries; do not
merge it wholesale as part of this documentation review. Canonical publication
contains ai-workflow only. Inventory implementation requires a new assignment.
Combat03 fixes await separate review; Test04 R1 restart proof pending, Test03 early
observer deferred. Next actor: orchestrator reviews report and orders bounded proof.
