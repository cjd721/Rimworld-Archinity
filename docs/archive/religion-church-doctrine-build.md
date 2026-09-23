# Superseded build — replacing the player faith with Church doctrine

> Archived from [`docs/specs/RELIGION.md`](../specs/RELIGION.md): this build rested on the founders converting to the Church's ideology, which the campaign withdrew — the Church and the player faith never merge ([`plot/ENDING.md`](../plot/ENDING.md) § *The Alignment Rule*; [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)). Its live engine facts are in [`docs/engine/ideology.md`](../engine/ideology.md). History, not authority.

## The build

**Mid-game ideology conversion of the player faction is not merely possible — it is what
vanilla does on its own.** `RimWorld.FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns`
recomputes the player faction's `primaryIdeo` from live free-colonist ideo counts, on every
member gain or loss and on every colonist ideo change [V]. So the campaign does not need a
mechanism that *moves* the ideology. It needs a rite that moves it **deliberately**, and a
record saying it did.

The build is one ritual outcome worker, one `RoleRequirement` subclass, two `PreceptDef`s
and three scribed fields. No Harmony patch, no new Def type, no new saved collection.

### 1. The rite — one `RitualOutcomeEffectWorker` subclass

On a good outcome the worker does three things, in order:

1. `pawn.ideo.SetIdeo(churchFaction.ideos.PrimaryIdeo)` for each founder in the rite's roles.
   `RimWorld.Pawn_IdeoTracker.SetIdeo(Ideo)` is public and accepts **any** `Ideo` — it performs
   no `IdeoManager` membership check of its own, so passing an unregistered `Ideo` is our
   responsibility, not the engine's. Its one refusal is a **baby early-return** [V], which is
   irrelevant to a founder but would matter if the rite were ever opened to the colony at large.
2. Writes the commitment record (§2).
3. `Precept_Role.Assign(founder, addThoughts: true)` for the leader and preacher rungs.
   `RimWorld.Precept_Role.Assign(Pawn, bool)` is public abstract, concrete on
   `Precept_RoleSingle` [V].

**Everything downstream of step 1 is vanilla's, unpatched** [V]:

- `SetIdeo` calls `pawn.Faction.ideos.Notify_ColonistChangedIdeo()` for a player-faction
  member, which calls `RecalculateIdeosBasedOnPlayerPawns()`.
- That method promotes the new plurality, sends `LetterLabelNewPrimaryIdeo` /
  `LetterNewPrimaryIdeo`, calls `Ideo.Notify_NotPrimaryAnymore` on the old primary, and
  rebuilds `ideosMinor` from scratch.
- `SetIdeo` itself already unclaims an ideologically forbidden bed, strips forbidden
  bonds with a letter, dirties situational thoughts, re-evaluates needs, apparel and
  temporary abilities, and files a `HistoryEventDefOf.ChangedIdeo` event.

**A colonist holding an NPC faction's `Ideo` is an ordinary state, not an exotic one.**
`RimWorld.InteractionWorker_ConvertIdeoAttempt.ConversionSelectionFactor` weights an
`NPC_Free → Colonist` conversion at 0.5 [V] — vanilla preachers do this to colonies every
playthrough.

**The nearest shipped donor performs this exact sequence mid-game, inside a synced command.**
`Multiplayer.Client.Factions.FactionCreator.CreateFaction` is a `[SyncMethod]` that runs
while a game is in progress and calls `IdeoGenerator.GenerateIdeo(…)`,
`Find.IdeoManager.Add(ideo)`, `faction.ideos.SetPrimary(ideo)` and then
`startingPawn.ideo.SetIdeo(faction.ideos.PrimaryIdeo)` for every pawn [V]. The mechanism is
not theoretical; a mod we already ship drives it.

⚠ **State the precedent's limit with it.** `CreateFaction` runs that sequence on a **brand-new
faction with freshly generated pawns**, not on an established colony changing its mind [V]. What
it proves is that the four calls compose and survive `[SyncMethod]` serialisation mid-game. What
it does not prove is the part our rite actually does: `SetIdeo` onto founders who already hold an
ideology, already have beds, bonds, apparel and thoughts bound to it, inside a colony whose
believer counts then drive `RecalculateIdeosBasedOnPlayerPawns`. That composition is the [I] this
capability carries, and § *Verification* names the observation that closes it.

**The Church's doctrine is authored in XML and costs nothing.** `FactionDef` carries
`fixedIdeo`, `ideoName`, `ideoDescription`, `forcedMemes`, `requiredMemes`,
`disallowedMemes`, `deityPresets`, `styles`, `hiddenIdeo` and `requiredPreceptsOnly`, and
`RimWorld.FactionGenerator.CreateFactionAndAddToManager` funnels all of them into
`IdeoGenerationParms(fixedIdeo: true)` → `FactionIdeosTracker.ChooseOrGenerateIdeo` →
`IdeoGenerator.MakeFixedIdeo` [V]. Those fields are **NPC-only** — `Page_ChooseIdeoPreset.PostOpen`
applies them inside `if (allFaction != Faction.OfPlayer && …)` [V] — which is exactly why the
*player's* starting ideology needs the `.rid` route and the Church's does not.

