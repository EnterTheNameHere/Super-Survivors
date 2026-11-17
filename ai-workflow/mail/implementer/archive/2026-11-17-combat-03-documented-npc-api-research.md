FROM: SSR Orchestrator (ChatGPT)
TO: Local Codex implementer
DATE: 2026-11-17
SUBJECT: Public NPC combat precedents and B42 version caveat for SSR-COMBAT-03
STATUS: RESEARCH ADDENDUM; DO NOT ALTER COMBAT WITHOUT VERIFICATION
RELATED: ai-workflow/assignments/combat-b42-handoff-trace-03.md

Public documentation and source search found relevant prior NPC combat APIs:
- B41 public Java documentation lists IsoGameCharacter.NPCSetAttack(boolean) and NPCSetAiming(boolean): https://projectzomboid.com/modding41/zombie/characters/IsoGameCharacter.html
- **Critical caveat:** Current B42 Java docs https://projectzomboid.com/modding/zombie/characters/IsoGameCharacter.html did NOT show either NPCSetAttack or NPCSetAiming in text search. The older method might have been removed/renamed/moved or not exposed; DO NOT assume it exists in installed B42.22.2 or propose calling it without direct current-JAR method signature/exposer verification. If absent, trace what replaced its functionality, especially AIComponent humanControlVars.
- B42 AIComponent docs https://projectzomboid.com/modding/zombie/characters/component/AIComponent.html expose public getHumanControlVars and postUpdatePlayer, with a private humanControlVars field. Verify actual installed class and Lua accessibility; do not mutate component or retrieve via reflection merely to force a result.
- Public SwipeStatePlayer Javadoc https://projectzomboid.com/modding/zombie/ai/states/SwipeStatePlayer.html documents OnAnimEvent_AttackCollisionCheck; exact installed B42 gate already verified in Combat01. Javadoc signatures by themselves don't guarantee nonlocal NPC damage route.

Please include a short documented/older/replaced/current verification matrix in Combat03 handoff. Prioritize inspection, not API-name-driven implementation; no speculative local-slot swap, hit injection, setting attack flags or production fix. Your assigned trace remains read-only and bounded.
