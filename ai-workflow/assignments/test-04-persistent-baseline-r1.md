# SSR-TEST-04 R1 — Persist human appearance baseline in world save

Date: 2026-11-17
Status: REQUESTED / NOT ACKNOWLEDGED
Coordinator: ChatGPT SSR orchestrator
Implementer: existing exclusive Codex checkout codex/persistence-b42; verify current worktree/ownership
Canonical coordination: B42

## User request and reported testing
User requests that a user-captured known-good human appearance baseline survive a normal game save/restart, avoiding capture on every game start. User explicitly reports having run **all three Test 04 controls** (capture baseline, compare changed, diagnose invisible). This is user-reported execution, NOT automatically confirmation that either bug occurred during the test or that comparisons were correct; no Test 04 actual runtime results have yet been delivered to orchestrator inbox. Check actual local console/log as available and report findings separately, do not infer pass or symptom from execution alone.

## Existing implementation
SSRHumanVisualTest.lua stores baseline and four AFTER records only in Lua session, clearing on OnGameStart. Baseline includes raw actor/descriptor/visual/model references as well as scalar values. Some B42 HumanVisual getters are mutating/lazy: do not use them for observation. Native -debug controls whether raw hair/skin colors/styles are accessible. Historical diagnostics and safety guardrails must remain.

## Required bounded change
1. Inspect installed B42.22.2 native API and actual GlobalModData save/read lifecycle. Store a **separate, versioned, world-scoped test diagnostic record**, with only safely serializable scalar/plain-Lua-table baseline fields (including explicit UNAVAILABLE vs known null), capture time, save-world context and available stable human identity hints. **Never** persist Java actor/visual/descriptor/model refs, userdata, closures, arbitrary inventory objects or other nonserializable data. Do not use SSR production survivor registry or human native character save for this.
2. The baseline must be explicitly captured while the player looks correct through the existing UI. Store it for the *next normal world save*, without forcing a save or claiming a disk write already completed. On subsequent game restart load it and make it available to user-invoked appearance/invisibility comparison without recapturing. Current session-only baselines cannot be retroactively restored: user may need to capture once after implementing R1 and save normally.
3. Conservative identity handling: isolate worlds/saves. If installed engine lacks a robust cross-restart human character identifier, do NOT silently claim same actor across sessions. Show a meaningful warning or require explicit identity reconfirmation before comparison; do not use changing hairstyle/appearance as identity criterion. Within one session continue strong reference/slot checks. Cross-session raw pointer/reference equality is meaningless and must not be compared. Report which checks are verified versus not.
4. Preserve readonly AFTER captures. No automatic test execution on startup, no visual/invisible toggle, model reset, renderer changes, survivor creation or production persistence modifications. A user-initiated baseline capture intentionally updates diagnostic ModData; ensure UI semantics/doc are accurate. AFTER comparison never mutates game state or persistence. Optional last-four AFTER history may remain session-only; original baseline must persist.
5. Preserve existing safe/non-mutating inspection of HumanVisual fields; if preexisting baseline had unavailable hair/skin fields without -debug, they remain unavailable after reload and are NOT false-equal. If debug coverage later changes, label asymmetry. Dynamic skills/XP, gear and inventory are informative context, not invariant assertions.
6. Add tests for save/reload roundtrip with normal OnSave ordering; no-save/no-data; wrong world/new human; session vs cross-session identity labeling; missing native-debug fields; stale schema, corruption/invalid record, repeated comparisons not overwriting baseline; restart without completed normal save; and safety of readOnly operations. Prefer narrow additions to existing Testing module and UI.
7. Preserve previous actual logs and docs. No automatic branch merge or acceptance; no production loader, NPC rendering, gameplay or actor mutation fixes.

## Evidence and delivery
Update docs/HUMAN_VISUAL_DIAGNOSTICS_B42.md and docs/TESTS_UI.md, include user steps and durability caveats. Commit source only on existing implementation branch; report SHA, parent, changes, unit/mock and Lua syntax checks, inspected native API facts and unverified engine steps. Deliver to ai-workflow/mail/orchestrator/inbox on B42. A proper real-game confirmation needs user to capture baseline, normal save/exit/restart, run an explicit AFTER and check which baseline was loaded.