### 2. State and persistence — three fields, and why none of it is derivable

⚠ **`founder.Ideo == churchFaction.ideos.PrimaryIdeo` is not proof of a commitment.**
`InteractionWorker_ConvertIdeoAttempt.Interacted` → `Pawn_IdeoTracker.IdeoConversionAttempt`
converts any colonist whose `Certainty` reaches zero, and certainty decays on
`ConversionTuning.CertaintyPerDayByMoodCurve` [V]. A visiting Church preacher can walk a
founder through the one-way door by accident. Vanilla *does* announce it —
`LetterLabelConvertIdeoAttempt_Success` [V] — so it is loud, but the **resulting state is
identical to the deliberate act**, and no campaign gate may read it as consent.

Three fields on the religion `WorldComponent` (§ *The build — Reverence* §1's component;
if that component is ever split, these follow religion state):

| Field | Purpose |
|---|---|
| `Ideo committedIdeo` | `Scribe_References.Look` — `Ideo` is `ILoadReferenceable`, `GetUniqueLoadID() => "Ideo_" + id` [V] |
| `int commitmentTick` | when the rite completed; `-1` means never |
| `List<Pawn> committedFounders` | `Scribe_References.Look`, `LookMode.Reference` |

**The ideology itself needs no new persistence at all.** `Pawn_IdeoTracker.ideo` and
`FactionIdeosTracker.primaryIdeo` are both already `Scribe_References.Look` [V]. Adding the
three fields to a save that predates them is a no-op: they read as null, `-1` and empty,
which is the correct "not committed" state, on the backfill path already verified in
§ *The build — Reverence* §2.

### 3. What changes it — the rite, and one thing vanilla will undo behind you

The rite is the only writer.

⚠ **Do not also call `FactionIdeosTracker.SetPrimary` to force the promotion.** It is a bare
field write with no guard [V], and on the *player* faction the value is recomputed by
`RecalculateIdeosBasedOnPlayerPawns` on the next colonist gain, loss, death or conversion —
so a forced primary with fewer believers than the standing plurality is silently overwritten.
On **NPC** factions the same call is durable, because `Notify_MemberGainedOrLost` early-returns
unless `faction.IsPlayer` [V]. Vanilla's own use in `Page_ChooseIdeoPreset.AssignIdeoToPlayer`
is safe only because it runs at worldgen, where the recalculation early-returns on
`Current.ProgramState != ProgramState.Playing` [V].

**This is a design constraint, not a trap, and the distinction was audited.** An earlier draft
proposed it for `docs/TRAPS.md`. It does not qualify: the revert is **not silent**.
`RecalculateIdeosBasedOnPlayerPawns` sends `LetterLabelNewPrimaryIdeo` /
`LetterNewPrimaryIdeo` whenever it promotes an ideo that differs from the standing
`primaryIdeo` [V] — and a forced primary being overwritten by the standing plurality is exactly
that case, so the overwrite announces itself in a letter. It fails the register's silent-failure
bar and no ID is allocated. The behaviour stays documented **here**, because it still forbids a
call the build would otherwise be tempted to make.

⚠ **The plurality gate is real, and it is the design's price rather than a defect.**
The promotion test is `num > tmpPlayerIdeos.TryGetValue(primaryIdeo, 0)` — **strictly
greater** free-colonist believer count [V]. Two founders in a two-pawn colony flip the
primary; two founders in a ten-colonist colony do not.
[`ENDING.md`](../plot/ENDING.md) § *The Alignment Rule* already states that the Church route
costs the player their own religion, and the plurality gate is that sentence expressed as
arithmetic. **Do not engineer around it.**

### 4. The roles — and the requirement is wrong twice

> **Superseded selection.** These roles belong to the **player faith**, not the Church.
> The required shape is one or two founder-specific seats, several multi-holder
> preacher/converter seats for core disciples, at least one production specialist, and
> campaign-time role unlocks. The role mechanics collected below are inputs to the new
> capability ticket [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114); the
> single-leader/single-preacher build is not selected.

[`docs/requirements/RELIGION.md`](../requirements/RELIGION.md) asserts *"the two founding
pawns are mechanically forced into the ideology's defining leader/preacher roles."*
Neither half holds as written.

**A. The preacher role cannot activate in a two-founder colony.** Vanilla's moral guide,
`IdeoRole_Moralist`, inherits `activationBelieverCount: 3` / `deactivationBelieverCount: 1`
from the abstract `PreceptRoleSingleBase` in
`common/RimWorld/Data/Ideology/Defs/PreceptDefs/Precepts_Role.xml` [V].
`Precept_RoleSingle.RecacheActivity` gates on
`colonistBelieverCountCached >= def.activationBelieverCount || def.leaderRole`, and
`Ideo.RecacheColonistBelieverCount` counts **free colonists only**, excluding slaves, quest
lodgers **and pawns in cryptosleep** [V] — the last of which matters for a campaign that will
put founders under for a transit. There is **no primary-ideo escape hatch**: three lines away in the same
class, `Ideo.ObligationsActive` *does* have one (`return Faction.OfPlayer.ideos.IsPrimary(this);`)
[V], and the role path deliberately does not. With two believers the preacher role is
inactive, and if assigned it is unassigned on the next recache.

