# SSR-COMBAT-05 — Observe first natural attack of a fresh nonlocal survivor
Date: 2026-11-17
Status: DELIVERED FOR REVIEW / AUTOMATED CHECKS PASS / NATIVE EXECUTION PENDING
Priority: Combat; inventory implementation remains deferred
Branch: exclusive codex/persistence-b42, one owner; review existing local/user edits first.

## Evidence and purpose
Combat03 observed 98 completed natural requests all false,busy in five traces, each starting with attackStarted already true. Combat04 source report docs/COMBAT_B42_CORRECTION_OPTIONS_04.md shows AIComponent.postUpdatePlayer may overwrite initiateAttack before animator consumes it, leaving attackStarted latched, but this is not yet a runtime observed first transition. Independently ordinary SwipeStatePlayer melee collision listener requires actual local player, which SSR NPC lacks. Identify early natural handoff before any correction. DO NOT claim this single diagnostic solves damage.

## Implement **observation-only**, scoped to an existing SSR survivor explicitly selected from its Information -> Diagnostics UI. No NPC/zombie creation, teleport, new attack, damage, flag reset, AI input, animation update, local slot change, or user-save mutation.
- Reject already attackStarted=true selection. Initial false must be labeled earliest OBSERVED only unless fresh/never-attacked provenance is backed by actual registry metadata. Do not infer history from current false alone.
- Freeze and revalidate ID, wrapper, actor, world, player slots; debug-only, live/nonlocal, guarded ownership. Explicit user Start/Stop, maintain no SS Tests destructive-consent requirement for pure observation. Keep existing snapshot/trace available.
- Reuse Combat03 exact-once, non-pcall original invocation interception for instance-local requestCombatAttack; additionally observe naturally executed instance-local StopWalk, preserve exact call/args/returns/error/other-receiver behavior. Include reason and native pre/post flags. Do not wrap native Java methods or global classes.
- Record bounded identity-filtered early OnPlayerUpdate and OnTick flags, task/target, native range/readiness if proven pure getters, native state/animation data and OnWeaponSwing / OnWeaponSwingHitPoint. Distinguish sampled transitions from exact setter observation, never read mutating lazy getters.
- Hard cap 10s / 600ticks / 120 lines / 8 natural request entries, first wins; stop after first accepted request plus 3 ticks (and enough state/event capture) or swing/hitpoint plus short follow-up. Avoid heartbeat filling log before first event. No eligible natural request => INCONCLUSIVE, not a fail.
- Teardown on Stop/window close or hide, actor death/replacement/unload, debug-off, menu/world change, reload, cap/error. Restore only owned raw method slots; if external mod replaces one, don't overwrite it. No background capture.
- Instrumented observation cannot alter human UI/window/slot state or NPC action queue.
- Add mock/unit regressions including original return/error exactness, no passive trace without click, preexisting stuck rejected, first transition labels, no duplicates, caps, cancelled/stale actor, restored hooks, simultaneous info windows, nonlocal only, user UI callbacks and reload. Native rendering/test must remain PENDING until user runs it.

## Delivery
Source changes only for new diagnostic, not production combat; docs/COMBAT_FIRST_NATURAL_ATTACK_B42.md with exact use steps, sample limitations; report source commit, tests, deliver to B42 orchestrator inbox; no merge.
If safe observer cannot be implemented (Kahlua/native event limitations), report blocker instead of a broader patch.
After native trace, independently assess native damage path. No Java patch, PZNS B41 helpers or direct Hit under this assignment.
