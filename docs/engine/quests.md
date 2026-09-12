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

## The intel workbench already ships, twice

> Provenance note: this section was verified during the sessions on
> [#23](https://github.com/cjd721/Rimworld-Archinity/issues/23) and
> [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) and recorded only in the
> map's fog. Not re-verified at the time of the move — provenance is those sessions.
> The caveat applies to this section only.

Fog-only material behind *the acquisition ledger*. The archive's parked "intel workbench"
idea — a player-initiated way to turn *"I am blocked"* into an action
(`docs/archive/sys/06-quests.md`) — does not need building.

- **Medieval Overhaul's explorer's workbench** (`MedievalOverhaul.Building_QuestScanner`) is
  a player-built quest generator fuelled by consumable **Torn Notes**, gated on linkable
  facilities, exposing an open `MedievalOverhaul.QuestInformation` extension that any
  `QuestScriptDef` can join.
- **VFE Deserters ships a second**: an intel-priced rolling queue on a comms tab.

## The accept-time gate is one abstract base, and only three things touch it

Verified against RimWorld 1.6.

`RimWorld.QuestPart_RequirementsToAccept` is a twelve-line abstract base — `CanAccept()` returning
an `AcceptanceReport`, `CanPawnAccept(Pawn)`, `ShowInRequirementBox`, `Culprits`. **Twelve vanilla
subclasses**: `Bedroom`, `ColonistWithTitle`, `FactionRelation`, `NoDanger`,
`NoOngoingBestowingCeremony`, `PawnOnColonyMap`, `PlanetLayer`, `PlayerWealth`, `Research`,
`ThingStudied`, `ThingStudied_ArchotechStructures`, `ThroneRoom`. **Four have XML `QuestNode`
wrappers** — `Bedroom`, `ColonistWithTitle`, `PlanetLayer`, `Research`; the last spells its field
`<reserach>`, misspelt identically in the C# and in the two shipped Odyssey defs that use it. [V]

- **`QuestUtility.CanAcceptQuest(Quest)` is the sole enforcement point**, and consults only this
  base class — ignoring `ShowInRequirementBox`.
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
