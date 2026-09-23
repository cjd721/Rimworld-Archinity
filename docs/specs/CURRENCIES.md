# Spendable currencies

## Purpose and scope

Implements the two **spendable operational currencies** the campaign requires:

- **Influence** — [`docs/requirements/RELIGION.md` § *The Schism Path — Influence + Reverence*](../requirements/RELIGION.md).
  Earned by Schism operations, spent through the anti-Church network on favors
  Goodwill cannot buy.
- **Intel** — [`docs/requirements/GLITTERTECH.md` § *Intel Is Capability, Not Exposition*](../requirements/GLITTERTECH.md).
  Recovered from Glitterite raids, destructive analysis and site lore; held as a balance;
  **exchanged** at an authored table or through a capable faction for a techprint or another
  Instruction item. Research and hacking **never** debit it — see *The build* § *The Intel
  exchange* ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54), closed; catalogue
  [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117)).

Established on [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54), which
absorbed [#55](https://github.com/cjd721/Rimworld-Archinity/issues/55)'s currency half,
and extended by [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106) with the
**purchasable quest catalogue** — the *Purchase* arrival channel of
[`docs/requirements/QUESTS.md`](../requirements/QUESTS.md).

**This document owns** the mechanism that holds a spendable balance, moves it, persists
it, shows it, and spends it against a catalogue. It owns that mechanism for *any* number
of currencies, because nothing in it names either fiction.

**It does not own:**

| | |
|---|---|
| The **exemplar gate** — a research project requiring a physically-analysed item | [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67). The interface between the two is stated below, and what it does *not* commit either side to is the load-bearing part. |
| **Destructive artifact analysis** — the long job that consumes a recovered artifact, credits Intel and raises Trace | [#115](https://github.com/cjd721/Rimworld-Archinity/issues/115). Its only contact with this document is `Credit`. |
| **Which Instruction items are for sale, their Intel prices and cadence, and whether a table, a faction or both carries each one** | [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117), the Ultra acquisition session. This document supplies **both venues as mechanism** at *The Intel exchange*; selecting and pricing them is #117's. |
| **What a delivered item unlocks, when it is not a techprint** | [`HACKING.md`](HACKING.md) § *New verbs* has one shipped consumer: `USH_ExecData_*` items install `Hediff_LearningAbility`, which grants an ability. Any other kind of non-techprint unlock item needs its own consumer; content on [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) / [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119). The exchange delivers a `Thing` and stops. |
| **Exaltation** and **Reverence** | [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53), [#98](https://github.com/cjd721/Rimworld-Archinity/issues/98) / [`RELIGION.md`](RELIGION.md). Threshold ladders, not spends. |
| **Trace** | [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) / [`TRACE.md`](TRACE.md). A band ladder, not a balance. #56 has now **ruled** on whether sharing one store with Intel couples it to Church standing — see *What is shared*. |
| **Which bought quests return on failure, and at what price** | Authoring, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) for the Schism, and [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117). The **mechanism** — what observes the failure and how an entry comes back free, paid or refunded — is here, at *A failed bought quest returns to the shop*, from [#145](https://github.com/cjd721/Rimworld-Archinity/issues/145). |
| **Which quests are for sale, and what they contain** | Authoring. The **machinery** that offers and sells a quest is [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106)'s and is **in this document**, at *The purchasable quest catalogue* — because it is a purchase, and purchases live here. |
| The **ordered Schism chain** that Influence purchases advance | Routes, stranding and the marking act: *The Schism catalogue — a spend that advances the plot*, from [#132](https://github.com/cjd721/Rimworld-Archinity/issues/132). The reveal, ground and finale are [#130](https://github.com/cjd721/Rimworld-Archinity/issues/130)'s. |
| Cross-cutting political-UI layout | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map). Every surface has a route ([#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)); tab shape and placement are the build map's. The readout for these two numbers is here. |

**Why this is its own document rather than a section of [`RELIGION.md`](RELIGION.md).**
The verdict is that one mechanism serves both currencies. Filing it under religion would
make Glittertech reach into the religion spec for Intel's storage, persistence and
readout, and would file a Glitterite mechanism under Church politics — the shape #56
exists to guard against. Two systems consume this; neither owns it.

## The Schism catalogue — a spend that advances the plot

### Purpose and scope

Answers [`RELIGION.md` § *The Schism Path*](../requirements/RELIGION.md): *"Influence is spent with the Schism: on the missions that advance its plot against the Church, and on favors… techprints"*, plus the marking act that commits the founders and turns the Church permanently hostile. Established on [Influence — earned as a chosen reward, spent to advance the Schism plot](https://github.com/cjd721/Rimworld-Archinity/issues/132).

**This section owns:** how a spend can advance an ordered chain, whether spending elsewhere can strand it, and what each route allows as the marking act.

**It does not own:**
- Influence as a reward option: [Credit for a deed, chosen with the quest's reward](https://github.com/cjd721/Rimworld-Archinity/issues/135).
- The reveal, ground passing to the Schism, and the finale: [The Schism — revealed, taking the Church's ground, allied for good](https://github.com/cjd721/Rimworld-Archinity/issues/130).
- The Church's standing: ordinary Goodwill until betrayal's latch ([`RELIGION.md`](RELIGION.md) § *The build — Exaltation* › *6. Betrayal — the permanent-hostility latch*; [#123](https://github.com/cjd721/Rimworld-Archinity/issues/123)).

### Verdict

- **Possible? Yes.** VFE Deserters already ships a paid ordered chain: each step is accepted by spending Intel, and only the step's outcome advances the index **[V]**. **Under every route, spending elsewhere stalls the plot and never strands it.** Stranding comes down to income stopping or a step failing to generate.
- **Multiplayer? Yes** for A (the existing synced `TryPurchase`) and D (MP Compat syncs VFED's paid plot accept **[V]**). **With work** for B, where the price check runs before the synced `Quest.Accept` and is not repeated inside it **[V]**, and for C.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A — A paid ordered chain in the catalogue** | Ordered Schism blows. The current step waits in the catalogue, and buying it debits and accepts in one synced command. Success moves on; failure re-offers the same step. Favours and techprints are rows beside it | Ours; donor VFED `WorldComponent_Deserters` + `DeserterTabWorker_Plots` | C# + XML | Medium | Yes |
| **B — The price sits on an ordinary offer** | Steps arrive as normal quest offers showing *"Requires N Influence"*, debited on accept. Ordered by VEF `QuestChainExtension` or by A's list | Vanilla `QuestPart_RequirementsToAccept` + a debit part | C# + XML | Medium | With work |
| **C — One VEF `QuestGiverDef` for plot and favours** | Steps and favours as purchasable offers in one contract window | VEF `VEF.Storyteller` + a gate node + a refill hook | C# + XML | Medium | With work — **not recommended** |
| **D — Adopt VFE Deserters' network as the Schism** | Its plot tab, services, techprint contraband and one-way hostility | VFE Deserters + patches | patch + C# | Hard (to fit) | Yes — **not recommended as shipped** |

**Route A.**

*Levers:*
- Chain order and length are an authored list.
- Several approaches per blow, each with its own price, combat level and exposure. VFED's `VFED_PlotMission` authors `raid` / `shootDown` / `falseInvitation` this way **[V]**.
- Re-pay or refund on a failed blow. VFED makes the player re-pay **[V]**.
- One advance hook, where #130's ground transfer and finale attach.
- Either marking act.
- A second `CurrencyDef` as a plot-only accumulator, giving #39's two-accumulator shape **[I]**.

*Cannot:*
- Produce Influence.
- Keep *Structural separation* layer 3 as it was written. The plot purchase must reach the current step; only the index's single writer (the quest outcome) survives.

*Consequences:* spending stalls, never strands. Strands only on lost income or a step whose generation throws (VFED's `GeneratePlotQuest` has no retry **[V]**).

**Route B.**

*Levers:*
- Free presentation: offer letter, quest-tab row, and a locked-requirement line carrying the price.
- Chain topology in VEF XML.
- The same gate can price any deed.

*Cannot:*
- Show steps in the Schism window unless drawn there too.
- Enforce the price where `Quest.Accept` is called directly — VFED's plot tab and VEF's `ActivateQuest` do that **[V]**.
- Use VEF's expiry features (**T-72**, **T-73**), or its XML gates on the chain path (**T-71**).

*Consequences:*
- An offer that expires while unaffordable strands the plot under VEF ordering, so plot offers must not expire.
- In Multiplayer, two founders spending in the same tick can let a step through free unless the check moves inside a synced call **[I]**.

**Route C — not recommended.** `QuestWorker.GenerateQuests` draws `RandomElement` without replacement, so the giver has no order. Order can come only from `CanRun` gates, which do run on this path (unlike **T-71**), but no shipped node reads chain progress. The pool fills only at `Init` and `Reset`, and `Reset` clears every unbought offer. `ActivateQuest` regenerates nothing. So the next step waits for a reset that discards every favour, and with `resetEveryTick = -1` it never comes. A capped pool can omit the step at random, and a step that throws vanishes (**T-77**). All **[V]**. It needs A's code anyway, behind a worse surface.

**Route D — not recommended as shipped.** The network is a comms-console target only after joining, and it counts Intel only on powered orbital trade beacons. Both buildings require `MicroelectronicsBasics`, while the Schism arrives in the Medieval era. The marking act is fixed at accepting `VFED_ChasedDeserter`, so no Schism work is possible before commitment. `VFED_EmpireBargain` offers a betrayal after plot successes, which contradicts *"no option to sell the Schism out"*. And Influence would be items, not this document's balance. All **[V]**. Its value is as A's donor.

**The marking act.**
- **Both acts work under A, B and C.** Under D the act is joining.
- **The hostility carrier is the same for both.** VFED's `JoinDeserters` sets goodwill to `GoodwillToMakeHostile`, then `GoodwillPatches.CanChangeGoodwillFor_Postfix` freezes Empire↔player goodwill while a stored flag is set **[V]**. Vanilla hostility alone is recoverable through gifts and peace talks (`RELIGION.md` § *Exaltation — what survives the Church's hostility*) **[V]**.
- **First Influence gained** makes banking while favoured impossible by construction. Operations before commitment then pay no Influence, and the Influence option must warn at acceptance, as `VFED_ChasedDeserter` does **[V]**.
- **First plot spend** lets Influence bank without limit while the Church stays friendly. That breaks `RELIGION.md`'s banking clause, *"cannot bank Influence and keep the Church's favor"*, so the requirement as written rules it out.

**Recommendation, not a selection:** A for the plot, with favours and techprints as rows in the same catalogue. B as a complement if blows should arrive as ordinary offers. First Influence gained as the marking act, because it alone meets the requirement's banking clause by construction.

### Constraints

- **The index moves only on a quest outcome, in every route.** A purchase gates a step; it never writes the index **[I — route property]**.
- **Stranding reduces to income and generation.** The routes add these failure surfaces:
  - B: an expiring offer (**T-72**, **T-73**).
  - C: a pool that never resets, and swallowed generation errors (**T-77**).
  - A: no retry when a step fails to generate.
- **One-way hostility needs a goodwill freeze.** Vanilla hostility alone does not hold.
- **An unaccepted plot step never expires in the donor.** VFED shelves steps with `acceptanceExpireTick = -1` and handles `EndedFailed` / `EndedInvalid` only **[V]**.
- **#39 is analogy, not rule.** Its *"never paid for out of the economy's supply"* governs Charting's site pools **[V]**. Here one balance pays for plot and favours by design. The difference that makes sharing survivable: Influence banks, labour does not **[I]**.

### Available mechanisms

| Mechanism | What it does | Evidence |
|---|---|---|
| **VFED paid plot chain** — `WorldComponent_Deserters.InitializePlots` / `GeneratePlotQuest` / `Notify_PlotQuestEnded`; `HarmonyPatches.MiscPatches.CheckForPlotEnd` (`Quest.End` postfix); `DeserterTabWorker_Plots.DoMainPart` | Ordered list built from `VFEEmpire.WorldComponent_Hierarchy.Titles` ≥ Knight. Steps are shelved hidden with no expiry. *Select* runs `TrySpendIntel(cost, useCriticalIntel)`, then `Choose`, then `Accept`. `EndedSuccess` (4) generates index + 1; `EndedFailed`/`EndedInvalid` (5/6) regenerate the same index | [V] `…/294100/3025493377/1.6/Assemblies/VFED.dll`; `QuestState` in `Assembly-CSharp.dll` |
| **VFED approaches** — `QuestNode_ApproachChoices`, `PlotMission.xml` | Per-approach `intelCost`, `combatLevel`, `visibilityGain`, and `UseCriticalIntel` (only `falseInvitation`) | [V] |
| **VFED join / betray** — `QuestPart_JoinDeserters` (in `VFED_ChasedDeserter`), `JoinDeserters`, `GoodwillPatches`, `QuestPart_BetrayDeserters` (in `VFED_EmpireBargain`) | Joining force-hostiles the Empire, allies the Deserters and strips titles, and goodwill stays frozen while `Active`. Betrayal sets `Locked` and ends every Deserter quest | [V] |
| **VFED access** — `GetCommTargets_Postfix`, `Dialog_DeserterNetwork.PostOpen` | A comms-console target only while `Active`; Intel counted on powered orbital trade beacons; both buildings require `MicroelectronicsBasics` (Core `Buildings_Misc.xml`) | [V] |
| **MP Compat for VFED** — `Multiplayer.Compat.VanillaFactionsDeserters` (`1629973374/1.6/Referenced/`) | Transpiles the plot button to `SyncedAcceptPlot` (spend → `Choose` → `Accept`) and registers `InitializePlots` and `EnsureQuestListFilled` | [V] |
| **VEF quest giver** — `QuestWorker.GenerateQuests`, `QuestGiverManager.Init` / `Tick` / `Reset` / `ActivateQuest`, `StorytellerWatcher.AddQuestGiverManager`, `CompQuestGiver.Use`, `QuestInfo..ctor` | Random draw without replacement, capped, with `CanRun` live. Refills only at `Init` and `Reset`, and `Reset` clears unbought offers. `ActivateQuest` does not refill. Offers carry a pre-rolled reward | [V] `…/294100/2023507013/1.6/Assemblies/VEF.dll` |
| **VEF quest chains** — `GameComponent_QuestChains.TryScheduleQuest`, `QuestChainExtension` | `conditionSucceedQuests` ordering, working `grantAgainOnFailure`, and a live-duplicate refusal. Any quest whose root carries the extension is recorded by the `QuestManager.Add` postfix, whatever granted it | [V]; hazards **T-71–T-73** |
| **Vanilla accept gate** — `QuestPart_RequirementsToAccept`, `QuestUtility.CanAcceptQuest`, `Quest.Accept` → `PreQuestAccept` | The price can be an accept requirement plus a debit before `Initiate` | [V]; `docs/engine/quests.md` § *The accept-time gate* |
| **Multiplayer** — `Multiplayer.Client.SyncMethods` | `SyncMethod.Register(typeof(Quest), "Accept")` and `PatchQuestChoices.Choose` are synced; `CanAcceptQuest` is not re-checked inside | [V] `…/294100/2606448745/1.6/AssembliesCustom/Multiplayer.dll` |

**What does not exist:**
- No shipped `QuestNode` reads quest history or our state. VEF's are `QuestNode_ForceMusic`, `QuestNode_GetFaction` and `QuestNode_Site`, and vanilla's `QuestNode_GetFieldValue` reads only an instance field of an object already on the slate **[V]**.
- Outside VFED and VEF, the wide pass for chain identifiers (`plotmission|questchain|questline|storyline|campaignstage|plotstage`, ASCII, both roots, `.dll`) found only RimPacts' `WorldWarQuestLine`, a status string **[V]**. The residual is a chain named otherwise.

### Status

**Evidence class: READ.** The mechanisms above are **[V]**; routes A–C are **[I]** as compositions. From [#132](https://github.com/cjd721/Rimworld-Archinity/issues/132).

### Open questions

| Question | Owner |
|---|---|
| The marking act | *First plot spend* breaks `RELIGION.md`'s banking clause; *first Influence gained* meets it by construction (§ *Routes* above). Which ships is the build map's ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)) |
| Does a failed blow cost its price again, refund it, or retry free? All three are possible — *A failed bought quest returns to the shop* ([#145](https://github.com/cjd721/Rimworld-Archinity/issues/145)) | Capability: all three, per entry (*A failed bought quest returns to the shop*). Which ships is the build map's ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)) |
| Influence decay: a steady state below a step's price strands the plot | Capability: yes — item rot (*Three Intel delivery options* (a)/(c)) or a tick debit on `WorldComponent_Currencies` ([`TRACE.md`](TRACE.md) § *What changes it* › *Decay* has the shape). Decay can strand the plot (*Failure and recovery*). Choice: [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) |
| Chain state storage; shelving in `QuestManager` vs deep save; per-approach price snapshot; retry on generation failure; the synced accept check (B); plot rows and cooldowns in the window | Build map, on selection |

---

## Shop entries — a quest or an item, each with its own eligibility and shelf life

### Purpose and scope

Answers [`docs/requirements/QUESTS.md` § *Shops*](../requirements/QUESTS.md): a shop's stock
comes from an authored set; **an entry is a quest or an item, and that stays open**; each entry
declares its eligibility from saved state; each entry's shelf lifetime is its own — standing
until bought, or expiring; an entry that stops being eligible may leave the shelf. Both shops,
Influence and Intel, are in. Established on
[#144](https://github.com/cjd721/Rimworld-Archinity/issues/144).

**This section owns:** what a shop *entry* can be, what gates its appearance, and how long it
stays on the shelf.

**It does not own:**
- The shelf itself, the currency pair and the accept sequence: *The purchasable quest catalogue*,
  from [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106). Read as-is — its shelf,
  its `QuestCurrency`/`QuestCurrencyInfo` pair and its `ActivateQuest` seam are unchanged. **What
  this section adds is what may ride on that shelf**: items as well as quests (*Items on the
  shelf*).
- **A failed bought quest returning to the shop:** *A failed bought quest returns to the shop*,
  below, from [#145](https://github.com/cjd721/Rimworld-Archinity/issues/145). It runs on the
  quest-**end** seam, not route B's tick. VEF's `grantAgainOnFailure` is its route C, which
  re-grants *outside* the shop.
- Which entries exist, their prices and their cadence:
  [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117). This section supplies the
  vocabulary; the values are balance.
- The ordered Schism chain, whose steps are entries of a particular kind: *The Schism catalogue*.

### Items on the shelf

`QuestNode_AddItemsReward.RunInt` constructs a `QuestPart_Choice` holding a single
`Reward_Items` and adds the `QuestPart_DropPods` it yields **[V]**, so an item entry on VEF's
`QuestGiverDef` shelf renders as an ordinary reward row and delivers on accept, and **T-76**
(which prunes entries lacking a `QuestPart_Choice`) does not touch it; the generator run and
quest-tab entry per item are route A's consequences, and the two-shelf case survives as
route D.

### Verdict

- **Possible? Yes, with one part built.** One shelf holds both kinds, because **an item entry is
  a quest whose only content is an items reward** — `QuestNode_AddItemsReward` builds the
  single-choice `QuestPart_Choice` the shelf requires and the `QuestPart_DropPods` that delivers
  it **[V]**. Per-entry eligibility is declared per entry in XML, gated at generation **and**
  re-checked every frame the row is drawn, by one shipped node **[V]**. Every entry already
  carries its own expiry clock, rolled from its own def, and that clock resolves with **no
  ticking at all** **[V]**. What nothing ships is the *removal*: VEF rotates the whole shelf or
  nothing, and a reset discards standing unbought offers **[V]**. Per-entry leaving is ours, on a
  tick seam that is verified to exist.
- **Multiplayer? Yes, with the fill and the accept on synced paths.** VEF's own entry point
  generates inside a job toil, i.e. in the sim **[V]**; a main-tab button that lazily fills the
  shelf would draw `Rand` from `OnGUI`. MP Compat's VEF entry touches only the quest-chain
  **dev-mode** window — never `QuestGiverManager` or `Window_Contracts` **[V]** — so #106's single
  `RegisterSyncMethod` on `ActivateQuest` remains the whole MP cost, and any per-entry pruning
  belongs on `QuestGiverManager.Tick`, never in the `AvailableQuests` getter.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A — One shelf; an item entry is an items-reward quest** | A single shop selling missions and techprints side by side, every entry an authored `QuestScriptDef` with its own gates and its own expiry clock | VEF `QuestGiverDef` / `QuestWorker` / `Window_Contracts` + vanilla `QuestNode_GenerateThing`, `QuestNode_AddItemsReward`, `QuestNode_RequirementsToAccept*` | XML, on top of #106's currency pair | Easy | Yes |
| **B — A per-entry pass on the shelf's tick** (composes with A) | Entries leave one at a time: expired ones drop off, an ineligible one leaves, stock refills per entry | Ours; seam donors `VEF.Storyteller.QuestGiverManager.Tick` + `StorytellerWatcher.GameComponentTick`, predicate donors `RimWorld.FactionPermit.OnCooldown` + `RoyalTitlePermitDef.AvailableForPawn` | C# | Medium | Yes |
| **C — One gate node of ours** (composes with A) | An entry gated on era, a currency balance or a political flag, not only on research, wealth, title or faction relation | Ours; donors `QuestNode_RequirementsToAcceptResearch` and `QuestPart_RequirementsToAcceptPlayerWealth` | C# | Medium | Yes |
| **D — Two shelves: VEF for quests, our `CurrencyPurchaseDef` catalogue for items** | Item entries with per-entry `project` gate, `maxIssued`, cooldown and venue availability, free of every quest-shaped constraint | Ours (*The Intel exchange*, below) + VEF for the quest half | C# + XML | Medium — largely already specified | Yes |
| **E — Reskin a vanilla trader** | A stock list with per-generator tech gating and a visit-lifetime shelf | vanilla `TraderKindDef` + `StockGenerator_*` | XML + C# | Hard — **not recommended** | Unknown |

**Every mechanism cited is [V]; each route is [I] as a composition.**
**Recommend A + B + C together** — A is XML on machinery already selected, B closes the only
clause nothing ships, C is what lets an entry read the campaign rather than the colony. D stays
as the fallback if an authored item proves too awkward inside a quest, and as where a non-item
"favour" would go.

#### A — one shelf, both entry kinds

**What it gets us.**
- **An item entry that is a first-class shelf row.** `QuestNode_AddItemsReward.RunInt` builds a
  `QuestPart_Choice` with exactly one `Choice` holding a `Reward_Items`, then adds the parts
  `Reward_Items.GenerateQuestParts` yields — a `QuestPart_DropPods` off the quest's `inSignal`, or
  a `QuestPart_GiveToCaravan` **[V]**. `QuestNode_GenerateThing` makes the `Thing` into the slate
  from XML **[V]**. A techprint entry is: generate the thing, make it the reward. It renders in
  `Window_Contracts.DoRewards` like any reward and drops on accept.
- **Per-entry eligibility, in XML, with the re-check included.**
  `VEF.Storyteller.QuestWorker.GenerateQuests` calls `QuestScriptDef.CanRun` before generating, and
  `CanRun` runs `root.TestRun(slate.DeepCopy())` **[V]** — every `TestRunInt` in the entry's own
  graph is live (**T-71** is the chain path, not this one).
  `QuestNode_RequirementsToAcceptResearch` is the shape: `TestRunInt` false while the project is
  unfinished **and** `RunInt` attaches a part that `QuestUtility.CanAcceptQuest` re-evaluates every
  frame the row is drawn **[V]**. `QuestNode_GiveTechprints` self-gates the other way — false once
  the project is finished or its techprint requirement is met **[V]**, which is *The Intel
  exchange*'s "`project` hides the entry" behaviour, shipped.
- **Shelf life is already per entry, and needs no ticking.** `QuestGen.InitializeQuestGen` sets
  `acceptanceExpireTick` from the def's `expireDaysRange`, rolled per entry **[V]**;
  `QuestNode_SetTicksUntilAcceptanceExpiry` sets it from inside the graph **[V]**.
  `Quest.TicksUntilExpiry` and `Quest.State` are **computed** — `State` is `EndedOfferExpired` the
  moment the clock runs out **[V]** — so an offer held by `Scribe_Deep` outside
  `Find.QuestManager`, which is never ticked, still knows it has expired.
- **Standing until bought is the default:** `QuestGiverManager.Tick` resets only when
  `resetEveryTick != -1` **[V]**.
- **The XML gate vocabulary with no code**: `QuestNode_RequirementsToAcceptResearch`, `_Bedroom`,
  `_ColonistWithTitle`, `_PlanetLayer` (the four `QuestPart_RequirementsToAccept` subclasses with
  wrappers — [`docs/engine/quests.md`](../engine/quests.md) § *The accept-time gate*), plus
  generation-time `QuestNode_ExpansionActive`, `QuestNode_ModIsActive`,
  `QuestNode_HasRoyalTitleInCurrentFaction`, `QuestNode_IsFactionHostileToPlayer`,
  `QuestNode_RequireRoyalFavorFromFaction`, `QuestNode_ViolentQuestsAllowed`,
  `QuestNode_QuestUnique`, `QuestNode_CannotRun` and the `…OrFail` arithmetic family **[V]**.

**What it cannot do.**
- **Read our campaign state from XML.** `QuestNode_GetFieldValue` takes **instance** fields only
  and needs the object already on the slate **[V]**; nothing puts a `WorldComponent` there. Era, a
  balance or a political flag needs route C — the same wall `docs/engine/quests.md` records for
  `Faction.PlayerGoodwill`.
- **Make an entry leave.** Nothing in VEF reads `Quest.State` or `acceptanceExpireTick`;
  `AvailableQuests` prunes only on null / `askerFaction` / `choice` **[V]**.
- **Mix cadences inside one giver.** `Reset()` is `Clear()` then regenerate **[V]** — one cadence
  per `QuestGiverDef`, and it discards standing unbought offers. Standing entries beside rotating
  ones means several givers (XML, Easy) or route B.

**Consequences.**
- ⚠ **A per-entry shelf life introduces a pay-for-nothing failure, and it is silent.**
  `Quest.Accept` is wrapped in `if (State == QuestState.NotYetAccepted)` and is a **no-op**
  otherwise **[V]**, while `QuestGiverManager.ActivateQuest` still runs
  `Add → Accept → SendLetterQuestAvailable → currencyInfo?.Buy → Remove` **[V]**, and its only
  guard, `QuestUtility.CanAcceptQuest`, does not test `State` **[V]**. Buying an entry whose clock
  has run out **charges the currency, sends the "quest available" letter and accepts nothing**.
  Nothing logs. Proposed for the register on #144; the shop's own guard must test
  `State == NotYetAccepted`, or route B must prune first.
- ⚠ **`onlyOneReward: true` is necessary but not sufficient — T-76 is broader than its text.**
  `QuestInfo`'s constructor populates `quest_Part_choice`/`choice` only when `onlyOneChoice` is
  true **and** the generated quest actually contains a `QuestPart_Choice` **[V]**, and
  `AvailableQuests` discards entries missing either on every read **[V]**. So **an entry whose
  script builds no choice part is silently dropped from the shelf.** An item entry must go through
  `QuestNode_AddItemsReward`, not a bare delivery node.
- **The fill must not happen from the draw path.** VEF's own path is safe —
  `JobDriver_UseQuestGiver` runs `CompQuestGiver.Use()` from a Toil `initAction` **[V]**, so
  `GenerateQuests`' `RandomElement` draws inside the sim. Opening the shelf from
  `Window_ArchinityNetwork` instead moves the lazy `Init()` into `OnGUI`.
- **The shelf is lazy.** `CompQuestGiver.Use` creates the manager and calls `Init()` on first
  interaction, and `StorytellerWatcher.GameComponentTick` ticks only managers already in the
  dictionary **[V]**. A shop nobody has opened does not exist and does not rotate.
- **Two further silent config hazards, both [V]:** `CompProperties_QuestGiver.questManagerID` is a
  bare `int` keying `StorytellerWatcher.questGiverManagers`, so two comps sharing an id silently
  share one shelf built from whichever `QuestGiverDef` was used first; and with
  `generateOnce: true`, `AddQuestGiverManager` fills the shelf and `Use()` then calls `Init()`,
  filling it again — harmless only when `maximumAvailableQuestCount` is set.
- **No corpus example to copy.** `QuestGiverDef` appears in **zero XML files** across both roots,
  vanilla and the DLC **[V]**.

#### B — a per-entry pass on the shelf's tick

**What it gets us.** The three clauses A leaves open: an expired entry leaves; an entry that stops
being eligible leaves; an entry restocks on its own cadence.

**The seam is verified.** `VEF.Storyteller.StorytellerWatcher` is a `GameComponent` holding
`Dictionary<int, QuestGiverManager>` and calling `Tick()` on every manager every 60 ticks from
`GameComponentTick` **[V]** — simulation time on every client. `QuestInfo` already scribes
`tickGenerated`, `tickExpired` and `tickCompleted` **[V]**.

**The predicate has a shipped donor.** Royalty's permit card is a shelf whose entries each declare
their own eligibility and their own lifetime: `RoyalTitlePermitDef.AvailableForPawn` tests a
prerequisite permit, a point cost and `currentTitle.seniority >= minTitle.seniority`, and
`FactionPermit.OnCooldown` is `TicksGame < lastUsedTick + permit.CooldownTicks` over a per-entry
scribed tick **[V]**. `RoyalTitlePermitWorker_DropResources` is the entry that delivers goods
**[V]**. The architecture, not the currency.

**What it cannot do.** Nothing about authoring — A still supplies the entries — and it does not
fix the pay-for-nothing ordering, which is a guard in front of `ActivateQuest`.

**Consequences.** ⚠ **The pruning must not go in `AvailableQuests`.** That getter is reached from
`Window_Contracts.DoQuestsList` on every draw **[V]**; a time-dependent predicate there runs at a
different frequency on each client — a client with the window shut never prunes — and mutates
scribed state. VEF's existing null-prune is safe only because it is idempotent and
state-independent.

#### C — one gate node of ours

**What it gets us.** An entry whose XML says *"from the industrial era"* or *"once Influence ≥ N"*.
The donors are exact: `QuestNode_RequirementsToAcceptResearch` for a node that both fails
`TestRunInt` and attaches a re-checking part **[V]**, and
`QuestPart_RequirementsToAcceptPlayerWealth` for the numeric-threshold part — one `float`, a live
comparison, the threshold in the refusal message, a two-line `ExposeData` **[V]**. Twelve vanilla
subclasses of the abstract base exist to copy (`docs/engine/quests.md`).

**What it cannot do.** It does not remove the entry: `CanAcceptQuest` blocks the purchase and
`Window_Contracts.DoAcceptanceRequirementInfo` explains why — arguably the better shop behaviour,
but *leaving* the shelf still needs B.

**Consequences.** ⚠ **In Multiplayer the gate is advisory.** `Multiplayer.Client.SyncMethods`
registers `Quest.Accept`, not `CanAcceptQuest`, and `ActivateQuest` calls `Accept` directly **[V]**
(`docs/engine/quests.md`). A threshold over a shared balance must be re-checked *inside* the synced
call — which *Failure and recovery* already requires of `TrySpend`.

#### D — two shelves

Already specified below at *The Intel exchange*: `CurrencyExchangeExtension` carries `project`,
`maxIssued`, a purchase cooldown and an `ExchangeVenue.Available` check — per-entry eligibility and
per-entry lifetime on our own surface, free of every quest-shaped constraint. Its cost is that the
player learns two places to buy things, and that "a shop's stock" becomes two stocks.

#### E — reskin a vanilla trader — not recommended

`StockGenerator` carries `countRange`, `customCountRanges`, `totalPriceRange`,
`maxTechLevelGenerate`, `maxTechLevelBuy` and a `PriceType`, and `TradeabilityFor` falls through to
`ThingDef.tradeability` **[V]**. Per-entry tech gating and a visit-lifetime shelf exist. But the
shelf is priced in silver through `Tradeable`, the cadence belongs to the visit rather than the
entry, and **it cannot sell a quest at all** — which fails the requirement's load-bearing clause.
Listed so it is visibly considered.

### Available mechanisms

The survey behind the routes. Every line **[V]**.

**VFE Deserters, the named donor.** Its item shelf is `ContrabandManager`, a
`[StaticConstructorOnStartup]` static walking `DefDatabase<ThingDef>`, auto-attaching a
`ContrabandExtension` to anything carrying `CompProperties_Techprint` and deriving a missing
`intelCost` from `BaseMarketValue / 100`. `ContrabandExtension` has `category`, `countMult`,
`intelCost`, `useCriticalIntel`, `priority` — **no eligibility field and no lifetime field**. Every
eligible item is on the shelf permanently, from turn one. Its services shelf (`DeserterServiceDef`)
scales price by `WorldComponent_Deserters.Instance.VisibilityLevel.intelCostModifier` — saved state
moving a **price**, not an eligibility.

**And the donor already delivers a bought item as a quest, which is route A's precedent.**
`DeserterTabWorker_Contraband` finishes a purchase with
`QuestUtility.GenerateQuestAndMakeAvailable(VFED_DeadDrop, slate)` and an `availableTime` slate var,
or `DropPodUtility.DropThingGroupsNear` for rush delivery. `VFED_DeadDrop` is a `QuestScriptDef`
with `isRootSpecial`, `autoAccept`, a `QuestNode_WorldObjectTimeout` on `$availableTime` and a
`QuestNode_AddItemsReward`.

**VEF's quest-chain scheduler is a sibling mechanism, not this one.** `QuestChainExtension` is the
richest per-entry eligibility vocabulary in the corpus — `requiredResearch`,
`conditionSucceedQuests`, `conditionFailQuests`, `conditionSucceedQuestsCount`, `conditionEither`,
`conditionMinDaysSinceStart`, `isRepeatable`, `mtbDaysRepeat`, `grantAgainOnFailure/Success/Expiry`
with day ranges, `delayTicksAfterTriggering` — read by `GameComponent_QuestChains.TryScheduleQuest`
against a scribed history of `QuestInfo` outcomes. But it ends in `questDef.CreateQuest()` or a
`FutureQuestInfo`, both of which put the quest **straight into `Find.QuestManager`**. It never
touches `QuestGiverManager.availableQuests`. It is the donor for *what an eligibility clause can
say*, and the sibling half of #145.

**Vanilla.** No vanilla surface sells a quest (*The rest of the corpus, and vanilla*, unchanged).
Royalty's permit card is the nearest shipped shelf with per-entry eligibility and per-entry
cooldown, and its entries are aid effects and resource drops.

**Multiplayer.** `Multiplayer.Compat.VanillaExpandedFramework` reaches `VEF.Storyteller` at exactly
four points, all inside `PatchQuestChainsDevMode`: `QuestChainsDevWindow:ViewQuestChains`,
`GameComponent_QuestChains`'s `quests`/`futureQuests`, `QuestInfo:Quest`,
`FutureQuestInfo:questDef`, with two debug-only synced methods. `ActivateQuest` and
`QuestGiverManager` appear nowhere in the assembly.

**The wide pass**, both roots plus vanilla and the DLC, `-a -g '*.dll' -g '!**/obj/**'
-g '!**/Referenced/**'`, attributed through `tools/corpus.py --which -`; the UTF-16 half run as a
hand-typed null-interleaved literal, never through `$(…)`, validated on
`V\x00E\x00F\x00.\x00A\x00v\x00a\x00i\x00l\x00a\x00b\x00l\x00e\x00C\x00o\x00n\x00t\x00r\x00a\x00c\x00t\x00s\x00`:

- `QuestGiverDef` → **Vanilla Expanded Framework only**, 10 paths across both roots.
- `acceptanceExpireTick` → **VFE Deserters only**. One mod in the corpus touches vanilla's
  per-offer expiry field. The interleaved half returns zero, consistent with a field reference in
  `#Strings`.
- XML `QuestGiverDef` → **zero files**; `questgiver` case-insensitive → zero;
  `SetTicksUntilAcceptanceExpiry` → zero (vanilla uses `expireDaysRange` on the def).
- XML `ContrabandExtension` → VFE Deserters only.
- Shop-shaped def families (`ShopDef`, `VendorDef`, `PurchaseDef`, `CatalogDef`, `CatalogueDef`,
  `StoreDef`, `OfferDef`, `ShopEntry`, `MerchandiseDef`, case-insensitive) → all zero but two
  `StoreDef` hits that are keyed translations.
- `CanAfford` → two unrelated mods. No third currency-shop implementation in the corpus.

### Status

**Evidence class: READ.** Mechanisms **[V]**; routes A–E **[I]** as compositions. From
[#144](https://github.com/cjd721/Rimworld-Archinity/issues/144).
[#106](https://github.com/cjd721/Rimworld-Archinity/issues/106) and
[#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) were both re-read and their
mechanisms stand.

### Open questions

| Question | Owner |
|---|---|
| An entry that becomes ineligible — does it **leave**, or stay visibly locked with the reason shown (which vanilla's `QuestPart_RequirementsToAccept` gives free)? | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map) — [`QUESTS.md`](../requirements/QUESTS.md) § *Shops* allows either |
| Where the per-entry pruning attaches, and what it stores per entry beyond `QuestInfo.tickGenerated` | Build map, on selection |
| Whether route C's node also attaches a re-checking part, or gates at generation only | Build map, on selection |
| What `QuestGiverManager.CallWindow`'s `Find.WindowStack.Add` does under Multiplayer from the synced toil — one client or both. Moot if the shop opens from a main tab; settled by two clients, not by reading | Unowned |
| Which item entries exist, and what each one's eligibility clause and shelf life say | [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) |

---

## A failed bought quest returns to the shop

### Purpose and scope

Answers [`docs/requirements/QUESTS.md` § *Shops*](../requirements/QUESTS.md): *a bought quest can
fail without stalling its plot line; whether it returns to the shop, and whether free or at its
price again, is not decided.* This section says what is possible. Established on
[#145](https://github.com/cjd721/Rimworld-Archinity/issues/145).

**This section owns:** what counts as a bought quest failing, what can observe it, and every way
the entry can come back, free, paid again or refunded, set per entry.

**It does not own:**
- The shelf, the currency pair and `ActivateQuest`: *The purchasable quest catalogue*
  ([#106](https://github.com/cjd721/Rimworld-Archinity/issues/106)).
- Entry eligibility and shelf life: *Shop entries*
  ([#144](https://github.com/cjd721/Rimworld-Archinity/issues/144)).
- Whether a failed Schism blow is paid again, refunded or free: this section supplies the
  mechanism for every answer; which ships is the build map's
  ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)).
- Which entries return and at what price: [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117)
  and authoring.

### Verdict

- **Possible? Yes, with one small piece built.** No **currency shop** in the corpus returns a
  failed bought quest **[V]**. VEF forgets a quest as soon as it is sold: `ActivateQuest` removes
  its `QuestInfo` and keeps no record of it **[V]**. The nearest shipped return is Medieval
  Overhaul's quest finder. It records a quest as done only on `Success`, so an `onlyOnce` quest
  that failed can be found again and paid for again with scanner work **[V]**. Every failure ends
  in `CleanupQuestParts`, which a part inside the quest hears without Harmony. A `QuestPart` of ours, attached at purchase, can put a **fresh roll
  of the same `QuestScriptDef`** back on the same shelf. It can be free (`currencyInfo = null`,
  which VEF already draws and sells as free) or priced again **[V seams; route I]**. The *same*
  quest object can never return: an ended quest cannot be accepted again, and selling it would
  take payment for nothing **[V]**. Free, paid or refunded is a data field per entry.
- **Multiplayer? Yes for A, B and D.** A quest ends inside the simulation on every client. The
  restock is a state change driven from there, and generation draws `Rand` in the simulation. No
  new synced method is needed **[I, from V parts]**. **C needs care:** VEF's `LoadedGame`
  scheduling pass runs on a joining client and not on the host.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A — Restock the shelf with a fresh roll** | The failed entry reappears in the same shop, free or at a price, after an optional delay, set per entry | Ours: one `QuestPart` on the end seam + VEF `QuestGiverManager.AvailableQuests` | C# + XML policy | Medium | Yes |
| **B — Refund on failure, no restock** | The spent Influence or Intel comes back, in full or in part. The entry does not return, or returns through A | Ours: the same part + `Currencies.Credit` | C# + XML policy | Medium (shares A's part) | Yes |
| **C — Re-grant outside the shop** | A free copy arrives as an ordinary quest offer after N days. No shop, no price | VEF `QuestChainExtension.grantAgainOnFailure` | XML | Easy | With care: `LoadedGame` runs only on a joining client. See C. **Not recommended for plot entries** |
| **D — The Schism re-offers its step** | The ordered chain's current step is regenerated on failure, paid again or free by policy | *The Schism catalogue* route A (VFED donor) | C# + XML | Medium, already specified | Yes |
| **E — Adopt VFE Deserters' shop as shipped** | Plot steps regenerate and are paid again. **Service missions never return** | VFED | patch | Hard to fit — **not recommended** | Yes |

**Blocked by an engine fact: re-adding the same `QuestInfo`.** `Quest.State` is computed from a
private `ended` flag that nothing resets. `Quest.Accept` is wrapped in
`if (State == QuestState.NotYetAccepted)`. `ActivateQuest` still charges and sends the letter
when that check fails, so re-shelving the ended quest would **take payment and start nothing**
(*Shop entries* § A, consequences) **[V]**. So "the same entry" always means *the same script,
rolled again*.

**Recommend A, with B's refund as a per-entry mode of the same part.** D is A applied to the
chain's current step and needs nothing extra. C is the cheapest way to make a free, shopless
return possible. It fits side content, not a plot entry, because of its hazards (below). The policy
is not selected here. For the Schism it is
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s, because #122 is closed. For
everything else it is authoring's. Medieval Overhaul is the donor for keying the policy on a
`DefModExtension` on the quest script.

#### What ends a bought quest as failed

All **[V]**, `Assembly-CSharp.dll` 1.6:

- **Every outcome end goes through one method.** `Quest.End(QuestEndOutcome, sendLetter,
  playSound)` sets `ended` and `endOutcome`, then calls `CleanupQuestParts()`. `State` then
  reads `EndedFailed` for `Fail`, `EndedSuccess` for `Success`, `EndedInvalid` for
  `InvalidPreAcceptance`, and `EndedUnknownOutcome` otherwise. **Offer expiry skips `End`:**
  `Quest.QuestTick` calls `CleanupQuestParts()` directly on an unaccepted offer whose clock ran
  out. A bought quest is accepted at purchase, so this cannot happen to it. It does matter for
  choosing a seam.
- **Almost always through a part on a signal.** `QuestPart_QuestEnd.Notify_QuestSignalReceived`
  calls `quest.End(outcome)` on its `inSignal`, taking the outcome from the part or from the
  signal's `OUTCOME` argument. `QuestGen_End.End` is the builder every root uses.
  `QuestNode_Root_Mission`'s fail triggers are `shuttle.Killed`, `shuttle.LeftBehind`, the
  shuttle-leave delay and one further `inSignal` pass. `QuestNode_Root_WorkSite` fails on the site's own
  signal. `QuestPartUtility`'s world-object timeout emits `OUTCOME = Fail`.
  `QuestPart_QuestEndParent` ends a parent from a child.
- **A few direct calls, and most of them end `Unknown`, not `Fail`.**
  `MoveColonyUtility.MoveColonyAndReset` (Archonexus) and `Precept_Relic` end quests `Unknown`
  with no letter. `RoyalTitleUtility` ends quests `InvalidPreAcceptance`.
  `GameComponent_Anomaly` ends a quest `Unknown`, and `QuestPart_SpawnMonolith` ends one `Fail`.
- **The accepter dying is not a failure condition in general.** `AccepterPawn` is read by
  `QuestPart_GiveRoyalFavor`, the refugee delayed reward and the quest tab. None of them ends a
  quest. A pawn's death fails a quest only where that script wires its own signal.
- **The player cannot abandon an accepted quest.** `MainTabWindow_Quests` has no `End` call. The
  only way out of a bought quest is its own script.
- **Expiry does not apply after purchase.** `State` reads `EndedOfferExpired` only while
  `acceptanceTick < 0`, and `ActivateQuest` accepts at once.

**So "failed" is a choice of outcome set.** Only `EndedFailed` is certain. VFED re-offers on
`EndedFailed` **or** `EndedInvalid` (`Notify_PlotQuestEnded`: `state - 5 <= 1`) **[V]**. A script
whose loss path ends `Unknown` would never trigger a restock keyed on `Fail`. Which outcomes count
is a per-entry parameter.

#### What can observe it

| Seam | How | Harmony | Evidence |
|---|---|---|---|
| **A part of ours inside the bought quest** | `CleanupQuestParts` calls `Notify_PreCleanup()`, then `Cleanup()`, on every part after `ended`/`endOutcome` are set. The part reads `quest.State`. It also hears expiry | None | [V] `Quest.End`, `Quest.CleanupQuestParts`, `Quest.QuestTick` |
| **Postfix on `Quest.End`** | Look the quest up in our own registry of bought quests. **Never hears expiry** | 1 patch | [V] shipped four times: VFED `MiscPatches.CheckForPlotEnd`, VFEE `Patch_Quest_End`, Medieval Overhaul `MedievalOverhaul.Patches.Quest_End` (postfixes), VEF `VanillaExpandedFramework_Quest_End_Patch` (prefix) |
| **Prefix on `Quest.CleanupQuestParts`** | Same, reading the private `endOutcome`. Hears expiry | 1 patch | [V] VEF `VanillaExpandedFramework_Quest_CleanupQuestParts_Patch` (it routes expiry to `QuestExpired`) |
| **Polling `quest.State`** | Checking a held quest's state on a tick | None | [V] vanilla `StorytellerComp_RefiringUniqueQuest` (refires `refireEveryDays` after `cleanupTick` unless `EndedSuccess`); `QuestPart_SubquestGenerator` (`docs/engine/quests.md`, from #151) |
| Medieval Overhaul's quest finder | `GameComponent_QuestFinder.Notify_QuestComplete`, called from its `Quest.End` postfix, records `completed` only on `Success`. `CompQuestFinder.CanFind` then keeps a failed `onlyOnce` script (`QuestInformation` extension) in `AvailableForFind` | — | [V] `…/3219596926/1.6/Assemblies/MedievalOverhaul.dll` |
| `QuestManager` notify hooks | **None for quest end.** Its `Notify_*` cover pawn discarded or killed or born, things produced, plants harvested, faction removed | — | [V] |
| A signal | **`End` sends none.** Only the script's own trigger signals exist, and each script names them differently | — | [V] |
| VEF's quest-giver tracking | **None after purchase.** `ActivateQuest` ends in `availableQuests.Remove(questInfo)` | — | [V] |
| VEF's chain tracking | Records only quests whose root carries `QuestChainExtension` (`QuestManager.Add` postfix → `CleanupQuestParts` prefix → `QuestCompleted`) | — | [V] |

**The part is the natural seam, and it can be attached without Harmony or XML.**
`CurrencyQuestCurrencyInfo.Buy(QuestInfo)` is ours. It runs inside the synced `ActivateQuest`,
after `Accept`, holding the `Quest` and the price, and `Quest.AddPart` is public **[V]**. The
alternative is a `QuestNode` of ours placed in each entry's script. Either way the part must be a
**top-level** part. `QuestPart_Choice.Choose` runs `Notify_PreCleanup`/`Cleanup` on the parts of
the options that were not chosen (`docs/engine/quests.md` § *Reward choices*). A part inside a
choice is cleaned up at purchase. Gating on `State == EndedFailed` makes that harmless, not
correct.

#### A — restock the shelf with a fresh roll

**What it gets us.**
- **The same shop, the same script, a new roll.** `QuestGiverManager.AvailableQuests` returns
  the live list, so appending a `QuestInfo` is a public call **[V]**. The part runs
  `QuestGen.Generate(quest.root, slate)` and builds the entry. For a priced return it goes
  through our `CurrencyQuestCurrency.Allows`. For a free one it builds a
  `new QuestInfo(q, faction, null, onlyOneChoice: true, saveQuestDeeply: true)`.
- **Free return with no UI work.** With `currencyInfo == null`, `Window_Contracts` skips the price
  label, and `ActivateQuest`'s `currencyInfo?.Buy` charges nothing **[V]**. A "returned" badge is
  one row in `Window_ArchinityNetwork`.
- **Paid return at the old price or a new one.** The part can carry the original
  `QuestCurrencyInfo.amount` and reapply it, or let `Allows` price the new roll.
- **Delay and count.** The part can store a return tick, which a manager tick checks. It can also
  carry a return count across rolls, for example *free once, then paid*.
- **The Schism for free.** Route D is this mechanism applied to the chain's current step.

**What it cannot do.**
- **Return the same quest.** Site, reward, choice and pawns are all rolled again. `QuestInfo`'s
  constructor also re-draws the displayed choice **[V]**.
- **Outlive a rotating shelf.** `Reset()` is `Clear()` then regenerate **[V]**. On a giver with
  `resetEveryTick` set, a returned entry lasts until the next rotation. Standing returns need a
  standing giver or *Shop entries* route B.
- **Guarantee a roll.** `CanRun` may no longer pass: a research gate, `QuestNode_QuestUnique`, or a
  faction gone. `QuestGen.Generate` can throw. Our call is not wrapped by VEF's silent catch
  (**T-77**), so a throw is loud unless we catch it. Refunding (B) is the fallback.

**Consequences.**
- ⚠ **Free returns are a reward re-roll.** A player who fails a bought quest on purpose draws a
  new reward for nothing. The protections are paid-again, a delay, or a return cap. That choice
  is balance ([#117](https://github.com/cjd721/Rimworld-Archinity/issues/117)).
- **`maximumAvailableQuestCount`.** A returned entry either takes a slot or goes over the cap.
  `GenerateQuests` fills only up to `max − Count` **[V]**, so going over is harmless but
  permanent until something is bought.
- **Generating inside `End`.** VFED calls `QuestGen.Generate` from inside its `Quest.End`
  postfix **[V]**, so this is shipped practice. Moving it to the next
  `StorytellerWatcher.GameComponentTick` is a build choice.
- **The shelf must exist.** Managers are lazy. A quest was bought through this one, so it exists,
  but the part must look it up by `questManagerID` in `StorytellerWatcher.questGiverManagers`
  **[V]**, not hold a reference across a save.

**Multiplayer.** Every `End` caller found is a tick-driven part, a signal, or a utility reached
from a player action (`MoveColonyAndReset`). The quest tab cannot end a quest **[V]**. Player
actions and the signals they cause (a shuttle launch) reach the simulation through Multiplayer's
own synced commands **[I]**. The restock runs on both clients in the same tick, and
`QuestGen`'s and `QuestInfo`'s `Rand` draws happen in the simulation. **No new `SyncMethod`**
**[I]**. It inherits #106's one registration on `ActivateQuest` unchanged.

#### B — refund on failure

**What it gets us.** The part credits back `amount × refundFraction` through this document's
`Credit`, with a message. Uses: *the network makes good a failed job*, a partial refund, or a
refund when a roll fails. **Cannot:** return the entry. Combine it with A for that.
**Consequence:** a full refund combined with a free return pays the player to fail. A policy
validator refuses that pair. **MP:** the same as A. `Credit` is an in-sim mutation, never a UI
call **[I]**.

#### C — re-grant outside the shop — not recommended for plot entries

**What it gets us.** Pure XML. On an entry's `QuestScriptDef`, VEF's
`QuestChainExtension.grantAgainOnFailure: true` + `daysUntilGrantAgainOnFailure` works like this.
`ActivateQuest`'s `QuestManager.Add` triggers VEF's postfix, which records the quest. On
`Fail`, `CleanupQuestParts`'s prefix calls `QuestCompleted` → `TryGrantAgainOnFailure` → a
`FutureQuestInfo` → `QuestUtility.GenerateQuestAndMakeAvailable` **[V]**. The copy is free and
arrives as an ordinary offer.

**What it cannot do.** It cannot return to the shop or carry a price. It reacts only to `Fail`, not
`Invalid` or `Unknown`.

**Consequences, all [V]:**
- ⚠ **The extension also hands the entry out free at game start** (**T-153**). `StartedNewGame`/`LoadedGame`
  → `TryScheduleQuests` reaches `quest.CreateQuest()` for any script carrying the extension that
  no gate stops. Offers held on the shop shelf are not in `QuestManager`, so the live-duplicate
  check cannot see them. `TryGrantAgainOnFailure` does **not** re-check `requiredResearch`. So a
  `requiredResearch` that is never finished blocks the free start grant and still allows the
  re-grant **[I composition]**. A hack, stated as one.
- The re-granted offer carries the script's own acceptance expiry. VEF's expiry handling is broken
  (**T-72**, **T-73**), and a chain-granted quest skips `TestRun` (**T-71**).

**Multiplayer: with care.** The failure path is in the simulation. It runs `CleanupQuestParts`,
and the `FutureQuestInfo` fires from `GameComponentTick`, including its `Rand.MTBEventOccurs`
**[V]**. **`LoadedGame` is the exception.** It runs `EnsureAllQuestChainUniquePawns()` and
`TryScheduleQuests()` **[V]**. A client joining a running game loads the save and runs both. The
host, already in the game, does not **[I, Multiplayer's join-by-load]**. MP Compat's VEF entry
does not touch either one (*Shop entries* § Multiplayer).
- **Harmless when no chain script can schedule at that moment.** Every `TryScheduleQuest` exits at
  a gate before any `Rand`: `requiredResearch` unfinished, already pending, already live, or not
  repeatable and already recorded **[V]**. The unique-pawn pass must also find its pawns already
  made. Route C's own entries pass this test by construction, because their `requiredResearch`
  gate never opens.
- **A desync when anything can schedule.** Take a chain script whose conditions became true since
  the last scheduling pass. On the joining client, `CreateQuest` or a `RandomInRange` delay runs
  and the host never runs it. The risk is the whole load order's chain scripts, not just ours.
  #158 inherits it if it uses VEF chains.

#### D — the Schism re-offers its step

Already specified: *The Schism catalogue* § Route A. VFED's donor regenerates the same index on
`EndedFailed`/`EndedInvalid` and makes the player pay again **[V]**. Free, paid again or refunded
is route A's or B's part applied to the step. The re-offer itself needs nothing new.

#### E — adopt VFED's shop — not recommended

VFED's `ServiceQuests` shelf has **no return**. `EnsureQuestListFilled` only tops it up to 10,
and no end handler reads `ServiceQuests` **[V]**. Its plot re-offer is D's donor, and D already
rejected adopting it (*The Schism catalogue* § Route D). Note also that a plot quest ending
`Unknown` matches neither branch of `Notify_PlotQuestEnded`, so the step is never re-offered
**[V]**. Route D must not copy that gap.

### Per-entry policy — where the flag lives

The policy has four fields: which outcomes count (`Fail` / `+Invalid` / `+Unknown`); the mode
(`none` / `free` / `paid` / `refund`, and refund combines with a return); a delay; a cap. Every
home below is authored in **XML** and read by **our C#**:

| Home | Scope | Note |
|---|---|---|
| A `DefModExtension` on the entry's `QuestScriptDef` | One policy per script, wherever it is sold | Simplest. **T-06**: a second extension of the same type is inert |
| A field on our `CurrencyQuestCurrency`, keyed by script | Per shelf: the same script can return free from one shop and paid from the other | `QuestGiverDef.currency` is already polymorphic (`Class=`) **[V]** |
| A `QuestNode` of ours in the script | Per branch or variant, can read the slate | Also the attach point if `Buy` does not attach the part |
| `QuestGiverDef` | **No field exists** **[V]**. It would mean a def subclass | Not worth it: the currency object already carries per-shelf data |

### Available mechanisms

Every line **[V]**. `VEF.dll` = `…/294100/2023507013/1.6/Assemblies/VEF.dll`; `VFED.dll` =
`…/3025493377/1.6/Assemblies/`; `VFEEmpire.dll` = `…/2938820380/1.6/Assemblies/`.

- **Vanilla:** `Quest.End`, `Quest.State`, `Quest.Accept`, `Quest.CleanupQuestParts`,
  `Quest.AddPart`, `Quest.QuestTick`; `QuestState` / `QuestEndOutcome`; `QuestPart.Notify_PreCleanup`
  / `Cleanup`; `QuestPart_QuestEnd`; `QuestManager.Add` / `Remove` / `QuestManagerTick` / its
  `Notify_*` set; and the direct `End` callers listed above.
- **VEF:** `QuestGiverManager.ActivateQuest` / `AvailableQuests` / `Reset` / `GenerateQuests`;
  `QuestInfo` (constructor, fields, `ExposeData`); `QuestWorker.GenerateQuests`;
  `StorytellerWatcher.questGiverManagers`; `Window_Contracts` null-`currencyInfo` draw;
  `GameComponent_QuestChains.QuestCompleted` / `TryGrantAgainOnFailure` / `TryScheduleQuest`;
  `FutureQuestInfo.TryFire`; `QuestUtils.CreateQuest`; the `QuestManager.Add`, `Quest.End` and
  `Quest.CleanupQuestParts` patches.
- **VFED:** `WorldComponent_Deserters.Notify_PlotQuestEnded` / `GeneratePlotQuest` /
  `EnsureQuestListFilled`; `HarmonyPatches.MiscPatches.CheckForPlotEnd`.
- **VFEE:** `Patch_Quest_End`, a success-only postfix, as a `Quest.End` precedent.
- **Medieval Overhaul** (`…/3219596926/1.6/Assemblies/MedievalOverhaul.dll`):
  `Patches.Quest_End` → `GameComponent_QuestFinder.Notify_QuestComplete`, which adds to
  `completed` only on `Success`. `CompQuestFinder.CanFind` refuses an `onlyOnce` script only once
  it is `Completed`. `QuestInformation` is the per-script `DefModExtension` (`onlyOnce`,
  `WorkTillTrigger`, `requiredLinkable`, `LinkablesNeeded`). A finder-issued quest goes out
  through `QuestUtility.GenerateQuestAndMakeAvailable`. **The only shipped fail-then-return**:
  the price is scanner work, not a currency, and the return is a fresh generation.
- **Vanilla, polling:** `StorytellerComp_RefiringUniqueQuest` refires a unique quest
  `refireEveryDays` after `cleanupTick` unless it ended `EndedSuccess`, `Ongoing` or
  `NotYetAccepted`. That makes it a free fail-then-return with no shop.

**The wide pass**, both roots, `-a -g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'`, attributed
through `tools/corpus.py --which -`:
- ASCII, case-insensitive: `grantAgainOn` → VEF only; `ReturnOnFail|RetryOnFail|OnQuestFailed|
  QuestFailed|Notify_QuestEnded|Notify_QuestFailed|QuestEnded` → only VFED's
  `Notify_PlotQuestEnded`, VFEE's `questEnded`/`questEndedSignal` and 1.2–1.4 Achievements
  Expanded; `restock|requeue|reoffer` and `refund` → trader, vehicle, building and fuel restocks
  and refunds, **none on a quest**.
- UTF-16, hand-typed null-interleaved, validated on `questDeep` (VEF, both roots):
  `grantAgain` → zero (VEF reads it by XML reflection, not a literal);
  `onFail|retry|reoffer|requeue` → Mining Outpost's KCSG retries and RimPacts' `retryCount`,
  **none on a quest**.
- **Missed by these patterns, found in review:** Medieval Overhaul's `Notify_QuestComplete`,
  above. The name-based sweep did not reach it. A sweep of `Quest.End` patches would have: the
  `HarmonyPatch(typeof(Quest), "End")` attribute sites. **Residual:** a return-on-fail named
  some other way, outside a `Quest.End` or `CleanupQuestParts` patch.

### Status

**Evidence class: READ.** Mechanisms **[V]**. Routes A–E **[I]** as compositions. From
[#145](https://github.com/cjd721/Rimworld-Archinity/issues/145).
[#106](https://github.com/cjd721/Rimworld-Archinity/issues/106)'s `ActivateQuest` order and
[#132](https://github.com/cjd721/Rimworld-Archinity/issues/132)'s re-offer were re-read and stand.
The return runs on the quest-**end** seam, not *Shop entries*' route B tick;
`grantAgainOnFailure` is route C, which re-grants *outside* the shop.

### Open questions

| Question | Owner |
|---|---|
| Does a failed bought quest return, and free, paid again or refunded, per entry or everywhere? | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map) — [`QUESTS.md`](../requirements/QUESTS.md) § *Shops* allows either; routes A–E above |
| Which outcomes count as failure: `Fail` only, or also `Invalid` / `Unknown` | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119), with the answer above |
| Delay, return cap, refund fraction; whether free returns are capped against reward re-rolling | [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) |
| Attach in `Buy` or by a `QuestNode`; restock inside `End` or on the next tick; skip `CanRun` on a return or refund instead; old price or new | Build map, on selection |

---

## The build

**One implementation, two `CurrencyDef` rows in one store, and it is ours to write** — the
named donor holds no currency to donate. See *Available mechanisms*.

The build is **one `WorldComponent_Currencies` holding one `Dictionary<CurrencyDef,int>`**;
Influence and Intel are two *rows* in that dictionary, under one `Scribe` key, in one
component. Nothing is instanced twice. [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)
has ruled on that coupling — see *What is shared*, which states what the sharing does and does
not imply.

Everything lands in the single assembly we already ship, `ArchinityAltar.dll`, namespace
`Archinity.Core` (`CODING_STANDARDS.md` § *Hard constraints*). No second assembly.

### Mechanism

Two new `Def` types and one `WorldComponent`. **The currency is a `Def`**, which is the
whole reason one implementation serves two fictions — and would serve a third.

```
CurrencyDef : Def
    label, description, iconPath, color, Texture2D Icon (resolved in PostLoad)

CurrencyPurchaseDef : Def
    CurrencyDef currency
    int         cost
    Type        workerClass      -> CurrencyPurchaseWorker
    CurrencyPurchaseDef prerequisite
    float       cooldownDays
    int         uiOrder
    CurrencyCategoryDef category

CurrencyPurchaseWorker (abstract)
    CurrencyPurchaseDef def
    virtual int      Cost => def.cost         // overridable — see The purchasable quest catalogue
    AcceptanceReport CanPurchase(Map map, Thing at)   // map/at null for context-free entries
    void             Purchase(Map map, Thing at)
```

> **`Cost` is `virtual` rather than a bare read of `def.cost`, and that is
> [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106)'s one amendment to
> this design.** A purchasable quest's price is *derived from the quest that was
> generated*, not authored — the donor computes it from the offered rewards' market
> value **[V]**. A fixed `int` cannot express that. Making the worker the authority on
> its own price costs five lines here and removes the only reason #106 would have
> needed a catalogue mechanism of its own. Every other entry ignores the override and
> reads `def.cost`.

`CurrencyPurchaseDef` is modelled on vanilla **`RimWorld.RoyalTitlePermitDef`**, which is
the same idea — a Def-driven catalogue of favors with a worker per entry — and already
carries `workerClass`, a cost, `prerequisite`, `cooldownDays` and a UI position **[V]**.
Taking the shape from vanilla rather than from `VFED.DeserterServiceDef` costs nothing and
buys no VFE dependency.

Two `CurrencyDef`s ship: `Archinity_Influence` and `Archinity_Intel`. Adding a third is
one XML file.

### Where state lives

`WorldComponent_Currencies`, holding exactly three dictionaries:

```csharp
private Dictionary<CurrencyDef, int>         balances;
private Dictionary<CurrencyPurchaseDef, int> lastPurchasedTick;   // cooldowns
private Dictionary<CurrencyPurchaseDef, int> purchaseCount;       // issued items — added by the Intel exchange
```

`purchaseCount` is the *"issued instruction items"* record
[`GLITTERTECH.md` § *Saved state and remaining work*](../requirements/GLITTERTECH.md) asks for.
It is per purchase, exactly like `lastPurchasedTick`, and names no project, chapter or quest.

**Nothing else lives here, and that is the design.** No campaign index, no chapter, no
quest reference. See *Structural separation*.

Public surface — the whole of it:

```csharp
int  Balance(CurrencyDef c);
bool CanAfford(CurrencyDef c, int amount);                  // pure; safe from a draw method
bool TrySpend(CurrencyDef c, int amount, string reason);    // mutating; Job or synced callers only
void Credit(CurrencyDef c, int amount, string reason);
[SyncMethod] void TryPurchase(CurrencyPurchaseDef purchase, Map map, Thing at);   // map/at null for context-free entries
```

### What changes it

**Credit A — a mission pays.** `Reward_Currency : RimWorld.Reward` emitting
`QuestPart_GrantCurrency`, with `QuestNode_GrantCurrency` for hand-authored quests.
`RimWorld.Reward` is abstract with exactly three abstract members — `InitFromValue`,
`GenerateQuestParts`, `GetDescription` — plus `StackElements` and `TotalMarketValue`
**[V]**. `VFED.Reward_Visibility` is the working precedent for a non-item reward and uses
only vanilla API **[V]**.

So one mission family can pay differently by approach — a covert operation offers a
`Reward_Currency` for Influence, a public miracle offers Reverence, and both rows appear in the
same quest-choice list.

**Credit B — an artifact is analysed.** [`RESEARCH.md`](RESEARCH.md) § *Destructive artifact
analysis* route A ([#115](https://github.com/cjd721/Rimworld-Archinity/issues/115)) calls
`Credit` from an `IThingStudied` comp on the study job's tick, so a long, interruptible
analysis pays as it goes and consumes the artifact at the end.

`CompUseEffect_GainCurrency` (`{CurrencyDef currency, int amount}`) on the artifact's
`ThingDef`, paired with vanilla `CompUseEffect_DestroySelf`, is that section's route D — a
one-shot use item, **not recommended** for a long job because interruption loses all
progress. Its template is `RimWorld.CompUseEffect_FinishRandomResearchProject`, a 25-line
`CompUseEffect` subclass overriding `DoEffect(Pawn)` and `CanBeUsedBy(Pawn)` to mutate global
game state **[V]**.

**Credit C — optional site lore.** A `Study` override calling `Credit(CurrencyDef, int,
string)` directly, per [`CHARTING.md`](CHARTING.md) § 10 — **not** a use-effect comp.
`CompUseEffect_GainCurrency` fires only from `CompUsable` / `JobDriver_UseItem`, and
`VEF.Buildings.StudiableBuilding.Study` never reaches either **[V]**; a studiable object
carrying that comp would simply never pay. The alternative on this route is
`QuestPart_GrantCurrency` on a site-completion signal. This is the requirement that
*"optional investigation can provide Intel progress"* — which is why Intel must be a
number and not an item, since curiosity cannot spawn loot.

**Debit.** `TrySpend`, reached only from `TryPurchase` or from a Job. Never from a draw
method. **For Intel there are exactly two debit sites:** the exchange (*The Intel exchange*,
below) and the #106 quest catalogue's `CurrencyQuestCurrencyInfo.Buy`. No `ResearchProjectDef`,
hacking project, bill or analysis job reaches `TrySpend(Archinity_Intel, …)` — checkable by
grep, and required by [`GLITTERTECH.md`](../requirements/GLITTERTECH.md): *"Research does not
spend Intel directly."*

### Where the player sees it

**D1 — the catalogue, with the balance in it.** A `MainTabWindow` subclass reached by a
`MainButtonDef`. `MainButtonDef` carries `workerClass` (defaulting to
`MainButtonWorker_ToggleTab`) and `tabWindowClass`, both `System.Type` fields that
`Verse.ParseHelper` resolves from a plain XML string, and `MainButtonsRoot` orders
`DefDatabase<MainButtonDef>.AllDefs` by `order` in its constructor **[V]** — so the button
itself is **XML only, no C#**.

Layout template: **`RimWorld.MainTabWindow_Research`'s Anomaly knowledge readout** — two
persistent category balances drawn above a catalogue of things to spend them on, each with
a category icon and colour **[V]**. That is this window's exact shape. (The *readout code*
is in `Assembly-CSharp.dll` and is [V]; the Anomaly *content* it draws is not on disk here —
see *The wide pass*. Copying the layout does not require the DLC.)

> Set `minimized: true` on the `MainButtonDef`. `MainButtonsRoot.DoButtons` divides the
> screen width by total button weight, so every added tab shrinks every existing one;
> `minimized` halves the weight **[V]**.

**D2 — the payoff, before the player accepts.** Free. `Reward_Currency.StackElements`
returns `QuestPartUtility.GetStandardRewardStackElement(label, icon, tipGetter, onClick)`,
vanilla's own reward-row helper **[V]**.

**D3 — the always-visible number.** A Harmony postfix on
**`RimWorld.GlobalControlsUtility.DoDate(float leftX, float width, ref float curBaseY)`** —
`public static`, with the running y **by ref**, which is how vanilla's own rows stack
**[V]**. The postfix draws a 26px row at `curBaseY - 26f` and decrements. `DoDate` is
called from both `GlobalControls.GlobalControlsOnGUI` and
`RimWorld.Planet.WorldGlobalControls.WorldGlobalControlsOnGUI`, so one postfix covers map
and world view **[V]**.

> `GlobalControls.GlobalControlsOnGUI()` itself is a dead end — `void`, no arguments,
> running y is a local **[V]**. The seam is one level down.
>
> In world view `DoDate` is guarded by `Current.ProgramState == Playing && (Find.CurrentMap
> != null || Find.WorldSelector.AnyObjectOrTileSelected)` **[V]**. If the row must show on
> the world map with nothing selected, postfix `DoTimespeedControls` instead.
>
> **Eight mods in the corpus carry the name `GlobalControls` in a 1.6 assembly** — RimFantasy,
> VPE, Facial Animation, Replace Stuff, Faction Customizer, Compositable Loadouts, Multiplayer
> and Multiplayer Compatibility — and that is a **`#Strings` metadata-name hit, which is
> [I]**, not evidence of a patch. **One of the eight demonstrably patches
> `GlobalControlsOnGUI`**: Faction Customizer, which carries `GlobalControlsOnGUIPrefix`
> **[V]**. The rest are bare type references. **None of the eight is a currency readout**
> **[I]**.
>
> VFE Power's only hits are in its **1.2** and **1.3** assemblies and Medieval Overhaul's only
> hit is in its **1.5** assembly; neither ships a 1.6 copy carrying the name **[V]**, so
> neither is in this game's stack. **A hit is evidence only if it is in the assembly 1.6
> loads.**
>
> The contention this seam creates is **additive by construction rather than by survey**: the
> parameter is `ref float curBaseY`, so any patcher that draws a row must decrement it, and
> rows stack rather than collide **[V]**. Which row sits above which is patch order **[I]**.

**Optionally D4 — a number on the tab button.** `MainButtonWorker.DoButton(Rect)` is
`public virtual` **[V]**; subclass `MainButtonWorker_ToggleTab`, call `base.DoButton(rect)`,
then label the integer. `MainButtonWorker.ButtonBarPercent` exists but renders a fill bar,
not a number **[V]**.

**Ruled out: `RimWorld.ResourceReadout`.** Both of its paths key every row on a `ThingDef`
and pull the count from `map.resourceCounter`, and `ResourceCounter.UpdateResourceCounts()`
clears and rebuilds `countedAmounts` from map contents on a tick, so an injected value is
overwritten **[V]**. A pure number cannot live there.

> This is the one place the item-versus-number choice has a visible price. An
> **item-backed** currency gets the top-left readout for free — `ThingDef.resourceReadoutPriority`
> plus `resourceReadoutAlwaysShow`, with `CountAsResource => resourceReadoutPriority !=
> Uncounted` **[V]** — and D1/D3 would not need writing. We pay that cost deliberately,
> because the requirements put Intel in two places an item cannot go: *"Intel progress"*
> granted by inspecting site lore, and a saved *"Intel balance"* distinct from stockpile
> contents. See *Available mechanisms*.

### The Intel exchange — a balance into an Instruction item

This is *Shop entries* route D. [#144](https://github.com/cjd721/Rimworld-Archinity/issues/144)
recommends route A (one shelf) for items; which ships is the build map's
([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)). The venue split
(table/faction) below applies to either.

From [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54). The rule, from
[`GLITTERTECH.md` § *Intel Is Capability, Not Exposition*](../requirements/GLITTERTECH.md):
research never spends Intel; *"at an authored table or through an appropriate faction —
potentially the Traders Guild — the player exchanges an Intel balance for a techprint or other
unlocking item. Research then consumes that ordinary Instruction gate."*

**Verdict: two carriers already turn a stored number into delivered items, and neither is
adoptable — so we build, from their parts.** Faction Territories' `Dialog_Vassalage` spends
vassalage points on drop-podded goods, but the mod is **declined** (map #2 *out of scope*,
settled on [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)); vanilla's
`RoyalTitlePermitWorker_DropResources` spends royal favor, which is **per pawn** and bound to the
title ladder. Both are donors for delivery (see *Delivery surfaces*), and this document's own
catalogue is the purchase half. The exchange is one `CurrencyPurchaseWorker` subclass plus a pluggable
**venue**; a table and a faction are two venue classes of 20–30 lines each. **Build both
venue classes** — the difference is ~30 lines and a set of external failure surfaces, not an
architecture — **and author every Spine Instruction item at a table venue.** Which items sit at
which venue is [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117)'s.

#### The Instruction half is already vanilla

- **The item.** `ThingDefGenerator_Techprints.ImpliedTechprintDefs` generates
  `Techprint_<defName>` for every `ResearchProjectDef` with `TechprintCount > 0`, only when
  `ModLister.RoyaltyInstalled` **[V]**. `DefGenerator.GenerateImpliedDefs_PreResolve` runs it
  before `DirectXmlCrossRefLoader.ResolveAllWantedCrossReferences(FailMode.LogErrors)` in
  `PlayDataLoader.DoPlayLoad` **[V]**, so XML may name `Techprint_X` by defName. Royalty is in
  the closed DLC floor ([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6)) **[V]**;
  without it `ResearchProjectDef` zeroes `techprintCount` (see the **T-40** body).
  `ResearchProjectDef.Techprint` returns the def **[V]**, so an entry can name the project and
  never spell the item.
- **The consumption.** `CompTechprint.CompFloatMenuOptions` → `JobDriver_ApplyTechprint` →
  `ResearchManager.ApplyTechprint(TechprintComp.Props.project, pawn)` **[V]**. A Job, so
  Multiplayer syncs it natively. `CanStartNow` ANDs `TechprintRequirementMet` **[V]**.
- **"Another authored unlock item."** `JobDriver_ApplyTechprint` reads the project off
  `CompTechprint.Props.project`, not off the def's name **[V]**, so a hand-authored `ThingDef`
  carrying `CompProperties_Techprint { project }` is an Instruction item with its own label, art
  and lore at **zero C#** **[I — composition]**. `ApplyTechprint` only credits while
  `proj.TechprintCount > GetTechprints(proj)` **[V]**, so the project must still declare
  `techprintCount`. An item that unlocks something *other than a research project* needs its
  own consumer, owned by that unlock's ticket (see *Purpose and scope*).

#### Mechanism

```
CurrencyExchangeExtension : DefModExtension     // on a CurrencyPurchaseDef; one extension, never two (T-06)
    ThingDef           thing                    // null => project.Techprint
    ResearchProjectDef project                  // optional; hides the entry once IsFinished || TechprintRequirementMet
    int                count     = 1
    int                maxIssued = -1           // -1 = unlimited; see Failure and recovery before setting it
    bool               campaignCritical         // a Spine item: validator refuses maxIssued and a faction-only route
    ExchangeVenue      venue                    // polymorphic, Class= in XML

ExchangeVenue (abstract)
    AcceptanceReport Available(Map map, Thing at)
    void             Deliver(List<Thing> things, Map map, Thing at)

ExchangeVenue_Table   { ThingDef building; bool requiresPower = true }
    Available: at spawned on map, at.def == building, CompPowerTrader.PowerOn if required
    Deliver:   GenPlace.TryPlaceThing(t, at.InteractionCell, map, ThingPlaceMode.Near)

ExchangeVenue_Faction { FactionDef faction; int minGoodwill; bool requiresComms = true }
    Available: map != null && map.IsPlayerHome,
               FactionManager.FirstFactionOfDef(faction) != null, !Hidden, !HostileTo(OfPlayer),
               PlayerGoodwill >= minGoodwill, a comms console on map with CanUseCommsNow
    Deliver:   TradeUtility.SpawnDropPod(DropCellFinder.TradeDropSpot(map), map, t)

CurrencyPurchaseWorker_Exchange : CurrencyPurchaseWorker
    override CanPurchase(map, at): venue.Available && CanAfford && cooldown && project gate && issued < maxIssued
    override Purchase(map, at):    ThingMaker.MakeThing(...) × count; venue.Deliver(...) as the LAST statement
```

Each piece is vanilla API **[V]**: `Faction.Hidden => hidden ?? def.hidden`;
`Building_CommsConsole.CanUseCommsNow`; `TradeUtility.SpawnDropPod(IntVec3, Map, Thing)` wraps
`DropPodUtility.MakeDropPodAt`; `DropCellFinder.TradeDropSpot(Map)` prefers an unroofed orbital
trade beacon, then powered beacons and comms consoles. **The faction venue has two donors.** `RoyalTitlePermitWorker_DropResources.CallResources` —
make the things, `MakeDropPodAt`, send a message with `LookTargets`, `TryRemoveFavor` when
`!free` **[V]**. And Faction Territories' `Dialog_Vassalage`, which prices goods in a stored
number, picks `Find.AnyPlayerHomeMap`, delivers through `TryDeliverToMapSinglePod` (a reflected
`DropCellFinder.TradeDropSpot` → `DropPodUtility.MakeDropPodAt`) or `TryDeliverToCaravan` when
there is no home map, then calls `TrySpendPoints` **[V]**. We take the home-map choice and the
single pod; we drop the caravan fallback, because a colony with no home map simply finds the
venue unavailable.

#### Where state lives, and what changes it

- **New state: one dictionary**, `purchaseCount`, under *Where state lives*. Nothing on the
  venue, nothing on the item.
- **The settled purchase API changed; the balance did not.** `TryPurchase` and the base
  `CurrencyPurchaseWorker.CanPurchase` / `Purchase` all gain `(Map map, Thing at)`, nullable for
  context-free entries (#106's quest worker ignores both). `Balance`, `CanAfford`, `TrySpend`
  and `Credit` are unchanged.
- **The debit.** Inside the sync: re-evaluate `CanPurchase` → `Purchase` (delivery last) →
  `TrySpend` → `purchaseCount[purchase]++` → `lastPurchasedTick[purchase] = now`.
  **Delivery before debit, deliberately.** Faction Territories does the same and needs a
  *"Delivery succeeded but points could not be deducted (state changed)"* message **[V]**,
  because its check and its spend are not one atomic step. Ours are: the whole body is one
  synced command, executed identically and single-threaded on every client right after
  `CanAfford` is re-checked, so `TrySpend` cannot fail there. The order then matters only if
  `Deliver` throws — and delivering first means an exception costs the player nothing, which is
  the side *Failure and recovery* already chooses.
- **Entry points.** *Table:* `CompExchangeTerminal : ThingComp` on the table's `ThingDef`;
  `CompGetGizmosExtra` yields one `Command_Action` opening the exchange window, pre-filtered to
  entries whose venue is `ExchangeVenue_Table` for `parent.def`, and passes `parent` as `at`.
  *Faction:* **no dialog patch** — the entries sit in D1 under the faction's category, enabled
  when `Available(Find.CurrentMap, null)`, and the map is **read in the window and passed as an
  argument**. See *Multiplayer* for why both of those choices matter.

#### Where the player sees it

- **D1 exchange rows**: item icon, label, Intel price, a venue line (*"at a decoder"* /
  *"Traders Guild · goodwill ≥ N · comms console"*), and for a techprint the
  `(applied/required)` suffix the donor already draws —
  `$"({project.TechprintsApplied}/{project.TechprintCount})"` in
  `VFED.DeserterTabWorker_Contraband` **[V]**. A greyed row shows its `AcceptanceReport` reason.
- **The table's gizmo** opens the same rows, filtered. Nothing else to draw.
- **Delivery**: a message with `LookTargets` on the placed item or landing pod, as
  `CallResources` sends **[V]**; then vanilla's *Apply techprint* float option and its letter
  **[V]**.

**The player's loop:** the D3 Intel number rises from raids and analysis → the network tab (or
the decoder's gizmo) lists each Instruction item with its price, where it can be had and why it
is greyed → *Exchange* drops the number and the item appears at the table or by drop pod → a
colonist applies it at a research bench → the project becomes startable.

#### The three options, priced

| | Table only | Faction only | Both |
|---|---|---|---|
| Shared core — extension, venue base, worker, base-worker signature change, `purchaseCount` + scribe + `TryPurchase` args, D1 exchange rows, startup validator | ~140 | ~140 | ~140 |
| `ExchangeVenue_Table` + `CompExchangeTerminal` | ~45 | — | ~45 |
| `ExchangeVenue_Faction` | — | ~30 | ~30 |
| Techprint exclusion postfix (see *Failure and recovery*) | ~15 | ~15 | ~15 |
| **New C#** | **~200** | **~185** | **~230** |
| Harmony patches | 1 | 1 | 1 |
| New saved state | `purchaseCount` | `purchaseCount` | `purchaseCount` |
| XML | table `ThingDef` ~40 + ~12 per entry | ~12 per entry | both |
| Depends on the world roster | no | **yes** (**T-07**) | faction entries only |
| Can lose availability mid-campaign | only if the table is destroyed — rebuildable | **yes** — hostility, goodwill, `Hidden`, no powered comms | faction entries only |
| Delivery lands on a gravship or orbit map | yes, at the table | **unverified** — RUN | faction entries only |
| Multiplayer | `TryPurchase` only | `TryPurchase` only | `TryPurchase` only |

**What separates them.** The table is always reachable once built, and its own
`researchPrerequisites` are an XML cadence lever. The faction route adds a relations lever and a
fiction — a broker, not a decoder — and pays for it with three things the table does not have:

1. **It depends on the faction existing.** The roster is fixed at world creation (**T-07**), and
   [`ORBIT.md`](ORBIT.md) already records that on a Neolithic World Tech Level start every
   Spacer orbital faction, `TradersGuild` included, drops out of `info.factions` before
   `WorldGenStep_Factions` runs. `ORBIT.md` also plans to hide `TradersGuild` until its orbit
   reveal, which `Faction.Hidden` makes this venue respect.
2. **It can close.** A hostile or low-goodwill Traders Guild greys every faction entry. For a
   Spine item that is a **campaign softlock**, which *Failure and recovery* otherwise says this
   document cannot produce.
3. **Its landing is unproven in orbit.** `DropCellFinder.TradeDropSpot` falls back to
   `Log.Error("Could find no good TradeDropSpot…")` and a random standable cell **[V]**; whether
   a drop pod lands sensibly on a gravship map is not settled by reading.

**Recommendation: build both venue classes and author Spine Instruction items at the table.**
Faction entries are safe for Muscle and Comfort items, or as a *second* route to a Spine item at
a different price — which is also the cheapest way to make *"deliberately both"* mean something.

**Rejected surfaces** — vanilla trade with Intel as its currency, bills, a comms-console
`DiaOption`, and VFED's contraband shop — are surveyed under *Available mechanisms* §
*Delivery surfaces for the Intel exchange*. VEF's `QuestGiverDef` is *Shop entries* route A.

> **This is option (b) of three, and the other two are recorded priced rather than rejected.**
> *Available mechanisms* § *Three Intel delivery options* carries (a) adopting VFE Deserters'
> contraband economy wholesale (~15 lines of ours) and (c) our own Intel `ThingDef` with our own
> vendor (~120–150 C#), each with what it buys and what it costs. Which one ships is selected on
> [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map).

**Influence is untouched.** The exchange worker is currency-agnostic by construction, but no
requirement gives Influence an item catalogue, so no Influence entry ships. Influence's
balance, its #106 quest giver, and the Trace modifier's Influence exemption are unchanged.

### The purchasable quest catalogue

[#106](https://github.com/cjd721/Rimworld-Archinity/issues/106). **VEF already ships a
Def-driven, XML-authorable, save-backed purchasable quest catalogue with a *pluggable
currency*. We write the currency and nothing else** — a `QuestCurrency` /
`QuestCurrencyInfo` pair that reads `WorldComponent_Currencies`, about 50 lines for the pair —
**~95** with the `Window_Contracts` subclass and the sync registration (see *Cost*). What VEF
carries, read out of the assembly, is at *Available mechanisms* § *The purchasable-quest seam*.

#### The build — one piece replaced

`VEF.Storyteller` (`…/294100/2023507013/1.6/Assemblies/VEF.dll`), all **[V]**:

```
QuestGiverDef : Def
    QuestCurrency        currency            // polymorphic, Class= in XML
    FactionDef           fixedQuestGiverFaction
    List<QuestScriptDef> onlySpecifiedQuests
    int                  maximumAvailableQuestCount = -1
    int                  resetEveryTick      = -1
    bool                 generateOnce, onlyOneReward, hideGeneratedQuestsInVanilla
    Type                 workerClass         -> QuestWorker
    Type                 windowClass         = typeof(Window_Contracts)
    string               windowTitleKey

QuestCurrency                                 // the eligibility + pricing half
    float costToAcceptQuest
    virtual bool Allows(QuestGiverManager, Quest, Slate, out QuestInfo)

QuestCurrencyInfo : IExposable                // the debit + display half
    float  amount                             // scribed
    virtual void   Buy(QuestInfo)
    virtual string GetCurrencyInfo()
```

**`QuestCurrency.Allows` is handed the freshly generated `Quest` and returns the
`QuestInfo` it wants to offer** — so it decides eligibility, computes the price, and
attaches the `QuestCurrencyInfo` that will later be debited. `GoodwillCurrency` /
`GoodwillCurrencyInfo` are the shipped subclass: `Allows` reads the `asker` off the slate,
checks `GoodwillWith(Faction.OfPlayer) >= minimunGoodwillRequirement`, and `Buy` debits
through `TryAffectGoodwillWith` **[V]**. That is the entire extension surface.

**Ours:**

```csharp
class CurrencyQuestCurrency : QuestCurrency {          // ~30 lines
    CurrencyDef currency;
    float       costPerMarketValue;
    public override bool Allows(QuestGiverManager m, Quest q, Slate s, out QuestInfo info) {
        var ci = new CurrencyQuestCurrencyInfo { currency = currency,
                     amount = PriceFor(q) };           // snapshot, see below
        info = new QuestInfo(q, m.FixedQuestGiverFaction, ci,
                             onlyOneChoice: true, saveQuestDeeply: true);
        return true;
    }
}
class CurrencyQuestCurrencyInfo : QuestCurrencyInfo {  // ~20 lines
    CurrencyDef currency;                              // scribed alongside amount
    public override void   Buy(QuestInfo qi) => Currencies.TrySpend(currency, (int)amount, "quest");
    public override string GetCurrencyInfo() => $"{amount} {currency.label}";
}
```

**What that inherits, at zero cost** — every one **[V]**:

| Need | Provided by |
|---|---|
| the pool | `QuestGiverManager.availableQuests`, `List<QuestInfo>` |
| persistence | `QuestInfo : IExposable` with `Scribe_Deep.Look<Quest>(ref questDeep, "questDeep")` |
| refill cadence | `QuestGiverManager.Tick()` → `Reset()` when `TicksAbs > lastResetTick + def.resetEveryTick` |
| pool membership | `QuestGiverDef.onlySpecifiedQuests`, or all `!isRootSpecial && IsRootAny` scripts |
| pool size | `maximumAvailableQuestCount` |
| price display | `Window_Contracts` draws `questInfo.currencyInfo.GetCurrencyInfo()` |
| challenge rating before commitment | `Window_Contracts` draws one pip per `Quest.challengeRating` |
| choice resolution | `Window_Contracts` calls `selected.quest_Part_choice.Choose(selected.choice)` **before** accepting |
| add → accept → charge → remove | `QuestGiverManager.ActivateQuest(Pawn, QuestInfo)` |

**`ActivateQuest` is, line for line, the `Purchase()` Build B writes:**

```csharp
Find.QuestManager.Add(questInfo.Quest);
questInfo.Quest.Accept(accepter);
QuestUtility.SendLetterQuestAvailable(questInfo.Quest, null);
questInfo.currencyInfo?.Buy(questInfo);
availableQuests.Remove(questInfo);
```

**And VEF does not need the donor's shelving idiom at all.** `QuestInfo` is constructed
with `saveQuestDeeply: true`, so an unbought offer is held by `Scribe_Deep` on the
manager's own list and **never enters `Find.QuestManager` until purchase** **[V]**. A
quest that is not in `QuestManager` is never ticked, so there is nothing to hide from and
nothing to stop expiring. That is strictly cleaner than
`hidden` + `hiddenInUI` + `acceptanceExpireTick = -1`, which is reaper-*evasion* rather
than reaper-*avoidance*.

**Two `QuestGiverDef`s ship**, one per currency — `QuestGiverDef.currency` is a single
object, so Influence and Intel are two givers rather than two columns of one. That is the
better shape anyway: two networks, two fictions, two windows' worth of framing.

**The window.** `QuestGiverDef.windowClass` is a `Type` field defaulting to
`Window_Contracts`, and `QuestGiverManager.CallWindow()` does
`Activator.CreateInstance(def.windowClass, this)` **[V]**. We ship
`Window_ArchinityNetwork : Window_Contracts`, inheriting every row VEF draws and adding the
balance header and [`TRACE.md`](TRACE.md)'s band row. ~40 lines. Under Build A there are two
windows: the VEF shelf (`Window_ArchinityNetwork`) and `MainTabWindow_Network`. Where the
balance header and band row sit, or whether they merge, is
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

#### The three defects we must fix on the way in

**1. The price must be snapshotted, not recomputed.** `QuestCurrencyInfo.amount` is a
scribed `float` set once in `Allows`, and `PriceFor(q)` therefore runs **at generation,
against the unresolved quest**. This matters more than it looks: `QuestPart_Choice.Choose`
**destroys the non-chosen choices** — it calls `Cleanup()` and `quest.RemovePart` on their
parts and does `choices.RemoveAt(num)` **[V]** — so a price averaged over *N* choices
before `Choose` and over *1* after it are different numbers. Storing `amount` makes
displayed price and charged price the same number by construction. A design that
recomputed from a draw method would show one price and charge another.

**2. `Buy` runs *after* `Accept`, and that is the ordering this document warns about.**
`ActivateQuest`'s fourth statement is the debit; the quest is already added and accepted
**[V]**. This document's *Failure and recovery* names that failure — *"a worker that
grants its goods and then throws hands them out free"*. We cannot reorder VEF's method, so
the discipline moves into ours: **`CurrencyQuestCurrencyInfo.Buy` must not be able to
throw** — `TrySpend` returns a bool and logs, and the affordability check happens in the
window before the button is live.

**3. `ActivateQuest` is reached from `OnGUI` and needs one sync wrapper.**
`Window_Contracts.AcceptQuestByInterface` calls it from the draw path **[V]**. That is one
`RegisterSyncMethod` on `QuestGiverManager.ActivateQuest` against `Multiplayer.API` — **not
a reason to rebuild the catalogue**. See *Persistence and multiplayer*.

#### The alternative, and what separates them

**Build B — write it ourselves**:
`WorldComponent_QuestCatalogue` holding `List<QuestOffer>`, an
`Arch_PurchasableQuestExtension` for membership, `EnsureFilled` modelled on
`VFED.WorldComponent_Deserters.EnsureQuestListFilled`, the donor's shelving idiom, and
quest rows in `MainTabWindow_Network`. **~260 lines of new C#.**

**What separates them is a dependency, not a capability.** Build B re-derives the pool,
the persistence, the refill cadence, the price display, the challenge-rating row, the
choice resolution and the accept sequence that VEF already ships. It costs roughly five
times the code and carries two defects VEF does not (the shelving idiom instead of
deep-save, and the `Choose` hazard below).

**Recommend Build A.** VEF is already a dependency —
[`PRESSURE.md`](PRESSURE.md) § 4 takes `IncidentWorker_RaidEnemySpecial` and
`StorytellerDefExtension` from it, and [`HACKING.md`](HACKING.md)'s carrier depends on it —
so this adds no new mod to the ledger. **Build B is the fallback if
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) declines VEF**, and it is
kept below for that reason.

> **Build B carries a defect worth naming.** Dropping the donor's
> `questPartChoice.Choose(choices.RandomElement())` call as "an unsynced `Rand` draw from
> `OnGUI`" is not a change of location only.
> `QuestPart_Choice.PreQuestAccept()` — invoked by `Quest.Accept` — does
> `if (choices.Count >= 2) { Log.Error("Tried to accept a quest but … still has a choice
> unresolved. Auto-choosing the first option."); Choose(choices[0]); }` **[V]**. Dropping
> the call means **every purchase of a multi-choice quest throws a red error and silently
> hands the player option zero.** The fix is not to restore `RandomElement` — it is to let
> the *player* pick in the window and pass the index through the synced method, and to
> guard `.OfType<QuestPart_Choice>().First()`, which throws outright on a quest with no
> choice part and which the donor evaluates from a draw method every frame **[V]**.

#### Build B, retained as the fallback

**The pool.** `Archinity.Core.WorldComponent_QuestCatalogue`, a new `WorldComponent`
holding one flat list:

```csharp
private List<QuestOffer> offers;          // Scribe_Collections.Look(..., LookMode.Deep)

class QuestOffer : IExposable {
    public CurrencyDef currency;          // Scribe_Defs
    public Quest       quest;             // Scribe_References
}
```

A flat deep-scribed list rather than a `Dictionary<CurrencyDef, List<Quest>>`, because
a dictionary whose *values* are collections has no clean `Scribe_Collections` form.
`VFED.WorldComponent_Deserters.PlotMissionInfo` is the shipped precedent for a
deep-scribed `IExposable` row holding a `Scribe_References` quest **[V]**.

It does **not** live on `WorldComponent_Currencies`, which states *"Nothing else lives
here, and that is the design. No campaign index, no chapter, no quest reference."*

**Pool membership is XML.** `Arch_PurchasableQuestExtension : DefModExtension
{ CurrencyDef currency; }` on a `QuestScriptDef`. The eligible set is built once in a
static constructor by walking `DefDatabase<QuestScriptDef>.AllDefs` and keeping those
carrying the extension — the donor's `VFED.Utilities.DeserterQuests` shape, which uses
`QuestExtension_Deserter` the same way **[V]**, generalised by putting the currency on
the extension. **One extension type, one currency field, never two extensions** —
`Def.GetModExtension` returns the first match and a second is inert (**T-06**).

**Refill.** `EnsureFilled(CurrencyDef)` reproduces
`VFED.WorldComponent_Deserters.EnsureQuestListFilled` **[V]**, which is worth copying
almost line for line because every line is vanilla API:

```csharp
float points = StorytellerUtility.DefaultThreatPointsNow(Find.World);
StoryState storyState = Find.World.StoryState;
while (CountFor(currency) < TargetCount(currency)
       && PoolFor(currency).Where(root => root.CanRun(points, Find.World))
            .TryRandomElementByWeight(
                root => NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight(
                            root, points, storyState),
                out QuestScriptDef root))
{
    Slate slate = new Slate();
    slate.Set("points", points);
    slate.Set("purchasable", true);
    Quest q = QuestGen.Generate(root, slate);
    q.hidden = true; q.hiddenInUI = true; q.acceptanceExpireTick = -1;
    Find.QuestManager.Add(q);
    offers.Add(new QuestOffer { currency = currency, quest = q });
}
```

**Those three flags are the whole trick and each is load-bearing [V]:**
`hidden` and `hiddenInUI` keep a shelved offer out of the quests tab and out of the
"new quest" letter; `acceptanceExpireTick = -1` makes `Quest.TicksUntilExpiry` return
`-1`, so `Quest.State` never becomes `EndedOfferExpired` and `Quest.QuestTick`'s
`TicksUntilExpiry == 0 && State == NotYetAccepted` cleanup branch never fires. A
shelved offer therefore lives until it is bought or the pool is trimmed.

> **"Lives until bought" is only true for scripts we author.** A quest script may carry a
> `QuestPart_QuestEnd` whose `SignalListenMode` is `NotYetAcceptedOnly` or
> `OngoingOrNotYetAccepted`, which ends a quest *before* acceptance. The default is
> `OngoingOnly`, so the behaviour is controllable — but a third-party script pulled into
> the pool can end itself on the shelf, and Build B must handle a dead offer. Build A does
> not have the problem: its offers are not in `QuestManager` and receive no signals.

**`$purchasable` is consumed in XML, by a vanilla node, at zero C# cost.** The donor's
`Defs/QuestScriptDefs/Base.xml` reads it with `QuestNode_IsTrue` and branches the
challenge-rating subscript **[V]**. So the flag does not mean "buyable" to the engine —
it is simply a slate bool our own quest scripts may branch on, and branching the
difficulty roll is exactly what we want it for, since a bought mission should be worth
buying.

**Price.** `CurrencyPurchaseWorker_Quest.Cost` overrides the `virtual` above:

```
Cost = ceil( averageRewardMarketValue(quest) / def.costPerMarketValue
             * BandModifierFor(def.currency) )
```

`averageRewardMarketValue` walks the quest's single `QuestPart_Choice` and averages
`Reward.TotalMarketValue` over its choices — the donor's `VFED.Utilities.GetIntelCost`
**[V]**. **The price therefore falls out of the reward the generator actually rolled**,
so nothing has to be re-authored when a reward table changes.

> **`BandModifierFor` is currency-scoped, and this is not a detail.** The donor applies
> `VisibilityLevelDef.intelCostModifier` to **everything in its shop** **[V]**. Ported
> naively into a window that also sells Schism operations, Glitterite pursuit would
> silently set the price of Church politics.
> [`TRACE.md`](TRACE.md) § *Decoupling from Church politics* rules that
> `TraceBandDef.intelCostModifier` applies **only** where
> `CurrencyPurchaseDef.currency == Archinity_Intel`; `BandModifierFor` returns `1f` for
> every other currency. Checkable by grep: no code path may read a band def without a
> `CurrencyDef` in scope.

**Purchase.** `CurrencyPurchaseWorker_Quest.Purchase(Map map, Thing at)` — both arguments ignored:

```csharp
int cost = offer.price;             // snapshotted at generation, never recomputed here
quest.hidden = false;
quest.hiddenInUI = false;
choicePart?.Choose(choicePart.choices[choiceIndex]);   // player's pick, passed through the sync
offers.Remove(offer);
EnsureFilled(def.currency);
quest.Accept(null);                 // LAST statement — see Failure and recovery
```

`Quest.Accept(Pawn by)` is `public`, accepts a null accepter, and no-ops unless
`State == NotYetAccepted` **[V]**. The whole of it runs inside a single
`[SyncMethod] TryPurchase(CurrencyPurchaseDef purchase, int choiceIndex)`.

**Three things in those seven lines are load-bearing:**

- **`choiceIndex` travels through the synced method.** The donor resolves the choice with
  `RandomElement` from `OnGUI`; omitting the call entirely makes `QuestPart_Choice.PreQuestAccept` log a red error and auto-choose option zero
  **[V]**. Letting the player pick is both deterministic and better than either.
- **`cost` is read before any mutation.** `Choose` destroys the non-chosen choices
  **[V]**, so a price derived from the reward set is a different number before and after
  it. Snapshot at generation; store it on the offer.
- **`choicePart` is null-guarded.** `.OfType<QuestPart_Choice>().First()` throws on a
  quest with no choice part, and the donor evaluates it from a draw method every frame
  **[V]**.

**The synced boundary is the difference from the donor**, whose identical lines run from
`DeserterTabWorker_Services.DoMainPart` — a draw method **[V]** — and which MP Compat has
to reach with two transpilers and four synthetic sync methods.

**Refill must never run from a draw method either.** The donor calls
`EnsureQuestListFilled` from `Notify_Open` *and* from the purchase path, both inside
`OnGUI` **[V]**, and MP Compat has to sync `EnsureQuestListFilled` explicitly. Ours
runs from `TryPurchase` (already synced) and from `WorldComponentTick` on a slow
cadence, and from nowhere else. Opening the window must not generate a quest.

**Display.** The `MainTabWindow_Network` this document already builds, with one
`CurrencyCategoryDef` per currency. Each offer row draws the quest's
`challengeRating` — which is how
[`docs/requirements/QUESTS.md`](../requirements/QUESTS.md)'s *"Every quest declares a
challenge rating the player sees before committing to it"* is satisfied, using
vanilla's own `QuestChallengeRatingTip` string; the donor does exactly this and even
splits its two columns on `challengeRating <= 3` **[V]**. Reward rows come free from
`Reward.StackElements`, which the donor draws with `GenUI.DrawElementStack` **[V]**.

`QUESTS.md` also names **Purchase** as one of its seven arrival channels; this is that
channel's mechanism.

**The cost of a shelved pool, stated rather than glossed.** `QuestGen.Generate` runs
the whole generator up front — pawns are generated, sites are generated. They do not
appear in the world: `QuestNode_SpawnWorldObjects` emits a
`QuestPart_SpawnWorldObject` that fires on the quest's `inSignal`, i.e. on accept
**[V]**. But the objects exist in the save, and ten shelved offers per currency is
twenty generated quests. `TargetCount` is a `CurrencyDef` field for that reason, and
the donor's hardcoded `10` is not copied.

### Cost

| Piece | Kind | Lines | Lands in |
|---|---|---|---|
| `CurrencyDef` | new C# | ~15 | `Archinity.Altar/Source/Currencies.cs` |
| `CurrencyPurchaseDef` + `CurrencyCategoryDef` + `CurrencyPurchaseWorker` | new C# | ~45 | same |
| `WorldComponent_Currencies` | new C# | ~90 | `Archinity.Altar/Source/Currencies.cs` |
| `Reward_Currency` | new C# | ~60 | `Archinity.Altar/Source/CurrencyQuests.cs` |
| `QuestNode_GrantCurrency` + `QuestPart_GrantCurrency` | new C# | ~70 | same |
| `CompUseEffect_GainCurrency` + properties — Credit B's route D, optional | new C# | ~35 | `Archinity.Altar/Source/Currencies.cs` |
| `MainTabWindow_Network` (catalogue + balance header) | new C# | ~140 | `Archinity.Altar/Source/CurrencyUI.cs` |
| `MainButtonWorker` subclass (D4, optional) | new C# | ~20 | same |
| `GlobalControlsUtility.DoDate` postfix (D3) | patch | ~25 | `Archinity.Altar/Source/Patches.cs` |
| MP registration behind an `MP.enabled` guard | new C# | ~15 | `Archinity.Altar/Source/Patches.cs` |
| **— the Intel exchange, *The Intel exchange* ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54), closed), both venues —** | | | |
| `CurrencyExchangeExtension` + `ExchangeVenue` base | new C# | ~25 | `Archinity.Altar/Source/Exchange.cs` |
| `CurrencyPurchaseWorker_Exchange` | new C# | ~45 | same |
| `ExchangeVenue_Table` + `CompExchangeTerminal` (+ props) | new C# | ~45 | same |
| `ExchangeVenue_Faction` | new C# | ~30 | same |
| `purchaseCount` + scribe + `TryPurchase(purchase, map, at)` + base `CanPurchase`/`Purchase(Map, Thing)` | new C# | ~20 | `Archinity.Altar/Source/Currencies.cs` |
| Exchange rows in `MainTabWindow_Network` | new C# | ~40 | `Archinity.Altar/Source/CurrencyUI.cs` |
| Startup validator — venue null; a `campaignCritical` entry with `maxIssued` set or no table-venue route; a techprint project without `techprintCount` | new C# | ~10 | `Archinity.Altar/Source/Exchange.cs` |
| Postfix on `TechprintUtility.GetResearchProjectsNeedingTechprintsNow` excluding exchange projects | **patch** | ~15 | `Archinity.Altar/Source/Patches.cs` |
| Decoder table `ThingDef`; one `CurrencyPurchaseDef` + extension per Instruction item; `techprintCount` on each project | **XML** | ~40 + ~12 per entry | `Archinity.Glitterites/Defs/Exchange/` |
| **Intel exchange total new C#** | | **~230** (table only ~200, faction only ~185) | one assembly, 1 Harmony patch |
| **— the purchasable quest catalogue, [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106), Build A (recommended) —** | | | |
| `CurrencyQuestCurrency : VEF.Storyteller.QuestCurrency` | new C# | ~30 | `Archinity.Altar/Source/QuestCatalogue.cs` |
| `CurrencyQuestCurrencyInfo : VEF.Storyteller.QuestCurrencyInfo` | new C# | ~20 | same |
| `Window_ArchinityNetwork : VEF.Storyteller.Window_Contracts` (balance header + Trace band row) | new C# | ~40 | `Archinity.Altar/Source/CurrencyUI.cs` |
| One `RegisterSyncMethod` on `QuestGiverManager.ActivateQuest` | new C# | ~5 | `Archinity.Altar/Source/Patches.cs` |
| Two `QuestGiverDef`s (one per currency) with `onlySpecifiedQuests`, `maximumAvailableQuestCount`, `resetEveryTick`, `onlyOneReward: true`, `windowClass` | **XML** | ~40 | `Archinity.Altar/Defs/QuestGivers.xml` |
| **Build A total new C#** | | **~95** | one assembly |
| **— Build B, the fallback if [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) declines VEF —** | | | |
| `WorldComponent_QuestCatalogue` + `QuestOffer` (pool, `EnsureFilled`, scribe) | new C# | ~110 | `Archinity.Altar/Source/QuestCatalogue.cs` |
| `Arch_PurchasableQuestExtension` + the static eligible-set build | new C# | ~25 | same |
| `CurrencyPurchaseWorker_Quest` (`Cost` override + `Purchase` + choice handling) | new C# | ~70 | same |
| Quest rows in `MainTabWindow_Network` (challenge rating, reward stack, choice picker) | new C# | ~85 | `Archinity.Altar/Source/CurrencyUI.cs` |
| `$purchasable` branch in each authored `QuestScriptDef` — vanilla `QuestNode_IsTrue` | **XML** | ~8 per script | `Archinity.*/Defs/QuestScriptDefs/` |
| `Arch_PurchasableQuestExtension` on each eligible `QuestScriptDef` | **XML** | ~4 per script | same |
| **Build B total new C#** | | **~290** | one assembly |
| **Total new C# — currencies plus Build A** | | **~525–615** | one assembly |
| **Total new C# — currencies plus Build A plus the Intel exchange (both venues)** | | **~755–845** | one assembly |
| Two `CurrencyDef`s, one `MainButtonDef`, every catalogue entry, every price, every reward amount, every artifact's comp, every purchasable quest script | **XML** | — | `Archinity.Altar/Defs/`, `Archinity.Glitterites/Defs/` |

Marked **[I]**: the mechanisms composed above are each **[V]**, but the claim that they
compose into the required behaviour is inferred until something compiles, and the line
estimates with it.

---

## Persistence and multiplayer

### Persistence

```csharp
Scribe_Collections.Look(ref balances, "balances", LookMode.Def, LookMode.Value,
                        ref tmpCurrencies, ref tmpAmounts);
```

This is vanilla's own idiom for a durable per-Def number: `RimWorld.ResearchManager.ExposeData`
scribes `progress`, `techprints` and `anomalyKnowledge` exactly this way **[V]**.

`lastPurchasedTick` and the exchange's `purchaseCount` are scribed the same way. A save that
predates the exchange loads `purchaseCount` null and `FinalizeInit` initialises it empty
**[I]**, so every entry's issued count starts at zero. That is harmless: the default
`maxIssued` is unlimited, and a techprint entry's visibility reads `ResearchManager`'s own
scribed `techprints` through `TechprintRequirementMet` **[V]**, not this counter.

**Do not use `Verse.DefMap`.** See **T-37** (`docs/traps/defs-and-patching.md`).
`DefMap<D,V>` persists a bare `List<V>` positionally indexed by `def.index`, and `def.index`
is assigned from def-database insertion order **[V]** — adding, removing or reordering a
`CurrencyDef`, or another mod inserting one, silently reassigns every stored balance to a
different currency. The same `ResearchManager.ExposeData` reserves `DefMap` for
`tabInfoVisibility`, a transient UI bool **[V]**, which is the line to copy.

**Adding the component to an existing save is safe.** `RimWorld.Planet.World.ExposeComponents`
scribes `components` and then calls `FillComponents()`, which constructs any `WorldComponent`
type not present **[V]** — so the component appears initialised-empty rather than erroring.

**A `CurrencyDef` removed from the load order leaves an unresolvable key, not a wrong one.**
`LookMode.Def` writes the defName, so on load `Scribe_Defs` holds a name with no def behind
it and the entry arrives with a null key **[I]** — that is the behaviour the defName-based
idiom is chosen *for*, but this specific path was not read against 1.6. `FinalizeInit` drops
null keys and logs once; it does not silently retain them. **T-04** (*"unresolvable
cross-references are omitted, not nulled"*) does not apply: it is XML def loading, and this
is save loading.

### Multiplayer

**Credits are free.** Credit B's route A credits from `IThingStudied` on the study job's
tick ([`RESEARCH.md`](RESEARCH.md) § *Destructive artifact analysis*) — a Job, which
Multiplayer syncs natively. Route D's `CompUseEffect_GainCurrency` is likewise reachable only
through `CompUsable.CompFloatMenuOptions` → `TryStartUseJob` → `JobDriver_UseItem` →
`CompUsable.UsedBy` → `CompUseEffect.DoEffect(Pawn)` **[V]**. That is the same argument
`Archinity.Altar.csproj` already makes for the altar. Quest-part credits fire on quest
signals inside the synced quest machinery.

**The debit is the only new sync surface**, because it originates at a button — and it is a
single method by design.

`TryPurchase(CurrencyPurchaseDef, Map, Thing)` carries `[SyncMethod]` from **`Multiplayer.API`**, in
`0MultiplayerAPI.dll` under the Multiplayer mod's `1.6/Assemblies/` **[V]**. It is a
compile-time-only reference with **no hard dependency**: `Multiplayer.API.MP`'s static
constructor looks for the `Multiplayer` assembly among `LoadedModManager.RunningMods` and
falls back to a `Dummy` implementation with `MP.enabled == false` when it is absent **[V]**.
Register with one `MP.RegisterAll(assembly)` behind an `MP.enabled` guard. The attribute
type is `SyncMethodAttribute` — there is no `Multiplayer.API.SyncMethod` **[V]**; the
similarly-named `ISyncMethod` is a registration handle.

**Build A adds exactly one more.** `VEF.Storyteller.Window_Contracts.AcceptQuestByInterface`
calls `QuestGiverManager.ActivateQuest(Pawn, QuestInfo)` from the draw path **[V]**, so that
method needs a `RegisterSyncMethod` against `Multiplayer.API`. **One registration** — it is
a public instance method on a scribed `IExposable` whose arguments Multiplayer can address,
which is the whole reason the catalogue is worth adopting rather than rebuilding. VEF's
*generation* path is not a sync surface: `QuestGiverManager.Tick()` and `Init()` run off the
game tick **[V]**.

> **One residual, stated rather than assumed.** `QuestInfo` is not an
> `ILoadReferenceable`, so whether Multiplayer can serialise it as a sync argument
> unaided — or whether the registration must take `(QuestGiverDef, int index)` instead —
> **is not settled by reading** and is listed under *Verification*. The index form works
> regardless and is the fallback.

**The Intel exchange adds no second sync surface.** It rides `TryPurchase`, which gains
`Map map, Thing at`; Multiplayer's `SyncDictRimWorld` serialises both `Thing` and `Map`
(`WriteSync<Map>` / `ReadSync<Map>`) **[V]**; a *null* `Map` argument is **[I]**. Four rules make it deterministic:

- **The map is chosen in the window and passed in**, never read inside `Purchase`: a table
  entry passes the table's own map; a faction entry passes `Find.CurrentMap` when it
  `IsPlayerHome`, else `Find.AnyPlayerHomeMap` (Faction Territories' choice **[V]**), and
  `ExchangeVenue_Faction.Available` refuses any non-home map — so a pod never lands on a raid
  site the camera happens to be on. It
  is per-client camera state; the donor's `DeserterServiceWorkers.CallShuttle`,
  `TauntImperials` and `ChangeCritical` read it while mutating state, and VFED's rush delivery
  reads `Parent.Map` inside the tab's draw method **[V]**.
- **`CanPurchase` is re-evaluated inside the synced body.** Between the click and execution
  the table can lose power, the faction can lose goodwill, and the other founder can spend the
  balance. The window's check is advisory.
- **No targeter.** Delivery picks its own cell. Multiplayer auto-registers `OrderForceTarget`
  only for `ITargetingSource` types **declared in `Assembly-CSharp`** —
  `Multiplayer.Client.SyncMethods` filters `t.Assembly == typeof(Game).Assembly` **[V]** — so
  vanilla's `RoyalTitlePermitWorker_DropResources` is synced and a modded copy of its
  targeting path would not be.
- **Applying the item is a Job** (`JobDriver_ApplyTechprint`) **[V]**. Nothing to add.

`DropCellFinder.TradeDropSpot`'s fallback calls `list.Shuffle()` and
`CellFinderLoose.RandomCellWith` **[V]** — `Rand` inside a synced command, which Multiplayer
seeds **[I]**.

**Defs, not settings** (**T-18**). Every price, amount, cooldown and catalogue entry is a
`CurrencyPurchaseDef` or `QuestGiverDef` field. No `ModSettings` is read anywhere in this
mechanism.

**Presentational state stays out of the tick path** (**T-21**). Scroll position, open
categories and the pending selection are instance fields on the window — never static,
never scribed. This is the direct opposite of `VFED.ContrabandManager`, whose cart, totals
and open-category flags are static mutable fields **[V]**.

> **The cost of getting this wrong is measured.** Multiplayer Compatibility's
> `Multiplayer.Compat.VanillaFactionsDeserters` (in `Multiplayer_Compat_Referenced.dll`)
> needs a prefix that replaces `DesertersUIUtility.DoPurchaseButton` wholesale, two
> transpilers rewriting button call sites in `DeserterTabWorker_Services.DrawService` and
> `DeserterTabWorker_Plots.DoMainPart`, five `RegisterSyncMethod` calls, seven lambda
> registrations, and **four synthetic sync methods invented on the compat class** to carry
> the shopping cart across the wire **[V]** — precisely because VFED's balance is not
> stored state. A stored `int` on a `WorldComponent` reduces all of that to one
> `[SyncMethod]`.

### Structural separation

Spending Influence advances the Schism plot ([#122](https://github.com/cjd721/Rimworld-Archinity/issues/122)); routes are in *The Schism catalogue — a spend that advances the plot*.

What holds:
1. **Different owners.** Balances live in `WorldComponent_Currencies`; chain state lives in its own component under its own `Scribe` key.
2. **The spending API still has no vocabulary for progression.** `TrySpend(CurrencyDef, int, string)` names no chapter, quest or step.
3. **The chain index has exactly one writer, and it is a quest outcome.** A purchase may *accept* the current step. It never writes the index — checkable by grep.

VFED's `Notify_PlotQuestEnded` is the only writer of its index **[V]**, but `DeserterTabWorker_Plots.DoMainPart` gates every step but the free endgame (`VFED_DeserterEndgame`) on `TrySpendIntel` **[V]**. It shows *spend gates, outcome writes*, not that spending cannot move the campaign.

### The interface to [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67)

**Exchanging Intel, studying an exemplar and destructively analyzing an artifact are
three distinct acts and must not be folded together.** Intel is a scalar with no identity beyond its `CurrencyDef` and no
location. An exemplar is a particular `Thing` the colony holds, with a `ThingDef`, a stack,
a quality and a position.

Folding either into the other makes a required case inexpressible, in each direction:

- [`GLITTERTECH.md`](../requirements/GLITTERTECH.md) gives Intel a source with **no item** —
  *"optional investigation can provide Intel progress/bonuses"*. If Intel were an item,
  curiosity would have to spawn loot.
- The same file gives a branch that uses the Exemplar route a case with **no cost** —
  *"Exemplar: a colonist studies a physical likeness to unlock the project; the item
  survives."* That is possession, not payment. If the exemplar were "N Intel", any N Intel
  would open any branch and the acquire→analyze loop collapses.

**Vanilla already models them as two independent fields.** `Verse.ResearchProjectDef` carries
`requiredAnalyzed : List<ThingDef>` (satisfied via `AnalyzedThingsRequirementsMet`) *and*
`techprintCount` (satisfied via `TechprintRequirementMet`, backed by
`ResearchManager.techprints`), and `CanStartNow` ANDs them along with the rest **[V]**.

**What this document offers #67:** `Balance`, `CanAfford`, `TrySpend`, `Credit` above. The
sync boundary and the balance stay on this side.

**#67 never calls this balance.** The exemplar gate is independent and surviving.
*The Intel exchange* ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)) is the
surface that exchanges Intel for an Instruction item. [#115](https://github.com/cjd721/Rimworld-Archinity/issues/115)
owns the destructive work that credits Intel and raises Trace.

**What this document needs from #67:** nothing at debit time, under either ruling.

**Relevant negative for #67, established here:** no field on `ResearchProjectDef` debits a
quantity of an arbitrary resource. `baseCost` is pawn-work points; `techprintCount` consumes
one specific `ThingDef` pre-completion by a job; `knowledgeCost` replaces `baseCost` and
accrues into the project rather than draining a pool **[V]**. A project that costs Intel
must be written. `ResearchManager.FinishProject(ResearchProjectDef, bool, Pawn, bool)` is
public and is the single funnel **[V]** — but it **recurses into unfinished prerequisites**
**[V]**, so a naive postfix debits once per project in the chain, and a *gate* belongs in a
prefix because by postfix time `progress[proj]` is written and the unlock signal has fired.
Analysis is not priced — research never debits Intel — so this negative is recorded for
completeness only.

### What is shared — [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) has ruled

**Ruling: the shared dictionary stays. The escape hatch is not taken.**
[`TRACE.md`](TRACE.md) § *Decoupling from Church politics* carries it in full, with the
one place the coupling is real — the band's price modifier, which is currency-scoped
and must stay that way. The report below stands as written and the ruling is appended
to it.

- **Shared:** `WorldComponent_Currencies` stores Influence and Intel as **two rows in one
  dictionary under one `Scribe` key, in one component**. This is the coupling; the headline
  above now says so.
- **Not shared, and cannot be:** Trace is a band ladder with thresholds, effects and no
  spend. It wants `VisibilityLevelDef`'s shape, not this one. Exaltation is likewise a
  ladder.
- **What sharing does and does not imply.** The only coupling a shared dictionary creates is
  a shared save key and a shared null-key prune. `TrySpend(Archinity_Intel, …)` cannot read
  the Influence row — the API takes one `CurrencyDef`. Nothing here is keyed on a faction,
  and Church standing is not an input to any code path.
- **The escape hatch, which exists on purpose.** If #56 judges even a shared save key too
  close, the same class instantiated as two `WorldComponent`s costs about 15 lines and no
  design change **[I]**. **Not taken** — see the ruling above.
- **What #56 added to this list, which was not on it.** The *shop window* is shared too,
  and the donor scales **every price in its shop** by its heat meter's band
  (`VisibilityLevelDef.intelCostModifier` reaches `DeserterServiceDef.intelCost`,
  `ContrabandExtension` and the derived quest price alike **[V]**). That is a live
  coupling this document did not report, and it is the one #56 actually had to rule on.
  Resolved by scoping the modifier to `CurrencyPurchaseDef.currency == Archinity_Intel`.

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| A `CurrencyDef` leaves the load order | Key resolves null on load **[I]** | `FinalizeInit` drops null keys and logs once. The balance is lost, which is correct — the currency no longer exists. |
| Stored balances silently rebind to the wrong currency | **None — this is the silent one** | Prevented, not recovered: `LookMode.Def`, never `DefMap`. **T-37**. |
| A purchase worker throws mid-`Purchase()` | Log error, and the balance in D1 is visibly unchanged | `TryPurchase` checks `CanPurchase(map, at)` first and debits **after** `Worker.Purchase(map, at)` returns, so a worker that throws *before* granting anything costs the player nothing. **The ordering admits the opposite failure, and this document should say so:** a worker that grants its goods and *then* throws hands them out **free and un-cooldowned**, because the debit is never reached. `CanPurchase()` makes it narrow; it does not make it absent. The mitigation is a worker discipline, not a mechanism — **perform the grant as the last statement**, so anything that can throw throws before it. Debiting first would trade this for a charge with no goods, which is the worse failure. **[I]** |
| Two clients disagree on a balance | MP desync | `TryPurchase` is the only mutation reachable from UI and carries `[SyncMethod]`. Every other mutation is inside a Job or a quest part. |
| The catalogue is empty or every entry unaffordable | Visible in D1 | Not a failure. The window states the balance and the shortfall, as `TrySpendIntel`'s `"VFED.NotEnough"` message does **[V]**. |
| The D3 postfix breaks on a game update | **Visible** — the row vanishes or misdraws | Layout arithmetic only; the balance and every spend path are unaffected. This is the piece most exposed to a RimWorld update, and it fails loudly rather than silently. |
| A shelved quest offer's `QuestScriptDef` leaves the load order | Loud — `Quest.root` is null and `QuestManager` prunes it on load (`allQuests.RemoveAll(q => q.root == null)`) **[V]** | `EnsureFilled` tops the pool back up. The offer row is dropped with it. |
| The eligible quest pool is empty, or every candidate fails `CanRun` | Visible in D1 — the currency's category is empty | Not a failure. `EnsureFilled`'s `while` terminates on the first failed draw rather than spinning, because `TryRandomElementByWeight` returns false. |
| A shelved offer is bought and its `Accept` throws | The debit never happens — see the worker-discipline row above | `Accept` is the **last** statement of `Purchase()` precisely so the failure mode is "no quest, no charge" rather than "charged, no quest". |
| **A `QuestGiverDef` is authored `onlyOneReward: false` and its catalogue is permanently empty** | **Silent — nothing logs and the window simply shows no rows.** `QuestGiverManager.AvailableQuests` prunes every entry whose `quest_Part_choice` or `choice` is null, and `QuestInfo`'s constructor populates those two fields **only** when `onlyOneChoice` is true **[V]** | Prevented, not recovered: a startup validator asserting `onlyOneReward: true` on every `QuestGiverDef` we ship, ~10 lines. The same prune also fires on a null `askerFaction`, which happens when `fixedQuestGiverFaction` is unset and the player has no allies — so **set `fixedQuestGiverFaction`**. |
| **A quest script throws during generation and silently never appears in the catalogue** | **Silent** — `QuestWorker.GenerateQuests` wraps the body in `catch (Exception) { }` **[V]** | Not repairable from outside; use `onlySpecifiedQuests` so the pool is a list we authored and can test, rather than every `IsRootAny` script in the load order. |
| **`QuestCurrencyInfo.Buy` throws** | The quest is already added and accepted — `ActivateQuest` debits fourth **[V]** | `Buy` must not be able to throw: `TrySpend` returns a bool and logs, and affordability is checked before the button is live. The ordering is VEF's and we cannot reorder it. |
| **A Glitterite techprint arrives from somewhere other than the exchange** | **Silent — T-99** — it simply appears in a trader's stock, a quest reward or loot. `TechprintUtility.GetResearchProjectsNeedingTechprintsNow` skips the `heldByFactionCategoryTags` filter when its `faction` is null **[V]**; `ThingSetMaker_Techprints` passes `parms.makingFaction` **[V]**, which `Reward_Items` sets from `giverFaction` **[V]** and which is null on a quest with no asker **[I]**; it is used by Core `Reward_ItemsStandard`, Core `ThingSetMakers_MapGen.xml` (two sites) and Ideology's map-gen loot sets **[V]**. **Orbital trade ships run without a faction too:** `TradeShip.GenerateThings` sets only `traderDef` and `tile`, and `ThingSetMaker_TraderStock.Generate` passes that null `makingFaction` to every stock generator **[V]** — so any orbital trader carrying `StockGenerator_Techprints` (`Orbital_CombatSupplier`, `Orbital_Exotic`) sells the techprint of **every** unfinished `techprintCount` project, whatever its tags and whoever the ship belongs to. Settlement, caravan and visitor traders do set `makingFaction` (`Settlement_TraderTracker`, `PawnGroupKindWorker_Trader`, `IncidentWorker_VisitorGroup`) **[V]** and respect the tags. | Prevented **only by the postfix** — omitting `heldByFactionCategoryTags` covers settlements and caravans but not ships, rewards or loot. Postfix `GetResearchProjectsNeedingTechprintsNow` to drop every project named by a `CurrencyExchangeExtension` — World Tech Level's `Patch_TechprintUtility` postfixes exactly this method **[V]**. **Not covered by that postfix:** VFE Deserters' `ContrabandManager` static constructor registers **every** `ThingDef` carrying `CompProperties_Techprint` as Intel-priced contraband **[V]**, and VPE's `Ability_ReverseEngineer` writes `AddTechprints` directly **[V]** — both owned outside this document ([#14](https://github.com/cjd721/Rimworld-Archinity/issues/14); `RESEARCH.md`'s bypass list). |
| An exchange venue becomes unavailable between click and execution | Visible — the row greys, a rejection message, **no debit** | `CanPurchase` is re-evaluated inside `TryPurchase`. |
| **The faction venue's faction is absent, hidden, hostile or below `minGoodwill`** | Visible — the row is greyed with its reason | A missing faction is **not repairable** (**T-07**). Hostility or goodwill are, slowly. **Author no Spine item at a faction venue alone** — mark it `campaignCritical` and the validator refuses an entry set with no table-venue route. |
| A delivered Instruction item is destroyed before it is applied | Visible | Re-buy — the default `maxIssued` is unlimited, and the entry stays listed until `TechprintRequirementMet`. **Setting `maxIssued` on a Spine item converts a burnt techprint into a softlock**; the validator refuses it on a `campaignCritical` entry. |
| The player buys the same techprint twice before applying the first | Visible — the row stays listed until `TechprintRequirementMet`, so the second purchase wastes Intel | **Deliberate, not capped.** A cap on `purchaseCount − TechprintsApplied` would stop a re-buy after a techprint burns — the softlock above — and `TechprintsApplied` counts techprints from every source, so the arithmetic is not even exact. The row instead shows *"N issued, not yet applied"* and asks for confirmation when N > 0. ~5 lines inside the D1 rows. |
| A drop pod has nowhere good to land | `Log.Error("Could find no good TradeDropSpot near dropCenter …")`, then a random standable unfogged cell **[V]** | Loud and self-recovering on a planet. On a gravship or orbit map: **RUN**. The table venue does not drop. |
| Shelved offers bloat the save | **Silent** — the save grows and nobody looks | `QuestGen.Generate` runs pawn and site generation up front **[V]**. `TargetCount` is a `CurrencyDef` field, not the donor's hardcoded 10, so the pool size is a tuning decision rather than an accident. Worth measuring once with a real save. **[I]** |

**Spending stalls the Schism plot; it never strands it.** Under Routes A and B a purchase elsewhere leaves the balance short of the current step's price, and the index never moves backward. What can strand the plot is Influence income stopping, a step failing to generate (A), an expired offer (B) or a pool that never resets (C). See *The Schism catalogue — a spend that advances the plot* § *Constraints*.

---

## Status

**Evidence class: READ.** Settled from decompiled 1.6 assemblies and shipped XML.

| | |
|---|---|
| **Verified available mechanisms** | `WorldComponent` + `Scribe_Collections.Look(…, LookMode.Def, LookMode.Value)`; `World.FillComponents` backfill; `RimWorld.Reward` + `QuestPartUtility.GetStandardRewardStackElement`; `CompUsable` → `JobDriver_UseItem` → `CompUseEffect.DoEffect`; `MainButtonDef` as pure XML; `GlobalControlsUtility.DoDate`'s `ref float curBaseY`; `Multiplayer.API.SyncMethodAttribute` with soft-dependency fallback. **Added by [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106):** **`VEF.Storyteller`'s whole quest-giver stack** — `QuestGiverDef`, `QuestCurrency.Allows`, `QuestCurrencyInfo.Buy` / `GetCurrencyInfo`, `QuestInfo` with `saveQuestDeeply`, `QuestGiverManager.ActivateQuest` / `Tick` / `Reset` / `CallWindow`, `QuestWorker.GenerateQuests`, `Window_Contracts`, and `GoodwillCurrency` as the worked subclass. Plus, for Build B only: `QuestGen.Generate` into a `Slate`; the `hidden` / `hiddenInUI` / `acceptanceExpireTick = -1` shelving idiom with `TicksUntilExpiry` returning `-1`; `QuestManager.Add` / `Remove`; `Quest.Accept(null)`; `QuestScriptDef.CanRun` + `NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight`; `QuestNode_IsTrue`; `QuestNode_SpawnWorldObjects`; and `QuestPart_Choice.Choose` / `PreQuestAccept`. All **[V]**. |
| **Retracted** | *"Nothing in the corpus or in vanilla sells a quest except VFE Deserters."* **False** — VEF does, with a pluggable currency ([#106](https://github.com/cjd721/Rimworld-Archinity/issues/106)). |
| **Confirmed negative** | Nothing in vanilla, the DLC or the corpus holds a **Def-keyed, world-level, spendable balance**. The named donor holds no balance at all. Independently re-verified by the close-out audit, which re-ran the highest-signal sweep family and found the negative holds **harder** than either #54 comment claimed. **The sweep form used to reach it was itself defective** — see *Verification* and [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103). |
| **Proposed, not selected** | The whole build above. It is **[I]** as a composition, and the line estimates with it. |
| **Added by [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)** | **The Intel exchange.** Verified available mechanisms: `ThingDefGenerator_Techprints.ImpliedTechprintDefs` run from `DefGenerator.GenerateImpliedDefs_PreResolve` before cross-reference resolution; `ResearchProjectDef.Techprint` / `TechprintRequirementMet`; `CompTechprint` → `JobDriver_ApplyTechprint` → `ResearchManager.ApplyTechprint`; `TradeUtility.SpawnDropPod`; `DropCellFinder.TradeDropSpot`; `Building_CommsConsole.CanUseCommsNow`; `Faction.Hidden`; `RoyalTitlePermitWorker_DropResources.CallResources` as the spend-and-drop precedent; `TechprintUtility.GetResearchProjectsNeedingTechprintsNow`'s null-faction branch. All **[V]**. **Two carriers exist, neither adoptable:** Faction Territories' `Dialog_Vassalage` (declined mod) and vanilla `RoyalTitlePermitWorker_DropResources` (per-pawn favor) both spend a stored number on delivered items. Vanilla's only non-silver *trade* currency is sell-only. **Proposed, not selected:** the exchange build, **[I]** as a composition. |
| **Open parameters** | Every number — Intel prices, the exchange catalogue, its cadence, and which venue carries each item ([#117](https://github.com/cjd721/Rimworld-Archinity/issues/117)). **Analysis pricing is resolved: research never debits Intel** ([`GLITTERTECH.md`](../requirements/GLITTERTECH.md)). See *Outstanding decisions*. |

Established on [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)
(absorbing [#55](https://github.com/cjd721/Rimworld-Archinity/issues/55)'s currency half).

---

## Available mechanisms

### The named donor — VFE Deserters, and what it actually is

`…/294100/3025493377/1.6/Assemblies/VFED.dll`. `MOD-SNAPSHOT.md` marks
`oskarpotocki.vfe.deserters` **Src 1.4 ⚠**, so everything below is read from the 1.6
assembly the game loads, not the stale source tree.

**It now follows the Church.** Under [`RELIGION.md`](RELIGION.md) § *The build — Exaltation* the
Empire *is* the Church, transformed in place, so VFED's 49 `OfEmpire` sites — imperial patrols,
force-size patches, intel extraction, `WorldComponent_Deserters` — point at the Church with no
patch of ours **[V, #53]**.

**Deserters Intel is a warehouse, not a currency.**

- `VFED_Intel` and `VFED_CriticalIntel` are stackable `ThingDef`s in
  `…/1.6/Defs/ThingDefs_Items/Items_Resource_Exotic.xml`, carrying
  `VFED.CompProperties_Intel` **[V]**. `VFED.CompIntel` ticks `tickTillOutOfDate` and
  **destroys the stack** on expiry **[V]** — Deserters Intel rots.
- `VFED.WorldComponent_Deserters` holds no balance. Its `ExposeData` scribes `active`,
  `locked`, `visibility`, `serviceQuests`, `plotMissions`, `extraSiteData` — and nothing
  else **[V]**.
- The balance is a **window field, recomputed on open**:
  `VFED.Dialog_DeserterNetwork.PostOpen` walks `Building_OrbitalTradeBeacon.AllPowered(Map)`
  and sums matching stacks into `TotalIntel` / `TotalCriticalIntel` **[V]**. Intel not on a
  powered beacon on that map does not exist; Intel in a caravan does not exist.
- **VFED does draw a readout — a modal one.** `VFED.Dialog_DeserterNetwork.DoWindowContents`
  draws both balances as labelled, icon'd rows in the window header **[V]**. There is **no
  persistent readout** — the only one is modal, computed in `PostOpen`, and dies with the
  window. D3 is ours to write for that reason,
  which is enough of a reason on its own.
- Spending **launches the items**: `VFED.Dialog_DeserterNetwork.TrySpendIntel(int,int)` calls
  `TradeUtility.LaunchThingsOfType(VFED_DefOf.VFED_Intel, normal, Map, null)` **[V]**. It is
  a trade, not a debit.
- **Two currencies, hardcoded, not Def-keyed.** `VFED.DeserterServiceDef` and
  `VFED.ContrabandExtension` each carry `int intelCost` plus `bool useCriticalIntel`, and
  that bool selects between two `VFED_DefOf` fields in `ContrabandManager.AddToCart`,
  `.RemoveFromCart`, `DesertersUIUtility.DrawIntelCost`, `Dialog_DeserterNetwork.HasIntel`
  and `.TrySpendIntel` **[V]**. **A third currency is not a def, it is a refactor.**

**Why this shaped the build.** Everything in *The build* is an answer to one of these: the
balance is a `Def`-keyed dictionary because the donor's is a hardcoded pair; it lives in a
`WorldComponent` because the donor's lives in a `Window`; it is scribed because the donor's
cannot be; the readout is persistent because the donor's is modal; and the debit is one
synced method because the donor's is a call from a draw method.

**The donor's defects, recorded because they are the specification for not repeating them:**

- The whole purchase path runs inside `OnGUI`. `DeserterTabWorker_Services` calls
  `Parent.TrySpendIntel(…)`, then `service.worker.Call()`, then for a mission
  `ServiceQuests.Remove(selected); EnsureQuestListFilled(); selected.Accept(null)` — from
  the tab's draw method, unsynced **[V]**. `PARTS-BIN.md` § 7.4's *"MP: BLOCK as a
  dependency"* is confirmed, and this is the reason.
- `VFED.ContrabandManager` is `[StaticConstructorOnStartup]` with a static mutable cart,
  totals and open-category flags, and its static constructor **appends `ContrabandExtension`
  onto other mods' `ThingDef.modExtensions` at load** **[V]** — read that second half
  against **T-06**, since `GetModExtension` returns the first match.
- Three of the six shipped `DeserterServiceWorkers` statics read `Find.CurrentMap` while
  mutating game state — `CallShuttle`, `TauntImperials`, `ChangeCritical` **[V]**.

**What is worth keeping.**

| Piece | Verdict |
|---|---|
| The Intel currency | **REPLACE.** Nothing to keep. |
| `DeserterServiceDef`'s shape (`{icon, cost, worker}`) | **REBUILD on vanilla `RoyalTitlePermitDef`**, which is the same idea with `prerequisite`, `cooldownDays` and `uiPosition` already on it **[V]**, and costs no VFE dependency. |
| The contraband shop | **REPLACE.** |
| `Dialog_DeserterNetwork` + `DeserterTabDef`/`DeserterTabWorker` | **REBUILD the tabbed-window shape.** `DeserterTabDef` is a two-field `Def` with `workerClass` and a lazy `Activator.CreateInstance` **[V]** — cheap to re-author, not worth a dependency. |
| The purchasable quest pool (`ServiceQuests` + `EnsureQuestListFilled`) | **KEEP THE SHAPE** — and it belongs to [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106). See below. |
| The ordered chain | **KEEP THE SHAPE, REPLACE THE DRIVER** — owned by *The Schism catalogue* ([#132](https://github.com/cjd721/Rimworld-Archinity/issues/132)), route A's donor. See below. |
| `Reward_Visibility` | **KEEP THE PATTERN, not the type** — it is a plain `RimWorld.Reward` subclass using only vanilla API. |

### The purchasable-quest seam, and why it is [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106)'s

`VFED.WorldComponent_Deserters.EnsureQuestListFilled` refills `ServiceQuests` and sets
**`slate.Set<bool>("purchasable", true)`** on every quest it generates **[V]** — that is
exactly the `$purchasable` node the map named, and the corpus does carry it.

The map made a purchasable quest catalogue conditional on #54 and #55 settling their
currencies. Both are settled;
[#106](https://github.com/cjd721/Rimworld-Archinity/issues/106) resolved it, and **the
build is above rather than here** — a purchase belongs in the purchases document. This
section is the survey behind it.

**#106 consumed this document's design and added one line to it.** One behavior, one
owner — the split as it actually landed:

- **Already here:** the balance, `CurrencyPurchaseDef`, `CurrencyPurchaseWorker`,
  `MainTabWindow_Network` and the single synced debit `TryPurchase`. None of them names a
  quest, a fiction or a price.
- **#106's addition:** `virtual int CurrencyPurchaseWorker.Cost`, because a quest's price
  is derived from the reward the generator rolled rather than authored. Five lines. **It
  is needed only by Build B** — Build A prices through `QuestCurrency.Allows` instead — but
  it is kept, because it costs nothing and the fallback needs it.
- **#106's own, Build A:** a `QuestCurrency` / `QuestCurrencyInfo` pair and a
  `Window_Contracts` subclass.
- **#106's own, Build B:** the pool, its refill policy, `Arch_PurchasableQuestExtension`,
  and how `slate` carries `purchasable` into an authored `QuestScriptDef`.

**No second balance, no second store, no second shop window was opened.**

#### VEF carries it

**`VEF.Storyteller` ships a complete purchasable quest catalogue with a pluggable
currency** — `QuestGiverDef`, `QuestCurrency`, `QuestCurrencyInfo`, `QuestInfo`,
`QuestGiverManager`, `QuestWorker`, `Window_Contracts`, held by
`GameComponent_QuestChains`, with `GoodwillCurrency` / `GoodwillCurrencyInfo` as a shipped
working subclass **[V]**. *The build* above is written against it.

`Window_Contracts` draws `questInfo.currencyInfo.GetCurrencyInfo()` as the price and
routes accept through `AcceptQuestByInterface` → `QuestGiverManager.ActivateQuest`, whose
fourth statement is `questInfo.currencyInfo?.Buy(questInfo)` **[V]**. `CanAcceptQuest` is
one guard among several, not the whole gate.

**What VEF does *not* carry, stated precisely so the remaining build is honest:**

- **No currency but goodwill.** `QuestCurrency` is abstract-in-practice with one shipped
  subclass **[V]**. A pooled spendable balance is still ours — which is what the rest of
  this document is.
- **A flat price per giver, not per quest.** `QuestCurrency.costToAcceptQuest` is one
  `float` on the Def **[V]**. Deriving a price from the generated quest is possible only
  because `Allows` is handed the `Quest` — our subclass does the arithmetic itself.
- **Unweighted offer selection.** `QuestWorker.GenerateQuests` draws with plain
  `RandomElement` over `!isRootSpecial && IsRootAny` scripts **[V]**, where VFED uses
  `NaturalRandomQuestChooser.GetNaturalRandomSelectionWeight`. If the offer mix matters,
  that is a `workerClass` override — `QuestGiverDef.workerClass` exists for it.
- **Two silent failure modes we must author around**, both **[V]**, both proposed for the
  register on [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106):
  `QuestGiverManager.AvailableQuests` does
  `RemoveAll(x => x == null || x.askerFaction == null || x.quest_Part_choice == null || x.choice == null)`,
  and `QuestInfo`'s constructor populates `quest_Part_choice` and `choice` **only when
  `onlyOneChoice` is true** — so a `QuestGiverDef` with `onlyOneReward: false` has a
  catalogue that is **silently, permanently empty**; and `QuestWorker.GenerateQuests`
  wraps generation in `catch (Exception) { }`, so a quest script that throws simply never
  appears.

#### The rest of the corpus, and vanilla

**Beyond VEF and VFED, nothing sells a quest** **[V]**. Run over
both roots plus vanilla and the DLC, `-a -g '*.dll' -g '!**/obj/**'`, with the `#US`-heap
half as a hand-typed null-interleaved literal
(`p\x00u\x00r\x00c\x00h\x00a\x00s\x00a\x00b\x00l\x00e\x00`) after validating that the
ASCII form returns **zero** hits on VFED.dll and the interleaved form returns one:

- `purchasable` appears in **three VFED assemblies and three VFED XML files and nowhere
  else** in 228 mods, and not at all in `Assembly-CSharp.dll` **[V]**.
- Thirteen 1.6 assemblies carry both `QuestGen` and `QuestScriptDef`; **`TradeUtility.LaunchThingsOfType`
  appears in exactly one of them, VFED** **[V]**. None of the other twelve removes a
  currency anywhere near a quest-generation site.
- **Vanilla cannot sell a quest.** `RoyalTitlePermitWorker_CallShuttle` spends
  `royalAid.favorCost` through `Pawn_RoyaltyTracker.TryRemoveFavor`, and
  `PermitsCardUtility` prices permits in `permitPointCost` and honor — none of it touches
  `QuestUtility` or `QuestGen` **[V]**. The nearest vanilla thing to a bought quest is an
  aid effect that fires immediately.

> **The `purchasable` sweep's negative is sound and its *scope* was overread.** It proves
> nobody else uses VFED's slate key. It does not prove nobody else sells a quest, because
> VEF's catalogue uses no such key — it never puts an unbought quest in `QuestManager` at
> all. A symbol sweep bounds the *symbol*, never the *behaviour*, and the behaviour was
> the ticket.

**What the donor gets wrong, recorded because it is the specification for not repeating
it** — all **[V]**:

- `EnsureQuestListFilled` is called from `Notify_Open` and from `DoMainPart`, both inside
  `OnGUI`. So is the accept. MP Compat's `VanillaFactionsDeserters` entry needs a prefix
  replacing `DesertersUIUtility.DoPurchaseButton` wholesale, two transpilers, five
  `RegisterSyncMethod` calls, seven lambda registrations and four synthetic sync methods
  to paper over it.
- `EnsureQuestListFilled` also calls
  `questPartChoice.Choose(questPartChoice.choices.RandomElement())` — an unsynced `Rand`
  draw from a draw method, which is the canonical Divergence-gate failure.
- The pool target is a hardcoded `10`, the price divisors are hardcoded `500` and `2000`,
  and the column split is a hardcoded `challengeRating <= 3`.
- Payment is `TradeUtility.LaunchThingsOfType(VFED_Intel, n, Map, null)` — the items
  physically launch off the map. It is a trade, not a debit, and it is why the donor's
  Intel must sit on a powered orbital trade beacon to exist at all.

### The ordered-operation surface

`VFED.WorldComponent_Deserters.InitializePlots` builds `List<PlotMissionInfo>` once, and `Notify_PlotQuestEnded` (reached from the `Quest.End` postfix `HarmonyPatches.MiscPatches.CheckForPlotEnd`) advances by **index**. On `EndedSuccess` it generates `PlotMissions[IndexOf(info) + 1]`; on `EndedFailed` or `EndedInvalid` it regenerates *the same index*. `EndedOfferExpired` is not handled and needs no handling, because steps are shelved with `acceptanceExpireTick = -1` **[V]**. **Each step but the endgame is bought**: `DeserterTabWorker_Plots.DoMainPart` spends Intel before `Accept`; `VFED_DeserterEndgame` starts free after a confirmation **[V]**. This is the donor for Route A of *The Schism catalogue*, which owns the chain's routes.

The **driver** is not: `InitializePlots` iterates `VFEEmpire.WorldComponent_Hierarchy.Titles`
filtered on `seniority >= RoyalTitleDefOf.Knight.seniority`, and the branch chance is a
`switch` on literal seniority integers 700/701/800/801/802/900/901 **[V]**. Repointing it to
Schism operations replaces the method rather than patching it — roughly 50–60 lines **[I]**,
and the rewrite drops the Empire coupling entirely.

### Delivery surfaces for the Intel exchange

The survey behind *The Intel exchange*. Each candidate was asked one question: **can it turn
a numeric Intel balance into a delivered Instruction item, and at what cost?**

| Surface | What it does **[V]** | Verdict |
|---|---|---|
| **Vanilla trade with a non-silver currency** | `enum TradeCurrency { Silver, Favor }`; `TraderKindDef.tradeCurrency`; only Royalty's `Empire_Caravan_TributeCollector` sets `Favor`. `Tradeable_RoyalFavor.CountHeldBy` returns `99999` for the trader and **`0` for the colony**, `Interactive => false`, and `ResolveTrade` acts only on `PlayerBuys` — the player *receives* favor. **The engine has never shipped a trade in which the player spends a non-`Thing` number.** The currency is chosen by equality in `TradeDeal.CurrencyTradeable`, `TradeDeal.AddAllTradeables`, `Dialog_Trade`'s cached currency row and `TradeUtility.GetPricePlayerSell`; `GetPricePlayerBuy` has no currency parameter at all. Multiplayer replaces the session with `MpTradeSession`, and its transferable serializer addresses a `Tradeable` by `(FirstThingTrader ?? FirstThingColony).thingIDNumber` — a non-`Thing` row has nothing to address (favor escapes only by being non-interactive **[I]**). | **Rejected.** A dedicated Intel-currency trader for the Traders Guild is ≥4–6 Harmony patches (~150 lines) in Multiplayer's most-patched window, for what one venue class does in 30. |
| **Orbital traders' techprint stock** | `Orbital_CombatSupplier` and `Orbital_Exotic` (`<faction MayRequire="Ludeon.RimWorld.Odyssey">TradersGuild</faction>`) carry `StockGenerator_Techprints`. A passing ship generates stock with **no** `makingFaction` (`TradeShip.GenerateThings` sets only `traderDef` and `tile`; `ThingSetMaker_TraderStock.Generate` passes it through), so `GetResearchProjectsNeedingTechprintsNow` skips the tag filter entirely. | **Rejected, and a leak to prevent.** It sells for **silver**, and it would sell *every* unfinished `techprintCount` project's techprint regardless of `heldByFactionCategoryTags` — which is why the exclusion postfix is mandatory (**T-99**). The same bypass is what keeps Empire-tagged techprints on sale after the Church turns hostile: the tag-gated Church trader route needs the Church non-hostile and a colonist holding Knight (Baron for its orbital trader) — [`RELIGION.md`](RELIGION.md) § *Verification* § *Exaltation*. |
| **Faction Territories — `FactionTerritories.Vassalise.Dialog_Vassalage`** (`jaeger972.factionterritories`, `3626725895/Assemblies/FactionTerritories.dll`) | **A real carrier.** `DoWindowContents` reads `VassalagePointsComponent.GetPoints`; the *Buy* button builds goods with `ThingMaker.MakeThing`, delivers to `Find.AnyPlayerHomeMap` through `TryDeliverToMapSinglePod` (reflected `DropCellFinder.TradeDropSpot` → `DropPodUtility.MakeDropPodAt`) or to a caravan via `TryDeliverToCaravan`, and only then `TrySpendPoints` — logging *"Delivery succeeded but points could not be deducted (state changed)"* when that fails. All from a draw method. | **Not adoptable — the mod is declined** (map #2 *out of scope*, settled on [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)), its balance is keyed per faction and accrued passively (see *The wide pass*), and its purchase is unsynced. **Donor for `ExchangeVenue_Faction.Deliver`**: home-map choice and a single pod at `TradeDropSpot`. The points are spent *"on pawns, items and roads"*. |
| **Royal aid** — `RoyalTitlePermitWorker_DropResources` — **a real carrier** | `CallResources(IntVec3)` makes `royalAid.itemsToDrop`, `DropPodUtility.MakeDropPodAt`, messages with `LookTargets`, `TryRemoveFavor`. Multiplayer syncs it through the `OrderForceTarget` sweep and `CallResourcesToCaravan` explicitly. | **Adopt the shape, not the worker.** It is `ExchangeVenue_Faction.Deliver` plus a debit; the favor is per pawn and bound to the title ladder (see *Vanilla and the DLC*). |
| **VEF `QuestGiverDef`** — this document's #106 Build A | Sells a *quest*: `QuestGiverManager.ActivateQuest` adds, accepts and then debits. | **Recommended for items** (*Shop entries* route A, [#144](https://github.com/cjd721/Rimworld-Archinity/issues/144)). `QuestNode_AddItemsReward` builds the `QuestPart_Choice` **T-76** prunes for and the `QuestPart_DropPods` that delivers, so an item entry is an ordinary reward row **[V]**. Its costs — a generator run, a quest-tab entry and a letter per item — are route A's consequences. |
| **Bills** — a `RecipeDef` producing `Techprint_X` at a bench | The product resolves in XML (implied defs precede cross-references). But no ingredient takes a non-`Thing` (`RecipeWorker.ConsumeIngredient(Thing, …)`); `RecipeWorker.AvailableOnNow` is reached through `RecipeDef.AvailableOnNow` from `ITab_Bills` (listing and pasting) and `PlayerItemAccessibilityUtility` **[V]**, and from the health-tab surgery lists **[I]** — never from `WorkGiver_DoBill`, which tests `bill.ShouldDoNow()` / `PawnAllowedToStartAnew`; and `RecipeWorker.Notify_IterationCompleted` — the only per-iteration hook — runs **after** `GenRecipe.MakeRecipeProducts` in `Toils_Recipe.FinishRecipeAndStartStoringProduct`. | **Rejected as the default.** ~70 lines plus a Harmony postfix on `Bill_Production.ShouldDoNow`, **grant-before-debit**, and two bills can both pass the gate against one balance. Worth revisiting only if #117 wants a colonist to *work* the exchange — and then as a Job on the table venue, not a bill. |
| **Comms-console `DiaOption`** — `FactionDialogMaker` | The vanilla surface for talking to a faction. | **Rejected.** Multiplayer syncs a `DiaOption` click by index and re-resolves the dialog client-locally (**T-82**), a `Dialog_NodeTree` subclass drops out of its bindings (**T-95**), and a missing `resolveTree` strands the dialog (**T-97**). D1 rows gated on `CanUseCommsNow` do the same job with none of that. |
| **VFE Deserters' contraband shop** — the only corpus shop that already exchanges Intel for techprints | `ContrabandManager`'s static constructor runs `TryGiveExtension` over every `ThingDef` and registers each one carrying `CompProperties_Techprint` into `VFED_Imperial`, priced by `SetCostIfMissing` at `BaseMarketValue / 100` Intel. `DeserterTabWorker_Contraband` draws the `(applied/required)` suffix, and its purchase either generates `VFED_DeadDrop` with `itemStashThings` (a site to collect from) or, at double price, `DropPodUtility.DropThingGroupsNear(DropCellFinder.TradeDropSpot(Parent.Map), …)` — **both from the tab's draw method**. | **Donor for the row layout and both delivery ideas; not a dependency** (see *The named donor*). **And a leak:** if VFED ships, every Glitterite techprint is on its shelf. The dead-drop quest is a real faction-venue variant, but its script uses VFED's own nodes (`QuestNode_GetEmpire`, `QuestNode_GetDeserters`, `QuestNode_HiddenDelay`), so it is not free. |

**The wide pass.** Both roots plus vanilla and the DLC, `rg -a -i -g '*.dll' -g '!**/obj/**'
-g '!**/Referenced/**'`, attributed with `corpus.py --which`, reading only assemblies the game
loads for 1.6.

- **ASCII `TradeCurrency|Tradeable_RoyalFavor|IsFavor`** — validated first against vanilla
  `Assembly-CSharp.dll` (hit). Hits in 1.6: RimPacts `RptArmsTrader.TradeCurrency => 0`, TW
  Capitalistic Militor `NCL.CompTrader.TradeCurrency => 0` and
  `Tradeable_MechanoidEmploy.IsFavor => false`, VFE Medieval 2 `MerchantGuild.TradeCurrency =>
  0`, Worksites Expanded (its only `<tradeCurrency>` is `Silver`) **[V]**. **Every modded
  `ITrader` in the corpus trades in silver.** Vehicle Framework's hits are 1.4/1.5 copies only.
- **ASCII `techprint`** in 1.6 assemblies, each call site read: VFED (contraband registration,
  `QuestNode_BetrayalRewards`, `GenStep_FlagshipRuins`); VFE Classical (`Profectus` perk reads
  `TechprintCount`); VFE Tribals (a ritual filter); VPE (`Ability_ReverseEngineer` →
  `AddTechprints`); Hacking Expansion (`JobDriver_ApplyResearchGiver` plays the techprint
  sound); World Tech Level (`Patch_TechprintUtility` postfix — the exclusion precedent); More
  Realistic Research (a project filter); RimPacts (`RptGoodsUtility` tech level); Multiplayer
  **[V]**. **None sells a techprint for a stored number.**
- **`#US` literal, null-interleaved with hand-typed escapes**
  (`T\x00e\x00c\x00h\x00p\x00r\x00i\x00n\x00t\x00`), validated with `Techprint_` → 1 hit in
  vanilla. 1.6 hits: More Realistic Research, Worksites Expanded's `MiningOutpost.dll`,
  NiceBillTab, Multiplayer — **[I]**, literals not depth-read.
- **XML:** `Techprint_` appears only in Vanilla Base Generation Expanded's Empire layouts
  (loot placement); `techprintCount` only in Dwarves of the Rim, VFED and GravTech **[V]**.

**Residual gap.** A shop whose currency is neither a `Tradeable`, a `TradeCurrency`, a
techprint literal nor a `DeserterServiceDef`-style cost field would survive every sweep here.
The #54 affordability-string family (`NotEnough*`, `CannotAfford`, `Insufficient`) remains the
best net for that, and it found only VFED spending Intel.

### Three Intel delivery options — priced mechanisms, not a selection

**All three are verified available mechanisms.** (b) is the exchange mechanism; route A of
*Shop entries* is the current item-shelf recommendation. **(a)** and **(c)** are recorded here,
priced, so either can be taken without re-running this research. Which one ships is selected
on [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map).

Every line count is **[I]**: an estimate of unwritten code. Every mechanism claim is **[V]** unless
marked otherwise.

#### (a) Adopt VFE Deserters' contraband economy wholesale — ~15 lines of ours

The only C# we would write is the **T-99** exclusion postfix on
`TechprintUtility.GetResearchProjectsNeedingTechprintsNow`. Everything else already ships.

**What ships free** [V], all from `…/294100/3025493377/1.6/Assemblies/VFED.dll` unless noted:

| Piece | What it is |
|---|---|
| The currency items | `VFED_Intel` and `VFED_CriticalIntel` `ThingDef`s — `VFED.CompIntel` rots the stack at **30** and **10** days, `stackLimit 50`, `tradeability None`, `DeteriorationRate 2.0` |
| A free top-left readout | both inherit `ResourceBase`, whose `resourceReadoutPriority Middle` puts them in `RimWorld.ResourceReadout` — the one surface *The build* § *Where the player sees it* records as closed to a pure number |
| The catalogue, auto-populated | `VFED.ContrabandManager`'s static constructor runs `TryGiveExtension` over the whole database and registers **every** def carrying `CompProperties_Techprint` into category `VFED_Imperial` at `BaseMarketValue / 100`. Implied techprints exist by then: `DefGenerator.GenerateImpliedDefs_PreResolve` precedes `StaticConstructorOnStartupUtility.CallAll` in `PlayDataLoader.DoPlayLoad` |
| The shop | `VFED.Dialog_DeserterNetwork` — categories, a cart, the `(applied/required)` suffix, an affordability message — entered from the comms console through a `GetCommTargets` postfix gated on `Active` |
| Two deliveries | the `VFED_DeadDrop` site quest, or a **2×**-price rush through `DropCellFinder.TradeDropSpot` → `DropPodUtility.DropThingGroupsNear` |
| Payment | `TradeUtility.LaunchThingsOfType` — a trade, not a debit |
| Price scaling | `VFED.Utilities.TotalIntelCost` = `intelCost × VisibilityLevel.intelCostModifier` (2 / 5 / 10) |

**What it costs us** [V]:

- **The whole economy is keyed to the Empire — which [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)
  turned into the Church.** Intel is *extracted from Empire-titled pawns*
  (`VFED.CompIntelExtractor`'s validator is
  `pawn.royalty.GetCurrentTitle(Faction.OfEmpire) != null`) and dropped by
  `VFED.EmpireRaidLootMaker`. The shop opens only after
  `VFED.WorldComponent_Deserters.JoinDeserters`, which force-hostiles `Faction.OfEmpire` via
  `GoodwillToMakeHostile` and strips titles. Adopting (a) therefore imports an anti-Church war
  as the *precondition of buying anything*.
- **It re-imports the Trace dependency [`TRACE.md`](TRACE.md) deliberately re-authored away**:
  `intelCostModifier` is driven by VFED *visibility*, not by our band. Plus **T-18** —
  `VisibilityChangePerDay` and `IntelFromExtraction` are `ModSettings` sliders, so two clients
  with different settings files price and earn Intel differently.
- **Intel becomes cargo.** It rots, it is raid-lootable, it has mass, and it is spendable only
  while sitting on a powered orbital trade beacon *on that map*
  (`Dialog_DeserterNetwork.PostOpen` sums `Building_OrbitalTradeBeacon.AllPowered(Map)`): no
  Neolithic spending, no caravan spending, no gravship or orbit spending.
- **Site-inspection-grants-Intel becomes impossible.** That is a
  [`GLITTERTECH.md`](../requirements/GLITTERTECH.md) requirement (*"optional investigation can
  provide Intel progress"*), and curiosity cannot spawn loot — see *The build* § *What changes
  it*, Credit C.
- **It hard-depends on VFED *and* VFE Empire.** VFED's `About.xml` requires Royalty, VFE Empire,
  VEF and Harmony, and `VFEE_Deserters` is a VFE Empire def.

**Multiplayer.** Synced by `Multiplayer.Compat.VanillaFactionsDeserters` — `SyncedPurchaseContraband`,
`SyncedPurchaseContrabandRushedDelivery`, `SyncedPurchaseQuest`, `SyncedPurchaseService`,
`SyncedAcceptPlot` — which lives only in the conditionally loaded
`1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll` [V]. **The sync is real but fragile:**
`PreDoPurchaseButton` dispatches on **translated button-text equality**, so a locale change breaks
it silently.

#### (b) The stored balance plus our own exchange worker — ~230 new C#, 1 Harmony patch, `purchaseCount`

**The exchange mechanism**, specified above: *The build* § *The Intel
exchange* and § *Cost*. What it trades away and what it buys, stated against (a):

- **Forfeits** the free `ResourceReadout` row — D1 and D3 are ours to write.
- **Keeps** site-inspection grants (Credit C), Trace-driven rather than visibility-driven pricing,
  no rot, no raid loss, no mass, and a balance spendable anywhere a venue is available.

#### (c) Hybrid — our own Intel `ThingDef` with our own vendor — ~120–150 new C# [I estimate]

An item-backed Intel that is **ours**, sold at **our** venue: the item inherits `ResourceBase`, so
it gets the free top-left readout and the stacking behaviour (a) gets, while the vendor is the
`CurrencyPurchaseWorker_Exchange` / `ExchangeVenue` pair of (b) with `TrySpend` replaced by a
`ThingOwner` count-and-consume.

- **Buys:** the free readout and stacking, and a fiction free of VFED's anti-Empire war, its
  Empire-keyed extraction and its two mod dependencies.
- **Still cannot** grant Intel by site inspection — that is a property of items, not of VFED.
- **Re-inherits** rot (if we author a `CompRottable`-style timer), raid-lootability, mass, and
  whatever beacon-style location constraint we choose to impose on spending; every one of those is
  now a decision we own rather than one we inherit.

#### The one thing owed under all three

**The T-99 exclusion postfix is owed under (a) and (c) exactly as much as under (b), if VFED
ships** [V]. `ContrabandManager.TryGiveExtension` registers every `CompProperties_Techprint`-carrying
def in the database, so any Instruction item we author appears on VFED's shelf at
`BaseMarketValue / 100` regardless of which option we chose — a second exchange the spec cannot
see. Under (a) the postfix is the *only* code we write; under (b) and (c) it is one row of the cost
table. Whether VFED ships is [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s.

### Vanilla and the DLC

| Mechanism | What it gives | Why it is not the answer |
|---|---|---|
| **Royal favor** — `Pawn_RoyaltyTracker.favor : Dictionary<Faction,int>`, with `GetFavor`, `GainFavor`, `TryRemoveFavor`, `RefundPermits` **[V]**; earned from quests via `QuestPart_GiveRoyalFavor` / `Reward_RoyalFavor`, spent through `RoyalTitleDef.favorCost` and `RoyalAid.favorCost` **[V]** | A complete stored, spendable, quest-earned, catalogue-spent balance — **the closest thing to this build that already exists**. Its display name is even per-faction data (`FactionDef.royalFavorLabel`, `.royalFavorIconPath` — the Empire sets it to "honor") **[V]**, which is how [`RELIGION.md`](RELIGION.md) renames it to the Church's **Exaltation** without code. | **Per pawn, keyed by faction.** There is no colony-level row, so "the colony's Influence" has nowhere to sit; and `RoyalTitleDef.favorCost` binds the catalogue to the title ladder, which is [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)'s Exaltation. Reusing it couples Influence to the ladder the requirements explicitly say it is not. **This is the closest miss in the survey, and worth re-checking if the per-pawn constraint ever relaxes.** |
| **Permit purchases** — `Pawn_RoyaltyTracker.factionPermits : List<FactionPermit>`, scribed `LookMode.Deep` **[V]** | The inverse architecture: **store the purchases, derive the balance** | Not adopted — our balance is earned, not derived from a ladder. But it is the reason a *cooldown* is stored per purchase here (`FactionPermit.lastUsedTick`) rather than per currency. |
| **Permit points** — `Pawn_RoyaltyTracker.GetPermitPoints(Faction)` **[V]** | A budget spent on a Def catalogue | **Derived, not stored.** It sums `permitPointsAwarded` walking the title chain. A mission cannot pay you permit points. |
| **`RoyalTitlePermitDef`** **[V]** | The catalogue shape: `workerClass`, cost, `prerequisite`, `cooldownDays`, `uiPosition` | **Adopted** — this is `CurrencyPurchaseDef`'s model. Its `minTitle`/`faction` coupling is what we drop. |
| **Anomaly knowledge** — `ResearchManager.anomalyKnowledge : Dictionary<ResearchProjectDef,float>` **[V]** | Def-keyed persisted numbers, scribed `LookMode.Def, LookMode.Value` | **Per project, not a pool.** It is progress that accrues into a project, not a balance a mission pays. **Its persistence idiom is adopted.** (The code is in `Assembly-CSharp.dll`; the Anomaly *content* is not on disk — see *The wide pass*.) |
| **Techprints** — `ResearchManager.techprints`, `ApplyTechprint`, `JobDriver_ApplyTechprint` **[V]** | A consumable item satisfying a research requirement | Per project, one `ThingDef`, not a currency. **Adopted as the Instruction item the Intel exchange delivers** — see *Delivery surfaces for the Intel exchange*. |
| **`Verse.DefMap<D,V>`** **[V]** | Def-keyed storage | **Positional and load-order fragile.** See **T-37**. |
| **`ResourceReadout`** **[V]** | The top-left stockpile display | `ThingDef`-driven and rebuilt each tick. Cannot host a number. |

**There is no vanilla or DLC world-level pooled spendable currency.** `ResearchManager`'s
three dictionaries are all per-project; royal favor is per-pawn-per-faction; permit points
are derived.

### The wide pass

Run over both corpus roots — `steamapps/workshop/content/294100` and
`steamapps/common/RimWorld/Mods` — plus vanilla and the DLC, against compiled assemblies
(`rg -a -g '*.dll' -g '!**/obj/**'`) in **both** ASCII and UTF-16LE, and attributed with
`python tools/corpus.py --which -`. `python tools/corpus.py --check` reported the corpus
clean at 155 mods at both ends of this ticket.

> **Read this section against [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103).**
> The UTF-16LE half of every pass below was run as `rg -a --encoding utf-16le`, which is now
> known to miss `#US`-heap strings **non-uniformly**. See *Verification* for what that costs
> and what independently rescues the negative.

**Result: nothing in the corpus holds a Def-keyed, world-level, spendable balance.** Full
sweep list, per-carrier findings and the validation run are on
[#54](https://github.com/cjd721/Rimworld-Archinity/issues/54).

**Three carriers in the corpus hold a genuine stored spendable balance, and none is Def-keyed** **[V]**:

| Carrier | Shape | Why it is not the answer |
|---|---|---|
| `FactionTerritories.Vassalise.VassalagePointsComponent` (`jaeger972.factionterritories`) | `Dictionary<string,int>` keyed by `Faction.loadID`; `AddPoints` / `GetPoints` / `TrySpendPoints`; spent in `Dialog_Vassalage` on pawns, items and roads | **Accrues passively per vassal settlement on a tick**, not from missions. One currency, keyed by faction. The dictionary *is* the currency, so it cannot be instanced twice either. |
| `RimWar.Planet.RimWarSettlementComp` (`torann.rimwar`) | `int rimwarPointsInt` per world object, rolled up per faction | AI war budget, not a player wallet. Per settlement, single scalar, no catalogue. |
| `RimWorld.Pawn_RoyaltyTracker` (vanilla Royalty) | See the vanilla table above | Per pawn, keyed by faction, catalogue bound to the title ladder. |

**`RimWorld.KnowledgeCategoryDef` is the nearest currency-as-a-`Def` shape the engine
defines** — a currency type defined by a `Def`, with
`ResearchManager.ApplyKnowledge(KnowledgeCategoryDef, float)` routing income and an
`overflowCategory` **[V]**, read from `Assembly-CSharp.dll`.

The *type* exists in `Assembly-CSharp.dll` **[V]**. **Zero instances of it exist anywhere in
the corpus:** Anomaly is not on disk — `Data/` holds Biotech, Core, Ideology, Odyssey and
Royalty only — and an XML sweep for `KnowledgeCategoryDef` over both corpus roots returns
**0 files** **[V]**. The familiar pair (Basic, Advanced) is Anomaly content, and asserting it
is **[I], knowledge from outside the corpus**.

It is a progress meter rather than a held pool in any case. The narrower point survives intact
and is the one worth keeping: **currency-as-a-`Def` is a shape RimWorld's own code already
understands.**

**Notable negatives, each read rather than assumed** **[V]**: VFE Empire's Honor is an award
*ledger* (`VFEEmpire.HonorsTracker` holds `List<Honor>`, no integer); VFE Classical's "favor"
is a `bool` per senator; RimPacts' favor is a 0–100 reputation clamp consumed only by
thresholds; Worksites Expanded and VFE Medieval 2 charge silver.

**Achievements Expanded's `TryPurchasePoints` / `AvailablePoints` has no 1.6 copy.** It is
bundled inside **six** unique mod ids — `1814987817`, `1914064942`, `2134308519`,
`2562018758`, `3014906877`, `3014915404` — at `1.4/`, and `1814987817` ships **1.2** and
**1.3** copies as well **[V]**. **No 1.6 copy exists in either root** **[V]**, so it is dead
for this game version.

**Residual gaps, stated rather than papered over:**

1. **Generic instantiations remain invisible.** A `Dictionary<SomeDef,int>` field lives in the
   `#Blob` heap as a type signature, not a readable string. Bounded two ways — every
   `GameComponent_*` / `WorldComponent_*` type name in both roots was enumerated and the
   plausible ones read, and no currency-shaped `Def` type exists — but a currency keyed on a
   *pre-existing* Def type inside a component whose name carries no currency noun would
   survive both. **That residue is not closed.**
2. **A naming blind spot, demonstrated rather than theorised.** `VassalagePointsComponent`
   uses no `GameComponent_` prefix and was invisible to the component-name sweep; it surfaced
   only on the `TrySpendPoints` verb. A carrier with neither a currency noun nor a spend verb
   in any identifier would be missed by every sweep run.
3. **The sweep form itself was defective.** See *Verification* and
   [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103).
4. **Out-of-corpus lead:** Multiplayer Compatibility carries the literal
   `VanillaChristmasExpanded.FestiveFavorManager` **[V]** — a currency manager it considers
   worth syncing, in a mod that is **not on disk in either root**. Unassessed.

---

## Verification

**Already established** — read from decompiled 1.6 assemblies or shipped XML, and cited by
`Type.Method` on [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54). Every
*positive* mechanism above is of this kind, and none of it depends on the sweep.

### What the stated validation is actually worth

**The wide pass reads stronger than it is.** Every UTF-16LE sweep behind the negative was run
as `rg -a --encoding utf-16le`. That form is now known to **miss strings provably present in
the `#US` heap, and to miss them non-uniformly** —
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103); the prescribed replacement is
`-a` with a null-interleaved pattern (`G\x00a\x00m\x00e\x00`). The addendum's "seventeen
families, each run in ASCII and again in UTF-16LE" therefore does not license the exhaustive
reading its wording invites. Anything citing this document's negative outside it should cite
this paragraph with it.

**The negative survives anyway, and that is not this document's own claim.** The close-out
audit independently re-ran three of the addendum's sweep families plus its highest-signal one
— the UTF-16LE affordability-failure strings (`NotEnough*`, `CannotAfford`, `Insufficient`),
which is how a currency announces itself even when every identifier is obfuscated — and
reached the same result **harder** than either #54 comment claimed: **nothing in the corpus
stores a Def-keyed spendable balance** **[V]**. Re-running the remaining families in the
corrected form is cheap and is worth doing before the negative is leaned on anywhere outside
this document.

### Still needs a prototype

1. That the `Scribe_Collections.Look(…, LookMode.Def, LookMode.Value)` round-trip survives
   adding a `CurrencyDef` mid-save — the whole point of not using `DefMap` (**T-37**), and
   cheap to test with a save, a def addition and a reload. The same test covers the
   *removal* case, whose null-key behaviour is marked **[I]** in *Persistence*.
2. That the D3 postfix's 26px row lands where intended in both map and world view, that the
   world-view guard does not hide it in normal play, and that it stacks rather than collides
   with Faction Customizer's `GlobalControlsOnGUIPrefix` when both are active.
3. That `MP.RegisterAll` behind an `MP.enabled` guard leaves single-player untouched when
   `0MultiplayerAPI.dll` is present but Multiplayer is not.
4. **Whether `QuestInfo` can cross the wire as a sync argument.** It is `IExposable` but
   not `ILoadReferenceable` **[V]**, and Multiplayer's argument serialisation for such a
   type was not read. If it cannot, register
   `ActivateQuest(QuestGiverDef giver, int offerIndex)` on a wrapper of ours instead — the
   index form needs no serialiser and is the fallback either way. **[I]**

5. **A drop pod from the faction venue onto a gravship or orbit map** — does
   `DropCellFinder.TradeDropSpot` find a sane cell, or fall through to its logged random-cell
   branch? One client, one exchange, read the log. **RUN.**
6. **Two founders exchange the last affordable item in the same tick** — exactly one item
   delivered, one refusal, the balance never negative. Two clients. **RUN.**
7. **A hand-authored `ThingDef` carrying `CompProperties_Techprint`** offers *Apply techprint*
   and credits its project. **[I]** as a composition; a one-def test.

### Observable checks that demonstrate the requirements

- **Exchanging at the decoder** drops the Intel readout by the price, places the item at the
  table, and the row disappears once the techprint is applied.
- **No research or hacking project moves the Intel readout** — by play, and by grep: no
  `TrySpend(Archinity_Intel` outside the exchange worker and `CurrencyQuestCurrencyInfo`.
- **With the exclusion postfix on, no Glitterite techprint appears** in an orbital trader's
  stock, a quest reward or ancient-complex loot across repeated generations; with it off, one
  does. This is the silent failure, and the only way to see it is to look for it.
- **A faction entry greys with its reason** when the Traders Guild is hidden, hostile or below
  `minGoodwill`, and un-greys when that clears.

- A quest offering `Reward_Currency` shows an Influence row in the quest-choice list
  *before* acceptance, alongside a Reverence row on the alternative approach.
- Studying a recovered artifact to completion destroys it and raises the Intel readout by
  the def's amount, with no research project involved.
- A purchase debits the readout and the catalogue entry goes on cooldown; **a favour purchase
  does not move the Schism chain's index; only a step's quest outcome does** — checkable by grep as well as by play, per *Structural
  separation*.
- The number survives a save/reload, and survives the colony moving map.
- **A shelved quest offer does not appear in the quests tab, does not send a letter, and
  does not expire** across several in-game seasons; buying it makes it appear and accept in
  the same frame, and the pool refills to its target count.
- **A multi-choice purchasable quest charges the price it displayed**, and accepting it
  produces **no** `"still has a choice unresolved"` error in the log. Both halves matter:
  the error is the `Choose`-omission defect and the price is the `Choose`-destroys-choices
  defect, and they have the same root.
- **A `QuestGiverDef` authored `onlyOneReward: false` shows an empty catalogue** — confirm
  the startup validator catches it rather than the player discovering it.
- **Raising Trace raises the price of an Intel offer and leaves every Influence offer's
  price unchanged** — the decoupling ruling, visible in one window.
- **Opening the network window generates no quest**, on either client. This is the donor's
  defect and it is the one worth checking deliberately: watch the save's quest count across
  ten window opens.

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| **Every number** — earn rates, prices, starting balances, caps | Balance. `GLITTERTECH.md` § *Saved state and remaining work* leaves project costs and catalogues to authoring. | Whoever authors the catalogues. |
| **Does either currency decay or expire?** The donor's Intel rots **[V]**; Reverence decays by requirement. | A balance that never decays is a different economy from one that does, and it changes whether hoarding is a strategy. Influence decaying below a step's price can strand the Schism plot (*Failure and recovery*). | Capability: yes — item rot (*Three Intel delivery options* (a)/(c)) or a tick debit on `WorldComponent_Currencies` ([`TRACE.md`](TRACE.md) § *What changes it* › *Decay* has the shape). Choice: [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (Intel with [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117)). |
| **Which venue carries each Instruction item — table, faction or both** | A Spine item at a faction venue alone can softlock the campaign on hostility or a missing faction (**T-07**). Both venues are built either way. | [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117). |
| **The exchange catalogue, its Intel prices and its cadence** (`cooldownDays`, `maxIssued`, the table's own research gate, `minGoodwill`) | Balance and pacing. Every one is an XML field. | [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117). |
| **Does Trace raise exchange prices?** | [`TRACE.md`](TRACE.md)'s `intelCostModifier` applies wherever `CurrencyPurchaseDef.currency == Archinity_Intel`, which **includes every exchange entry by construction** — so aggression is taxed twice, in pursuit and in the price of Instruction. | [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) (exchange prices and Trace exposure); mechanism: a per-entry opt-out, ~2 lines. |
| **Is the exchange instant, or does a colonist work it?** | Instant is the build. A Job on the table venue — `JobDriver_ApplyTechprint`'s shape — is ~40 more lines; a bill is rejected (see *Delivery surfaces*). | [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) (*exchange cadence*). |
| **When is the Traders Guild contactable?** | Hidden until the orbit reveal ([`ORBIT.md`](ORBIT.md), Conrad 2026-09-15); the faction venue respects `Faction.Hidden`. Remaining risk: WTL dropping it from the roster (`ORBIT.md` § *Failure and recovery*, **T-07**). | [`ORBIT.md`](ORBIT.md). |
| **Does VFE Deserters ship?** | Its contraband manager registers every techprint `ThingDef` as Intel-priced stock, a second exchange this document cannot see. | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14). |
| **Which of the three Intel delivery options ships** — (a) VFED's contraband economy wholesale, (b) the stored balance and our exchange worker, (c) our own Intel item with our own vendor | All three are verified available mechanisms and are priced at *Available mechanisms* § *Three Intel delivery options*. (a) costs ~15 lines of ours but imports VFED's Empire-keyed extraction, its `JoinDeserters` force-hostility, VFED visibility pricing (displacing Trace), **T-18**, rot/loot/mass, beacon-only spending and the loss of site-inspection grants; (b) is the exchange mechanism; (c) buys back the free `ResourceReadout` row without VFED's war or dependencies but still cannot grant Intel by site inspection. **The T-99 exclusion postfix is owed under all three if VFED ships.** | Selected on [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map). |
| **How many offers sit in each currency's pool, and what each is worth** | Pool size is save weight; `costPerMarketValue` is the exchange rate between a mission's payout and its price. | Balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119); Intel prices [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117). |
| **Does VEF ship?** | Build A is ~95 lines of new C#; Build B is ~290 and re-derives the pool, persistence, refill, price display, challenge-rating row, choice resolution and accept sequence. | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14). **VEF is already required** by [`PRESSURE.md`](PRESSURE.md) § 4 and by [`HACKING.md`](HACKING.md)'s carrier, so this adds no new mod — but the ledger owns the decision, not this document. |
| **Is the always-visible readout (D3) the right surface, or does the campaign UI absorb it?** | D3's layout arithmetic is the maintenance cost; a tab of our own removes it. | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build map); every surface has a route ([#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)). D1 and D2 ship regardless. |
| **Which quests are purchasable, and what each contains** | Decides what the catalogue actually holds. The machinery is built here and the membership test is one `DefModExtension`; the contents are not this document's. | Authoring, alongside the era content. [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106) settled the mechanism. |
| **Which route carries the Schism chain, and which marking act commits the founders?** | Routes A–D and the marking-act comparison are in *The Schism catalogue — a spend that advances the plot*. *First plot spend* breaks `RELIGION.md`'s banking clause; *first Influence gained* meets it by construction. | Selection on the next map ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)). |
