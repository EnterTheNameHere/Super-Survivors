FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
SUBJECT: SSR-PERSIST-01 R1 clarification — engine behavior investigation and safe runtime probe
STATUS: SUPERSEDING CLARIFICATION / INVESTIGATION ASSIGNED / NOT ACCEPTED
DATE: 2026-11-15
CANONICAL COORDINATION REF: B42
SOURCE REVIEWED: dc4dde25d612d33650c1ed5ef4ad0401c02394b5 (codex/persistence-b42)
SUPERSEDES: ai-workflow/mail/implementer/inbox/2026-11-15-persist-01-r1-review.md

WHY THIS CLARIFICATION EXISTS
The earlier review promoted a potential performance concern into a mandatory rewrite without measuring it or establishing the native-engine contract. The user corrected that reasoning. Treat the older request's item 2 as an INVESTIGATION, not an instruction to replace working code. The rest of that mail remains historical context, not autonomous authorization for unrelated production changes.

PRIMARY ASSIGNMENT — RESEARCH AND USER-EXECUTABLE PROBE
1. Inspect INSTALLED B42.22.2 Lua and Java code (not three-year-old B40/B41 mod code) to establish precisely:
   - What IsoPlayer:save(String) serializes concerning actor X/Y/Z and world association.
   - What IsoPlayer:load(String) actually restores, including coordinates and current square.
   - What actor construction, square/world registration, add/remove lists and chunk loading require before/after load.
   - How loading callbacks and initial squares interact with registry and player initialization.
   Merely seeing method signatures or observing historical mod calls is insufficient.
2. Create a SAFE, FOCUSED, opt-in runtime diagnostic probe for the USER to execute after creating a fresh disposable B42 world and a player character. Prefer the smallest test harness with clear invocation and log output. Never overwrite the human player's snapshot or change their character, and do not alter game Java files. Use uniquely named test snapshots and test NPCs where necessary, carefully following verified engine actor lifecycle.
3. Probe should capture before and after X/Y/Z, actor/square identity, getCurrentSquare, membership in world object/add/remove lists if relevant, whether loaded actor's position changed without any manual setX/Y/Z, and meaningful failure/error cases. Distinguish a same-session roundtrip from a genuine save/quit/restart test; provide both if safe and manageable.
4. Investigate whether getGridSquare returns an object reference, what lifecycle bounds that reference has, and whether B42 provides an authoritative event/query for loaded squares/chunks. Explain whether already known saved position plus event-driven loading and a one-time catch-up can replace the per-tick global scan. Determine cost/need; do not assume the existing scan is a proven performance bottleneck.
5. Investigate SSPersistence.tick unload rules with actual B42 pending add/remove and streaming lifecycle. Do not assume native remove-list inclusion means our code should detach the actor immediately.

DECISION BOUNDARY
First deliver concrete findings and the runnable, opt-in diagnostic test with precise user instructions, and report any unavoidable safety assumptions. Do NOT rewrite persistence logic or optimize the tick scan yet solely to satisfy the previous wording. If an actual correctness defect is demonstrated, send the proposed bounded correction and supporting evidence to the orchestrator for review. User will run the in-game test; no Codex claim of actual engine gameplay results without such evidence.

REPORT BACK
Send an addressed findings/delivery message to ai-workflow/mail/orchestrator/inbox/ with exact branch and SHA, installed JAR source evidence, the probe invocation, expected recorded data and limitations, and automated test results if applicable. Update state. Do not merge onto canonical B42 without authorization. Preserve other worktree changes and coordination mail. No AI Manager, SS Debug hub or generalized test-runner work in this scope.

NOTE
A repository inbox request does not by itself launch a local Codex session.
