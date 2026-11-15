# User-requested startup error fixes

FROM: Local Codex
TO: SSR orchestrator
STATUS: SOURCE DELIVERED FOR REVIEW; in-game recipe reload pending

After successful probe, user requested checking logs, then explicitly requested
fixing our errors. Current session has no gameplay Lua stack trace. Mod-owned
startup errors: three percent-bearing option descriptions trigger Translator
format exceptions; three legacy grave recipes have rejected colon properties.

Source codex/persistence-b42: 29bebd072c83ae1de89a2b4129da24556eeb71a2.
Parent e4464bda8089a5c20fc969514f6f3c7ee2a0460a.
Changed: 42/media/scripts/SuperSurvivors.txt; English UI.json, UI_EN.txt and new
Recipes.json; docs/LOCAL_HANDOFF.md. Preserve unrelated local source/settings edits.

Descriptions spell out percent. Installed Recipe.Load confirms colon properties
except Override are unsupported. Converted three recipes to installed craftRecipe
syntax (inputs/outputs, retained tools, same ingredients/counts and 500/100/500
durations), explicit module-qualified item/action references and translated names.
Installed timedAction schema and DigShovel/MakingHammer_Surface animation names,
Shoveling/Hammering sounds used. Existing grave items unchanged; these remain
inventory recipes, not an implementation of vanilla world grave burial.

178 automated tests/112 Lua syntax checks pass, changed JSON parses and staged
whitespace passes. Installed native source and generated vanilla recipes checked.
Actual game restart/load and crafting validation NOT RUN after edit. Restart
required. No claim that static tests execute recipe loading or gameplay crafting.
Unrelated font/map/vehicle errors not modified. No Java modifications, lifecycle
rewrite or automatic implementation merge into B42. Prior probe results stand.
