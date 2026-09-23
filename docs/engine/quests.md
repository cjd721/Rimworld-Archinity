# Quests

What the vanilla quest system can be made to do from XML: fixed rewards, standing
parent quests with sub-quests, what the quest tab will and will not show, the
two mods that already ship a player-initiated quest generator, and Royalty's decrees.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Gating a quest by tech

`QuestScriptDef` has no `minTechLevel` (see `docs/TRAPS.md` T-16); the available
gates are `rootMinPoints`, `rootMinProgressScore`, `rootEarliestDay`,
`rootSelectionWeight`, `isRootSpecial` and `randomlySelectable`. VEF's
`QuestChainExtension.requiredResearch` is the mechanism that gates a quest on
research instead — see `docs/engine/research-and-tech-tiers.md` for that
extension and the theory defs it keys on.

---

## The `Quest.`-prefixed global signal is the only way XML can hear a world event

Two independent halves compose into one bridge [V on both halves, **[I]** on the
composition]:

- `QuestGenUtility.HardcodedSignalWithQuestID` returns a signal string **verbatim**
  when it starts with `Quest` and contains a `.`; every other form is stamped
  `Quest{id}.` and is therefore private to one quest instance.
- `Quest.Notify_SignalReceived` accepts any signal whose `global` flag is set,
  whatever its prefix, and drops any non-`global` tag that does not start with the
  quest's own prefix.

So a signal broadcast as `new Signal("Quest.SomethingHappened", args, global: true)`
is the **one shape** an arbitrary `QuestScriptDef` can put in an `<inSignal>` and
actually receive. That is the general bridge from a Harmony-observed act to XML, and
it is also why **cross-quest exclusion is structurally impossible in pure XML**: quest
A cannot hear quest B, because every in-quest signal is `Quest{id}.`-namespaced.
`signalListenMode` still gates the receiving part.

**Vanilla ships exactly four global signal names** — `MonolithLevelChanged`,
`EntityDiscovered`, `ThingStudied`, `ResearchCompleted` — and reaches them only
through bespoke C# nodes.

### `QuestScriptDef.CanRun` has 16 non-debug vanilla callers

Not two, as an earlier draft claimed. The useful fact is not the count: it is that
**VEF's quest-chain path is not among them**. A chain-granted quest runs `root.Run()`
without `TestRun`, so every XML gate living in a `TestRunInt` is inert on that path.
That is `docs/TRAPS.md` **T-71**.

