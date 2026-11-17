FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: SSR-INVENTORY-01 — audit actual B42 inventory UI and SSR reuse possibilities
STATUS: REQUESTED / NOT ACKNOWLEDGED
ASSIGNMENT: ai-workflow/assignments/inventory-b42-investigation-01.md

User agrees to INVESTIGATE FIRST rather than replace anything. Separate survivor-owned native-style inventory UI (icons, worn/held, bags, wear/unequip/drop/right click), while leaving human inventory UI alone; later additive human right-click Give To -> Survivor Name. Trace installed B42.22.2 native Lua/Java APIs, legacy/obsolete behavior, implicit local-player assumptions, and current SSR inventory/loadout/transfer/clothing utilities. Produce compatibility matrix and safe phased implementation proposal. No UI source edits, transfer behavior changes, menu hook, or merge. One exclusive implementer; coordinate with current Combat03 work and report ordering.
