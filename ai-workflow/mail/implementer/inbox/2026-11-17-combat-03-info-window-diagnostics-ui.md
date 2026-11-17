FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-COMBAT-03 UX refinement — contextual diagnostics in survivor info window
STATUS: AMENDMENT TO PENDING ASSIGNMENT; NO PRODUCTION COMBAT FIX
RELATED: ai-workflow/assignments/combat-b42-handoff-trace-03.md

User asks whether an observation-only log button should be added to the existing survivor info window, without SS Tests' world-mutating confirmation. Coordinator agrees. This is a UI/diagnostic placement refinement; preserve Combat03 core goals, bounds and safety.

Source inspection confirms two legacy info views:
- 42/media/lua/client/5_UI/SurvivorInfoWindow.lua (ISCollapsableWindow; Load(ASuperSurvivor); currently Call button)
- 42/media/lua/client/5_UI/SuperSurvivorInfoPanel.lua (PanelSurvivorInfo; show_survivor_info(member_index); Call and Close)
Investigate which is actually used in current B42 gameplay and whether both paths can be reached; don't duplicate blindly or modify unused UI alone. The first Load function currently writes player ModData().PerkCount while presenting info, and the latter also does so; avoid piggybacking such mutated state for new diagnostic, and consider isolated callbacks.

Desired workflow:
1. A debug-only Diagnostics button on the active survivor info window, bound to exactly that survivor (wrapper ID + actor ref/world, validated when clicked and when observation executes), not a global last-selected NPC.
2. An immediate "Log combat state" action that reuses existing Combat02 read-only capture logic and output format, with NO SS Tests destructive-test consent or need to choose NPC twice; do not fork another unsynchronized implementation. Show a small result indicator (logged, invalid/unavailable); do not incorrectly claim a combat PASS.
3. If implementing Combat03 bounded trace, offer "Start combat trace" / "Stop combat trace" here, with time/log cap and teardown on close, world/menu change, reload, death/unload, actor replacement. No extra attack or flag mutation. Keep ability to access diagnostic via SS Tests only if useful for regression/testing, but the user should not need it.
4. Button appears only when SSR Debug Options is ON, and never for the human or invalid/dead/unloaded SSR actor. No dangerous world-effect confirmation for verified observation-only operations; separate explicit start is appropriate for temporal tracing due to overhead. Do not disable safety/consent for world-mutating tests in SS Tests.
5. No production AI/combat/persistence change and no speculative rendering refresh. Verify existing UI button layout and lifecycle, avoid overlaps. Preserve user worktree edits. Test callback revalidation, wrong/changed survivor, cancellation, close/open/reload and no UI changes without debug.
6. Report if the current Combat02 snapshot implementation is coupled to SS Tests context and what safe refactoring is necessary. Ask coordinator review if significant adaptation is required rather than introducing global test framework bypass.
No code merge without review. If Combat03 already being implemented, incorporate only if it can be done safely in the same exclusive worktree; otherwise report proposed next bounded UI change.