**VEF's *quest-giver* path is the opposite of its chain path.** `VEF.Storyteller.QuestWorker.GenerateQuests` calls `val.CanRun(slate, Find.World)` before `QuestGen.Generate` **[V]**, so `TestRunInt` gates **are live** on a purchasable-catalogue offer and dead on a chain grant (**T-71**). The draw is `GenCollection.RandomElement` over `onlySpecifiedQuests`, removing each pick, so a script appears at most once per pass and list order means nothing. Sequencing can only come from gates. No shipped node reads quest history: VEF's `QuestNode` types are `QuestNode_ForceMusic`, `QuestNode_GetFaction` and `QuestNode_Site`, and `QuestNode_GetFieldValue` reads only an instance field of an object already on the slate **[V]**. ([#132](https://github.com/cjd721/Rimworld-Archinity/issues/132))

---

## Quest rewards

### Fixed rewards ARE possible in pure XML

**Preferred — shipped precedent.** `Data/Royalty/.../Script_Intro_Deserter.xml:90-96`:

```xml
<li Class="QuestNode_SetItemStashContents">
  <items>
    <li>PsychicAmplifier</li>
    <li>PsychicAmplifier</li>
  </items>
</li>
```

Stocks an item stash at a site the player must travel to and clear. Threats are
attached to the same site via `Util_Raid` (see the node directly above it in
that file). Reward and danger authored together.

**Alternative — code-verified, no shipped XML usage.** `QuestNode_GenerateThing`
(calls `ThingMaker.MakeThing` directly, bypassing ThingSetMaker filters and
budgets) feeding `QuestNode_AddItemsReward`. Delivers by drop pod.

> **Gotcha:** the reward node must be nested inside a signal node.
> `Reward_Items.GenerateQuestParts` reads `slate.Get<string>("inSignal")`; at top
> level the pods drop on quest *accept* rather than on completion.

There is no `ThingSetMaker_Fixed`. VEF adds no reward nodes.

### Reward choices — who builds them, and how the window resolves them

Verified against RimWorld 1.6.4871 on [#135](https://github.com/cjd721/Rimworld-Archinity/issues/135).

**The data model.** `QuestPart_Choice.choices` is a list of `Choice`, each holding
`List<Reward> rewards` (deep-scribed) and `List<QuestPart> questParts` (by reference). An
option can hold any number of rewards and any quest parts. `Choose(choice)` calls
`Notify_PreCleanup` and `Cleanup` on every unchosen option's parts, unless the chosen
option shares the part, then removes them and the options. `PreQuestAccept` auto-picks
option 0 with a red error if two or more options remain. Nothing in vanilla adds an option
after generation; `Choose` is the only remover. [V]

**Choosing is accepting.** When a quest has a `QuestPart_Choice`,
`MainTabWindow_Quests.DoAcceptButton` shows no Accept button outside dev mode. `DoRewards`
draws one row per option with an "Accept for:" button that runs `Choose(localChoice)` and
then `Quest.Accept`. If the chosen option's parts need an accepter
(`QuestPart_GiveRoyalFavor.giveToAccepter`), a colonist menu picks the pawn first.
Rows with no `StackElements` are skipped (**T-101**). [V]

**Acceptance requirements are quest-wide.** `QuestUtility.CanAcceptQuest` checks every
`QuestPart_RequirementsToAccept` in the quest, including unchosen options' parts, and
`AcceptQuestByInterface` runs that check before `Choose`. A requirement placed inside one
option therefore blocks all of them. [V]

**Who builds a choice.**
- **From XML, with several options:** only `QuestNode_GiveRewards` → `QuestGen_Rewards.GiveRewards`.
  Its variants are random: social-only, favour-only, things-only, with fallbacks. It drops a
  non-item variant whose reward-type set repeats an earlier one. It adds
  `Reward_DevelopmentPoints` to every option under a fluid ideoligion, and a whole
  `Reward_ReimplantXenogerm` option under Biotech. Royal favour needs a titled asker (**T-102**).
  If `giverFaction` is set and `asker` is null, the same gate dereferences `asker.royalty`
  and throws.
- **From XML, with one option:** `QuestNode_AddItemsReward`, `_CampLootReward`, `_AddPawnReward`,
  `_AddPassageOffworldReward`, `_GiveRoyalFavor` (`isSingleReward`),
  `_GiveRoyalFavorAndDevelopmentPoints`, `_PawnsArrive`.
- **From C#:** 24 `QuestNode_Root_*` files build their own through `QuestGen_Misc.RewardChoice`.
- **`RewardsGenerator.DoGenerate` can only produce** `Reward_Items`, `Reward_Pawn`,
  `Reward_Goodwill` and `Reward_RoyalFavor`, through a hardcoded `GenerateReward<T>`. Custom
  types need a patch: VFE Empire (`Patch_GenerateRewards` → `Reward_Honor`) and VFE Classical
  (`SenatorQuests.AddFavorReward` → `Reward_SenatorFavor`) both patch it.
- **XML-reachable mod nodes with hand-built options:** VFED `QuestNode_DeserterRewards`
  (three options, several rewards each, `Reward_Visibility`) and BTG
  `QuestNode_BTG_SmugglersDen_Rewards` (`Reward_CargoClaim`, per-option parts, a conditional
  goodwill option). No generic node lists options from XML.

**Multiplayer.** `Multiplayer.Client.SyncMethods` registers `Quest.Accept` and
`PatchQuestChoices.Choose(part, index)`. The latter is reached by a prefix on the quest window's
`localChoice` closure, so **only the vanilla quest window's choose is synced**. A second player
choosing on the same quest runs `Choose` by index against the list after the first choice has
collapsed it. Index 0 silently takes the first player's option; any other index throws. The
second `Accept` does nothing. [V code; MP's exception handling I]

---

## Quest presentation

Read against **1.6.4871**. Full evidence and file/line citations on
[#12](https://github.com/cjd721/Rimworld-Archinity/issues/12#issuecomment-5588065933).

### A standing parent quest with nested sub-quests is native

`Quest.parent` (`Quest.cs:33`) is Scribe'd, and `MainTabWindow_Quests.cs:262-285` draws
children recursively **indented 10px under their parent**, with "Has subquest" /
"Subquest of" hyperlinks in the detail pane. A quest with `isRootSpecial`, `autoAccept`,
no `expireDaysRange` and no end part stands forever — nothing in `QuestManagerTick` ever
removes a quest. Odyssey's `GravEngine` and Ideology's `RelicHunt` are the two shipped
precedents.

> **Gotcha:** the indent only renders when parent and child are on the **same tab**.
> `ShouldListNow` splits by `QuestState`, so a `NotYetAccepted` child draws flat on
> Available while its `Ongoing` parent sits on Active. Every Odyssey `Gravcore_*` def sets
> `autoAccept true` to avoid this.

`QuestPart_SubquestGenerator` is **abstract**, with no generic XML-drivable concrete
class — all three vanilla subclasses are C# and each is reached only from a bespoke
`QuestNode_Root_*`. Using this costs a subclass plus a root node.

**Multiplayer does not reference quest parentage at all**, and the generator's RNG runs
inside `DoSingleTick`. Under async time a subquest-generator parent is not on
`MultiplayerAsyncQuest`'s map-binding whitelist, so it ticks at world speed.

### The quest tab offers no per-quest icon, colour or tag

`Quest.tags` is never read by the UI. What the row gives you for free is the
challenge-rating stars (unbounded) and, on a generator parent, a `3 / 9` progress
readout. A custom `LetterDef` per quest is authorable in XML.

Any per-player filtering of the quest tab must filter at draw time, never at
list-membership time (see `docs/TRAPS.md` T-21).

### 13 vanilla quests are events wearing the quest carrier

They ship `defaultHidden true` and never appear in the tab — `WandererJoins`,
`RefugeePodCrash`, `PollutionRaid`, `Bossgroup`, `DelayedRewardDropPods` and others. The
quest system is the engine's event scheduler as much as its quest board.

### A quest's sender is often decided at generation, not in the def

`Util_DecideRandomAsker` makes dozens of quests roll for whether they have an asker at
all. `OpportunitySite_ItemStash` carries both an intercepted-comms description and a
faction-leader description; `BuildMonument`'s no-asker branch is commented *"fictionally,
an archotech"*. Any classification of quests by their fiction cannot be read off the def.

---

## A quest shuttle's pawns pass through one virtual method

Verified against RimWorld 1.6.4871 on [#134](https://github.com/cjd721/Rimworld-Archinity/issues/134).

- **`CompShuttle.requiredPawns` names pawns that must board**, and it is XML-reachable through
  `QuestNode_GenerateShuttle.requiredPawns` (`SlateRef<IEnumerable<Pawn>>`, forwarded by
  `Util_TransportShip_Pickup` / `_DropOff`). `IsAllowed` admits them, `AllRequiredThingsLoaded`
  waits for them, and the inspect string lists them as *Required*. `SendLaunchedSignals` emits
  `SentSatisfied` / `SentUnsatisfied`, plus `SentWithExtraColonists` for colonists not on the
  list. **Every shipped XML use names NPCs** (`$asker`, `$lodgers`, `$laborers`). Shuttle nodes
  require Royalty or Ideology (`ModLister.CheckRoyaltyOrIdeology`). [V]
- **`CompShuttle.IsAllowed(Thing)` is `virtual` and is the only admission check.**
  `TransporterUtility.AllSendablePawns` (the load dialog, as `IsRequired || IsAllowed`),
  `CompFloatMenuOptions` / `CompMultiSelectFloatMenuOptions` (via `IsAllowedNow`),
  `FloatMenuOptionProvider_CarryToShuttle`, `FloatMenuOptionProvider_CarryingPawn` and the
  `JobDriver_EnterTransporter` fail condition all go through it. It returns true early for Odyssey
  `playerShuttle` ships. RimPacts postfixes it (`Patch_ShuttleAllowMech`). Multiplayer's synced
  loading session is a `Dialog_LoadTransporters` subclass (`TransporterLoadingProxy`) and reaches
  the same code. [V]
- **Lending takes whoever is aboard.** `QuestPart_LendColonistsToFaction.Enable` lends every
  `IsFreeColonist` in the shuttle's `CompTransporter`, with no filter. Any exclusion must happen at
  loading. [V]

---

## The intel workbench already ships, twice

> Provenance note: this section was verified during the sessions on
> [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) and
> [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) and recorded only in the
> map's fog. Not re-verified at the time of the move — provenance is those sessions.
> The caveat applies to this section only. **The VFE Deserters half is now verified**, on
> [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) against
> `3025493377/1.6/Assemblies/VFED.dll` (`docs/specs/CURRENCIES.md` § *Delivery surfaces for the
> Intel exchange*); the Medieval Overhaul half is still session provenance.

Fog-only material behind *the acquisition ledger*. The archive's parked "intel workbench"
idea — a player-initiated way to turn *"I am blocked"* into an action
(`docs/archive/sys/06-quests.md`) — does not need building.

- **Medieval Overhaul's explorer's workbench** (`MedievalOverhaul.Building_QuestScanner`) is
  a player-built quest generator fuelled by consumable **Torn Notes**, gated on linkable
  facilities, exposing an open `MedievalOverhaul.QuestInformation` extension that any
  `QuestScriptDef` can join.
- **VFE Deserters ships a second**: an intel-priced rolling queue on a comms tab. Its contraband
  shelf also sells **techprints** — `ContrabandManager` registers every `CompProperties_Techprint`
  def as Intel-priced stock (**T-99** covers the other routes they leak through).

## The accept-time gate is one abstract base, with a quest-wide half and a per-pawn half

Verified against RimWorld 1.6.

`RimWorld.QuestPart_RequirementsToAccept` is a twelve-line abstract base — `CanAccept()` returning
an `AcceptanceReport`, `CanPawnAccept(Pawn)`, `ShowInRequirementBox`, `Culprits`. **Twelve vanilla
subclasses**: `Bedroom`, `ColonistWithTitle`, `FactionRelation`, `NoDanger`,
`NoOngoingBestowingCeremony`, `PawnOnColonyMap`, `PlanetLayer`, `PlayerWealth`, `Research`,
`ThingStudied`, `ThingStudied_ArchotechStructures`, `ThroneRoom`. **Four have XML `QuestNode`
wrappers** — `Bedroom`, `ColonistWithTitle`, `PlanetLayer`, `Research`; the last spells its field
`<reserach>`, misspelt identically in the C# and in the two shipped Odyssey defs that use it. [V]

- **Two enforcement points, one per half.** `QuestUtility.CanAcceptQuest(Quest)` enforces the
  quest-wide half. It calls every part's `CanAccept()` and ignores `ShowInRequirementBox`.
  `QuestUtility.CanPawnAcceptQuest(Pawn, Quest)` enforces the per-pawn half. It calls every part's
  `CanPawnAccept(p)` and also requires `IsFreeColonist`, not downed, not suspended and not
  `IsQuestLodger()`. The per-pawn half runs only when some part sets `RequiresAccepter`. Then
  `MainTabWindow_Quests.AcceptQuestByInterface` opens an "Accept with <pawn>" menu of the pawns
  passing it, and calls `Quest.Accept(pawn)`, which stores `Quest.AccepterPawn` (saved as
  `acceptedBy`). `QuestPart.PreventsAutoAccept` defaults to `RequiresAccepter`. Vanilla's two
  accepter parts are `QuestPart_RequirementsToAcceptColonistWithTitle` and
  `QuestPart_GiveRoyalFavor` (`giveToAccepter`). [V]
- **`MainTabWindow_Quests.DoAcceptanceRequirementInfo` is the sole renderer**, and runs only while
  `!EverAccepted && !Historical` — exactly while the offer is pending. Whatever the
  `AcceptanceReport` says is the locked row's text, free.
- ⚠ **`ShowInRequirementBox: false` enforces while rendering nothing.**
  `QuestPart_RequirementsToAcceptPlanetLayer` is vanilla's one deliberate use.
- ⚠ **The Accept button is greyed, not disabled.** `DoAcceptButton` sets `GUI.color = Color.grey`
  plus a warning tooltip; `Widgets.ButtonText` still fires. The refusal is one layer down in
  `AcceptQuestByInterface`. A Harmony patch aimed at the wrong one gives a visually correct,
  functionally open gate.

**Two numeric-threshold subclasses ship**, and they are the donors for any new one:
`QuestPart_RequirementsToAcceptPlayerWealth` (one `float`, a live comparison, the threshold in the
message, a two-line `ExposeData`) and `QuestPart_RequirementsToAcceptColonistWithTitle` (ordinal, on
title seniority).

**Two subclasses gate on a named pawn**, and they are the donors for "this particular colonist".
- `QuestPart_RequirementsToAcceptPawnOnColonyMap` has `public Pawn pawn`. It passes only while
  `pawn.Map.IsPlayerHome`, and its refusal (`QuestPawnNotOnColonyMap`) names and hyperlinks the pawn.
- `QuestPart_RequirementsToAcceptThroneRoom` has `forPawn`.

`NoDanger.mapPawn` only locates a map, and `Bedroom.targetPawns` are the lodgers. Parts stack, so two
`PawnOnColonyMap` parts require both pawns. `QuestNode_Root_BestowingCeremony` uses both named-pawn
gates on the title-holder. VFE Empire 1.6 uses `PawnOnColonyMap` on a colonist in `GrandBall`,
`RoyalParade` and `ArtExhibit`. **Neither has an XML `QuestNode` wrapper, and no mod ships one.**
Slate pawns reach the description for free (`QuestGenUtility.AddSlateVar` →
`GrammarUtility.RulesForPawn`). [V] Established on
[#134](https://github.com/cjd721/Rimworld-Archinity/issues/134).

**XML cannot reach a goodwill number.** `QuestNode_GetFieldValue` is the only generic reflection
reader and takes **fields** (`GetField(name, Instance|Public|NonPublic)`); `Faction.PlayerGoodwill`
is a *property* over a private `List<FactionRelation>`. All 301 `QuestNode_*` types — 70 of them
`QuestNode_Root_*`, 231 non-root — were enumerated: **none reads `PlayerGoodwill`.** The generic
comparison nodes (`QuestNode_Greater` / `_Less` / `_Equal` and their `OrFail` variants) therefore
stop one step short of a standing predicate. [V]

⚠ **`QuestPart_RequirementsToAcceptFactionRelation` cannot express a threshold.** Its `CanAccept` is
`Faction.OfPlayer.RelationKindWith(otherFaction) == relationKind` — an equality against a
three-valued enum, plus an `acceptIfDefeated` escape — and its `ReasonText` is one of three fixed
keys carrying no number. The enum is not a function of the goodwill value either:
`RelationKindWith` reads the latched `FactionRelation.kind`, and `CheckKindThresholds` flips Hostile
at ≤ −75, Ally at ≥ +75 and back to Neutral only on crossing **0**, so a faction at +74 is `Ally`
coming down from 80 and `Neutral` coming up from 10. [V]

Established on [#93](https://github.com/cjd721/Rimworld-Archinity/issues/93); the system built on it
is `docs/specs/POLITICS.md` § *Standing as a content gate*.
- ⚠ **Multiplayer syncs `Quest.Accept`, not the gate.** `Multiplayer.Client.SyncMethods` registers `SyncMethod.Register(typeof(Quest), "Accept")` **[V]**, and `Quest.Accept` runs `PreQuestAccept` on every part and `Initiate` without consulting `CanAcceptQuest` **[V]**. The requirement is evaluated on the clicking client before the command is sent. A requirement over shared state that another player can change in the same tick (a balance) is therefore advisory in Multiplayer unless it is re-checked inside a synced call of ours.
- **Two accept paths bypass the gate entirely:** VFE Deserters' `DeserterTabWorker_Plots.DoMainPart` and VEF's `QuestGiverManager.ActivateQuest` both call `Quest.Accept` directly. VEF's `Window_Contracts.AcceptQuestByInterface` does check `CanAcceptQuest` before reaching `ActivateQuest` **[V]**. ([#132](https://github.com/cjd721/Rimworld-Archinity/issues/132))

---

## Offers: no decline, per-script refire, and no hostile settlement

Verified against 1.6.4871 and `Multiplayer.dll` (`2606448745`).

- **A vanilla quest offer cannot be declined.** The quest tab's *Dismiss* toggles `Quest.dismissed`,
  which Multiplayer syncs as a field. The offer stays offered until it reaches
  `QuestState.EndedOfferExpired` [V]. Only letter-borne joiner offers carry a reject option
  (`ChoiceLetter_AcceptJoiner`, `ChoiceLetter.Option_Reject`) [V]. A modded letter's options are
  T-96.
- **`QuestScriptDef.minRefireDays` is per script and counted from appearance.**
  `NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight` returns 0 while any quest with that
  `root` has `TicksGame - appearanceTick` below the window [V]. It never reads a faction or an expiry
  time. On a chain-granted quest it is inert (T-71).
- **Spacing from when the last offer *ended* has a vanilla precedent.**
  `StorytellerComp_MechanitorComplexQuest` spaces quests by `minSpacingDays` from the latest
  `cleanupTick` of that script [V]. Expired offers have a `cleanupTick`. Ended quests are never pruned:
  `QuestManager.Remove`'s only callers are debug code [V].
- **`QuestNode_GetNearbySettlement` never returns a hostile settlement.** It filters on
  `Settlement.Visitable`, which is false when the settlement's faction is hostile to the player [V].
  `QuestNode_GetFaction` does take `allowEnemy` and `allowedHiddenFactions` [V].
- **Controllable allied pawns are XML.** Royalty's `Scripts_Utility_Helpers.xml` generates pawns, then
  applies `QuestNode_JoinPlayer`, `QuestNode_ExtraFaction` (`factionType HomeFaction`,
  `areHelpers true`), apparel lock and `QuestNode_Leave` after a delay [V].
- **Accepting a quest is synced**: `SyncMethod.Register(typeof(Quest), "Accept")`. Under async time,
  `MultiplayerAsyncQuest` caches the quest against a map on accept [V].
- **A shelf life is set at generation and resolves without the quest ever being ticked.**
  `RimWorld.QuestGen.QuestGen.InitializeQuestGen` sets `acceptanceExpireTick` from
  `QuestScriptDef.expireDaysRange` [V], and `Quest.State` is **computed** — it returns
  `EndedOfferExpired` as soon as `TicksUntilExpiry == 0 && acceptanceTick < 0`, where
  `TicksUntilExpiry` derives from `acceptanceExpireTick` [V]. So a per-entry shelf life works
  on an offer held **outside** `Find.QuestManager` that nothing ticks — which is what makes a
  shop shelf possible, and what makes **T-124** possible on the same shelf.
  ([#144](https://github.com/cjd721/Rimworld-Archinity/issues/144))
- **`QuestNode_GetSiteTile` cannot be aimed.** Its `nearTile` is slate `map` (a `Map`), else a
  random player home map, and its distance is slate `siteDistRange` (default 7–27) [V,
  `QuestNode_GetSiteTile.TryFindTile`]. A site near a settlement that is not the player's needs a
  node of ours around `TileFinder.TryFindNewSiteTile(out tile, nearTile, min, max, …)`, which takes
  any tile. ([#154](https://github.com/cjd721/Rimworld-Archinity/issues/154))
- **`IncidentWorker_GiveQuest` makes any `QuestScriptDef` storyteller-fired in XML**
  (`def.questScriptDef ?? parms.questScriptDef`) [V]. ([#154](https://github.com/cjd721/Rimworld-Archinity/issues/154))

Established on [#131](https://github.com/cjd721/Rimworld-Archinity/issues/131).

---

## Decrees: who issues them, what missing one costs, what ends one

Verified against decompiled `Assembly-CSharp.dll` and Royalty's
`Defs/QuestScriptDefs/Decree/` [V throughout].

- **A decree is a titled colonist's demand on the colony, and in vanilla it comes only from a
  breakdown.** `Pawn_RoyaltyTracker.IssueDecree` has two callers: `MentalBreakWorker_WildDecree`
  (commonality = highest `RoyalTitleDef.decreeMentalBreakCommonality` held; colonists only) and
  `RoyalTitle.RoyalTitleTick` on `decreeMtbDays`, which fires only for `conceited` free colonists
  and is `-1` (off) on every Empire title, vanilla's and VFE Empire's.
- **Selection is by tag across every ladder.** `PossibleDecreeQuests` pools `decreeTags` from all
  titles in effect and keeps each `QuestScriptDef` sharing a tag whose `CanRun` passes. `CanRun`'s
  memo is keyed on tick and `points`, not on the `asker` in the slate (**T-39**), so a per-asker
  `TestRun` gate answers every titleholder on a map with the first one's result that tick.
- **`decreeDays` is not a deadline that fails the quest.** `isQuestTimeout` on `QuestNode_Delay`
  only sets `isBad` and the "expires in" label. On completion the delay enables
  `QuestPart_SituationalThought` → `DecreeUnmet`, whose `Thought_DecreeUnmet.MoodOffset` ramps
  −5 → −15 over 15 days (private static curve) on the asker only. `DecreeSetup` ends the quest
  as Fail 80 days in, with no further cost. That mood ramp is vanilla's entire failure cost, plus
  `DecreeFailed` (−4) if a completed monument is destroyed early.
- **Signed favour and goodwill changes are XML.** `QuestNode_GiveRoyalFavor.amount` feeds
  `Pawn_RoyaltyTracker.GainFavor`, which adds a negative without clamping; `UpdateRoyalTitle` only
  promotes, so lost favour never costs a title. `QuestNode_ChangeFactionGoodwill.change` feeds
  `TryAffectGoodwillWith`. Both need `faction` or `factionOf`; vanilla XML has no node that
  yields `Faction.OfEmpire` (`QuestNode_GetFaction` has no def filter) — VFED's
  `QuestNode_GetEmpire` does.
- **Nothing ends decrees on hostility.** No trigger or `PossibleDecreeQuests` reads relations.
  `Faction` sends `BecameHostileToPlayer` to its `questTags` on turning hostile to the player, and
  `QuestNode_IsFactionHostileToPlayer` + `QuestNode_CannotRun` can fail a `TestRun` from XML.

Established on [#137](https://github.com/cjd721/Rimworld-Archinity/issues/137); the routes are
`docs/specs/RELIGION.md` § *Decrees — what failing one costs, set per decree*.

---

## What ends a quest, and what can hear it end

Verified against decompiled `Assembly-CSharp.dll` [V throughout].

- **Every outcome end goes through `Quest.End(QuestEndOutcome, sendLetter, playSound)`, but not
  every end does.** `End` sets `ended` and `endOutcome` and then calls `CleanupQuestParts()`,
  which runs `Notify_PreCleanup()` and then `Cleanup()` on every part. **An offer that expires
  unaccepted skips `End`.** `Quest.QuestTick` calls `CleanupQuestParts()` directly when
  `TicksUntilExpiry == 0 && State == NotYetAccepted`. `State` is computed: `Fail` gives
  `EndedFailed`, `Success` gives `EndedSuccess`, `InvalidPreAcceptance` gives `EndedInvalid`,
  and anything else gives `EndedUnknownOutcome`. `EndedOfferExpired` applies only while
  `acceptanceTick < 0`.
- **`End` sends no signal, and `QuestManager` has no end hook.** Its `Notify_*` set covers pawns
  discarded, killed or born, things produced, plants harvested and factions removed. **Three
  event seams can hear a quest end, and polling is a fourth listener:**
  - **A part inside that quest**, reading `quest.State` in `Notify_PreCleanup`. It hears expiry
    too.
  - **A Harmony patch on `Quest.End`.** It **never hears expiry**. It is shipped four times: VFED
    `MiscPatches.CheckForPlotEnd`, VFEE `Patch_Quest_End`, Medieval Overhaul
    `MedievalOverhaul.Patches.Quest_End` (all postfixes), and VEF
    `VanillaExpandedFramework_Quest_End_Patch` (a prefix).
  - **A patch on `CleanupQuestParts`.** It hears expiry, and VEF's
    `VanillaExpandedFramework_Quest_CleanupQuestParts_Patch` routes it to `QuestExpired`.
  - **Polling `quest.State` from outside.** Vanilla's `StorytellerComp_RefiringUniqueQuest`
    refires a unique quest `refireEveryDays` after `cleanupTick` unless it ended `EndedSuccess`.
    `QuestPart_SubquestGenerator` polls its children (below).
- **Failure almost always comes from a script's own signal.** `QuestPart_QuestEnd` ends the quest
  on its `inSignal`, taking the outcome from the part or from the signal's `OUTCOME` argument. The
  builder is `QuestGen_End.End`. **Direct callers mostly end `Unknown`:** `MoveColonyUtility`,
  `Precept_Relic` and `GameComponent_Anomaly` end `Unknown`, `RoyalTitleUtility` ends
  `InvalidPreAcceptance`, and `QuestPart_SpawnMonolith` ends `Fail`.
- **The accepter dying fails nothing generically, and the player cannot abandon an accepted
  quest.** Nothing that reads `AccepterPawn` ends a quest, and `MainTabWindow_Quests` never calls
  `End`.
- **An ended quest cannot be accepted again.** `Accept` is a no-op unless the state is
  `NotYetAccepted`, and `ended` is never reset. To re-offer, generate the script again.

Established on [#145](https://github.com/cjd721/Rimworld-Archinity/issues/145); the routes are
`docs/specs/CURRENCIES.md` § *A failed bought quest returns to the shop*.

---

## Giver tags: a closed enum, five callers, no `CanRun`

`QuestScriptDef.givenBy` is a `List<QuestGiverTag>`. The enum is closed: `Traders`, `OrbitalScanner`,
`Reading`, `Beggars`. `givenBy` is read only by `QuestUtility.GetGiverQuests`, which is `public
static` and yields nothing unless Odyssey is active **[V]**.

**Five vanilla callers:**

| Caller | Tag | Draw |
|---|---|---|
| `CompOrbitalScanner.LocateSignal` | `OrbitalScanner` | `RandomElementByWeight` |
| `CompAncientUplink.Notify_Hacked` | `OrbitalScanner` | `RandomElementByWeight` |
| `TradeUtility.ReceiveQuestFromTrader` | `Traders` | `rootSelectionWeight` |
| `BookOutcomeDoer_GiveQuest` | `Reading` | `rootSelectionWeight` |
| `QuestNode_Root_Beggars`, fired later by `QuestPart_AddGiverQuest` | `Beggars` | `rootSelectionWeight` |

The two orbital callers weight their draw by `NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight`
**[V]**.

- **None of them calls `CanRun`.** Each goes from the draw straight to `QuestGen.Generate`, so a
  `TestRunInt` gate is inert on every giver path. This is the **T-71** class.
- **The two orbital givers use `RandomElementByWeight`, not the `Try` form.** An empty or zero-weight
  list logs an error and hands `null` onward, and `CompOrbitalScanner` then throws on every tick.
  **Never empty a tag while its giver can fire.**
- **Reading a tag is free; adding one is not.** Our code can call `GetGiverQuests` for any of the
  four, and our quests can join any of the four by XML. A fifth tag needs C#. `ParseHelper` parses
  enums with `Enum.Parse`, which accepts an undefined numeric value such as `<li>4</li>` **[I]**, but
  no reader would ever find it.
- **The six Odyssey `OpportunitySite_*` quests are giver-agnostic.** Each sets `discoveryMethod`
  itself when the slate lacks one, so any caller can run them. Their root,
  `QuestNode_Root_Asteroid`, places 1–3 tiles from a random player tile and ignores
  `siteDistRange` **[V]**.

Established on [#149](https://github.com/cjd721/Rimworld-Archinity/issues/149);
`docs/specs/CHARTING.md` § *The orbital scanner and Charting*.

---

## A visitor group can be sent to a specific thing — in C#, not XML

Verified against RimWorld 1.6 [V throughout].

- **`QuestPart_Venerate : QuestPart_MakeLord`** takes a `Thing target`, `venerateDurationTicks`,
  `outSignalVenerationCompleted` and `inSignalForceExit`, and makes a `LordJob_Venerate`. Its graph
  is travel to `target.InteractionCell` → `LordToil_Venerate` for the duration → exit, sending the
  completion signal on the way out. It exits early if the target takes damage, and exits defending
  itself if a member is killed or the group turns hostile. `LordToil_Venerate` rotates one pawn
  close in while the rest spectate around the target, using the Ideology-only
  `DutyDefOf.Pilgrims_Spectate`.
- **Its one user is Ideology's `QuestNode_Root_ReliquaryPilgrims`**, which aims it at a
  reliquary holding a relic. **No `QuestNode_*` constructs it**, and no corpus mod references it
  or `LordJob_Venerate`.
- ⚠ **`QuestPart_Venerate.ExposeData` does not save `outSignalVenerationCompleted`**, and
  `QuestPart_MakeLord.ExposeData` saves only the pawns, `inSignal`, `inSignalRemovePawn`, the
  faction, `mapParent`, `mapOfPawn` and `excludeFromLookTargets`. `LordJob_Venerate` does save
  the field, so it is safe once the lord exists. If the game is saved between generation and the
  part's `inSignal` (for example, while the quest sits unaccepted), the loaded part has `null`.
  The lord it later makes adds no completion action, because `CreateGraph` wires the signal only
  when the field is non-empty, so the signal never fires and nothing is logged (**T-158**). Vanilla's pilgrims
  do not notice: they drive success from every pawn's `LeftMap` through `QuestPart_PassAll`, and
  the completion signal only drives a message.
- **Any 1×1 thing is a valid target.** `ThingUtility.InteractionCellWhenAt` returns a standable,
  reachable adjacent cell for a 1×1 def without `hasInteractionCell`.
- **The XML visit cannot be aimed.** `QuestNode_VisitColony` → `QuestPart_VisitColony.MakeLord`
  puts the group at `RCellFinder.TryFindRandomSpotJustOutsideColony`, with no target field.
- **`QuestNode_GetFaction`'s `allowNeutral` and `allowAlly` default to `false`.** It draws
  uniformly (`TryRandomElement`) from `GetFactions(allowHidden: true)`, which already drops the
  player, defeated and temporary factions. VEF postfixes its private `IsGoodFaction` to honour
  `FactionDefExtension.excludeFromQuests` (global), and ships its own node with a `factionDef`
  pin.

Established on [#158](https://github.com/cjd721/Rimworld-Archinity/issues/158); the routes are
`docs/specs/ENCOUNTERS.md`.

---

## A quest site's map: leaving destroys the site, and one site part keeps it

Verified against decompiled 1.6 `Assembly-CSharp.dll` [V throughout].

- **Leaving a vanilla quest site destroys it.** `Site.ShouldRemoveMapNow` refuses while pawns
  block removal, on the map or on a pocket map sourced from it; while a building blocks it; or
  while a transporter is inbound. Otherwise it sets `alsoRemoveWorldObject = true`, unless a part
  holds a live condition causer or a hostile `SitePartWorker_RaidSource` threat.
  `MapParent.CheckRemoveMapNow` then removes the map and destroys the site. The quest hears
  `site.MapRemoved`, and its script decides the outcome: the hack complex and `Gravcore_Mechhive`
  end `Fail`. Odyssey's two orbital gravcore platforms also carry an `Unknown` end on it, **but they
  end `Success` on `site.MapGenerated` first, so it never fires.** There is no return visit, and
  anything not carried off is gone.
- **A `Settlement` is the opposite.** `ShouldRemoveMapNow` leaves the world object standing, so the
  next entry generates a fresh map from the `MapGeneratorDef`. Only
  `SettlementDefeatUtility.CheckDefeated` retires it, to a `DestroyedSettlement`.
- **The exception is a type test, so XML can opt in.** `Site.ShouldRemoveMapNow` keeps the site
  whenever a part's worker `is SitePartWorker_AncientAltar` and its relic is still on the map.
  `Notify_SiteMapAboutToBeRemoved` despawns the relic back into the `SitePart`, or, if it has left,
  sends `SitePartParams.relicLostSignal` — the relic hunt's success signal. The class has no DLC
  check. Any `SitePartDef` naming it as `workerClass` gets this behaviour once
  `SitePartParams.relicThing` is set, and so does any subclass.
- **Two things hold a map open.** Pawns (`AnyPawnBlockingMapRemoval`) and, with Odyssey, any
  `GravEngine` or `GravAnchor` on it (`Map.AnyBuildingBlockingMapRemoval`). A map generated by a
  gravship landing starts no `TimedDetectionRaids` countdown (`Site.PostMapGenerate`).
- **An unvisited site outlives its quest.** `QuestPart_SpawnWorldObject.Cleanup` destroys the
  world object only if it was never spawned. A spawned, never-entered site stays on the board
  after its quest ends, unless the script adds `QuestNode_DestroyWorldObject` or
  `QuestNode_WorldObjectTimeout` with `destroyOnCleanup`.
- **A parent generator hears its children end without a patch.** `QuestPart_SubquestGenerator`
  polls `quest.GetSubquests()` states each tick. Only `EndedSuccess` counts toward
  `maxSuccessfulSubquests`, and Odyssey's gravcore generator re-admits any script not `Ongoing` or
  `EndedSuccess`. So a failed or `Unknown` child is offered again as a fresh quest. This is a
  fourth listener beside the three in § *What ends a quest*. ⚠ The base `TryGenerateSubquest`
  skips `CanRun`. All three shipped subclasses test it themselves: `RelicHunt`, `ArchonexusVictory`
  and `Gravcores`.

Established on [#151](https://github.com/cjd721/Rimworld-Archinity/issues/151); the routes are
`docs/specs/ORBIT.md` § *A stronghold a quest generates*.
