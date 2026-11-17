FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-17
STATUS: NATIVE TRACE VERIFIED / ACTUAL NATURAL REQUEST REJECTION IDENTIFIED
SUBJECT:5 native traces:98 logged returns ALL false,busy; original flag preexisting

User says tried tracing. Current console has5 complete bounded traces:
ID9(Roderick per prior user association),ID1,ID5,ID5,ID5. Runtime source
codex/persistence-b42 a5b166d45e83a7450acc31b135f31cba937332a2, prior metadata
a33cde7. Evidence/docs commit6a51060e0c8f451c70fef2927e8bdcf7b642d0a8 (also
synchronizes new canonical Inventory01 coordination; inventory not executed).
Exclusive existing checkout; no new runtime/production code edits, no Java/flags/
slot/Hit/reset/forced attack. User source/settings/common save edits preserved.

PRESERVED docs/evidence/COMBAT_TRACE_2026-11-17.log, all400trace lines + source
consoleSHA256. Summary docs/COMBAT_HANDOFF_TRACE_B42.md and LOCAL_HANDOFF.md.

Trace ID/frame spans/entry count/complete return count:
9,3122-3433,15/15busy
1,7318-7678,17/16busy
5,13621-13851,22/21busy
5,14848-15091,24/23busy
5,16105-16351,24/23busy
102 request entries,98 COMPLETE observed returns, every return false,"busy".
Four return records censored because logger hit cap mid-call; not evidence of
unreturned/hung/error calls. All5 exactly80lines, terminate log cap, summary
ownedWrapperRestored=true. Durations about1.6-2.7seconds (cap before10s is expected).
Zero swingEvents/hitPointEvents/sampledFalseToTrue. No actual errors/exception/
stack/observer failure from first trace through inspected EOF. Ordinary text
"traceback includes observer frame" is not an error and was excluded from search.
Native trace/interception/cap/reported restoration verified; logs don't identify
Information vs SS Tests launch path, no assertion both native UI layouts tested.
Native error/teardown variants not exercised here, remain automated-only evidence.

RODERICK ID9:
ALL15 natural request entries in native range with Attack task/cooldown0. Actual
returns allfalse,busy, native attackStarted true/initiate false/no animation/swing.
Initial marker PREEXISTING true. No first setter orfalse->true event captured.
ID5 natural entries likewise in native range. ID1 native range false despite
task's close-distance fallback, additional range caveat independent of busy.

CONCLUSION ADVANCE:
Actual stage(d) NATURAL REQUEST REJECTION now observed, no longer just source
conditional. NPCs select Attack and INVOKE requestCombatAttack. Current busy guard
returns before native CombatManager.pressedAttack in these completed calls; native
isAttackStarted=true is sufficient to block it (AtkTicks0). This is not simply
perception/no weapon/no decision. Source AI-control-postUpdate handoff remains a
mechanism candidate for how initial state becomes stale; cause/first setter/reset
chronology not proven because alreadytrue at every start. Normal collision gate
is later and not reached through these rejected requests; no hit/animation success.
No fix or extra diagnostic was implemented while checking logs.

NEXT:
Review actual rejection evidence. Repeating alreadybusy traces is unnecessary to
establish gate. First natural request/handoff or separately reviewed adapter/
correction investigation should address origin; no speculative flag reset/direct
Hit/local slot swap. Native code modifications remain excluded. Inventory01 inbox
arrived on B42 while runtime check; preserved/read but NOT ACKNOWLEDGED/STARTED
as part of this bounded user log check. Separate startup/priority instruction next.
Test04 R1 restart proof pending; Test03 early observer deferred. No automatic merge.
No tests rerun for immutable logs/docs-only evidence change; prior267/116 source
validation remains separate from actual native observations.
