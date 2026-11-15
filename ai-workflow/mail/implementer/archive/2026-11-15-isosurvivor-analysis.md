FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-15
SUBJECT: SSR-ANALYSIS-01 — source-only IsoSurvivor versus IsoPlayer comparison
STATUS: REQUESTED, NOT ACKNOWLEDGED
COORDINATION: B42
ASSIGNMENT: ai-workflow/assignments/isosurvivor-vs-isoplayer-analysis.md

User clarification: primarily investigate installed B42 Java/Lua before proposing or running any in-game test. Analyze inheritance, constructors/factories, actual vanilla call sites, native persistence, registration/unload/death lifecycle, gameplay APIs, and implications for SSR's IsoPlayer assumptions.

Please inspect engine code read-only and produce the comparison/report. Do not modify runtime mod code, create new tests, switch actor types, or request that user execute a new in-game test as part of this assignment. If a test seems useful, describe it as a future proposal only. Keep SSR-TEST-02 separate and respect exclusive worktree ownership.

Deliver report and addressed findings with exact engine/source references, status/limits and commit. No merge to B42.
