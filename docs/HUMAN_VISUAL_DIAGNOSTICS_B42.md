# Human appearance and invisibility observations — B42

17 November 2026. SSR-TEST-04 R1 on codex/persistence-b42. Original three
controls exercised in-game; R1 persistent save/restart roundtrip **NOT RUN**. This is observation tooling, not a renderer,
player-control or appearance repair. The ordinary-play symptoms are user reports:
skin/hair/probable facial-hair change while clothes/gear seemed to remain theirs,
and an earlier invisibility incident recovered by toggling invisibility off.
Neither observation establishes which script or engine path caused it.

## Use the controls

1. Restart to load the new module. In the ordinary single-player world you want
   to diagnose, enable Options -> Superb Survivors -> Debug Options -> On.
2. After installing R1, capture once again: the earlier memory-only baseline
   cannot be recovered after restart. When the intended human **looks correct**, open SS Tests... from the world
   context menu, select **Human appearance - capture baseline**, acknowledge and
   Run. The output labels timestamp, fields and unavailable coverage. Baseline
   capture is a user assertion of a good appearance, not pixel validation.
   This updates diagnostic GlobalModData in memory for the **next normal world
   save**. Save/exit normally and restart. No forced save or confirmed disk write
   is claimed by the capture result. A crash/no completed save loses the capture
   or leaves the previously saved baseline. Saving-disabled mode blocks capture.
3. After reload, select an AFTER directly, **without capturing again**. It reads
   the saved baseline and prints its original capture timestamp. Cross-session
   human identity is UNVERIFIED; verify this is the intended character yourself.
   Continue ordinary gameplay. When skin/hair/facial hair looks different, select
   **Human appearance - compare changed** and Run with new acknowledgment.
4. When invisible, select **Human appearance - diagnose invisible** instead. Its
   output explicitly prints `CURRENT isInvisible=true/false/UNAVAILABLE` and
   relevant draw/opacity/model state. It never toggles visibility or resets a model.
5. Report which symptom occurred and the capture result. Logs use prefixes
   [SS Tests][human-visual-baseline], [human-visual-changed], [human-visual-invisible].
   Local console.txt/archived DebugLogs contain the per-field data; no pixels are
   recorded. Capture while the symptom is present; no automatic repro is installed.

Baseline capture changes **only diagnostic GlobalModData**, not the human. AFTER
controls are read-only. The shared window retains its warning/acknowledgment
because it also hosts destructive persistence tests. No operation bypasses consent.
Baseline capture is marked diagnosticWrite, not readOnly: prior cleanup failure
still blocks writes. AFTER can observe without clearing that failure. Neither
human control draws gameplay RNG/creates native-fixture boot tokens. No actor
constructors, native character saves/loads, actor/slot/singleton/appearance/
visibility/equipment setters or model resets are called. Native -debug is not
required to run the controls, but determines field coverage below.

## Baseline storage and identity

Separate world GlobalModData key `SSR.Tests.HumanVisual`, root `.baseline`:
`schema=1`, `engine="42.22.2"`, world-save name, capture timestamp string and
83 scalar field entries. Each entry records explicit availability; available
entries have scalar type/value (known null is kind `null`, value `<null>`), and
unavailable entries carry a reason. All entries are copied into fresh plain
Lua tables. No Java refs, userdata, functions, actor ModData, SSR production
registry or inventory objects are persisted. Version/build/shape/size/type/
finite-number/required-field/world checks reject invalid records without
repairing or overwriting them; explicitly recapture if appropriate. An
unavailable pre-debug value never becomes falsely equal to a later readable one.

Normal B42 GlobalModData writing controls durability (`global_mod_data.bin` in
the current save). No extra OnSave hook, explicit flush or save command is added.
OnGameStart clears only transient memory; it does not create data, inspect the
human, run tests or repair anything. Existing saved data is read/validated when
an AFTER becomes available; the selected AFTER still needs explicit Run.
Missing/invalid data is explained in Availability. AFTER never getOrCreates or
writes the diagnostic record. Capturing again intentionally replaces the
in-memory diagnostic record for the next normal save; no baseline archive is kept.

The current world's GlobalModData plus embedded save-world name isolate ordinary
worlds; a copied/cloned save remains a copy with no unique world UUID established.
No robust stable public human database ID getter was verified. Names and sex are
**hints only**, descriptor ID is not treated as durable identity, and appearance
is never used to identify the human. After restart every comparison warns
**CROSS-SESSION identity UNVERIFIED** and finishes INCONCLUSIVE. Matching name/sex
hints allow scalar comparison with that warning; differing/unavailable hints
withhold original-human comparison and print current data separately. A new
character with identical hints cannot be distinguished reliably; user verification
is required. Pointer equality is never compared to saved/reconstructed pointers.

