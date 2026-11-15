# Super Survivors Reloaded — AI Workflow

This directory is a repository-based coordination system between the user, a ChatGPT orchestrator, and a local Codex implementer. Inspired by Tertalis' workflow, but entirely independent.

**Start with `ai-workflow/index.md`.** Coordination lives on branch `B42`.

## Roles
- **User:** sets design direction, authorizes work and performs actual in-game checks.
- **Orchestrator:** records design decisions, sends bounded assignments, reviews implementation, returns questions/corrections and maintains this thread's handoff.
- **Implementer (local Codex):** reads assignments and inbox, claims exclusive source branch/worktree, inspects installed PZ B42 source and APIs, implements, tests, reports commits and limitations.

Sessions share repository files, **not live context**. Publishing inbox mail does not launch Codex and is not evidence a session is running.

## Where things live
- `index.md`: routing and current assigned work.
- `coordination-protocol.md`: participation, source ownership, barriers and reporting rules.
- `state.md`: current evidence-backed status, not history or a presence indicator.
- `handoff/orchestrator-thread.md`: context needed to resume coordination in a new chat.
- `assignments/`: concrete, bounded implementation specifications.
- `mail/implementer/inbox/`: outstanding requests for Codex.
- `mail/orchestrator/inbox/`: answers, questions and deliveries to orchestrator.
- `mail/<recipient>/archive/`: handled messages; Git retains history.

## Message cycle
1. User and orchestrator agree on scope.
2. Orchestrator publishes assignment + addressed implementer-inbox message, marks REQUESTED (not running).
3. Local Codex is explicitly started by user, reads startup documents, confirms branch ownership, acknowledges request in orchestrator inbox, then implements.
4. Codex commits on declared branch, executes available checks and writes a completion report and current status. Real PZ engine tests must be distinguished from mocks.
5. Orchestrator inspects report and exact code/ref, either requests corrections or accepts after appropriate evidence, including user-led in-game validation.
6. Both roles update durable current state and handoff. Process next task only when assigned.

The correspondence works through GitHub commits on `B42`, or through agreed dedicated coordination ref, not automatic push notifications. Each role must check its inbox on resumption and at meaningful barriers.

## Example filenames
- `mail/implementer/inbox/2026-11-15-persist-01.md` — real assignment notification.
- `mail/orchestrator/inbox/YYYY-MM-DD-persist-01-ack.md` — expected Codex acknowledgment (NOT yet created).
- `mail/orchestrator/inbox/YYYY-MM-DD-persist-01-delivery.md` — expected Codex results (NOT yet created).

Do not claim Codex is running, an assignment is delivered to a live session, or engine validation passed merely because coordination files exist.
