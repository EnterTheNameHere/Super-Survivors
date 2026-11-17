# Human appearance and invisibility observations — B42

17 November 2026. SSR-TEST-04 on codex/persistence-b42. **Actual in-game diagnostic
execution NOT RUN at delivery.** This is observation tooling, not a renderer,
player-control or appearance repair. The ordinary-play symptoms are user reports:
skin/hair/probable facial-hair change while clothes/gear seemed to remain theirs,
and an earlier invisibility incident recovered by toggling invisibility off.
Neither observation establishes which script or engine path caused it.

## Use the controls

1. Restart to load the new module. In the ordinary single-player world you want
   to diagnose, enable Options -> Superb Survivors -> Debug Options -> On.
2. When the intended human **looks correct**, open SS Tests... from the world
   context menu, select **Human appearance - capture baseline**, acknowledge and
   Run. The output labels timestamp, fields and unavailable coverage. Baseline
   capture is a user assertion of a good appearance, not pixel validation.
3. Continue ordinary gameplay. When skin/hair/facial hair looks different, select
   **Human appearance - compare changed** and Run with new acknowledgment.
4. When invisible, select **Human appearance - diagnose invisible** instead. Its
   output explicitly prints `CURRENT isInvisible=true/false/UNAVAILABLE` and
   relevant draw/opacity/model state. It never toggles visibility or resets a model.
5. Report which symptom occurred and the capture result. Logs use prefixes
   [SS Tests][human-visual-baseline], [human-visual-changed], [human-visual-invisible].
   Local console.txt/archived DebugLogs contain the per-field data; no pixels are
   recorded. Capture while the symptom is present; no automatic repro is installed.

These three operations observe only and require no disposable-world fixture.
The shared window retains its existing warning/acknowledgment because it also
hosts destructive persistence tests; consent is not bypassed. Native -debug is
NOT required to open/run the human controls, but determines coverage below.
The executor does not draw gameplay RNG or create a persistence boot token for
these vetted read-only definitions. They can observe after an unrelated mutation
test's cleanup failure, without clearing that failure or unlocking further
mutating tests; existing per-run consent and single-active-run rules remain. No actor constructors, native saves/loads,
slot/singleton/appearance/visibility/equipment setters or model resets are called.

**Baseline lasts only for this gameplay session.** Recapture explicitly after a
world reload, game restart, or intentional new character. No reliable public
Lua getter for stable human database identity was verified, so descriptor ID or
a cached filename is not used to join different sessions. World name plus cell
reference prevents mixing worlds in-session; OnGameStart clears only this
module's memory, without automatic capture. A changed local actor is reported
as identity change; its appearance is not compared as the old human's state.
No raw Java references or fingerprints are written to ModData/save files.

AFTER never overwrites the baseline. Last four AFTER scalar snapshots are kept
separately in Lua memory; full individual captures are logged. Clicking capture
baseline again explicitly replaces it and clears that bounded AFTER history.
Comparison timestamps are actual execution time. Shared execution is deferred
to OnTick, so the data may differ from the exact frame of the observed symptom.
Pause/context-menu limitations remain; no automatic polling/frame instrumentation.

## Coverage and getter safety

Installed 42.22.2, revision 3d39148846; projectzomboid.jar SHA256
3c4a7c5f149d784758c6fb5f8fa85f3a21d572e38bc081400e89035f8120d287.
Read-only decompilation/member/bytecode inspection is primary evidence, stored
ignored under .venv/human-visual-native and .venv/human-visual-decompiled.

