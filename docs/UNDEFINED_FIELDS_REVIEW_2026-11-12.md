# Undefined-field review — 2026-11-12

Checked runtime Lua with the installed Lua Language Server, actual vanilla Lua
libraries, and the editor API library. Initial output contained **168 distinct
source locations and 58 field names** (after removing repeated diagnostics).
Expanding return-type coverage exposed additional subtype checks, so the before
and after counts are not a one-to-one list of fixes.

## Missing editor coverage

Most initial reports referred to genuine APIs absent from the partial stubs:
player methods (`Say`, `CanSee`, `getCoopPVP`, equipment getters/setters), Core
settings, inventory operations, BodyPartType methods, drawing, reflection, and
other returned native objects. Verified their public Java signatures and added
coverage. `LoadGridsquare` and `RenderOpaqueObjectsInWorld` are real engine event
names omitted by the previous event-name filter.

The generator now also finds methods inherited through Java interfaces and
preserves native superclass relationships. For selected core types, it includes
public methods whose names occur at mod Lua call sites, ignoring comments and
strings. This does not infer which receiver a call uses: every emitted method
still has to exist on that Java class or its ancestors/interfaces. The generated
header records both game JAR and mod Lua source hashes. Regenerate after code
changes that introduce calls to further native methods.

No arbitrary-member index signatures, fabricated base-class methods, or broad
undefined-field suppression were added. Java signatures still do not establish
Lua exposure, nullability, or gameplay lifecycle correctness.

## Code defects fixed

- The old key-0 cover-test branch used nonexistent `IsoPlayer:getAngle()` and
  `IsoDirections.reverse`. It now obtains the opposite tile direction with
  `attacker:getDir():Rot180()`.
- `walkTo` called nonexistent `getOppositeSquare()` on a door, assigned the
  resulting building to an unused local, and could fail before handling the
  locked door. Removed that dead lookup. A regression test exercises the locked
  door path without providing that obsolete method.
- The dormant companion-manager prototype could dereference a missing
  `EnemySuperSurvivor` wrapper. Added the missing nil guard before its player read.

## Remaining subtype reports

There are **46 distinct undefined-field locations**. The named methods exist on
subclasses, while the Java getter declares a broader base return type. This is
not proof that all callers are safe. Some already check `instanceof`, but LuaLS
cannot refine repeated getter calls using that custom global function. Others
only assume the expected subtype.

| Category | Locations | Native owner / base return type |
| --- | ---: | --- |
| Door subtype | 17 | IsoDoor / IsoThumpable versus IsoObject |
| Weapon subtype | 14 | HandWeapon versus InventoryItem |
| Bag subtype | 11 | InventoryContainer versus InventoryItem |
| Human visual subtype | 3 | HumanVisual versus BaseVisual |
| Clothing subtype | 1 | Clothing versus InventoryItem |

For already checked values, the appropriate next change is to cache the returned
object in a local, check its subtype, and annotate that local. Do not add weapon
or bag methods to the InventoryItem base stub simply to silence the reports.

Specific assumptions still requiring code work:

- `giveWeapon` checks only whether `AddItem` returned nil, then invokes HandWeapon
  methods. A valid nonweapon item type would still reach invalid calls.
- `GunShotHandle` checks only whether the player is holding an item before
  `getSoundRadius`. Its correctness currently relies on its caller providing a
  gun-related situation.
- The old key-0 cover-test branch assumes the held item is a weapon when reading
  aiming properties. Direction calls are corrected, but the entire debug branch
  has not been ported or validated.
- `FindAndReturn` and `GetItemCount` assume a nonnil back-slot item is an
  InventoryContainer; the secondary-hand branch uses a category-string test.
- Blood operations use the broad `getVisual` return type. The verified native
  `getHumanVisual` getter offers an explicit HumanVisual return for player actors.

These reports remain visible. Runtime behavior for these assumptions was not
changed in this pass.

### Remaining locations

Line numbers reflect this checkout at review time. Repeated fields on the same
line can be separate expressions, so columns are retained.

| File | Line:column | Field | Category |
| --- | --- | --- | --- |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 791:44 | `getMaxDamage` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 811:43 | `isAimedFirearm` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1541:148 | `isAimedFirearm` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1548:169 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1549:169 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1550:163 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1566:162 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1566:261 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1567:162 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1567:261 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1800:30 | `isLocked` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1800:49 | `isLockedByKey` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1800:73 | `isBarricaded` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1890:29 | `isLocked` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1890:48 | `isLockedByKey` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1890:72 | `isBarricaded` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1901:29 | `isLocked` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1901:48 | `isLockedByKey` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1901:72 | `isBarricaded` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1911:29 | `isLocked` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1911:48 | `isLockedByKey` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1911:72 | `isBarricaded` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1921:29 | `isBarricaded` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1932:30 | `isBarricaded` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 1943:29 | `isBarricaded` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 2822:54 | `getRunSpeedModifier` | Clothing subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3237:36 | `IsOpen` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3238:15 | `ToggleDoor` | Door subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3749:12 | `isAimedFirearm` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3754:12 | `getMagazineType` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3755:45 | `getMagazineType` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3806:180 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3807:110 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3820:174 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3821:104 | `getItemContainer` | Bag subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3830:98 | `isAimedFirearm` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 3834:11 | `setJammed` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 4010:44 | `getMinRange` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 4734:43 | `getBlood` | Human visual subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 4769:48 | `getBlood` | Human visual subtype |
| `42/media/lua/client/3_Other/SuperSurvivor.lua` | 4770:27 | `setBlood` | Human visual subtype |
| `42/media/lua/client/3_Other/SuperSurvivorManager.lua` | 248:23 | `getSoundRadius` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivorsMod.lua` | 580:30 | `getHitChance` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivorsMod.lua` | 580:54 | `getAimingPerkHitChanceModifier` | Weapon subtype |
| `42/media/lua/client/3_Other/SuperSurvivorsMod.lua` | 581:63 | `getAimingTime` | Weapon subtype |
| `42/media/lua/client/5_UI/SuperSurvivorsContextMenu.lua` | 825:25 | `isAimedFirearm` | Weapon subtype |

## Validation

All 108 runtime Lua files compile. All 125 regression tests pass, including the
locked-door path and editor generation checks for native interface methods,
constructors, event names, inheritance, and preservation of base/subclass API
boundaries. The generated editor files pass LuaLS checks. These are local static
and mocked Lua checks; no live game test was performed for this review.
