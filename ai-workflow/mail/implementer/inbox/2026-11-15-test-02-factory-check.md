FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-15
SUBJECT: SSR-TEST-02 supplement — investigate engine-managed IsoPlayer factory/loading path
STATUS: ADDITIONAL READ-ONLY INVESTIGATION TO ACTIVE REQUEST
COORDINATION REF: B42
RELATED: ai-workflow/assignments/test-cell-only-isoplayer-02.md

USER QUESTION
Before advancing the cell-only constructor test, check whether PZ has a factory or engine-managed creation/loading API for IsoPlayer rather than only constructors.

INITIAL PUBLIC API FINDINGS (NOT PROOF OF INSTALLED ENGINE IMPLEMENTATION)
- SurvivorFactory.CreateSurvivor returns SurvivorDesc (not IsoPlayer).
- SurvivorFactory.InstansiateInCell returns IsoSurvivor (not IsoPlayer).
- IsoCell.LoadPlayer(int worldVersion) returns boolean and appears to be human/world player-loading, not an arbitrary NPC factory.
- IsoPlayer exposes constructors; official API lists three overloads.
Public docs do not establish absence of internal/private factory methods.

REQUEST
Inspect installed 42.22.2 Java and relevant vanilla Lua, searching *actual IsoPlayer creation call sites* and factory-like helpers, especially IsoWorld initialization, IsoCell.LoadPlayer, LuaManager/NewGame and player-slot/singleton wiring. Distinguish:
1. factory that returns a fully usable IsoPlayer,
2. descriptor factory,
3. engine-managed human-player load path,
4. raw constructor followed by registration.
If factory exists, document exact signature, Lua accessibility, side effects, ability to create a separate NPC without altering player slots or singleton. Do not call any human-loading API on the user's character in a runtime probe. If none is found, report scope of searched classes and don't claim global proof of absence.

Fold findings into SSR-TEST-02 research/delivery and decide whether the cell-only experiment remains the best bounded test. Do not change SSR production loading yet, no auto-merge.