| Fields | Without native debug | With native debug already enabled |
| --- | --- | --- |
| Human/descriptor/visual presence, descriptor name/ID/sex, local/NPC state | Pure cached getters | Same |
| Human actor/descriptor/visual/model references; singleton and all four slots | Same-session comparisons only | Same; never cross-restart pointer equality |
| Actor and descriptor skin texture index, body-hair index, non-attached hair | Pure direct getters; sentinel -1 remains -1 | Same |
| Hair/beard styles, skin texture name, skin/hair/beard/natural RGBA colors, visual owner | Explicitly UNAVAILABLE | Read raw declared fields, never lazy getters; missing/null distinguished |
| isInvisible, ghost, god/no-clip, sprite invisible, culling, doRender, alpha/target-alpha viewport 0 | Pure getters | Same |
| Existing model/texture-creator presence | Pure field-returning getters | Same plus raw model name, tint, texture name and creator rendered flag when available |
| Animation player / true rendered pixel fingerprint | UNAVAILABLE | Still unavailable; no animation allocation/rebind or pixel fingerprint |
| XP/levels for Axe/Strength/Fitness, HP, needs, position, equipment and inventory | Dynamic context | Same |

The most important limitation: **full hair/style/color capture cannot safely be
provided without native debug through this installed public API.** If those
fields are needed, start with native -debug already enabled and capture a fresh
known-good baseline then. The diagnostic never enables native debug itself.
If the baseline lacked a field, a later newly readable value is not evidence
of a change; recapture only when the correct appearance is visible again.

Exact source checks:

- IsoPlayer.getHumanVisual returns the cast existing baseVisual; SurvivorDesc
  getHumanVisual returns its final visual. Descriptor getID/name/sex getters
  read fields. Descriptor ID is not a verified stable save identity.
- HumanVisual.getSkinTextureIndex, getBodyHairIndex, getNonAttachedHair are
  direct field reads. Installed-JAR tests assert their simple getter bytecode.
- HumanVisual.getSkinColor, getHairColor, getBeardColor, getNaturalHairColor,
  getNaturalBeardColor initialize missing colors. getHairModel may pick a random
  style; getBeardModel may clear female beard or choose a style. getSkinTexture
  may pick/adjust skin index or zombie state. **None is called.**
- HumanVisual.copyFrom calls several of those getters on its source; using a
  copied visual is therefore not a safe observational workaround. HumanVisual
  save involves nested visual serialization, so it is not used as a fingerprint.
- LuaManager.validateReflectionAccess rejects reflection when Core.debug is
  false. getNumClassFields/getClassField/getClassFieldVal read declared fields
  only when already allowed; no attempt to bypass debug restrictions. Java field
  objects are metadata; appearance values are never written. ImmutableColor
  getRed/Green/Blue/AlphaFloat return existing components, formatted as RGBA.
- IsoGameCharacter.getModelInstance returns legsSprite/modelSlot/model when
  present, and getTextureCreator returns its field. Texture.getName is a simple
  field getter. In contrast getAnimationPlayer can allocate/release/rebind an
  AnimationPlayer and notify animation state, so it is deliberately not called.
- IsoObject draw/cull/alpha getters read current state; isSpriteInvisible reads
  the sprite invisible property. IsoPlayer.isGhostMode aliases isInvisible and
  setGhostMode delegates to setInvisible in this build; these are not independent
  evidence. The diagnostic calls neither setter.

Inventory is a sorted, bounded top-level type/count/condition summary (first
64 items, text capped at 2400 characters), not a recursive inventory dump.
Worn types use the same bound, held item type is recorded, empty hands are
known null. XP getters and getPerkLevel are lookups, not XP awards. Dynamic
fields are labeled context, not equality requirements for a healthy character.
Unavailable API, known null and concrete values are different states; two
unavailable values are never printed as an unchanged/matching field.

## Interpret results

Example fragments:

    CHANGED visual.actor.skinTextureIndex: baseline=2; current=5
    CHANGED visibility.isInvisible: baseline=false; current=true
    CHANGED context.xp.Axe: baseline=0; current=25
    UNAVAILABLE visual.actor.hairModel: baseline=UNAVAILABLE (...); current=UNAVAILABLE (...)
    CURRENT isInvisible=true ... no toggle performed

Baseline PASSED means a requested baseline was captured, not that the game
proved the appearance is correct. Comparisons are diagnostic observations:

