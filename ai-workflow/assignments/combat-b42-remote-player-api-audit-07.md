# SSR-COMBAT-07 — B42 remote-player and multiplayer combat API audit

Date: 2026-11-18
Status: REQUESTED / NOT ACKNOWLEDGED
Priority: narrow investigation only; no combat implementation or new runtime experiment.
Source checkout: exclusive codex/persistence-b42. Canonical coordination B42.

## Purpose
SSR stays Lua-only. NO Java mods, loaders, bytecode patches, class-exposure bypass, spoofed player slots or fabricated networking. Combat05 showed natural attack accepted with flags true, then initiateAttack lost while attackStarted remained latched. Combat06 found no complete ordinary Lua entry for nonlocal native NPC initiation and melee collision. User asks whether existing MP **remote-player** state/animation/combat replication exposes reusable legitimate Lua APIs even though we expect ownership barriers.

## Questions and evidence
1. Inspect actual installed B42.22.2 media/Lua and read-only game class signatures/implementation for local vs remote IsoPlayer roles, creation/identity, network components (NetworkPlayerAI, NetworkPlayerComponent or actual names), input ownership, server authority vs client-local calculations, server/client combat messages, collision/damage and state/animation representation. Identify paths by verified exact class names and call contracts; don't assume old B41 or generic networking documentation matches.
2. Trace how an actual remote player gets movement and animation updates and which client/server computes or validates swing, hit/miss, damage, weapon/ammo/inventory and zombie state; clearly distinguish observed source behavior from inferred authority, and handle whether specific flows differ in SP, hosted MP and dedicated server.
3. Identify ordinary **Lua-exposed**, non-network-spoofing mechanisms that can show a survivor's animation or make the native hit pipeline accept a standalone SP nonlocal actor. Pay special attention to whether remote visual/state application is display-only and whether native collision is local-owner gated or computed on another endpoint. Verify Lua Exposer and installed calls, not just Javadoc method visibility.
4. Check whether any safe, supported remote-player reuse preserves SSR actor ownership, native action lifecycle, no fake packets, no local player registration or session/server authority and does NOT introduce duplicate hits. If none, record concise negative finding and exact blocker. NO force sends, packet injection, network emulation, GameClient/GameServer toggles, Java, NPC class replacement, state forced entry or direct Hit.
5. Compare results with Combat04/05/06 native evidence and identify whether research changes recommended next decision. If it doesn't, explicitly close the path without creating new repeated diagnostics.

## Deliverables
Evidence-rich short report docs/COMBAT_B42_REMOTE_PLAYER_API_07.md on source branch with exact installed-source references, compact capability matrix (remote visual replication, attack lifecycle, collision, damage, authority, Lua usability), applicable to SSR vs remote-only; list caveats. Publish ACK and completion in orchestrator inbox on B42 with source commit. Docs-only, no runtime modifications, no new tests or user game run needed, no merge. Preserve user worktree/settings/common saves and unrelated changes, maintain one implementer and avoid concurrent code edits. Current invariant: no Java, even if technically feasible.
