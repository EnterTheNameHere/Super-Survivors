FROM: Local Codex implementer
TO: SSR Orchestrator
DATE: 2026-11-18
STATUS: STAGE A DELIVERED / BLOCKED FOR FULL NATIVE COMBAT / STAGE B NOT ENTERED
SUBJECT: Neither ordinary NPC control nor nonlocal native collision gate passes

Exclusive existing codex/persistence-b42 checkout. Report/evidence commit
349a180019a6125578599c179f41ef0c95a69c72; parent
4c554a04da65015f92eb238a6baaa68c58772c96. ACK canonical publication
e50dea563bc289bda68f4d94fbaeb6b08f2f6a76.
Changed docs/COMBAT_NATIVE_INTEGRATION_PROTOTYPE_06.md, docs/LOCAL_HANDOFF.md,
docs/evidence/COMBAT_NATIVE_API_06.txt only. No runtime/prototype code.

FEASIBILITY RESULT:
No verified ordinary Lua route meets BOTH attack lifecycle and nonlocal native
melee collision/damage. Gate requires stop; no cosmetic/flag/animated prototype.
Installed JAR SHA256 recomputed same3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287,
B42.22.2rev3d39148846. Prior key extraction bytes checked equal current JAR;
extra input/state/IsoSurvivor/config/ballistics classes freshly inspected.

POSITIVE/NATIVE EVIDENCE:
pressedAttack public/exposed and actual Combat05 accepted ID3 request proved
immediate flags. Ordinary public AttemptAttack/DoAttack overloads follow same
player path; no method-name correction. Actor's entire superclass/interface
public combat-related surface enumerated, inherited defaults included.
AIComponent owns controls and writes before animation. No direct control-class
PUTFIELD producer located by whole-JAR candidate scan; matched source consumers
read controls. Public Java APIs exist but AIComponent/control/ECSComponent/manager
not registered. Exposer recursive whitelist + public/static field handling
doesn't expose arbitrary control instance fields. Component map isn't a bridge.

ADDITIONAL ROUTES CHECKED:
Human force-aim/input defaults act on CharacterInputComponent; NPC input update
uses AIComponent instead. Native state broadcaster forwards into SAME local-only
listener; fake Lua HitPoint skips native collision but triggers vanilla reload/
chamber bookkeeping. CombatManager collision public Java but no normal Lua getter/
registration found; whole-JAR caller scan finds ordinary gated Swipe listener.
IsoSurvivor exposed but no overriding attack; old inherited DoAttack changes to
Swipe, enter unconditionally casts owner to IsoPlayer. Actor replacement is not
compatible minimal lifecycle/damage solution. CombatConfig config only; ballistics
is not ordinary NPC melee API. No reflection/token/exposer bypass attempted.

SSR CALLERS/INVARIANTS:
Attack/NPC_Attack/requestCombatAttack + task/PlayerUpdate path preserved. Building
entry also has AttemptAttack call (not universal wrapper interception). StopWalk
and native lifecycle separate. Existing WeaponReady/ReadyGun repair/unjam/ammo/
reload policies are mutating, not proof native resource invariants; inspected,
not invoked or rewritten. Native condition/stamina/ammo/miss/hit ownership must
be independently preserved by any future backend.

ALTERNATIVE DESIGN, NOT IMPLEMENTED:
Separate intent from an actor/world-owned combat backend with distinct lifecycle
and native-damage capabilities, single request lifetime/interruption authority.
No dummy/no-op adapter installed. Under current constraints, native backend must
wait for verified ordinary engine Lua NPC control+nonlocal collision support.
If user wants functionality without that, a separate custom Lua combat backend
design would require explicit scope approval relaxing native-damage-only; no
direct Hit loop/formula/code proposed as this fix. Java remains excluded.
Report includes re-opening criteria, disposable-save opt-in/rollback contract,
hit-vs-miss/resource/second-attack/interruption/other-mod acceptance checklist.

VALIDATION/LIMITS:
Source/provenance/member/exposure/caller/installed-Lua/SSR audit + diff --check.
No new runtime experiment/test suite/syntax run for docs-only gate; no mock claim
of native success. Prior291tests/117syntax belong Combat05. Actual accepted
ID3 first-observed flag-loss evidence preserved; exact setter remains unobserved,
short interval not permanent-animation proof, no native damage proof. No repeated
already-busy diagnostics. Negative finding scoped to audited installed ordinary
APIs, not a universal claim against any future engine/mod mechanism.

No prototype/option/production AI/Combat05 observer/persistence/UI/inventory/
settings/save/flags/state/slot/damage/Java/global-context changes. User source and
common saves preserved. No restart/user test needed for this report. Source push
and ai-workflow-only canonical publication; no protected-source merge. Assignment
delivered BLOCKED as its gate requires. Next orchestrator/user scope decision or
future supported native API; other porting tasks require separate ordering.
