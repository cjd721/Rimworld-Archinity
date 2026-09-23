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

**All of the above is `Precept_RoleSingle`.** `PreceptRoleMultiBase` sets no believer
counts. `Precept_RoleMulti.Init` sets `active = true`, and `Precept_RoleMulti.RecacheActivity`
only drops holders that fail `ValidatePawn`, so a multi-holder role is active at any believer
count [V]. A believer count written on a multi-holder def is inert. `Precept_Role.GetTip`
still prints it whenever it is not −1 [V].

**Two edges on the single-holder gate** [V, `Precept_RoleSingle.RecacheActivity`]:
- With `activationBelieverCount` −1 (the `PreceptDef` default for a def not inheriting
  `PreceptRoleSingleBase`), the role never activates.
- With activation ≤ deactivation, at that exact believer count the deactivation branch and
  then the activation branch both fire in the same call. That happens every world tick,
  sending `LetterLabelRoleInactive` and `LetterLabelRoleActive` and unseating the holder each
  time.

## Nothing restricts a ritual role to `Precept_RoleSingle`

`RitualRole.precept` is a bare `PreceptDef`, and `AppliesToRole` compares
`p.Ideo.GetRole(p).def == precept` [V]. The class of the precept is never tested, so a
`Precept_RoleMulti` is equally usable as a ritual role gate. What *is* true in 1.6 is
that the only two role precepts referenced by any vanilla ritual behaviour are
`IdeoRole_Moralist` and `IdeoRole_Leader`, and both are `Precept_RoleSingle` [V] —
which is a fact about vanilla's content, not a constraint in the code.

`RimWorld.RoleRequirement` is the live extension point for role eligibility: a
four-member abstract — `labelKey`, `virtual string GetLabel(Precept_Role)`, `GetLabelCap`,
`abstract bool Met(Pawn, Precept_Role)` — selected per role in XML as `<li Class="…">` [V].
`GetLabel` is overridable, and it is what the role menu prints as the reason a pawn cannot
take the role (`SocialCardUtility.DrawPawnRoleSelection` → `Precept_Role.GetFirstUnmetRequirement`) [V]. `VanillaMemesExpanded` ships five subclasses of
it in its 1.6 assembly [V].

## Role precepts: what the two classes hold, and how a role enters a live ideology

From [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114).

**Holders.**
- `Precept_RoleSingle` holds one pawn (`chosenPawn`).
- `Precept_RoleMulti` holds a list (`chosenPawns`), and its `Assign` has no cap. No reader
  outside the class caps it either [V].
- `PreceptDef.maxCount` limits *instances of a def* in the ideology editor
  (`IdeoUIUtility.AddPrecept`, default 1), not holders [V].
