# Autosave writer failure — 10 November 2026

## Separate sudden-death investigation

User clarifies that the death itself was sudden. Debug log00-19 records GAMESTART
at00:25:13.689 and `Bernard has died` at00:25:16.123 (frame286), about2.4 seconds
after the second world load in that process. Missing StrangeMeat messages follow
the death handler; they cannot be the initiating cause. Respawn/player creation
appears at00:26:25.190. No `weaponhitcharacter` callback print precedes the death
in this console session, and there is no logged health/damage cause.

Static review found retained B41 damage code in SuperSurvivorPVPHandle:100 extra
body-part damage on an injured nonzero-ID target, a500-per-part surrendered-target
execution path, and version-gated NPC damage compensation. The version gate is
false for42.22.2; the extra100 branch excludes ID0. All run inside the weapon-hit
callback whose print is absent here. They deserve a separate combat review, but
are not established explanations for this death. No speculative damage change
or health override was made. User was asked whether Bernard was the local player
and whether an attack/bleeding was visible. Current players.db was inspected
read-only; it contains the replacement living character, not Bernard's prior
health history. Cause remains unresolved; existing logs do not establish whether
saved injuries/infection, zombie/native damage or another mod caused the death.

## Follow-up: typed game mode in survivor save path

Next run reached native survivor saving at frame10244 and failed:
`__concat not defined for operands: Sandbox and \\2026-11-06_04-21-12\\`.
Stack: getSaveDir(SuperSurvivorTablesUtilities.lua:205), SaveSurvivor, update,
manager update, SuperSurvivorsOnTick.

Installed42.22.2 IsoWorld.getGameMode returns zombie.core.GameMode; toString()
returns its directory ID. Vanilla MapSpawnSelect uses that explicit conversion.
Updated both duplicate getSaveDir definitions (client table utility and shared
Utilities.lua) to call toString, preserving the save location/trailing separator.
Two regression tests use a typed-mode mock that rejects concatenation and cover
either definition being active.69 tests and110 syntax checks pass; touched Lua
files pass diff --check. Linked files need no copying; restart/live save pending.

The same log also reports missing Subpar.StrangeMeat on death. That item is not
defined in this checkout; changing its module name alone would not fix it.
This is a separate legacy death-loot feature, not the fatal save-path failure.

## Original writer-ID failure

Latest console reports42.22.2 revision3d39148846. Recurring stack:

```text
attempted index: write of non-table: null
save(SuperSurvivorTablesUtilities.lua:116)
Save(SuperSurvivorGroup.lua:489)
Save(SuperSurvivorGroupManager.lua:65)
SuperSurvivorsOnTick(SuperSurvivorsMod.lua:77)
```

The linked checkout declares `id=Super-Survivors`, while the legacy table IO
utility still used `SuperbSurvivors` for getModFileReader/getModFileWriter.
The installed getModFileWriter implementation resolves ChooseGameInfo.getModDetails
and returns null when that ID cannot resolve. The next unguarded write caused
the observed failure. Linking exposed the checkout's different metadata; the
junction itself is functioning.

Updated the utility's mod ID for all its readers/writers, centralized writer
opening with a descriptive error when opening fails, and closed the reader in
doesFileExist. Serialization and existing relative file paths remain unchanged.
This does not implement the planned ModData persistence port or migrate files
from the backed-up old copy. Legacy getModFileWriter writes below the active
mod's common directory, which is now linked to the checkout; moving save data
out of the mod directory remains separate persistence work.

Validation:67 tests pass with PZ_GAME_DIR set against the current installation;
110 Lua syntax checks pass. New tests compare the IO mod ID with mod.info, check
table/map serialization and close calls, and verify useful missing-writer errors.
The touched utility passes git diff --check. Unrelated script edits elsewhere
already have whitespace warnings and were left alone.

The installed file is the source through the verified42/common junctions. No
copy/deploy step. Restart to load the corrected utility; live autosave validation
is still pending. The log also contains removed-item warnings for disabled
KCMweapons/ZombieDismemberment mods; these are separate from the autosave stack.
