# LuaLS duplicate-set-field review — 2026-11-12

Reviewed **27 distinct diagnostic locations** with the installed vanilla Lua
libraries indexed. This rule reports repeated assignments to a field, including
intentional replacements of game methods; it does not establish whether an
override is compatible with Build 42.

## Accidental reassignment fixed

`WindowSuperSurvivors:createChildren` assigned the base Modify header's
`onMouseDown` handler twice. The second assignment was in the companion-header
block and should have targeted `headers_companions_call`. Corrected that target,
so the Call header is noninteractive like the other headings. Both diagnostics
on the repeated base-header field are resolved.

## Deliberate chained overrides documented

Three declarations capture and call the previous implementation:

- `SurvivorLocator.lua`: wraps `ISWorldMap.render` to add survivor markers after
  normal map drawing.
- `ZOverrides.lua`: wraps `ISInventoryTransferAction.perform` and
  `ISGrabItemAction.perform` to observe theft before delegating.

Each now has a comment and a next-line-only `duplicate-set-field` annotation.
This documents intentional ownership at those assignments. It does not validate
the old theft action timing, unloaded-member map handling, hot reload behavior,
or other API usage. Those concerns remain in the
[vanilla override review](VANILLA_OVERRIDES_REVIEW_2026-11-10.md).

## Remaining full replacements

The refreshed scan reports **22 diagnostic locations**, all in three old action
replacements. Their warnings remain visible; the rule is still enabled.

| File | Reports | Methods |
| --- | ---: | --- |
| `client/TimedActions/ISBarricadeAction.lua` | 7 | `isValid`, `waitToStart`, `update`, `start`, `stop`, `perform`, `new` |
| `client/TimedActions/ISEatFoodAction.lua` | 8 | `isValid`, `update`, `start`, `stop`, `perform`, `getRequiredItem`, `eat`, `new` |
| `client/Vehicles/TimedActions/ISEnterVehicle.lua` | 7 | `isValid`, `update`, `start`, `stop`, `perform`, `getExtraLogData`, `new` |

These files define the same global classes and methods as vanilla rather than
chaining the current implementations. There are no repeated method definitions
inside each individual file. Their global replacement behavior is deliberate,
but current lifecycle/signature compatibility remains porting work. Removing
individual methods merely to clear diagnostics could combine incompatible old
and new action implementations.

The existing override review recommends restoring current vanilla actions and
adapting the NPC callers, retaining a narrowly scoped NPC-specific behavior only
when its need is demonstrated. That migration was not performed as part of this
diagnostic review.

## Validation

All **108 runtime Lua files compile**. LuaLS confirms the header/wrapper reports
are resolved and the remaining 22 reports belong only to the three action
replacements above. No new runtime tests were needed for the heading assignment
and diagnostic annotations; no live UI test was performed.
