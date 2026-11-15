# SSR Coordination Protocol

Inspired by the Tertalis coordination workflow; operational notes, not gameplay design.

## Branches and ownership
- `B42` is canonical for coordination messages and status. Reads/writes must name the ref explicitly.
- Implementation may occur on a dedicated branch from B42. Report exact branch/base/commit; do not change `master` or merge silently.
- One active implementer per implementation branch/worktree; one coordinator for overlapping repository work. Check for conflict before claiming ownership. If another implementer is active on the same branch, STOP and request direction.
- Publishing a request doesn't execute it. Acknowledgment is required before claiming implementation is in progress.

## Messaging
- Address each message to its recipient: `mail/implementer/inbox/` or `mail/orchestrator/inbox/`.
- Include FROM, TO, SUBJECT, STATUS, CONTEXT, REQUEST, RELEVANT REFS, REPORT BACK, BLOCKERS when appropriate.
- Prefer immutable published mail. Replies and corrections are NEW files. Move handled mail into recipient archive only after its content is processed, with traceable Git history.
- Promote durable decisions and findings from mail into `state.md`, handoff or design documents.

## Lifecycle
Requested → acknowledged / ownership registered → implementing → committed → tested (to stated extent) → reviewed → accepted. None are automatic transitions. Implementer completion is not orchestrator acceptance.

## Start barrier
1. Read index, README, protocol, state and handoff from canonical B42.
2. Inspect addressed inbox and assignment.
3. Verify repository head, branch/worktree status, current owner and source reality.
4. Declare and report exclusive implementation branch/worktree; acknowledge request in orchestrator inbox before modifying production code.
5. Check installed B42 Lua and Java source for APIs; earlier B40/B41 code is not authoritative.

## Finish/pause barrier
1. Commit intended code to declared branch and report exact SHA, parent and modified paths.
2. Report test commands, results, limitations and separate actual in-game evidence from unit/mocked tests.
3. Update state to material reality and keep thread handoff current where appropriate.
4. Send report/blocker to orchestrator inbox. Archive only processed messages.
5. Orchestrator reviews exact evidence before acceptance and coordinates user in-game verification.

## Scope policy
An assignment is not permission for unrelated rewrites. Design disagreements or unsupported engine assumptions go back to orchestrator/user with concrete evidence. No Java-side game-engine modifications. Initial runtime target single-player B42. No B40/B41 or experimental B42 save migration required. Do not assume unread inbox is automatically consumed.

## Scenario warning (future UI)
> **Warning — World Modifications**  
> Tests will **irreversibly alter the game world**. Running tests may spawn, modify, or delete characters, objects, items, and zombies.  
> This feature is intended for testing mod behavior in a temporary world that you don't mind deleting.

Future test scenario functionality is not part of SSR-PERSIST-01.
