FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: New user-observed issue — human player appears to have changed to someone else
STATUS: INVESTIGATION REQUEST (NO FIX AUTHORIZED)
RELATED: SSR-TEST-03, native IsoPlayer reconstruction, rendering/identity

User says: "my player now changed to someone else. Very likely just graphical, so that's another one to deal with the rendering proper."

Do not presume graphical-only; the report is an observed change in appearance/represented identity, with actual cause undetermined. We must distinguish:
(a) correct human IsoPlayer with wrong visual/appearance render,
(b) descriptor/model/visual or clothing state contamination on same actor,
(c) actual local-player slot/singleton/control actor mutation or unexpected player-switching path.

Your prior tests guard human identity/XYZ/singleton and all four slots in bounded callbacks; they do not establish safety at arbitrary later frame or after NPC creation/reconstruction/other scripts. Consider legacy SuperSurvivorManager:switchPlayer, IsoPlayer singleton changes around native save/load, actor creation events and other mods. Do not assert a cause without source/log evidence.

Please acknowledge and conduct a *read-only* source/evidence triage when available: inspect relevant human/survivor actor/visual ownership paths, player control functions and available actual logs for crashes/character changes; identify a safe developer-only observation probe of player identity, local slots, descriptor/visual fingerprint, clothing, NPC actors and rendering if needed. Avoid any automatic player/visual reset or native load changes. Don't overwrite the user's save. Preserve live user state. If a focused in-game diagnostic is warranted, propose scope and exact safe steps for approval rather than introducing speculative changes under unrelated persistence work. Keep this issue separate from successful scoped Test 3 snapshot/registry evidence, but flag risk for eventual acceptance.

Reply with findings/evidence and recommended bounded next action via orchestrator inbox. R1 earliest actor observer remains deprioritized pending this report and later lifecycle priorities. No merge.