For a baseline captured this session, original strong actor/slot/singleton/ref
checks remain. For a loaded baseline, the first explicit AFTER keeps a separate
session-only reference anchor; later AFTERs check for changes since that anchor
and label that scope. It does not certify cross-session identity. Actor changes
within the session withhold original-human comparison. No baseline auto-adoption.

AFTER never overwrites the baseline. The last four AFTER scalar snapshots stay
in Lua memory and are cleared on a new session; full captures are logged. Explicit
baseline recapture clears that history and anchor. Raw refs exist only transiently.
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

At original delivery: 219 automated tests and 113 Lua syntax checks pass in the working
copy; isolated staged-tree validation is reported separately in delivery mail.
Tests cover getter mutation traps, unavailable vs null, raw debug colors/styles,
normal dynamic drift, invisible flag, visual/reference/actor/slot changes, missing
baseline, another world/new character, bounded history, clearing on new session,
and no gameplay RNG draw from these read-only operations. No native appearance
bug was reproduced, no snapshots taken in-game by Codex, no repair performed.

User eyewitness AI movement after Test 03 restart is now recorded as direct
user evidence; its machine result remains historically INCONCLUSIVE. Test-03 R1
early observer was not started and is deferred, not silently implemented here.
Historical native/persistence evidence and tests are preserved. Original delivery
preceded the actual Test 04 execution reported below.


Final delivery checks: isolated export of staged source (excluding unrelated
user changes) passes 219 tests and 113 Lua syntax checks. LuaLS reports 88 legacy
diagnostics in 13 files, none in new test/UI modules. Editor source fingerprint
regenerated from isolated intended source. Documentation links checked; previous
evidence unchanged. Ignored logs: .venv/test04-delivery-suite.txt and
.venv/luals-test04-delivery-result.txt. No native baseline/symptom capture yet.


## Actual original Test 04 runtime observation (17 November 2026)

Read `C:/Users/Enter/Zomboid/console.txt`, source lines 1497–1779. Preserved
human-control log extract: [evidence/HUMAN_VISUAL_2026-11-17.log](evidence/HUMAN_VISUAL_2026-11-17.log).
Baseline capture timestamp 1794918818017; AFTER timestamps 1794918909857 and
1794918931559. All three completed: baseline PASSED as explicit capture, changed
and invisible INCONCLUSIVE. Each logged exactly 83 fields, with no missing/extra
comparison fields. All 25 UNAVAILABLE fields have intended reasons: 23 raw reads
require native debug, one animation getter deliberately skipped, one absent
texture creator. `context.nativeDebug=false`; debug reflection remains untested.

Readable stable identity/visual/visibility fields and same-session actor,
descriptor, visual, model, four slots and singleton refs were unchanged. Only
position X/Y and world time differed. `isInvisible=false`, ghost/sprite/culling
false, alpha/target alpha 1, getDoRender true, existing model present, texture
creator absent. Actor skinTextureIndex 3, descriptor -1, separate visual handles
already differed at baseline; this alone is not evidence of corruption. No error
or stack occurred after the first run through the inspected log end. Earlier
engine/asset/map errors are outside these runs. User did not confirm a symptom
was present at comparison: no symptom reproduction/root cause/renderer PASS claimed.

## R1 validation and native confirmation still needed

Automated tests simulate normal OnSave callback ordering followed by native data
serialization, reload/no-data/no-save/incomplete save, old saved baseline fallback,
scalar-only separation, corruption/schema rejection, wrong world/new human hints,
strong within-session refs, debug coverage asymmetry and read-only AFTER behavior.
These are mocked world-save writes; they do not substitute for an actual game run.

Real R1 check: restart to load code, capture while correct, note timestamp, normal
save/exit, restart/load the same world, run an AFTER without recapture, verify the
original saved timestamp and CROSS-SESSION warning. R1 native roundtrip NOT RUN.

R1 final validation: isolated intended source export passes **230 tests** (no
skips with installed PZ_GAME_DIR) and **113/113 Lua 5.1 syntax checks**. LuaLS
reports the same 88 legacy diagnostics in 13 files, none in the human diagnostic
module or Tests UI/registry. JAR SHA256 unchanged from the inspected build above.
No R1 native baseline-save/restart comparison has been run at delivery.