The leader role is fine. `IdeoRole_Leader` carries `leaderRole: true`, which short-circuits
the count on **both** the activation and the deactivation branch [V]. `Precept_RoleSingle.Assign`
additionally sets `Faction.OfPlayer.leader = p` and unassigns every other leader role across
`Faction.OfPlayer.ideos.AllIdeos` [V] — so seating a founder as the Church ideology's leader
also makes them the colony's diplomatic face, for free.

**Fix: ship our own two `PreceptDef`s** with `activationBelieverCount: 1`. **Do not
`PatchOperation` vanilla's `IdeoRole_Moralist`** — it is the moral guide for every ideology in
the game, NPC ones included.

⚠ **And the two roles do not take the same class.** The leader precept is
`ParentName="PreceptRoleSingleBase"`: one shared player faction has exactly one
`Faction.OfPlayer.leader`, `leaderRole: true` is what sets it, and one holder is the right
answer. **The preacher precept is `Precept_RoleMulti`**, and this reverses an earlier draft.
Under one shared player faction (`docs/engine/determinism.md` § *Presentational separation*) there are two colonies; a `Precept_RoleSingle` preacher
seats exactly one founder and leaves the other colony without one, permanently.
`Precept_RoleMulti.Assign` is uncapped [V], which is the whole reason closed #10 recommended
authoring our own role precepts as `RoleMulti` in the first place — a recommendation this
document previously recorded as *falsified*, and then built against its opposite.

**A `RoleMulti` preacher has no activation gate** [V, [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114)].
`Precept_RoleMulti.Init` sets `active = true` and `RecacheActivity` never reads
`activationBelieverCount`; the field on a `RoleMulti` def is inert and misleads the tooltip, so
leave it unset.

