# SSR-ANALYSIS-01 delivered; IsoSurvivor migration rejected

FROM: Local Codex
TO: SSR orchestrator
STATUS: ANALYSIS COMPLETE / PROPOSED MIGRATION REJECTED BY USER
DATE: 2026-11-15

User limited this turn to analysis and subsequently said to finish it as rejected.
Disposition: reject switching SSR to IsoSurvivor; keep current IsoPlayer actors.
No runtime source edits, new tests, Tests UI changes, game experiment, actor
migration or Java modification. No source merge or persistence acceptance.
SSR-TEST-02 and factory supplement remain unexecuted/pending separately.

Documentation source: codex/persistence-b42,
a4c523b35cc5e1cfac5958a75d41bd0548c3802a, parent
6234ff63df16dcd67dbed56f7836aad4ab254420 (analysis ACK).
Starting source head 090f424fe7fce1e2230f968eb7eeda452c51a3b6.
Changed report paths: docs/ISOSURVIVOR_VS_ISOPLAYER_B42.md and docs/LOCAL_HANDOFF.md.
Source acknowledgments/reports/status separately update ai-workflow only.
Exclusive existing W:/Projects/Super-Survivors checkout preserved, including
unrelated uncommitted source/settings/save edits.

Installed engine 42.22.2 revision 3d39148846; projectzomboid.jar SHA256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only native classes and vanilla Lua are primary evidence. 23,692 JAR class
entries scanned for constructor/factory call-site candidates, zero parse failures,
23 candidate caller methods; important bodies examined via CFR. This is not a
universal dynamic reachability proof. Declared/inherited API names and conservative
SSR actor-receiver sites compared; no whole-program Lua dataflow claim.

Verified decisive blockers:
- Both extend IsoLivingCharacter, but IsoSurvivor is final and lacks Player's
  modern visual interfaces/overrides. Inherited getVisual throws; inherited
  character save/load directly calls it.
- Common constructor gives Survivor null primary BodyDamage, Moodles, XP and
  sound emitter. bodyDamage/moodles are final native fields; shared API names
  do not provide initialized player-equivalent systems.
- Shared attack code enters SwipeStatePlayer; enter casts owner to IsoPlayer.
- Player filename snapshots, nutrition/fitness, NPC control methods and update
  events are not interchangeable with Survivor. SSR depends on these contracts.
- SurvivorFactory.CreateSurvivor returns descriptor; InstansiateInCell returns
  IsoSurvivor. Generic object factories are not fully usable NPC factories.
- Lua preview text hits include two commented-out ISCharacterScreen blocks;
  surviving helper definitions/event/list/corpse branches do not demonstrate a
  functioning world NPC. No unsupported claim that IsoSurvivor is universally
  unused or has an autonomous AI is made.

Report includes full comparison matrix, exact class/method references, constructor
and factory effects, serialization layers, square/list/removal/death differences,
SSR migration surface, options/costs and remaining uncertainties. No further
experiment needed to reject a direct class swap. Future runtime proposals are
conditional only, not implemented or requested of user.

Validation: documentation links, decisive source references and staged whitespace
checked; git diff confirms no committed 42/ changes relative to starting source.
No automated tests rerun for this documentation-only task, no new runtime evidence.
Prior scoped IsoPlayer probe remains accepted for its narrow purpose; full SSR
persistence lifecycle remains under review. No active implementation continues.
