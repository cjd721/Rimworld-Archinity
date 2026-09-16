# Quests

What the vanilla quest system can be made to do from XML: fixed rewards, standing
parent quests with sub-quests, what the quest tab will and will not show, and the
two mods that already ship a player-initiated quest generator.

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

Established on [#131](https://github.com/cjd721/Rimworld-Archinity/issues/131).