- Different actor/slots/singleton: INCONCLUSIVE identity change, preserving
  baseline. Verify intentional character/control change before rebaselining.
- Visual data or descriptor/reference changes: report categories, INCONCLUSIVE
  about cause. Haircuts, dyes, aging or normal model cycling can also change data.
- Invisibility/draw/opacity changes: report exact flags; no automatic recovery,
  no conclusion about who changed them or whether a particular mod is responsible.
- Readable fields unchanged but symptom visible: renderer state, unobserved data
  or timing remain possible. Coverage is partial, even with debug; no reliable
  pixel fingerprint. INCONCLUSIVE is appropriate, not evidence the user imagined it.
- Ordinary XP/equipment/inventory/needs/position drift: context, never automatic
  FAILED verdict. The log preserves old/current values for correlation.
- Missing session baseline/wrong world: unavailable selection; capture correctly
  in the intended session first. Getter failure is reported explicitly rather
  than fabricating a default or calling a mutating alternative.

Z'Ware Invincibility: Three Ways Out is known to be in use. Native isGodMod does
not establish that separate mod's protection state. A successful invisibility
off recovery is evidence about recovery only, not the original cause.

## Source-only triage: no appearance fix

Relevant source paths, not established causes:

- SSR native actor creation ordinarily supplies a fresh SurvivorFactory descriptor;
  IsoPlayer construction copies descriptor HumanVisual into its own visual. The
  constructor's copyFrom can initialize its source descriptor. This does not
  demonstrate an accidental human/NPC alias; ownership/reference snapshots may help.
- SuperSurvivorPresetSpawns applies skin/hair/beard styles/colors to its survivor
  target. The existence of those setters is not evidence they received the human.
- SuperSurvivorManager.switchPlayer changes singleton/local slot and NPC control;
  SuperSurvivorsContextMenu.DebugCharacterSwap invokes it through its debug option.
  No evidence the user invoked it. The new controls record rather than change slots.
- IsoPlayer native save temporarily swaps singleton and restores it in finally.
  Prior bounded callback guards do not rule out visual-data/cache effects or
  arbitrary later changes during ordinary gameplay.
- SuperSurvivorRender.updateObserverOpacity writes human alpha/target only when
  standalone NPCs exist and several visibility guards allow it. It does not set
  isInvisible or human skin/hair. Shared viewport/render-cache concerns were
  previously deferred; no renderer or Java modification is made now.
- Existing logs have no before/after human visual fingerprint establishing the
  ordinary-play symptom's cause. Do not attribute it to Test 3, SSR, vanilla or
  another mod solely from this source inventory.

## Validation / sequencing

At delivery: 219 automated tests and 113 Lua syntax checks pass in the working
copy; isolated staged-tree validation is reported separately in delivery mail.
Tests cover getter mutation traps, unavailable vs null, raw debug colors/styles,
normal dynamic drift, invisible flag, visual/reference/actor/slot changes, missing
baseline, another world/new character, bounded history, clearing on new session,
and no gameplay RNG draw from these read-only operations. No native appearance
bug was reproduced, no snapshots taken in-game by Codex, no repair performed.

User eyewitness AI movement after Test 03 restart is now recorded as direct
user evidence; its machine result remains historically INCONCLUSIVE. Test-03 R1
early observer was not started and is deferred, not silently implemented here.
Historical native/persistence evidence and tests are preserved. Actual Test 04
baseline/AFTER behavior is **NOT RUN** until user invokes the controls.


Final delivery checks: isolated export of staged source (excluding unrelated
user changes) passes 219 tests and 113 Lua syntax checks. LuaLS reports 88 legacy
diagnostics in 13 files, none in new test/UI modules. Editor source fingerprint
regenerated from isolated intended source. Documentation links checked; previous
evidence unchanged. Ignored logs: .venv/test04-delivery-suite.txt and
.venv/luals-test04-delivery-result.txt. No native baseline/symptom capture yet.
