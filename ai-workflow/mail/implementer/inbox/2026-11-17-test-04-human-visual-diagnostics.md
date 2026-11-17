FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-TEST-04 — player baseline + later appearance/invisibility diagnostic
STATUS: REQUESTED / NOT ACKNOWLEDGED
ASSIGNMENT: ai-workflow/assignments/human-visual-baseline-diagnostics.md
BRANCH: codex/persistence-b42

User clarifies: during ordinary gameplay the human's SKIN, HAIR and likely FACIAL HAIR changed; clothes/gear seemed their own. Separately user has experienced HUMAN INVISIBILITY; an earlier local Codex experiment toggled invisibility off and their visible model reappeared. They propose diagnostic tests: capture correct baseline whenever they choose; later compare after appearance change; separate compare when invisible. Skills/XP can evolve, equipment/inventory are dynamic; record them without marking drift as defect.

Please build narrowly on gated SS Tests UI, no automatic execution or repair, and inspect installed B42.22.2 getters first. Stable appearance fields, actual human identity/slots/singleton and relevant visibility flags are primary; XP, equipment and inventory are context. Separate later snapshots from the original baseline; no mutation or speculative renderer fix. Inspect distinction between visual-state changes and unchanged visual data with changed appearance; do not assume a cause from the invisibility toggle. Preserve prior test findings. Ack ownership and source branch; deliver evidence and precise UI steps through orchestrator inbox, no automatic merge. Outstanding SSR-TEST-03 early reconstruction observer is deprioritized; avoid conflicting implementation tasks.
