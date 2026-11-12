# Long-run errors and B42 key audit

Reviewed on 8 November 2026. Latest local console/debug logs are from
6 November, 05:38–06:10, game42.21.0 revision4a0e9546ec, ending at frame263147.
User confirms NPCs are drawn. This run contains multiple other mods, including
KCMweapons and vehicle/interior mods; warnings must not all be attributed to SS.

## What actually errors

There are no gameplay Lua fail/attempted-index stacks in this run. There are
four startup IllegalStateException stacks from UIManager.update at frame0.
Its native update explicitly removes and rejects root UI elements whose
getParent() is non-null. SS has exactly four offending button registrations:
dialogue Yes/No/Continue and the old survivor-info Call button. Each was added
to the UI manager and then parented to its window. Removed only those four
root registrations; buttons remain children. This is a direct fix for the
invalid condition, though the log does not identify each offending element.

At frame88547 ItemContainer.AddItem cannot find Base.HockeyStick, directly
referenced by the random melee list. Other absent IDs in the same catalogs would
fail only when selected, so the audit covers them before waiting for more logs.

The three SS grave recipes log invalid Result/Category/Sound/Time and
CanBeDoneFromFloor keys at startup. Installed Recipe.Load no longer supports
those old result/settings lines as a working recipe definition. These need a
coherent craftRecipe/inputs/outputs/action conversion, not punctuation changes.
They were not removed or rewritten in this pass.

Other collected messages:

- ItemPickInfo cannot get ID for inventorymale/inventoryfemale: recurrent native
  container-identity warnings, with no associated Lua stack. Standalone NPC
  inventory/transfer ownership remains a plausible issue; do not assign arbitrary
  IDs merely to silence the log.
- Five translation keys lack format arguments: PutInContainer, Rack,
  InsertBulletsInMagazine, DropNamedItem, Trade. No matching direct SS call was
  found. Other enabled UI mods and copied vanilla menus may be involved; the
  logger does not identify a caller, so ownership is unresolved.
- Three imported-skeleton Body-bone errors have no asset path. There is
  insufficient evidence for a simple mod animation edit.
- Missing fonts, vehicle templates/crossbow sounds, map room IDs/groundcover
  tiles, invalid Wooden_Windows SpriteConfig, failed requires and map-zone warnings
  are retained as separate engine/content/mod-interaction findings. This log does
  not establish a common SS cause. Saved-map metadata errors should not be
  addressed by deleting save data as an incidental fix.
- weaponhitcharacter, SSIsInventoryTransferAction perform and raid-time lines
  are normal mod prints, not exception stacks.

## Confirmed key corrections

All replacements were checked against installed generated scripts or JAR fields.
There were22 distinct missing fixed Base/farming IDs;18 were corrected, leaving
four deliberately unresolved semantic cases listed below.

| Old identifier | Correction |
| --- | --- |
| Base.HockeyStick | Base.IceHockeyStick (current item still uses HockeyStick icon) |
| Base.BaseballBatNails | Base.BaseballBat_Nails |
| Base.PlankNail | Base.Plank_Nails (all weighted entries retained) |
| Base.Pickaxe | Base.PickAxe |
| Base.Hat_SurgicalCap_Blue | Base.Hat_SurgicalCap |
| Base.Hat_SurgicalMask_Blue | Base.Hat_SurgicalMask |
| Base.Hat_HardHatYellow | Base.Hat_HardHat |
| Base.HoodieUP_GreenTINT | Base.HoodieUP_WhiteTINT |
| Base.HoodieDOWN_GreyTINT | Base.HoodieDOWN_WhiteTINT |
| Base.223Box in preset loot catalog | Base.556Box, matching B42 VarmintRifle ammo |
| Base.308Clip in starter hunting rifle setup | Query weapon:getMagazineType(); add only when present (HuntingRifle has no detachable magazine) |
| farming.BroccoliSeed/CabbageSeed/CarrotSeed/PotatoSeed/TomatoSeed/RedRadishSeed | Same names under Base |
| farming.HandShovel | Base.HandShovel |
| dynamic farming. seed creation | Base. prefix |
| Perks.FromString("Foraging") | Perks.PlantScavenging |
| Perks.FromString("First Aid") | Perks.Doctor; Doctor is one skill, not a second score contribution |

The B42 clothing IDs consolidate color variants; this pass does not reproduce
the old exact green/grey/blue/yellow tint choices. Othermod silencer/ammo variants
and dynamic old ammo-name maps are not claimed compatible by these replacements.
Changing seed/tool IDs does not port farming's fluid actions or plant lifecycle.

## Remaining fixed item identifiers

| Identifier | Current assessment |
| --- | --- |
| Base.WaterBottleFull | Farming still uses old drainable water arithmetic; needs a fluid-container port |
| Base.WaterPot | Preset water supply needs a current pot plus explicit fluid contents |
| Base.WoodenLance | Preset weapon needs an explicit current spear choice; no proven direct rename |
| Base.Cigarettes | Old cancellation predicate in copied ISEatFoodAction; same old predicate also exists in installed vanilla action. B42 uses cigarette variants/tags; not an AddItem failure in this run |

The existing copied admin UI, native player visibility/LOS ownership, and old
foraging/farming systems remain separate known port work. No render/LOS changes,
new debug probes or log suppression were added in this pass.

## Repeatable checks

```powershell
.\.venv\Scripts\python.exe tools/audit_b42_keys.py G:\Steam\steamapps\common\ProjectZomboid
```

The read-only audit compares fixed Base/farming/Survivors literals and selected
item-only tables against script declarations, typed constants against JAR public
static fields, and literal/SurvivorPerks names against PerkFactory.Perks. It also
lists old recipe blocks. It excludes comments and handles ordinary quoted strings.
It does not prove dynamic strings, third-party mods, Lua exposure, argument types,
action lifecycle or item initialization behavior. All explicit typed constants
and checked perk names now resolve. The four remaining item IDs and three recipe
blocks are reported rather than hidden.

Validation:64 tests pass with PZ_GAME_DIR set;110/110 Lua syntax checks and
git diff --check pass. New checks cover UI parenting and the key inventory against
the actual installed scripts/JAR. These are offline checks, not live validation
of the fixes. Nine changed Lua files were installed and hash-verified for the
next normal game launch. No special console test is required for this pass.
