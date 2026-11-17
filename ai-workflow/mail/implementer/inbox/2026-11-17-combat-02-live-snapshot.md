FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-COMBAT-02 — implement read-only inspect-existing-survivor diagnostic
STATUS: REQUESTED / NOT ACKNOWLEDGED
CANONICAL: B42
SOURCE: codex/persistence-b42
ASSIGNMENT: ai-workflow/assignments/combat-b42-observation-02.md

Reviewed SSR-COMBAT-01 delivery and native/source report. Proven impossible equip predicate and zombie PursueTask wrapper requirement; native NPC aiming/control and local-player collision gate remain serious B42 integration risks. No actual combat runtime stage identified yet. Please make the smallest explicitly user-run existing-NPC combat state inspection in SS Tests. Require selected owned loaded NPC, report cached perception/target/current task/weapon/AI inputs and safely readable native attack flags, without changing world/AI/actors. No forced swing, zombies, state updates or interception in this step. Preserve Test04 R1 baseline work; verify branch ownership and no concurrent implementer. Deliver actual UI steps and tested/unverified distinction, no production combat fix/merge. If temporal event tracing necessary, propose separately rather than implementing unbounded instrumentation.
