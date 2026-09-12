# Ideology

How the player faction's ideology actually changes, and what the believer count does
and does not gate.

Verified against decompiled RimWorld 1.6.4871 and the Ideology DLC's shipped defs
unless an entry says otherwise. These are *verified available mechanisms*, not
commitments to use them — selection happens in `docs/specs/`.

---

## One field, two lifecycles

`FactionIdeosTracker.primaryIdeo` is **derived state for the player faction** and
**stored state for every NPC faction** [V]. That asymmetry is the whole subject, and
it matters outside religion: the era gate, the storyteller and the altar all read
"the player's ideology" and none of them may assume it is fixed.

`FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` recomputes the player's
primary ideo from live free-colonist counts, promotes the new plurality, sends
`LetterLabelNewPrimaryIdeo` / `LetterNewPrimaryIdeo`, calls
`Ideo.Notify_NotPrimaryAnymore` on the old one and **rebuilds `ideosMinor` from
scratch** — it is not accumulated [V]. It runs on every membership gain or loss and on
every colonist ideo change (`Notify_ColonistChangedIdeo`), and it early-returns when
`Current.ProgramState != ProgramState.Playing`.

**The promotion rule is strict plurality**: `num > count(primaryIdeo)`, over free
colonists filtered to `HomeFaction == Faction.OfPlayer` [V]. Two converts flip a
two-pawn colony and do nothing to a ten-colonist one.

For NPC factions none of this runs: `Notify_MemberGainedOrLost` early-returns unless
`faction.IsPlayer` [V].

**So `FactionIdeosTracker.SetPrimary` on the player faction is reverted by the next
recalculation** — it is a bare field write with no guard, and the recomputed value
overwrites it on the next colonist who joins, leaves, dies or converts. On NPC
factions the same call is durable. This is recorded here rather than in
`docs/TRAPS.md` because **it is loud**: the revert is announced by vanilla's own
primary-ideo letter. Vanilla's use in `Page_ChooseIdeoPreset.AssignIdeoToPlayer` is
safe only because it runs at worldgen, where the recalculation early-returns.

## Moving a pawn's ideology

`Pawn_IdeoTracker.SetIdeo(Ideo)` is **public**, accepts **any `Ideo`**, has **no
`IdeoManager` membership check**, and early-returns on babies [V]. For a player-faction
member it calls `Notify_ColonistChangedIdeo`, which is what triggers the recalculation
above — so moving pawns is the supported way to move the faction, and forcing the
faction directly is not.

A colonist holding an NPC faction's `Ideo` is an ordinary vanilla state, not an exotic
one: `InteractionWorker_ConvertIdeoAttempt.ConversionSelectionFactor` gives an
`NPC_Free → Colonist` conversion a weight of 0.5 [V].

`Ideo` identity survives a doctrine change:
`IdeoDevelopmentUtility.ApplyChangesToIdeo` mutates the instance in place, so
`Scribe_References` to an `Ideo` never dangle across a reform [V]. The consequence
worth knowing is that the two routes differ on identity, not on doctrine — vanilla's
`RoleRequirement_SameIdeo.Met` is `p.Ideo == role.ideo`, **reference equality** [V].

`FactionDef.fixedIdeo` and its companions (`ideoName`, `forcedMemes`, `requiredMemes`,
`disallowedMemes`, `deityPresets`, …) author an NPC faction's doctrine at worldgen and
are **NPC-only** [V] — `Page_ChooseIdeoPreset.PostOpen` applies them inside
`if (allFaction != Faction.OfPlayer && …)`.

## Role activation and ritual obligations use the same count and different rules

Both read `Ideo`'s colonist believer count, and `Ideo.RecacheColonistBelieverCount`
counts free colonists only — **excluding slaves, quest lodgers and pawns in
cryptosleep** [V].

- **`Ideo.ObligationsActive` has a primary-ideo exemption**: `Faction.OfPlayer.ideos.IsPrimary(this)`
  short-circuits it [V].
- **`Precept_RoleSingle.RecacheActivity` does not.** It gates on
  `colonistBelieverCountCached >= def.activationBelieverCount || def.leaderRole` [V],
  three lines away in the same class, deliberately without the escape hatch.

`activationBelieverCount 3` / `deactivationBelieverCount 1` live on the abstract
**`PreceptRoleSingleBase`** (`Ideology/Defs/PreceptDefs/Precepts_Role.xml`), so every
role precept inheriting it — vanilla's moral guide included — is inactive below three
believers and is unassigned on the next recache if assigned anyway [V]. `leaderRole:
true` short-circuits the count on both the activation and deactivation branches.

## Nothing restricts a ritual role to `Precept_RoleSingle`

`RitualRole.precept` is a bare `PreceptDef`, and `AppliesToRole` compares
`p.Ideo.GetRole(p).def == precept` [V]. The class of the precept is never tested, so a
`Precept_RoleMulti` is equally usable as a ritual role gate. What *is* true in 1.6 is
that the only two role precepts referenced by any vanilla ritual behaviour are
`IdeoRole_Moralist` and `IdeoRole_Leader`, and both are `Precept_RoleSingle` [V] —
which is a fact about vanilla's content, not a constraint in the code.

`RimWorld.RoleRequirement` is the live extension point for role eligibility: a
three-member abstract whose only override is `bool Met(Pawn, Precept_Role)`, selected
per role in XML as `<li Class="…">`. `VanillaMemesExpanded` ships five subclasses of
it in its 1.6 assembly [V].
