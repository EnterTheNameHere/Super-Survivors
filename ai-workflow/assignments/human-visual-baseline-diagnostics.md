# SSR-TEST-04 — Human visual baseline and symptom-driven diagnostics

Date: 2026-11-17
Status: REQUESTED / NOT ACKNOWLEDGED
Coordinator: SSR Orchestrator (ChatGPT)
Source checkout: existing exclusive local Codex worktree on codex/persistence-b42; confirm ownership before implementing
Canonical coordination branch: B42

## User-observed symptoms
During ordinary gameplay, not while a test was running, the human player's visible **skin, hair, and probably facial hair changed**, while clothing/equipment and other apparent identity remained their own. A separate earlier problem is that the human sometimes becomes invisible; in a previous local investigation, toggling the character's invisibility setting OFF made the model appear again. This is a recovery observation, NOT proof of what set the flag or root cause.

User proposes an explicit baseline when human appears correct, then a user-invoked AFTER comparison when appearance changes, plus a separate AFTER invisibility diagnostic. User explicitly recognizes skills/XP may change naturally, equipment may change, inventory even more so. No current need for automatic repro or automatic repair.

## Required narrow task
1. Inspect installed PZ B42.22.2 actual exposed APIs, human IsoPlayer, HumanVisual, SurvivorDesc, hair/beard/skin data and available model/texture/visibility flags. Verify getter semantics, nullability and whether any getter mutates/initializes data. Investigate earlier invisibility toggle path if source/evidence allows. Don't assume appearance getters equal rendered pixels; note lack of reliable render fingerprint if applicable.
2. Reuse existing gated SS Tests UI and registry (Debug Options on, SP one human), adding **three individually selectable read-only controls**:
   - `Human appearance — capture baseline`: store a clearly labeled timestamped fingerprint of correct human player's stable appearance, actor identity, descriptor, visual fields, relevant rendering/invisibility flags, slots/singleton, and supporting skill/XP/equipment/inventory observations.
   - `Human appearance — compare changed`: capture current fingerprint and report per-field baseline/current/diff, without treating changes in XP, skills, equipment, inventory or ordinary needs/position as automatic failures; emphasize stable visual fields and identity.
   - `Human appearance — diagnose invisible`: capture fingerprint and visibility/model/render state and compare to baseline as above; explicitly report whether isInvisible or equivalent previously toggled flag is true or false when readable, plus any relevant other flags. NO toggling the value, reconstructing actor, refreshing model, inventory/equipment changes, or reset.
3. Keep the baseline across subsequent same-world comparisons, ideally persist modest serializable scalar-only data in a unique test ModData key when safe; ensure isolation by world and exact human identity. Before baseline capture after a known-good appearance, clearly instruct user to make sure appearance is correct. Never overwrite the baseline on AFTER. Archive multiple AFTER captures with bounded history (or at least separately record comparisons to test log) rather than silently replacing baseline. If session/restart semantics cannot be safely verified, keep session-scoped instead and explain.
4. Avoid saving raw Java references in ModData; avoid full recursive inventory detail or invasive enumeration if costly. Use deterministic bounded summaries for equipment/inventory and numeric XP values with explicit classification as observational/dynamic. For hair/skin/facial hair include style, colors, tint/skin tone or comparable documented exact fields; treat missing values explicitly as unavailable, not as equality.
5. Read-only nature means **no world-modification warning is necessary for these three operations** if the executor supports genuinely read-only definitions with appropriate explicit intent; if changing consent semantics would risk regressions, retain existing per-run consent UX and document that these are observation-only. No automatic capture/check on gameplay ticks, no auto-run during normal gameplay or startup, no polling/instrumentation until separately justified.
6. Compare the human actor reference at capture vs AFTER only while same Lua session; after restart use stable human identity evidence if available and label pointer comparison not meaningful. Compare singleton and all four local player slots at the same moment. Prevent mixing different worlds or intentional new human character when baseline is outdated. Don't assume changed descriptor/visual is automatically SSR-caused.
7. Prefer test/source-only modifications; **no production renderer, NPC constructor, persistence, human control or appearance fix**. If getters absent/unreliable report limits clearly. Reproduce neither bug by force. Preserve all previous Test 1/2/3 results/docs and concurrent work.
8. Include documentation of exact UI procedure, example output, and how to send logs when bug appears; capture a baseline first BEFORE behavior changes. Distinguish visual-data-change, identity-change, flag-change, and all-unchanged possibilities, and don't claim root cause based only on one comparison. Tests must operate on live human only, not SSR NPC fixture.

## Validation and handoff
- Source branch code commit, exact parent, changed paths, staged-tree test/syntax checks, no user code overwritten.
- Verify installed B42.22.2 APIs, unit/mock tests including normal dynamic inventory/XP drift, unchanged visuals despite visible symptom, changed visual fields, invisible flag changed, missing baseline, human identity mismatch, other world/new character, null API.
- Deliver via ai-workflow/mail/orchestrator/inbox on B42 with exact selection names, observed field definitions, safety limits and whether actual in-game run has occurred (default NOT RUN).
- Do not merge source branch, perform runtime appearance fixes, or claim the bug reproduced.
- Coordinate against outstanding SSR-TEST-03 R1 request; user eyewitness AI movement makes that request lower priority. Do not run two concurrent implementers on the same branch.
