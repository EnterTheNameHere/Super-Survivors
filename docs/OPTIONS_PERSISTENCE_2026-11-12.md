# Options persistence failure — 2026-11-12

The live options Apply error at frame 65807 was `attempted index: write of
non-table: null` in `SaveSurvivorOptions`. The action attempted
`getFileWriter("SurvivorOptions.lua", true, false)` and used the returned nil
writer. Repeated Apply attempts produced the same failure; the unrelated
Has Been Read wrapper in the stack was not the originating frame.

The installed GlobalObject.getFileWriter checks the filename extension against
`LuaManager.ALLOWED_FILE_EXTENSIONS` and returns nil for disallowed extensions.
The legacy `.lua` name is inappropriate for these line-oriented settings.

## Change

- Write `SurvivorOptions.txt` under the game's Lua cache directory
  (`C:/Users/Enter/Zomboid/Lua` in this development installation).
- Prefer the text file when loading; fall back to the old `SurvivorOptions.lua`
  file for existing installations. Saving writes the text file and leaves the
  original untouched. The data format remains whitespace-separated option names
  and numeric values, not executable Lua.
- Open the reader once rather than performing a separate existence probe before
  reading. Close readers, including the retained public existence-check helper.
- Ignore blank/malformed/non-numeric records instead of indexing missing tokens.
- If a writer cannot be opened, report the actual filename and unsuccessful save
  rather than dereferencing nil. The setter restores the previous in-memory
  option value for that failure before propagating the useful error.
- Define nullable native file-reader/writer return types in the editor library.

Regression coverage exercises save/reload, legacy migration and new-file
precedence, reader closure, malformed records, and writer-open failure without
changing the previous stored value. Restart the game to load this change, then
apply the options again; failed prior attempts did not persist their changes.
