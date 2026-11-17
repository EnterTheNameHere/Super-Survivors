FROM: SSR orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-COMBAT-01 — user sees survivors do not try to fight in gameplay
STATUS: NEW REQUEST / NOT ACKNOWLEDGED
CANONICAL: B42
ASSIGNMENT: ai-workflow/assignments/combat-b42-investigation-01.md

User reports survivors currently not attempting combat. Treat as important basic-survival gameplay blocker. Source first: trace NPC DoVision/getLuaObjectList, enemy selection, all task scheduling/role/fear/weapon checks, AttackTask validity/completion, requestCombatAttack and B42 native attack activation. Distinguish no perception, no decision, rejected native request, or missing damage. Note outdoor nil-room comparison alone doesn't prove invalid target. Do not rewrite AI or manufacture damage.

Please finish or explicitly defer the already pending Test-04 persistent-baseline R1 on your exclusive branch before combat work; confirm ownership/priority in ACK. Deliver source-backed findings and proposal for minimal user-consented diagnostics, no production combat fix or merge without separate review.
