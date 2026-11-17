# SSR-COMBAT-03 — Bounded passive native attack handoff trace

Date: 2026-11-17
Status: REQUESTED / NOT ACKNOWLEDGED. No production combat fix authorized.
Canonical B42; implementer exclusive codex/persistence-b42 worktree, verify ownership.

## Evidence
Actual Combat02 B42.22.2 test: Roderick ID9, 33 snapshots over ~278 seconds. 31 Attack-front, 11 native in-range (7 with WaitTicks=0); all33 isAttackStarted=true, isInitiateAttack=false, animation=false, swingState=false, native isWeaponReady=true, AtkTicks=0. Healthy, equipped WoodenMallet, valid living zombie target, AI updates progressing. Logs: docs/evidence/COMBAT_SNAPSHOT_RODERICK_ID9_2026-11-17.log. Inbox summary: ai-workflow/mail/orchestrator/inbox/2026-11-17-combat-02-roderick-runtime-results.md. Current requestCombatAttack would return "busy" if invoked while isAttackStarted true; no actual request return/flag setter seen yet. No hit or animation observed by diagnostic, snapshots not continuous.

## Requested next bounded test
1. Audit installed 42.22.2 actual call/event timing of pressedAttack/CombatManager, NPC AIComponent control variables and postUpdatePlayer, SwipeStatePlayer animation and collision, and SSR request. Cite source; don't assert cause without observed transition.
2. Add opt-in user-triggered "Combat - trace existing survivor" to development-gated SS Tests: explicitly select an existing loaded owned SSR NPC ID>0 with full human/slot/world/identity guards; observe natural behavior over a short, bounded frame/time window; proper cancellation/timeout/world/menu/death/actor-replaced teardown. No automatic startup monitoring, no extra attack invocation or new zombie/actor, no mutation of native attack flags, no visual reset, no local-player slot swap, no direct Hit calls.
3. Record only compact transitions / bounded cadence of native started/initiate/animation/swing/current state and SSR target/current task/native range/WaitTicks/AtkTicks. Cap events and logs, summarize outcomes. If initial flag already true, label preexisting state; do not claim false->true transition or original setter.
4. To capture naturally executed requestCombatAttack entry, return (including rejection reason), pre/post flags, consider minimally scoped tracing wrapper. Call original exactly ONCE with untouched args and returns/exceptions; avoid affecting nonselected NPCs. Verify real Lua dispatch and safe cleanup/restoration. If such interception is not demonstrably safe, omit it, deliver read-only temporal state tracing and explicit blocker; do not install global wrapper speculatively.
5. Observe native OnWeaponSwing/hit events only if actual installed signatures and NPC dispatch are verified, filter owned attacker, no assumed event contract or inference from absence.
6. Preserve all previous UI/tests, Test04 R1 baseline and logs. Automated tests cover no mutation/extra attack, wrong ID, replace/death/world/menu, cancellation, timeout, cap and optional wrapper exact-once/error preservation, no startup action. Lua syntax and native/JAR checks.
7. No production combat AI/loader/registry change, no cleanup of arbitrary actors, no merge. Report source SHA/parent, modified files, actual-vs-not-run validation, user steps and candidate next correction via orchestrator inbox on B42. If impossible safely, report blocker rather than force implementation.