**B. "Forced" has no vanilla mechanism, but it has a cheap XML-shaped one.**
`Precept_Role.Assign` is a free player action from the ideo UI and nothing pins a pawn.
`RimWorld.RoleRequirement` is a **four**-member abstract — an earlier draft said three — with
`abstract bool Met(Pawn p, Precept_Role role)` and a `virtual GetLabel(Precept_Role)` [V, #114], selected per role in XML as
`<li Class="…">` [V].
`VanillaMemesExpanded` ships five subclasses of it in its 1.6 assembly —
`RoleRequirement_BestCrafter`, `_BestPsycaster`, `_HighestTitle`, `_NoTitles`,
`_BestFighter` [V] — so it is a live 1.6 extension point; `RoleRequirement_BestCrafter.Met`
is eight lines.

One `RoleRequirement_Founder` makes the founders the **only eligible pawns**, and the rite
seats them. That is the honest reading of "forced": the player may leave the seat empty but
cannot give it to anyone else.

> **Rejected: a Harmony prefix on `Precept_RoleSingle.Assign` refusing `null`.** It makes a
> visible UI button silently do nothing, which is precisely what `CODING_STANDARDS.md`
> § *Silent failures* exists to prevent.

**Founder identity is an open parameter, not a blank — and it now has a carrier.**
[`TRANSCENDENCE.md`](TRANSCENDENCE.md) § *The store* rule 1 makes `CompFounderRecord`, on the
`Archinity_FounderRecord` hediff, **the** store for founder state, and forbids a second one;
[`ALTAR.md`](ALTAR.md) already extends that comp with a field of its own. So
`RoleRequirement_Founder.Met` should read `CompFounderRecord` — one `TryGetComp` on a comp that
already travels with the pawn, is already scribed and is already MP-serialisable — rather than
introducing a private `GeneDef` / `XenotypeDef` predicate here. **This document does not edit
either of those specs and claims nothing in them**; it states where the answer lives.

Archinity expresses founder-ness genetically today —
`Archinity.Altar/Defs/GenePoolDefs/GenePool_Archite.xml`'s `<founderOnlyGenes>` is `Deathless`
and `Ageless`, and the founders are the `Archinity_ArchonianSanguophage` xenotype in
`Archinity.Origins/Defs/XenotypeDefs/Xenotypes_Archinity.xml`. That is an implementation
accident standing in for a requirement. **Which predicate defines a founder is still a
requirement and no open ticket owns it** — *Outstanding decisions* 13; what has changed is that
the mechanism no longer has to wait on it, because the comp is the carrier whatever the
predicate turns out to be.

⚠ **A ritual role may gate on any `PreceptDef`, and an earlier draft of this section turned
vanilla's habit into an engine constraint.**

What vanilla *does* is narrow, and that part holds: the only role precepts any shipped ritual
behaviour references are `IdeoRole_Moralist` and `IdeoRole_Leader`, and both derive from
`PreceptRoleSingleBase` [V]. The count was wrong — **`<precept>` appears 11 times** in
`Ideology/Defs/Rituals/Ritual_Behaviors.xml`, five naming `IdeoRole_Moralist` and six naming
`IdeoRole_Leader` [V], not the "exactly twice" an earlier draft asserted and marked [V]. The
roster of two is right; the count of two was a miscount.

**What vanilla does is not what the engine allows.** `RitualRole.precept` is a bare
`PreceptDef` field, and `AppliesToRole` tests `p.Ideo.GetRole(p).def == precept` [V]. Nothing
on that path restricts the precept to `Precept_RoleSingle`, so a ritual role gating on a
`Precept_RoleMulti` we author is ordinary, not exotic. Vanilla's choice of two single-holder
roles is content, not a rule we inherit.

**So the final altar rite inherits neither the single-holder constraint nor §4A's three-believer
threshold.** (The Exaltation rite is now vanilla's bestowing ceremony — § *The build — Exaltation*
§4. Its participants are the quest's bestower and title-holder, not role precepts, so neither
constraint reaches it either [I].) The altar rite inherits whatever our own role precepts say — which, for the preacher rung, is `Precept_RoleMulti` with
`activationBelieverCount: 1` (§4A). Wherever this document previously propagated the
single-holder constraint to those rites, it was importing a claim that had already been
withdrawn; see § *Status* → *The commitment*.

### 5. Where the player sees it — almost entirely vanilla's

| Surface | Source | Evidence |
|---|---|---|
| "Your colony's primary ideoligion is now X" | `RecalculateIdeosBasedOnPlayerPawns` → `LetterLabelNewPrimaryIdeo` | [V] — free |
| "X is now the Y", with a sound, per role seated | `Precept_Role.Notify_PawnAssigned` → `Messages.Message("MessageRoleAssigned"…)` + `SoundDefOf.Quest_Succeded` | [V] — free |
| The colony's ideoligions, precepts and role slots with their holders | `MainTabWindow_Ideos` / `IdeoUIUtility` | [V] — free |
| The founder's ideo plate on the character card | `CharacterCardUtility.DoTopStack` | [V] — free. MP's `CharacterCardUtilityDontDrawIdeoPlate` suppresses it **only** when `Multiplayer.Client != null && generating`, i.e. on the pawn-config page, never in play [V] |
| The rite's outcome letter | our worker, on `RitualOutcomeEffectWorker_RoleChange`'s shape — it composes the outcome letter, then calls `Unassign`/`Assign` on a good result [V] | [V] on the donor |
| The door *before* it is walked through | the Church quest chain, or the `FactionDialogMaker` gate already specified for Reverence (D2) | — |

**This capability needs nothing from [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61).**
Every readout above is a vanilla surface we do not patch, which is the opposite of Reverence's
position and worth saying plainly.

### 6. The alternative build, and the one line of vanilla that separates them

`RimWorld.IdeoDevelopmentUtility.ApplyChangesToIdeo(Ideo ideo, Ideo newIdeo)` is **public
static** and overwrites `ideo` **in place** from `newIdeo` — foundation, culture, memes, the
whole precept list rebuilt through `PreceptMaker.MakePrecept` + `Precept.CopyTo`, plus `name`,
`memberName`, `leaderTitleMale`/`Female`, icon, colour and styles [V]. It preserves the `Ideo`
**instance**, so every scribed reference on every pawn and faction stays valid, and it has no
`Fluid` check of its own — `Fluid` gates `Dialog_ReformIdeo`, not the utility. *(Archive note: contradicted by `docs/engine/ideology.md` § *Role precepts: what the two classes hold, and how a role enters a live ideology* — a non-fluid target throws before anything is mutated.)*
`Multiplayer.Client.SyncMethods` already registers it with `.ExposeParameter(1)`, serialising
the entire replacement ideology across the wire [V].

That is a second, near-zero-code route: the colony's own ideology *becomes* the Church's
doctrine with no pawn changing `Ideo` reference.

**What separates the two is one line.** `RoleRequirement_SameIdeo.Met` is `p.Ideo == role.ideo`
— **reference equality** [V]. Under `SetIdeo` the founders and the Church's NPC believers
share one `Ideo` object and any "aligned" test is free. Under `ApplyChangesToIdeo` they hold
two doctrinally identical but distinct objects, and the Devotion alignment rule then needs a
doctrinal comparison nobody has specified.

**Selected: nothing.** § *Status* says nothing in this document is an implementation
commitment, and this section must say the same thing (`README.md` § *Verified is not
selected*). An earlier draft wrote "Selected: `SetIdeo`" three screens below a Status section
that contradicted it.

**The build above is written against `SetIdeo`, and these are the reasons it is:** it is what
[`ENDING.md`](../plot/ENDING.md) literally asks (*"become what the Church says they are"*), it
makes Devotion alignment reference equality, it is what Multiplayer's own `FactionCreator`
does mid-game, and it is what vanilla preachers already do to colonists.
`ApplyChangesToIdeo` is the recorded alternative, taken **if**
[#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) rules alignment doctrinal —
*Outstanding decisions* 12. The commitment between the two is #49's to make, not this
document's.

⚠ **The selected route moves Reverence's referent.**
`docs/requirements/RELIGION.md` says *"Reverence is tied to the player's actual ideology."*
After the rite the player's primary ideology **is** the Church's, which the Church faction
already follows completely — so a naive reading pins Church Reverence to its ceiling the
instant the rite completes. Owner: [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97),
whose existing question ("per (faction × ideo), or per faction against the player's current
primary") is the same question. *Outstanding decisions* 14.

**And the pin does not stay inside this document.** [`PRESSURE.md`](PRESSURE.md) § *The build*
feeds **global Reverence** into the global threat scalar as one bounded contributor, and again
into the `StorytellerComp.IncidentChanceFinal` selection weight — it names the Reverence term
but not this event. So if the rite pins Church Reverence to its ceiling, it also moves raid
magnitude and incident selection on the tick the rite completes, campaign-wide. That seam is
named here so it is visible from this side; the direction and size of the response are
[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)'s, and what the pin itself should
be is #97's.

### Cost

| Piece | Cost |
|---|---|
| The consecration rite | **New C#** — one `RitualOutcomeEffectWorker`, ~40 lines, plus the `RitualPatternDef` / `RitualBehaviorDef` / `RitualOutcomeEffectDef` trio in XML |
| Founder-only role eligibility | **New C#** — one `RoleRequirement` subclass, ~10 lines, reading `CompFounderRecord` ([`TRANSCENDENCE.md`](TRANSCENDENCE.md)) rather than a predicate of its own |
| The founders' leader role | **XML** — one `PreceptDef`, `ParentName="PreceptRoleSingleBase"`, `leaderRole: true`, `activationBelieverCount: 1` |
| The founders' preacher role | **XML** — one `PreceptDef` on `Precept_RoleMulti`, so both colonies get a holder under one shared faction (§4A). No activation fields: a `RoleMulti` has no believer gate [V, #114] |
| Commitment record | **New C#** — 3 fields and 3 `Scribe_*` lines on the religion `WorldComponent` |
| The Church's doctrine | **XML** — `FactionDef.fixedIdeo` and companions, no code |
| Announcement, role messages, ideo tab, character card | **Nothing** |
| Multiplayer | **Nothing** — the rite is inside simulation and `Precept_Ritual.ShowRitualBeginWindow` is already registered [V] |
| The alignment predicate | **[#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)** — a requirement, not a mechanism |

**Aggregate: ~55 lines of C# in the existing `ArchinityAltar.dll`, two `PreceptDef`s and one
ritual def trio. No new saved collection, no new Def type, no Harmony patch.** This is
cheaper than Exaltation, and for the same reason: we are not building a system, we are
invoking one the DLC already ships.

## Persistence and multiplayer — the commitment


- **The whole capability costs nothing in multiplayer, and the reason is structural.** The
  rite is a `LordJob_Ritual`; its outcome worker runs inside the synced tick on both clients,
  on the same reasoning the Exaltation rite inherits above. The one player-initiated act —
  opening the ritual window — is already covered:
  `Multiplayer.Client.SyncMethods` registers
  `SyncMethod.Register(typeof(Precept_Ritual), "ShowRitualBeginWindow")` [V]. **No
  `[SyncMethod]` of ours and no `Multiplayer.API` reference is needed for this capability**,
  unlike [`CURRENCIES.md`](CURRENCIES.md)'s `TryPurchase`.
- ⚠ **`Pawn_IdeoTracker.SetIdeo` draws `Rand`** —
  `Certainty = Mathf.Clamp01(ConversionTuning.InitialCertaintyRange.RandomInRange)` [V].
  Inside the ritual outcome that is safe by the standing rule
  ([`determinism.md`](../engine/determinism.md) § *Why `Rand` inside a synced tick is safe*),
  because both clients call it the same number of times in the same order. It would **not**
  be safe from a gizmo or a `DiaOption` action, and that is the reason the rite is a rite
  rather than a button.
- **Multiplayer already brackets the recalculation this build depends on.**
  `Multiplayer.Client.Factions.RecalculateFactionIdeosContext` is a Harmony prefix/finalizer on
  `FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` that pushes and pops
  `FactionContext` around it [V] — noted for Reverence above as a contingency, and load-bearing
  here.
- ⚠ **If the alternative route (§6) is ever taken, both ideos must be `Fluid`.**
  `Multiplayer.Client.SyncMethods.FixIdeoAfterCopy` is `[MpPostfix(typeof(Ideo), "CopyTo")]`
  and ends with `ideo.development.ideo = ideo; ideo.style.ideo = ideo;` with **no null check**
  [V]. `Ideo.development` is non-null only for a fluid ideo — `Ideo.Fluid`'s setter,
  `ExposeData`'s `if (fluid && development == null)`, and `CopyTo`'s own `if (ideo.fluid)`
  branch are its only writers, and the field has no initialiser [V]. Vanilla never reaches it
  because `Dialog_ReformIdeo` is only open for a fluid ideo. Calling `ApplyChangesToIdeo` on a
  non-fluid ideo throws a `NullReferenceException` on `ideo.development.Notify_PreReform`
  **before** `CopyTo`, with nothing mutated, identically on every client [V, #114]; `FixIdeoAfterCopy`
  needs a `CopyTo` target with null `development` inside a command, which `ApplyChangesToIdeo` on
  a fluid ideo does not produce. The rule stands: never on a non-fluid ideo.
- **`Page_ChooseIdeoPreset` is not the one-way door, and the ticket's "assume host-only" was
  the wrong premise** [V]. Under Multiplayer the page is not host-only: MP wraps it in
  `Multiplayer.Client.Factions.Page_ChooseIdeo_Multifaction`, shown to a player *creating* a
  faction, whose result is a `Multiplayer.Client.Factions.IdeologyData : ISyncSimple` record
  carried into `[SyncMethod] FactionCreator.CreateFaction`. But Archinity runs one shared
  player faction (`docs/engine/determinism.md` § *Presentational separation*), and joining an existing faction runs through
  `Multiplayer.Client.Factions.FactionsWindow` → `ClientSetFactionPacket` with no ideo page
  anywhere on the path [V]. The page runs once, on the host, at worldgen — before anyone
  joins, and the campaign ships a `.rid` for that anyway. The real door is the rite, which is
  inside simulation and therefore symmetric by construction.
- **One shared player faction means one commitment.** The record is world-scoped and both
  players see the same founders in the same roles (`docs/engine/determinism.md` § *Presentational separation*). **That is also why the preacher
  precept is `Precept_RoleMulti` and the leader precept is not** (§4A): under one faction a
  `RoleSingle` seat is one seat for two colonies, so the preacher rung would be permanently
  held by one founder and permanently empty for the other, while one leader is the correct
  answer because there is one `Faction.OfPlayer.leader` to set.

## Failure and recovery — the commitment


- ⚠ **A founder can be converted to the Church's ideology by accident, and the resulting state
  is indistinguishable from the rite's.** `InteractionWorker_ConvertIdeoAttempt` on a visiting
  Church preacher converts any colonist whose `Certainty` reaches zero [V]. Vanilla announces
  it with `LetterLabelConvertIdeoAttempt_Success`, so it is loud — but the campaign must gate
  on `commitmentTick`, never on `founder.Ideo`. **This is the entire reason §2 stores anything.**
  An acceptance check that reads the ideo reference will pass on an accident.
- ⚠ **A forced primary reverts — loudly, which is why it is not a trap.**
  `FactionIdeosTracker.SetPrimary` on the player faction is undone by the next
  `RecalculateIdeosBasedOnPlayerPawns` (§3). An earlier draft claimed the revert is silent and
  proposed it for the register; that is wrong. The recalculation sends
  `LetterLabelNewPrimaryIdeo` / `LetterNewPrimaryIdeo` whenever the promoted ideo differs from
  the standing `primaryIdeo` [V], and the revert case is precisely a promotion **over** a
  different primary — so the player gets a letter announcing the ideology they did not choose.
  No trap ID is allocated. The recovery-relevant point survives: **do not call `SetPrimary` on
  the player faction at all**; let the believer counts do the promotion.
- **A single-holder role fails quiet in the direction that matters — `Precept_RoleMulti` cannot**
  [V, [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114)]. Below
  `activationBelieverCount`, `Precept_RoleSingle.RecacheActivity` deactivates the role and
  nulls its holder. It *does* send `LetterLabelRoleLost` / `LetterLabelRoleInactive` when the
  player faction holds the ideo — but a role that has **never** activated sends nothing at all,
  because the deactivation branch requires `active` to have been true. A non-leader `RoleSingle`
  with activation ≤ deactivation instead flaps off and on every world tick (loud). The preacher,
  a `RoleMulti`, is always active (§4A).
- **Losing a founder unseats them, and vanilla handles it.**
  `Precept_RoleSingle.Notify_MemberChangedFaction` calls `Assign(null, addThoughts: false)`
  when the holder leaves the player faction, and `RecacheActivity` nulls the holder whenever
  `ValidatePawn` fails — dead, destroyed, no longer a free non-slave colonist, or no longer
  meeting a `RoleRequirement` [V]. `committedFounders` keeps the historical record; the seat
  does not.
- **The commitment record tolerates dangling references.** `committedIdeo` can resolve to null if the ideology is ever removed. `IdeoManager.Remove` is reachable through `TryQueueIdeoRemoval` when no faction lists it and **no pawn on a map** holds it. World pawns and caravan members do not count, and removal then moves every holder anywhere to its faction's primary (§ *An NPC faction's faith changes* § *Constraints*) [V] — and a dead founder's
  `Pawn` reference can resolve to null. Both read as "no commitment on record", which is the
  wrong answer for a campaign gate; the component must treat a non-null `commitmentTick` as
  authoritative and the references as decoration.
- ⚠ **Setting `awardWorkerClass`-style shortcuts has an analogue here: never give the founders'
  role precepts vanilla's `IdeoRole_Moralist` or `IdeoRole_Leader` `defName`s, and never patch
  vanilla's.** Both are conferred on *every* ideology in the game, NPC factions included, and a
  `PatchOperation` on them changes the moral guide for the whole planet with no error (§4A).

## Status — the commitment


Established by
[Mid-game ideology commitment for the founders](https://github.com/cjd721/Rimworld-Archinity/issues/75),
evidence class **READ** — vanilla `Assembly-CSharp.dll`, the Ideology DLC's shipped defs under
`common/RimWorld/Data/Ideology/Defs/`, `Multiplayer.dll`
(`2606448745/1.6/AssembliesCustom/`) and `VanillaMemesExpanded.dll`
(`2636329500/1.6/Assemblies/`), all decompiled with `ilspycmd` at the versions pinned in
`docs/data/MOD-SNAPSHOT.md`. `corpus.py --check` clean at the start and the end of that session.

**This is the one section of this document whose headline is a positive.** The mechanisms are
[V]; the claim that a rite composing three public calls delivers the campaign's commitment is
[I], as every build is until something is built. The untried part is small: `SetIdeo` onto an
NPC faction's `Ideo` from inside a ritual outcome worker, which is a combination of two things
each of which vanilla does separately.

**Three claims this ticket inherited were re-derived. One is half wrong, one holds — and the
third was never the claim this document said it was:**

| Inherited claim | Verdict |
|---|---|
| Closed #8 — *"`Faction.ideos` is generated once from the worldgen def and never regenerated"* | ⚠ **Half false, and the halves must be kept apart.** The player faction's **`primaryIdeo` pointer** is recomputed from live free-colonist believer counts on every member gain, loss and conversion [V] — so "never regenerated" is wrong about *which* `Ideo` the faction points at, and that is the half this capability runs on. But #8's actual claim was about **doctrine**: that a later def's `fixedIdeo` / `forcedMemes` never re-apply to a faction that already exists. **That half stands** — the doctrine is built once on the `CreateFactionAndAddToManager` → `ChooseOrGenerateIdeo` → `MakeFixedIdeo` path and nothing re-runs it on a live faction [V]. A recomputed pointer is not a regenerated ideology, and this document previously reported #8 as flatly false without that qualifier. |
| *"Forcing a specific ideology is not possible in XML; `FactionDef.fixedIdeo` / `ideoName` / `forcedMemes` are NPC-only"* | ✅ **Confirmed [V]** — `Page_ChooseIdeoPreset.PostOpen` applies them inside `if (allFaction != Faction.OfPlayer && …)`. |

⚠ **Withdrawn: the "#10 claimed role-gated rites use `Precept_RoleMulti`" falsification.** #10
made no such claim, so there was nothing to falsify and the row asserting it has been removed.
What #10 actually said was that **we should author our own role precepts as `Precept_RoleMulti`**,
so that under one shared player faction each of the two colonies gets a holder, and that
`Precept_RoleMulti.Assign` is uncapped. **Both are true** [V]. The damage was downstream: having
recorded #10 as falsified, this document then reimported the **single-holder constraint** as
fact and propagated it to the Exaltation and altar rites. That constraint is deleted (§4), the
preacher precept is `RoleMulti` (§4A), and `RitualRole.precept` accepts any `PreceptDef`
regardless (§4).

**And one framing premise was wrong:** the ticket's *"Assume host-only"* for
`Page_ChooseIdeoPreset`. See *Persistence and multiplayer* § *The commitment*.

## Available mechanisms — the commitment


| Mechanism | What it gives the commitment | Evidence |
|---|---|---|
| `Pawn_IdeoTracker.SetIdeo(Ideo)` | public; accepts **any** `Ideo` with no `IdeoManager` membership check of its own (registration is the caller's job) and one early-return, on babies; handles beds, bonds, thoughts, needs, apparel, abilities and the `ChangedIdeo` history event | [V] |
| `FactionIdeosTracker.RecalculateIdeosBasedOnPlayerPawns` | promotes the player faction's primary from live free-colonist counts, on every member gain/loss and every colonist ideo change, with a vanilla letter | [V] |
| `FactionIdeosTracker.Notify_ColonistChangedIdeo` / `Notify_MemberGainedOrLost` | the two entry points; the latter early-returns unless `faction.IsPlayer` | [V] |
| `FactionDef.fixedIdeo` + `ideoName` + `forcedMemes` + `requiredMemes` + `deityPresets` + `styles` → `FactionGenerator.CreateFactionAndAddToManager` → `IdeoGenerator.MakeFixedIdeo` | the Church's authored doctrine, pure XML, NPC-only and therefore ours to use | [V] |
| `InteractionWorker_ConvertIdeoAttempt` | proves a colonist holding an NPC faction's `Ideo` is an ordinary vanilla state (`NPC_Free → Colonist` weight 0.5) | [V] |
| `Precept_Role.Assign(Pawn, bool)` / `Unassign` / `RequirementsMet` / `ValidatePawn` | seating a pawn in a role, with vanilla's own message, sound and side effects; `leaderRole` also sets `Faction.OfPlayer.leader` | [V] |
| `RimWorld.RoleRequirement` — abstract, one `Met(Pawn, Precept_Role)` override, XML-selected per role | founder-only eligibility as data plus ten lines | [V] |
| `RitualOutcomeEffectWorker_RoleChange` | the shipped shape for "a rite seats a pawn in a role": compose the outcome letter, then `Unassign`/`Assign` on a good result | [V] |
| `Precept_Ritual.ShowRitualBeginWindow`, registered in `Multiplayer.Client.SyncMethods` | the only player-initiated act, already synced | [V] |
| `IdeoDevelopmentUtility.ApplyChangesToIdeo(Ideo, Ideo)` — public static, in-place, no `Fluid` check, already MP-synced with `.ExposeParameter(1)` | the alternative build (§6): wholesale doctrine replacement preserving the `Ideo` instance and every reference to it | [V] |
| `Multiplayer.Client.Factions.FactionCreator.CreateFaction` | the shipped proof that `GenerateIdeo` → `IdeoManager.Add` → `SetPrimary` → `SetIdeo` runs correctly **mid-game inside a synced command** | [V] |
| `VanillaMemesExpanded.RoleRequirement_BestCrafter` and four siblings | the shipped 1.6 precedent that a custom `RoleRequirement` works | [V] |

**What does not exist, and where it shaped the build:**

- **No lock on a role.** Nothing in vanilla pins a pawn to a `Precept_Role`; `Assign` is a free
  UI action. Hence the eligibility-narrowing approach in §4B rather than a refusal patch.
- **No primary-ideo exemption for role activation.** `Ideo.ObligationsActive` has one and
  `Precept_RoleSingle.RecacheActivity` does not [V]. Hence our own `PreceptDef`s rather than
  vanilla's.
- **No public installer.** `Page_ChooseIdeoPreset.AssignIdeoToPlayer` — the three lines that set
  the primary, clear every other `Ideo.initialPlayerIdeo` and add to the manager — is `private`
  [V]. Trivially reimplemented; recorded because it looks callable.
- **Nothing in the corpus carries a mid-game commitment mechanism**, and nothing needs to. A wide
  pass over both roots plus `common/RimWorld/Data/`, ASCII and null-interleaved UTF-16,
  `-g '*.dll' -g '!**/obj/**'`, returned: `SetIdeo` → VFE Medieval 2 only; `RoleRequirement_` →
  VIE Memes and Structures only; `Precept_RoleSingle` → VIE M&S and RimPacts; `ApplyChangesToIdeo`
  → Multiplayer only; `Precept_RoleMulti`, `ChosenPawnValue` and `Dialog_ReformIdeo` → nothing.
  The sweep was validated first: `ApplyChangesToIdeo` returns zero ASCII hits and hits
  `Multiplayer.dll` in UTF-16, the correct signature for a name existing only as a
  `SyncMethod.Register` string literal. **The `--encoding utf-16le` form
  ([#103](https://github.com/cjd721/Rimworld-Archinity/issues/103)) was not used.**

## Verification — the commitment


READ-class throughout, from decompiled 1.6 assemblies and the Ideology DLC's shipped XML at
the pinned versions. The headline is a **positive**, so by
`docs/agents/capability-research.md`'s asymmetry the wide pass was owed only for the two
negative sub-claims — that nothing locks a pawn into a role, and that no mod carries a
commitment mechanism — and it was run in both encodings and validated against a control
before either negative was trusted (*Available mechanisms*).

**What still needs the game: one observation, and it is narrow.** It belongs to the two-client
regime on [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16):

> The commitment rite completing produces the **same** `Faction.OfPlayer.ideos.PrimaryIdeo`,
> the same seated role-holders and the same `LetterLabelNewPrimaryIdeo` on both clients on the
> same tick.

That is the one place `SetIdeo`'s `Rand` draw could diverge — if the rite's participant set
were ever resolved client-side rather than from the `LordJob_Ritual`'s assignments.

A cheaper **STUB**-class confirmation of §4A is available first and does not need two clients:
ship the leader `PreceptDef` on `PreceptRoleSingleBase` with `activationBelieverCount: 1` and a
`deactivationBelieverCount` below it, start a two-colonist game, and check that the role is
assignable. With vanilla's value it will not be, and nothing will say why. The preacher half is
settled by reading: `Precept_RoleMulti` has no believer gate [V, [#114](https://github.com/cjd721/Rimworld-Archinity/issues/114)].

**Residual gap, stated:** a mod expressing a commitment as a chain of existing def types — a
`QuestScriptDef` chain reaching `SetIdeo` through a generically named quest part — would be
invisible to a name sweep. Bounded but not excluded; it would not be a better donor than
`Pawn_IdeoTracker.SetIdeo` itself.

## Outstanding decisions — the commitment

12. **Is Devotion alignment reference equality on `Ideo`, or doctrinal equivalence?** This is
    the single question that chooses between §1's build and §6's alternative, and it changes
    nothing else. Owner: [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) — its
    body already claims *"what the founders' commitment to the Church must mean, what it must
    gate, and what it must never measure."* The build assumes reference equality, which is the
    cheaper and more literal reading of [`ENDING.md`](../plot/ENDING.md).
14. **What Reverence measures after the commitment.** The player's primary ideology becomes the
    Church's, which the Church faction already follows completely. Owner:
    [#97](https://github.com/cjd721/Rimworld-Archinity/issues/97) — it is the same question as
    that ticket's existing "per (faction × ideo), or per faction against the player's current
    primary", now with a concrete campaign event that forces it.
16. **Is the commitment reversible, and at what price?** Mechanically it is trivially
    reversible — a second rite calling `SetIdeo` back, or enough colonists converting away —
    and `Pawn_IdeoTracker.previousIdeos` already records the founder's prior ideologies [V].
    Whether the campaign *permits* it is a requirement, and neither
    `docs/requirements/RELIGION.md` nor [`ENDING.md`](../plot/ENDING.md) says. **Gap, no owner.**
    This is the same unowned-numbers gap as decisions 4 and 8 and probably belongs in the same
    ticket.

Decisions 13 (the founder predicate) and 15 (player-faith roles) stayed live in `RELIGION.md`.
