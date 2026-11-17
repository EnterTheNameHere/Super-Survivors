FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-COMBAT-05 — bounded first natural attack diagnostic
STATUS: REQUESTED / NOT ACKNOWLEDGED
ASSIGNMENT: ai-workflow/assignments/combat-b42-first-natural-attack-05.md

Combat04 reviewed. Native source proves an AIComponent initiateAttack overwrite before animation transition is possible, but original first failure is not observed; separate collision isLocalPlayer gate remains. Implement ONE opt-in read-only bounded observation in existing survivor Information -> Diagnostics, only for nonlocal actor with attackStarted=false, capturing natural requestCombatAttack, StopWalk, early OnPlayerUpdate, OnTick and native swing/collision events. No forced attacks, fixtures, damage injection, flag setters/resets, player slot swaps, game Java changes, production AI fixes, or inventory work. Logs must distinguish first observed from first-ever. Preserve user source/settings/common save edits and exclusive checkout; report tests and actual game-run status; no merge. Source report docs/COMBAT_B42_CORRECTION_OPTIONS_04.md is definitive prior evidence.
