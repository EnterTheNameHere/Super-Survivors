FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
STATUS: REQUESTED / NOT ACKNOWLEDGED
SUBJECT: SSR-TEST-04 R1 — persist baseline with normal world save
ASSIGNMENT: ai-workflow/assignments/test-04-persistent-baseline-r1.md
SOURCE: codex/persistence-b42

User explicitly says all three original Test 04 controls were run in-game: baseline, appearance compare and invisibility check. The user has not said whether appearance/invisibility symptoms were present during these runs or reported the outputs; don't claim bug repro. Please examine local logs if available and deliver actual scoped runtime observations separately.

User requests captured baseline be stored in the world save so it can be reused after restart. Implement only a versioned, scalar serializable baseline in a separate diagnostic GlobalModData key; normal save controls durability, no forced save. Don't persist Java refs, don't rely on mutable appearance for identity, distinguish missing stable cross-session identity and unavailable raw hair fields, and keep AFTER tests read-only. No auto capture/repair. Existing session-based baseline requires one new capture and completed save to gain persistence. Keep explicit control/UI and no production changes. See full assignment; ack branch ownership, deliver reviewed code and evidence through orchestrator inbox. No source merge.