- **Vanilla's specialist posts are multi-holder.** All eight vanilla specialists
  (`IdeoRole_ShootingSpecialist`, `…Melee…`, `…Research…`, `…Plant…`, `…Production…`,
  `…Mining…`, `…Animals…`, `…Medical…`) inherit `PreceptRoleMultiBase` and so are
  `Precept_RoleMulti`, uncapped. A "one holder per post" design must author a
  `Precept_RoleSingle` or cap the post itself. Vanilla's role-eligibility classes are
  `RoleRequirement_NotChild`, `_SameIdeo`, `_SupremeGender` and `_MinSkillAny` (skill level only;
  nothing reads passion). `PawnGenerator` assigns no role. From
  [#156](https://github.com/cjd721/Rimworld-Archinity/issues/156);
  `Ideology/Defs/PreceptDefs/Precepts_Role.xml`, `RimWorld.Precept_RoleMulti.Assign`. 1.6.4871 [V].

**`leaderRole` is a single-holder concept** [V]:
- `Precept_RoleSingle.Assign` is the only writer of `Faction.OfPlayer.leader` among roles, and
  it unseats every other `leaderRole` precept across `Faction.OfPlayer.ideos.AllIdeos`.
- `Precept_RoleMulti.Assign` does neither.
- `RitualUtility.AllRolesForPawn` offers only the primary ideology's first `leaderRole`
  precept.

**Two multi-holder roles per ideology, where `CanAdd` is asked.** [V]
- `IdeoFoundation.CanAdd` returns `"MaxMultiRolesCount"` when the def's
  `preceptClass == typeof(Precept_RoleMulti)` (exact type) and the ideology already holds two
  *visible* `Precept_RoleMulti` (`IdeoFoundation.MaxMultiRoles = 2`).
- `CanAdd` sits behind the editor and reform listings (`IdeoUIUtility.CanListPrecept` →
  `Ideo.CanAddPreceptAllFactions`) and behind generation (`CanAddForFaction`).
- `Ideo.AddPrecept` performs no check, and a subclass of `Precept_RoleMulti` is not caught by
  the exact-type test.

**One role per pawn, as every reader sees it.** [V]
- `Ideo.GetRole(p)` returns the first role whose `IsAssigned(p)` is true.
- `StatWorker` (role stat effects), `QualityUtility.GenerateQualityCreatedByPawn`,
  `StatPart_RoleConversionPower`, `EquipmentUtility.RolePreventsFromUsing`, the role menu and
  ritual roles all read `GetRole`.
- `RitualOutcomeEffectWorker_RoleChange.Apply` unseats the current role before assigning.

**Effects** [V]:
- `RoleEffect` is abstract, with virtual `Label`, `CanEquip` and `Notify_Tended`. Every other
  effect is applied by a reader that type-tests a concrete vanilla subclass
  (`RoleEffect_PawnStatOffset`/`Factor` in `StatWorker`, `RoleEffect_ProductionQualityOffset` in
  `QualityUtility`, `RoleEffect_HuntingRevengeChanceFactor` in `PawnUtility`).
- `RoleEffect_ProductionQualityOffset` applies to every quality roll the pawn makes, not per
  recipe.
- Vanilla tailoring (`ApparelMakeableBase`) and armour-smithing (`ArmorSmithableBase`) both
  use `workSpeedStat` `GeneralLaborSpeed`.

**Adding a role to a live ideology.**
- `Ideo.AddPrecept(PreceptMaker.MakePrecept(def), init: true)` adds the precept, re-sorts, and
  calls `RecachePrecepts` → `RecachePossibleRoles`. It sends no letter or message [V].
- `Precept.Init` draws `Rand.Int` and `UniqueIDsManager.GetNextPreceptID`, and `Precept_Role.Init`
  draws a name and apparel requirements [V]. It is simulation work.
- Vanilla calls exactly this on loaded ideologies in `Ideo.ExposeData` (PostLoadInit), but only
  to backfill a missing ritual seat and missing hidden ritual precepts [V]. Nothing backfills
  roles.

**Generation places special role precepts everywhere.** [V]
- `IdeoFoundation.AddSpecialPrecepts` adds every def with `countsTowardsPreceptLimit` false and
  `canGenerateAsSpecialPrecept` true that passes `CanAddForFaction`, to every generated ideology,
  NPC ones included. That is how the moral guide and leader reach every ideology.
- `PreceptDef.enabledForNPCFactions` is not consulted there.

**A reform rebuilds every precept instance.** [V]
- `Ideo.CopyTo` makes new `Precept` objects via `PreceptMaker.MakePrecept` + `Precept.CopyTo`,
  copying `ID`, holders (`chosenPawn` / `chosenPawns`) and `active`.
- References to a `Precept` instance do not survive a reform. `Ideo` identity does (see
  *Moving a pawn's ideology*).
- `Precept.DrawPreceptBox` offers *Remove* in the editor and at reform only when
  `def.canRemoveInUI`.

**Fluid reform needs a fluid ideology.** [V]
- `IdeoDevelopmentUtility.ApplyChangesToIdeo` calls `ideo.development.Notify_PreReform` before
  `newIdeo.CopyTo(ideo)`.
- `Ideo.development` is created only by the `Fluid` setter, `ExposeData` (when fluid) and
  `CopyTo` (when the source is fluid).
- A non-fluid target therefore throws before anything is mutated.
- At reform, `Dialog_ReformIdeo` limits memes, structure and styles to one change, but lets the
  player add and remove precepts freely, roles included.

**A removed role def.** A precept whose def no longer loads is dropped in `Ideo.ExposeData` with
*"Some ideoligion precepts were null after loading"* [V].

## An NPC faction's faith, and who follows it

Established on [#133](https://github.com/cjd721/Rimworld-Archinity/issues/133). Verified against
RimWorld 1.6.4871.

**The label and the people are separate state.** `FactionIdeosTracker.SetPrimary` changes the
faction's primary and nothing else. No NPC faction ever has its primary recomputed from its members [V]
(§ *One field, two lifecycles*). Members change only through `Pawn_IdeoTracker.SetIdeo`.

**How pawns pick a faith** [V]:
- Fresh generation (`PawnGenerator`, both sites): `request.FixedIdeo`, else
  `faction.ideos.GetRandomIdeoForNewPawn()`, weighted **4 for the primary, 1 per minor**. Babies get none
  until `TryJoinIdeoFromExposures`.
- Redress of an existing world pawn: re-rolled only when `pawn.Faction != request.Faction` **and** the
  new faction does not `Has` the pawn's faith. A same-faction redress keeps whatever the pawn held.
- A new leader (`Faction.TryGenerateNewLeader`) is ordinary generation, with `FixedGender` from the
  primary's `SupremeGender`. Worldgen generates the first leader right after the faction's faith is chosen
  (`FactionGenerator.NewGeneratedFaction`).

**Minors on NPC factions exist but vanilla never writes them.** `ChooseOrGenerateIdeo` clears
`ideosMinor`, and there is no public add. `IdeosMinorListForReading` returns the backing list, which is
the only write path [V].

**Sharing a primary is vanilla's normal state** [V]. `ChooseOrGenerateIdeo` reuses an existing
compatible, non-`solid` `Ideo` at `Rand.Chance(0.2f)`, always for a `hidden` faction, and always once
ten non-solid faiths exist. `IdeoGenerator.MakeFixedIdeo` sets `solid = true`, so a `fixedIdeo` faith
is never reused at world creation. Two effects of sharing:
- `Ideo.Color` is `primaryFactionColor`, set once from the generating faction.
- `Ideo.CanAddPreceptAllFactions`, which the precept editor calls through `IdeoUIUtility.CanAddPrecept`,
  refuses a precept if **any** faction listing the faith has a `FactionDef` that disallows it. A player
  faith shared with an NPC faction is edited under that faction's def restrictions.

**What reads the label, not the people** [V]:
- `GoodwillSituationWorker_SameIdeo` (+10 natural goodwill when a faction's primary is the player's
  primary, by reference) and `GoodwillSituationWorker_MemeCompatibility`, both recalculated every 1000
  ticks;
- `Faction.LeaderTitle`;
- xenotype weights from primary memes in `PawnGenerator`;
- `StockGenerator_Slaves`;
- `IdeoUtility.GetIdeoColorForBuilding`;
- the Factions-tab ideo icons.

**A faith nobody lists is deleted, and its holders are moved** — `docs/TRAPS.md` T-109.

## Forcing and floor-setting a player ideology

Verified against 1.6.4871 (`Assembly-CSharp.dll`) on
[#140](https://github.com/cjd721/Rimworld-Archinity/issues/140). The system that selects
from this is `docs/specs/RELIGION.md` § *A campaign base for the player faith*.

**`MemeDef.requireOne` forces a precept per issue and narrows that issue to one authored
set.** It is `List<List<PreceptDef>>` [V]. `IdeoFoundation.AddRequiredPreceptsForMemes`
removes any non-required precept already holding the issue, then picks one member of each
sublist by `selectionWeight` [V]. The forced precept **cannot be removed**:
`Precept.DrawPreceptBox` builds the Remove option only when
`def.canRemoveInUI && !def.issue.HasDefaultPrecept`, then nulls its action when
`ideo.GetMemeThatRequiresPrecept(def) != null` and relabels it *"CannotRemove:
RequiredByMeme"* [V].

**The swap rule is where the floor comes from, and it turns on `checkDuplicates`.** The
float menu gates each alternative on
`IdeoUIUtility.CanListPrecept` → `Ideo.CanAddPreceptAllFactions` →
`IdeoFoundation.CanAdd(def, checkDuplicates: false)` [V]. With `checkDuplicates` **false**
the live branch is: if the ideology already holds a precept of this issue that a meme
requires, accept the candidate only if a meme requires it too — `return
ideo.PreceptIsRequired(precept)` [V]. `Ideo.PreceptIsRequired` is
`GetMemeThatRequiresPrecept(precept) != null`, scanning every sublist of every meme's
`requireOne` [V]. **So the legal set for that issue is exactly the authored sublist** — and
**any other meme's `requireOne` touching the same issue widens it**, because the scan covers
all the ideology's memes [V].

**It survives a reform.** `Dialog_ReformIdeo` edits a scratch `newIdeo` built by
`ideo.CopyTo(newIdeo)`, which carries the memes, so both the swap rule and the remove block
still apply [V]. What does *not* survive a reform is every `FactionDef` restriction —
**T-121**.

**`Ideo.CanAddPreceptAllFactions` reaches the player faction, and every colonist's faith.**
It loops `Find.FactionManager.AllFactions`, filtered only by `allFaction.def.humanlikeFaction`
and `ideos.IsPrimary(this) || IsMinor(this)`, with **no `isPlayer` exclusion**, calling
`IdeoFoundation.CanAddForFaction`, which rejects anything in `forFaction.disallowedPrecepts`
[V]. `humanlikeFaction` defaults true and no player faction def overrides it [V], and
`Page_ConfigureIdeo.SelectOrMakeNewIdeo` calls `Faction.OfPlayer.ideos.SetPrimary(ideo)`
*before* the editor opens [V]. Because the loop keys on `IsPrimary || IsMinor`, and
`FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` rebuilds `ideosMinor` from live
colonist faiths (§ *One field, two lifecycles*), **the gate applies to every faith any
colonist holds**. Generation respects it too: `Page_ChooseIdeoPreset.PostOpen` and `DoPreset`
build `IdeoGenerationParms(Find.FactionManager.OfPlayer.def)`, and `RandomizePrecepts`,
`AddPreceptsOfImpact`, `AddSpecialPrecepts` and `AddRequiredPreceptsForMemes` all pass
`parms.forFaction` to `CanAddForFaction` [V].

**This corrects the standing "`FactionDef` ideology fields are NPC-only" framing.** It is
right about `fixedIdeo` / `forcedMemes` / `ideoName` / `deityPresets`, which are applied in
`Page_ChooseIdeoPreset.PostOpen` inside `if (allFaction != Faction.OfPlayer …)` [V], and
wrong as a generalisation: `disallowedPrecepts` reaches the player by a different path
entirely, and vanilla's own `PlayerTribe` relies on it [V]. The *meme* fields go the other
way — **T-123**.

**`GenerateClassicIdeo` bypasses `CanAddForFaction` outright**: it adds every `PreceptDef`
with `classic: true` directly, consulting only `genParms.disallowedPrecepts` [V]. The
Classic / Custom / Fluid / "Load saved…" buttons are hardcoded in
`Page_ChooseIdeoPreset.DoWindowContents`, not drawn from defs, so no XML removes them [V].

**`ScenPart.PostIdeoChosen` is the one seam that sees the finished faith, whatever produced
it.** `Scenario.PostIdeoChosen()` walks `AllParts` and calls the virtual, and **every exit
from the ideo page calls it** — `DoClassic`, `DoLoad`, `DoPreset` and
`Page_ConfigureIdeo.CanDoNext` [V], including the two paths that bypass `CanAdd`. Vanilla
ships no ideology `ScenPart` [V], so a part there is new code, but it hooks a virtual and
needs no Harmony. It runs under Multiplayer:
`Multiplayer.Client.Factions.Page_ConfigureStartingPawns_Multifaction.GeneratingPawns` calls
`_scenario.PostIdeoChosen()` [V].

**`IdeoPresetDef` carries four fields** and is the preset-shaped route; vanilla, Biotech and
VIE Memes and Structures are the only sources on disk (108 tags) [V].

**`.rid` files are save data, not content.** `Verse.GenFilePaths.AllCustomIdeoFiles` reads
`FolderUnderSaveData("Ideos")` and nothing else, and `RimWorld.IdeoFiles.RecacheData` is its
only consumer [V]. **Zero `.rid` files exist in either corpus root** [V] — a mod cannot ship
one into the Load list, and anything loaded that way bypasses every gate above.

**Multiplayer.** Ideo authoring runs once on the host in single-player and the whole
`IdeoManager` is snapshotted to joiners (`HostUtil.HostServer` →
`SetupGameFromSingleplayer` → `SaveLoad.CreateGameDataSnapshot`) [V]. The one live edit path
is registered: `SyncMethod.Register(typeof(IdeoDevelopmentUtility), "ApplyChangesToIdeo")
.ExposeParameter(1)`, with `SyncMethods.FixIdeoAfterCopy` (`[MpPostfix(typeof(Ideo),
"CopyTo")]`) reassigning negative `Precept.ID`s inside command execution [V]. MP's own
multifaction ideo page (`Page_ChooseIdeo_Multifaction`) is **preset-only** — it filters
Classic, Custom and Fluid out of the category loop [V]. MP Compat carries no ideology-editor
compat class [V].
