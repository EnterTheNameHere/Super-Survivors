# SSR-TEST-02 — B42 cell-only IsoPlayer construction and native load

Date: 2026-11-15
Status: requested, pending local Codex acknowledgement
Coordinator: SSR ChatGPT orchestrator
User: design authority and in-game runtime tester
Implementation: existing exclusive codex/persistence-b42 worktree; current observed source head 090f424fe7fce1e2230f968eb7eeda452c51a3b6. Verify branch/worktree and mail before starting.

## Question to answer, not assumption to implement
Does installed PZ B42.22.2 support IsoPlayer.new(cell) for constructing an initially unplaced NPC that can be populated using :load(filename), and, if so, what explicit operations are needed to establish a correct currentSquare, moving-square membership and cell/world registration AFTER loading?

Our earlier test established native load restores independently differing X/Y but leaves the constructor square association unchanged. It used the 5-argument (cell, descriptor, x, y, z) constructor; it did NOT test cell-only construction. We must verify the exact existence/visibility/behavior of cell-only constructor against installed Java bytecode/decompiled source BEFORE exposing an unsafe runtime test. The prior conversational list of three overloads was a hypothesis, not independent engine verification.

## Codex work
1. Inspect installed 42.22.2 IsoPlayer constructors, invocation availability from Lua, superclass initialization, lifecycle registration, save/load behavior, nil/no-position state and any NPC flag requirements. Report evidence and potential failure modes. In particular distinguish an object existing in memory from an actor actually belonging to the world.
2. If and only if the engine inspection supports a safe experimental route, add an opt-in **cell-only construction + native load** entry to the existing SSRTests registry and Tests context-menu UI. Reuse existing warning, consent and single-active-test guarantees. No new UI framework.
3. Use a uniquely named test snapshot from an isolated test actor, never the human or SSR's actual registry. Construct a separate cell-only actor, capture pre-load XYZ/currentSquare/list memberships, invoke raw native load(filename) without manually setting position, capture immediate post-load XYZ/currentSquare/memberships, then try only those engine-documented explicit registration/placement steps that can be safely performed and reversed. Capture post-registration invariants (position vs square, square contains actor, cell object/add/remove membership, NPC identity/marker). Differentiate constructor side-effects from load side-effects and from explicit registration steps; do not allow an invalid actor to tick through normal AI updates accidentally.
4. Detect whether a created but unplaced actor becomes registered implicitly; do not assume it remains unregistered. Guard against constructor failures that may register an actor before Lua receives a handle. If safe construction/cleanup cannot be established, **do not run the risky branch**; report INCONCLUSIVE/SETUP ERROR and give engine-backed evidence instead. No blind cleanup of unfamiliar actors.
5. Prefer a direct comparison table in the log: conventional constructor (already measured), cell-only before load, cell-only after load, and after explicit registration (if possible). Include exact detected game build, errors, coordinate changes, currentSquare reference and world membership. Do not conflate method returning with successful load.
6. Preserve minimal single-player development gate; ensure human player singleton, position, saveFileName and local-player slots remain unchanged. Test in fresh disposable world only. Native snapshot residue is acceptable if documented.
7. Add focused unit/static regression checks and update docs/TESTS_UI.md and docs/NATIVE_POSITION_R1.md with engine findings, user steps and limits. Do not claim real runtime verification until user executes.

## Scope boundaries
- No SSR production loader, per-tick scan, unload policy, group registry, or persistence rewrite. This is a measurement before a design decision.
- No full debug hub, unrelated startup fixes, AI or generalized test infrastructure.
- Don't automatically test a full save/restart cycle unless the cell-only in-session experiment demonstrates a reason and safe process for doing so; propose next phase first.
- No merge into canonical B42 without orchestrator review; no force push. Keep user changes intact.

## Delivery
After read/acknowledgement, report exact parent/commit, installed-source findings and constructor signatures, tested execution path and safety constraints, automated results, and exact user-run steps for the Tests UI. Send addressed response to ai-workflow/mail/orchestrator/inbox and update state. Test status must say USER IN-GAME NOT RUN until logs arrive. Any blocker should be reported, not circumvented.
