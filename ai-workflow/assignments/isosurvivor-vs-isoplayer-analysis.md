# SSR-ANALYSIS-01 — IsoSurvivor vs IsoPlayer (installed B42 Java/Lua)

Date: 2026-11-15
Status: requested, not acknowledged
Coordinator: ChatGPT SSR orchestrator
Implementer: existing local Codex; verify current exclusive ownership
Canonical coordination: B42
Related but separate: SSR-TEST-02 cell-only IsoPlayer construction/factory investigation.

## Scope and intent
User requests a predominantly READ-ONLY Java/Lua analysis, BEFORE deciding whether an in-game test is warranted. No production edits and NO in-game experiment in this assignment. Do not treat legacy mod usage or class names as authoritative. Inspect installed Project Zomboid B42.22.2 JAR and bundled Lua to find what IsoSurvivor actually implements versus IsoPlayer.

## Investigate
1. Verify precise inheritance paths, Java constructor overloads, Lua exposure, descriptors and any factories, including SurvivorFactory. Distinguish factories returning descriptors, IsoSurvivors or IsoPlayers.
2. Identify actual engine instantiation/call sites for IsoSurvivor and IsoPlayer in installed Java/vanilla Lua, and whether IsoSurvivor participates in active B42 gameplay or appears retained from older systems. State the scope searched; no universal absence claims from limited search.
3. Compare serialization/deserialization and persistence: ByteBuffer overrides, filename save/load entrypoints, position, identity, inventory, skills, wounds/health, equipment and ModData. Explain whether equivalent round-trip is available for IsoSurvivor, and where caller-specific logic is required.
4. Compare actor initialization, registration and teardown: IsoCell and square membership, add/remove lists, streaming/chunk unload, death/corpses and special rules for living IsoPlayers.
5. Compare practical gameplay interfaces: movement/pathfinding, combat, animation, inventory/equipment, stats/needs, event hooks, NPC AI and scripting APIs. Don't assume functional AI because of class name. Note engine contracts used by SSR that assume IsoPlayer.
6. Assess migration surface WITHOUT changing code: which existing SSR classes, wrappers, and native save/load paths are IsoPlayer-specific and how hard a switch or common abstraction would be. Separate established blockers from open questions.
7. Summarize options (keep IsoPlayer; switch to IsoSurvivor; abstract over shared type) with confidence and costs, and identify any narrow runtime experiment that might eventually distinguish them. Do not implement experiments now.

## Evidence / deliverable
- Actual installed B42.22.2 Java bytecode/decompiled read-only + vanilla Lua are primary sources; public docs may corroborate, not replace.
- Written evidence-backed comparison matrix and findings with exact class/method references and relevant observed call sites.
- Explicit separation of verified, uncertain, and untested behaviors. If APIs are inaccessible or analysis inconclusive, say so.
- Put report in docs/ISOSURVIVOR_VS_ISOPLAYER_B42.md on implementation branch and send a new addressed summary to ai-workflow/mail/orchestrator/inbox/; commit documentation only and report SHA.
- No SSR production code modification, no Tests UI changes, no native game Java changes, no in-game test, no merge to B42, no competing implementer/worktree. Coordinate sequencing with existing SSR-TEST-02 investigation.
