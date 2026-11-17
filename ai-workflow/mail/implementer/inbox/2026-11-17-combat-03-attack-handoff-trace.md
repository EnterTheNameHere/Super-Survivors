FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-COMBAT-03 — bounded passive attack-state/hand-off tracing
STATUS: REQUESTED / NOT ACKNOWLEDGED
ASSIGNMENT: ai-workflow/assignments/combat-b42-handoff-trace-03.md
SOURCE: codex/persistence-b42

I reviewed Combat02 Roderick ID9's 33 real-engine snapshots (31 Attack front, 11 native in-range, 7 in-range WaitTicks0): all show isAttackStarted=true, isInitiateAttack=false, no animation/swing; equipped, ready, healthy, living zombie target. This strongly suggests a recurrent attack-state stall. Source busy guard would reject a new request, but no function return/first setter was captured. Stop manual still-frame sampling.

Audit native attack lifecycle and implement one short, user-invoked, owned-NPC passive temporal trace in SS Tests. If proven safe, also instrument naturally executed requestCombatAttack calls with original exactly once, unchanged arguments/results/errors; no forced calls, mutation, flag-reset, local-slot changes, damage, or prod fix. Strict bounds/teardown, verify installed callback/event APIs, otherwise report blocker. Preserve concurrent user edits and Test04 R1. ACK/delivery in orchestrator inbox; no source merge.
