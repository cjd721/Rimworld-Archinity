# Spendable currencies

## Purpose and scope

Implements the two **spendable operational currencies** the campaign requires:

- **Influence** — [`docs/requirements/RELIGION.md` § *The Schism Path — Influence + Reverence*](../requirements/RELIGION.md).
  Earned by Schism operations, spent through the anti-Church network on favors
  Goodwill cannot buy.
- **Intel** — [`docs/requirements/GLITTERTECH.md` § *Intel Is Capability, Not Exposition*](../requirements/GLITTERTECH.md).
  Recovered from Glitterite raids as artifacts, decoded at home, consumed by
  advanced research and hacking.

Established on [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54), which
absorbed [#55](https://github.com/cjd721/Rimworld-Archinity/issues/55)'s currency half.

**This document owns** the mechanism that holds a spendable balance, moves it, persists
it, shows it, and spends it against a catalogue. It owns that mechanism for *any* number
of currencies, because nothing in it names either fiction.

**It does not own:**

| | |
|---|---|
| The **exemplar gate** — a research project requiring a physically-analysed item | [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67). The interface between the two is stated below, and what it does *not* commit either side to is the load-bearing part. |
| **Exaltation** and **Reverence** | [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53), [#98](https://github.com/cjd721/Rimworld-Archinity/issues/98) / [`RELIGION.md`](RELIGION.md). Threshold ladders, not spends. |
| **Trace** | [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56). A band ladder, not a balance. #56 also rules on whether sharing one store with Intel couples it to Church standing — see *What is shared*. |
| The **purchasable quest catalogue** — which quests are for sale, at what price, out of what pool | [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106). It **consumes** the catalogue machinery below rather than duplicating it; see *The purchasable-quest seam*. |
| The **ordered campaign chain** that Schism operations advance | **No owning ticket yet.** Its separation from spending is this document's business; its carrier is not, and nothing currently owns it — see *Outstanding decisions*. |
| Cross-cutting political-UI layout | [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61). The readout for these two numbers is here. |

**Why this is its own document rather than a section of [`RELIGION.md`](RELIGION.md).**
The verdict is that one mechanism serves both currencies. Filing it under religion would
make Glittertech reach into the religion spec for Intel's storage, persistence and
readout, and would file a Glitterite mechanism under Church politics — the shape #56
exists to guard against. Two systems consume this; neither owns it.

---

## The build

**One implementation, two `CurrencyDef` rows in one store, and it is ours to write** — the
named donor holds no currency to donate. See *Available mechanisms*.

Read that headline precisely, because an earlier draft of it ("one implementation, instanced
twice") understated the coupling. The build is **one `WorldComponent_Currencies` holding one
`Dictionary<CurrencyDef,int>`**; Influence and Intel are two *rows* in that dictionary, under
one `Scribe` key, in one component. Nothing is instanced twice. **That coupling is exactly what
[#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) is being asked to rule on** — see
*What is shared*, which describes the shape correctly and states what the sharing does and does
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
    AcceptanceReport CanPurchase()
    void             Purchase()
```

`CurrencyPurchaseDef` is modelled on vanilla **`RimWorld.RoyalTitlePermitDef`**, which is
the same idea — a Def-driven catalogue of favors with a worker per entry — and already
carries `workerClass`, a cost, `prerequisite`, `cooldownDays` and a UI position **[V]**.
Taking the shape from vanilla rather than from `VFED.DeserterServiceDef` costs nothing and
buys no VFE dependency.

Two `CurrencyDef`s ship: `Archinity_Influence` and `Archinity_Intel`. Adding a third is
one XML file.

### Where state lives

`WorldComponent_Currencies`, holding exactly two dictionaries:

```csharp
private Dictionary<CurrencyDef, int>         balances;
private Dictionary<CurrencyPurchaseDef, int> lastPurchasedTick;   // cooldowns
```

**Nothing else lives here, and that is the design.** No campaign index, no chapter, no
quest reference. See *Structural separation*.

Public surface — the whole of it:

```csharp
int  Balance(CurrencyDef c);
bool CanAfford(CurrencyDef c, int amount);                  // pure; safe from a draw method
bool TrySpend(CurrencyDef c, int amount, string reason);    // mutating; Job or synced callers only
void Credit(CurrencyDef c, int amount, string reason);
[SyncMethod] void TryPurchase(CurrencyPurchaseDef purchase);
```

### What changes it

**Credit A — a mission pays.** `Reward_Currency : RimWorld.Reward` emitting
`QuestPart_GrantCurrency`, with `QuestNode_GrantCurrency` for hand-authored quests.
`RimWorld.Reward` is abstract with exactly three abstract members — `InitFromValue`,
`GenerateQuestParts`, `GetDescription` — plus `StackElements` and `TotalMarketValue`
**[V]**. `VFED.Reward_Visibility` is the working precedent for a non-item reward and uses
only vanilla API **[V]**.

This is the requirement that *"the same mission family can support radically different
approaches"* — a covert operation offers a `Reward_Currency` for Influence, a public
miracle offers Reverence, and both rows appear in the same quest-choice list.

**Credit B — an artifact is decoded.** `CompUseEffect_GainCurrency`
(`{CurrencyDef currency, int amount}`) on the recovered-artifact `ThingDef`, paired with
vanilla `CompUseEffect_DestroySelf` so the artifact is consumed.

Template: `RimWorld.CompUseEffect_FinishRandomResearchProject`, a 25-line `CompUseEffect`
subclass overriding `DoEffect(Pawn)` and `CanBeUsedBy(Pawn)` to mutate global game state
**[V]**. Once the comp exists, each new artifact is pure XML.

**Credit C — optional site lore.** The same comp on a studiable object, or
`QuestPart_GrantCurrency` on a site-completion signal. This is the requirement that
*"optional investigation can provide Intel progress"* — which is why Intel must be a
number and not an item, since curiosity cannot spawn loot.

**Debit.** `TrySpend`, reached only from `TryPurchase` or from a Job. Never from a draw
method.

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
> *Two names an earlier draft listed here were stale-version inflation and are struck.* VFE
> Power's only hits are in its **1.2** and **1.3** assemblies; Medieval Overhaul's only hit is
> in its **1.5** assembly. Neither ships a 1.6 copy carrying the name **[V]**, so neither is in
> this game's stack at all. This is the identical error the ticket's own addendum correctly
> caught on Achievements Expanded, and it was made two paragraphs later: **a hit is evidence
> only if it is in the assembly 1.6 loads.**
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

### Cost

| Piece | Kind | Lines | Lands in |
|---|---|---|---|
| `CurrencyDef` | new C# | ~15 | `Archinity.Altar/Source/Currencies.cs` |
| `CurrencyPurchaseDef` + `CurrencyCategoryDef` + `CurrencyPurchaseWorker` | new C# | ~45 | same |
| `WorldComponent_Currencies` | new C# | ~90 | `Archinity.Altar/Source/Currencies.cs` |
| `Reward_Currency` | new C# | ~60 | `Archinity.Altar/Source/CurrencyQuests.cs` |
| `QuestNode_GrantCurrency` + `QuestPart_GrantCurrency` | new C# | ~70 | same |
| `CompUseEffect_GainCurrency` + properties | new C# | ~35 | `Archinity.Altar/Source/Currencies.cs` |
| `MainTabWindow_Network` (catalogue + balance header) | new C# | ~140 | `Archinity.Altar/Source/CurrencyUI.cs` |
| `MainButtonWorker` subclass (D4, optional) | new C# | ~20 | same |
| `GlobalControlsUtility.DoDate` postfix (D3) | patch | ~25 | `Archinity.Altar/Source/Patches.cs` |
| MP registration behind an `MP.enabled` guard | new C# | ~15 | `Archinity.Altar/Source/Patches.cs` |
| **Total new C#** | | **~430–520** | one assembly |
| Two `CurrencyDef`s, one `MainButtonDef`, every catalogue entry, every price, every reward amount, every artifact's comp | **XML** | — | `Archinity.Altar/Defs/`, `Archinity.Glitterites/Defs/` |

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
null keys and logs once; it does not silently retain them.

> An earlier draft cited **T-04** for this. That was wrong and is withdrawn. T-04 is
> *"unresolvable cross-references are omitted, not nulled"* — XML **def loading**, a different
> subsystem, and the opposite outcome from the one described here. `Scribe_Collections` with
> `LookMode.Def` is save loading, not def loading.

### Multiplayer

**Credits are free.** `CompUseEffect_GainCurrency` is reachable only through
`CompUsable.CompFloatMenuOptions` → `TryStartUseJob` → `JobDriver_UseItem` →
`CompUsable.UsedBy` → `CompUseEffect.DoEffect(Pawn)` **[V]** — a Job, which Multiplayer
syncs natively. That is the same argument `Archinity.Altar.csproj` already makes for the
altar. Quest-part credits fire on quest signals inside the synced quest machinery.

**The debit is the only new sync surface**, because it originates at a button — and it is a
single method by design.

`TryPurchase(CurrencyPurchaseDef)` carries `[SyncMethod]` from **`Multiplayer.API`**, in
`0MultiplayerAPI.dll` under the Multiplayer mod's `1.6/Assemblies/` **[V]**. It is a
compile-time-only reference with **no hard dependency**: `Multiplayer.API.MP`'s static
constructor looks for the `Multiplayer` assembly among `LoadedModManager.RunningMods` and
falls back to a `Dummy` implementation with `MP.enabled == false` when it is absent **[V]**.
Register with one `MP.RegisterAll(assembly)` behind an `MP.enabled` guard. The attribute
type is `SyncMethodAttribute` — there is no `Multiplayer.API.SyncMethod` **[V]**; the
similarly-named `ISyncMethod` is a registration handle.

**Defs, not settings** (**T-18**). Every price, amount, cooldown and catalogue entry is a
`CurrencyPurchaseDef` field. No `ModSettings` is read anywhere in this mechanism.

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

### Structural separation — requirement, answered structurally

> *"Plot progression is tracked separately, so spending Influence never reverses the ordered
> campaign. That separation is load-bearing and must be structural, not a convention."*
> — [`RELIGION.md`](../requirements/RELIGION.md)

Three layers, none of them a convention:

1. **Different owners.** Balances live in `WorldComponent_Currencies`. The ordered Schism
   chain lives in whatever carrier is eventually built for it — **and no ticket owns that
   yet**; see *Outstanding decisions*. Separate components and separate `Scribe` keys,
   whichever carrier wins.
2. **The spending API has no vocabulary for progression.** `TrySpend(CurrencyDef, int,
   string) → bool` takes a currency and a number. It cannot name a chapter, a chapter
   index, a quest or a mission; there is no argument to pass and no return value to
   interpret.
3. **The chain has exactly one writer, and it is a quest outcome.** Purchases add to a
   *pool*; pool membership is a different field from the chain index. A purchase worker
   that wanted to touch the chain would have to acquire the progression component, a
   reference nothing hands it.

The donor demonstrates the same split and is worth citing for it: `VFED` keeps a
purchasable pool (`ServiceQuests`, refilled by `EnsureQuestListFilled`) separate from an
ordered chain (`PlotMissions`), and the only writer of the chain index is
`WorldComponent_Deserters.Notify_PlotQuestEnded`, which no spend path reaches **[V]**.

Layer 3 is **checkable rather than asserted**: no type in the purchase-worker namespace may
reference the progression component. That is a grep, not a review habit.

### The interface to [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67)

**Spending Intel and consuming an exemplar are two acts, on two objects, and must not be
folded together.** Intel is a scalar with no identity beyond its `CurrencyDef` and no
location. An exemplar is a particular `Thing` the colony holds, with a `ThingDef`, a stack,
a quality and a position.

Folding either into the other makes a required case inexpressible, in each direction:

- [`GLITTERTECH.md`](../requirements/GLITTERTECH.md) gives Intel a source with **no item** —
  *"optional investigation can provide Intel progress/bonuses"*. If Intel were an item,
  curiosity would have to spawn loot.
- The same file gives the exemplar gate a case with **no cost** — *"every major Glittertech
  branch requires an exemplar… Want their armor? Bring home armor."* That is possession,
  not payment. If the exemplar were "N Intel", any N Intel would open any branch and the
  acquire→analyze loop collapses.

**Vanilla already models them as two independent fields.** `Verse.ResearchProjectDef` carries
`requiredAnalyzed : List<ThingDef>` (satisfied via `AnalyzedThingsRequirementsMet`) *and*
`techprintCount` (satisfied via `TechprintRequirementMet`, backed by
`ResearchManager.techprints`), and `CanStartNow` ANDs them along with the rest **[V]**.

**What this document offers #67:** `Balance`, `CanAfford`, `TrySpend`, `Credit` above. The
sync boundary and the balance stay on this side.

**Whether #67 calls any of them is not decided here — and was never this document's to
decide.** An earlier draft of this section stated that "#67 calls `CanAfford` when drawing a
gate and `TrySpend` from inside an already-synced work path". **That expectation is
withdrawn.** It presumes an answer to *does Analysis ever cost Intel*, which is a
**requirements** question owned by
[`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md) and now tracked as
the Analysis-pricing question in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2). `docs/specs/RESEARCH.md`
reached the opposite presumption from the other side — it *ruled* "do not price analysis in
Intel" — and has withdrawn that ruling. **Neither spec decides it.** #67 and #54 are both
capability tickets; neither had the authority.

Conditional on that question, and stated conditionally:

- **If Analysis is priced in Intel**, the calling discipline is the one this document imposes
  on *every* caller and is not special to #67: `CanAfford` is pure and safe from a draw
  method; `TrySpend` mutates and may be reached only from a Job, a quest part or a synced
  method — never from a draw method, which is the specific defect in the donor **[V]**.
- **If it is unpriced**, #67 touches nothing in this document.

**What this document needs from #67:** nothing at debit time, under either ruling.

**Relevant negative for #67, established here:** no field on `ResearchProjectDef` debits a
quantity of an arbitrary resource. `baseCost` is pawn-work points; `techprintCount` consumes
one specific `ThingDef` pre-completion by a job; `knowledgeCost` replaces `baseCost` and
accrues into the project rather than draining a pool **[V]**. A project that costs Intel
must be written. `ResearchManager.FinishProject(ResearchProjectDef, bool, Pawn, bool)` is
public and is the single funnel **[V]** — but it **recurses into unfinished prerequisites**
**[V]**, so a naive postfix debits once per project in the chain, and a *gate* belongs in a
prefix because by postfix time `progress[proj]` is written and the unlock signal has fired.
That negative stands whichever way that is settled; it only becomes *relevant* if Analysis is priced.

### What is shared, for [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) to rule on

#56 is the single decision point for whether shared machinery couples Intel to Church
standing. Reported, not ruled on:

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
  design change **[I]**.

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| A `CurrencyDef` leaves the load order | Key resolves null on load **[I]** | `FinalizeInit` drops null keys and logs once. The balance is lost, which is correct — the currency no longer exists. |
| Stored balances silently rebind to the wrong currency | **None — this is the silent one** | Prevented, not recovered: `LookMode.Def`, never `DefMap`. **T-37**. |
| A purchase worker throws mid-`Purchase()` | Log error, and the balance in D1 is visibly unchanged | `TryPurchase` checks `CanPurchase()` first and debits **after** `Worker.Purchase()` returns, so a worker that throws *before* granting anything costs the player nothing. **The ordering admits the opposite failure, and this document should say so:** a worker that grants its goods and *then* throws hands them out **free and un-cooldowned**, because the debit is never reached. `CanPurchase()` makes it narrow; it does not make it absent. The mitigation is a worker discipline, not a mechanism — **perform the grant as the last statement**, so anything that can throw throws before it. Debiting first would trade this for a charge with no goods, which is the worse failure. **[I]** |
| Two clients disagree on a balance | MP desync | `TryPurchase` is the only mutation reachable from UI and carries `[SyncMethod]`. Every other mutation is inside a Job or a quest part. |
| The catalogue is empty or every entry unaffordable | Visible in D1 | Not a failure. The window states the balance and the shortfall, as `TrySpendIntel`'s `"VFED.NotEnough"` message does **[V]**. |
| The D3 postfix breaks on a game update | **Visible** — the row vanishes or misdraws | Layout arithmetic only; the balance and every spend path are unaffected. This is the piece most exposed to a RimWorld update, and it fails loudly rather than silently. |

**No campaign softlock is reachable from this document.** Spending cannot move campaign
state — see *Structural separation* — so no sequence of purchases can strand the player.

---

## Status

**Evidence class: READ.** Settled from decompiled 1.6 assemblies and shipped XML.

| | |
|---|---|
| **Verified available mechanisms** | `WorldComponent` + `Scribe_Collections.Look(…, LookMode.Def, LookMode.Value)`; `World.FillComponents` backfill; `RimWorld.Reward` + `QuestPartUtility.GetStandardRewardStackElement`; `CompUsable` → `JobDriver_UseItem` → `CompUseEffect.DoEffect`; `MainButtonDef` as pure XML; `GlobalControlsUtility.DoDate`'s `ref float curBaseY`; `Multiplayer.API.SyncMethodAttribute` with soft-dependency fallback. All **[V]**. |
| **Confirmed negative** | Nothing in vanilla, the DLC or the corpus holds a **Def-keyed, world-level, spendable balance**. The named donor holds no balance at all. Independently re-verified by the close-out audit, which re-ran the highest-signal sweep family and found the negative holds **harder** than either #54 comment claimed. **The sweep form used to reach it was itself defective** — see *Verification* and [#103](https://github.com/cjd721/Rimworld-Archinity/issues/103). |
| **Proposed, not selected** | The whole build above. It is **[I]** as a composition, and the line estimates with it. |
| **Open parameters** | Every number, plus whether Analysis is priced at all (the Analysis-pricing question in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2)). See *Outstanding decisions*. |

Established on [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)
(absorbing [#55](https://github.com/cjd721/Rimworld-Archinity/issues/55)'s currency half).

---

## Available mechanisms

### The named donor — VFE Deserters, and what it actually is

`…/294100/3025493377/1.6/Assemblies/VFED.dll`. `MOD-SNAPSHOT.md` marks
`oskarpotocki.vfe.deserters` **Src 1.4 ⚠**, so everything below is read from the 1.6
assembly the game loads, not the stale source tree.

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
  draws both balances as labelled, icon'd rows in the window header **[V]**. #54's resolution
  claimed *"VFED ships no balance readout"*; that is too strong and is corrected here. The
  defensible claim is that there is **no persistent readout** — the only one is modal,
  computed in `PostOpen`, and dies with the window. D3 is ours to write for that reason,
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
| The ordered chain | **KEEP THE SHAPE, REPLACE THE DRIVER** — and it does not belong to this document. No ticket owns it yet. See below. |
| `Reward_Visibility` | **KEEP THE PATTERN, not the type** — it is a plain `RimWorld.Reward` subclass using only vanilla API. |

### The purchasable-quest seam, and why it is [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106)'s

`VFED.WorldComponent_Deserters.EnsureQuestListFilled` refills `ServiceQuests` and sets
**`slate.Set<bool>("purchasable", true)`** on every quest it generates **[V]** — that is
exactly the `$purchasable` node the map named, and the corpus does carry it. **This evidence
was in hand when #54 was resolved and was not reported there**; it is recorded here.

The map made a purchasable quest catalogue conditional on #54 and #55 settling their
currencies. **Both are settled**, so the question has graduated out of *Not yet specified* and
is open as [#106 — The purchasable quest catalogue](https://github.com/cjd721/Rimworld-Archinity/issues/106).

**#106 consumes this document's design; it must not duplicate it.** One behavior, one owner:

- **Here:** the balance (`WorldComponent_Currencies`), the catalogue Def
  (`CurrencyPurchaseDef`), the entry base class (`CurrencyPurchaseWorker`), the shop window
  (`MainTabWindow_Network`) and the single synced debit (`TryPurchase`). None of these names
  a quest, a fiction or a price — a quest purchase is simply a `CurrencyPurchaseWorker`
  subclass whose `Purchase()` generates or accepts a quest, plus XML rows.
- **#106's:** the quest **pool** and its refill policy, which quests are in it, their prices,
  and how `slate` carries `purchasable` into whatever `QuestScriptDef`s we author. That is the
  one piece it owes that is not currency machinery. VFED's `ServiceQuests` +
  `EnsureQuestListFilled` is the shape to copy, and MP Compat's need to sync both
  `EnsureQuestListFilled` and `InitializePlots` **[V]** is the standing warning: a refill that
  runs from a draw method is a desync.

A second balance, a second store or a second shop window opened by #106 would be a
duplication, and this paragraph exists to make that visible before it is proposed.

### The ordered-operation surface, and why it is not this document's

`VFED.WorldComponent_Deserters.InitializePlots` builds `List<PlotMissionInfo>` once, and
`Notify_PlotQuestEnded` advances by **index**: on `QuestState.EndedSuccess` it generates
`PlotMissions[IndexOf(info) + 1]`; on failure or expiry it regenerates *the same index*
**[V]**. One live quest at a time, no skipping, no reversing. **The shape is exactly right
and is worth copying.**

The **driver** is not: `InitializePlots` iterates `VFEEmpire.WorldComponent_Hierarchy.Titles`
filtered on `seniority >= RoyalTitleDefOf.Knight.seniority`, and the branch chance is a
`switch` on literal seniority integers 700/701/800/801/802/900/901 **[V]**. Repointing it to
Schism operations replaces the method rather than patching it — roughly 50–60 lines **[I]**,
and the rewrite drops the Empire coupling entirely.

**That answers #54's question and hands the build to nobody, which is the honest statement.**
An earlier draft handed it to [#40](https://github.com/cjd721/Rimworld-Archinity/issues/40).
**#40 does not own it:** its body scopes it to *"the implementation surface for the
**Chronicle** and **nothing else**"*, it carries `wayfinder:grilling` + `hitl`, and it is
deliberately **last** in the Chronicle chain **[V]**. The Schism ordered-operation chain is a
different chain. A deferral needs a ticket that can actually answer the question, and widening
#40's scope to cover this is Conrad's call, not this document's. **So: gap, no owner.**

What the currency side needs from that carrier, whichever ticket eventually owns it, is
*nothing* — and that is the point.

### Vanilla and the DLC

| Mechanism | What it gives | Why it is not the answer |
|---|---|---|
| **Royal favor** — `Pawn_RoyaltyTracker.favor : Dictionary<Faction,int>`, with `GetFavor`, `GainFavor`, `TryRemoveFavor`, `RefundPermits` **[V]**; earned from quests via `QuestPart_GiveRoyalFavor` / `Reward_RoyalFavor`, spent through `RoyalTitleDef.favorCost` and `RoyalAid.favorCost` **[V]** | A complete stored, spendable, quest-earned, catalogue-spent balance — **the closest thing to this build that already exists**. Its display name is even per-faction data (`FactionDef.royalFavorLabel`, `.royalFavorIconPath` — the Empire sets it to "honor") **[V]**, so a second instance could be renamed without code. | **Per pawn, keyed by faction.** There is no colony-level row, so "the colony's Influence" has nowhere to sit; and `RoyalTitleDef.favorCost` binds the catalogue to the title ladder, which is [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)'s Exaltation. Reusing it couples Influence to the ladder the requirements explicitly say it is not. **This is the closest miss in the survey, and worth re-checking if the per-pawn constraint ever relaxes.** |
| **Permit purchases** — `Pawn_RoyaltyTracker.factionPermits : List<FactionPermit>`, scribed `LookMode.Deep` **[V]** | The inverse architecture: **store the purchases, derive the balance** | Not adopted — our balance is earned, not derived from a ladder. But it is the reason a *cooldown* is stored per purchase here (`FactionPermit.lastUsedTick`) rather than per currency. |
| **Permit points** — `Pawn_RoyaltyTracker.GetPermitPoints(Faction)` **[V]** | A budget spent on a Def catalogue | **Derived, not stored.** It sums `permitPointsAwarded` walking the title chain. A mission cannot pay you permit points. |
| **`RoyalTitlePermitDef`** **[V]** | The catalogue shape: `workerClass`, cost, `prerequisite`, `cooldownDays`, `uiPosition` | **Adopted** — this is `CurrencyPurchaseDef`'s model. Its `minTitle`/`faction` coupling is what we drop. |
| **Anomaly knowledge** — `ResearchManager.anomalyKnowledge : Dictionary<ResearchProjectDef,float>` **[V]** | Def-keyed persisted numbers, scribed `LookMode.Def, LookMode.Value` | **Per project, not a pool.** It is progress that accrues into a project, not a balance a mission pays. **Its persistence idiom is adopted.** (The code is in `Assembly-CSharp.dll`; the Anomaly *content* is not on disk — see *The wide pass*.) |
| **Techprints** — `ResearchManager.techprints`, `ApplyTechprint`, `JobDriver_ApplyTechprint` **[V]** | A consumable item satisfying a research requirement | Per project, one `ThingDef`, not a currency. Relevant to [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67), not here. |
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

**Read the scope of that claim carefully, because an earlier draft overstated it.** The
*type* exists in `Assembly-CSharp.dll` **[V]**. **Zero instances of it exist anywhere in the
corpus:** Anomaly is not on disk — `Data/` holds Biotech, Core, Ideology, Odyssey and Royalty
only — and an XML sweep for `KnowledgeCategoryDef` over both corpus roots returns **0 files**
**[V]**. The familiar pair (Basic, Advanced) is Anomaly content, and asserting it is
**[I], knowledge from outside the corpus**. It was previously written here as "instanced twice
(Basic, Advanced) **[V]**", which was unsupported: *"instanced twice in the entire corpus"* is
a statement the corpus cannot make.

It is a progress meter rather than a held pool in any case. The narrower point survives intact
and is the one worth keeping: **currency-as-a-`Def` is a shape RimWorld's own code already
understands.**

**Notable negatives, each read rather than assumed** **[V]**: VFE Empire's Honor is an award
*ledger* (`VFEEmpire.HonorsTracker` holds `List<Honor>`, no integer); VFE Classical's "favor"
is a `bool` per senator; RimPacts' favor is a 0–100 reputation clamp consumed only by
thresholds; Worksites Expanded and VFE Medieval 2 charge silver.

**Achievements Expanded's `TryPurchasePoints` / `AvailablePoints` is 1.4-only.** Two details
in the earlier statement of this were wrong. It is bundled inside **six** unique mod ids —
`1814987817`, `1914064942`, `2134308519`, `2562018758`, `3014906877`, `3014915404` — not
seven; and `1814987817` ships **1.2** and **1.3** copies as well, so "every copy is at `1.4/`"
is false **[V]**. The part that matters is confirmed and unchanged: **no 1.6 copy exists in
either root** **[V]**, so it is dead for this game version.

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

### Observable checks that demonstrate the requirements

- A quest offering `Reward_Currency` shows an Influence row in the quest-choice list
  *before* acceptance, alongside a Reverence row on the alternative approach — the
  *"different approaches, different reward profiles"* requirement, visible.
- Decoding a recovered artifact destroys it and raises the Intel readout by the def's
  amount, with no research project involved.
- A purchase debits the readout and the catalogue entry goes on cooldown; **the campaign's
  ordered chain does not move** — checkable by grep as well as by play, per *Structural
  separation*.
- The number survives a save/reload, and survives the colony moving map.

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| **Every number** — earn rates, prices, starting balances, caps | Balance. `RELIGION.md` says *"exact catalogs are implementation work"*; `GLITTERTECH.md` says *"project costs… remain implementation/authoring work"*. | Whoever authors the catalogues. |
| **Does either currency decay or expire?** Neither requirements file says. The donor's Intel rots **[V]**; Reverence decays by requirement. | A balance that never decays is a different economy from one that does, and it changes whether hoarding is a strategy. | **Requirements gap, no ticket** → [`RELIGION.md`](../requirements/RELIGION.md) for Influence, [`GLITTERTECH.md`](../requirements/GLITTERTECH.md) for Intel. |
| **Does any Analysis project cost Intel on top of its exemplar?** | Decides whether [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67) calls anything in this document at all. Two specs presumed opposite answers; **neither had the authority**, and both have withdrawn. | **Open requirements parameter**, owned by [`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md), tracked as the Analysis-pricing question in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2). |
| **Does sharing one dictionary between Influence and Intel couple Intel to Church standing?** | If yes, split into two `WorldComponent`s (~15 lines, no design change). | [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56), item 4. |
| **Is the always-visible readout (D3) the right surface, or does the campaign UI absorb it?** | D3's layout arithmetic is the maintenance cost; a tab of our own removes it. | [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61) rules on the shape; D1 and D2 ship regardless. |
| **Which quests are purchasable, out of what pool, at what price?** | Decides what the catalogue actually contains. The machinery is built here; the contents are not. | [#106](https://github.com/cjd721/Rimworld-Archinity/issues/106) — **consuming** `CurrencyPurchaseDef` / `CurrencyPurchaseWorker` / `MainTabWindow_Network`, not duplicating them. |
| **Which carrier holds the ordered Schism chain?** | This document requires only that it is *not* `WorldComponent_Currencies`. | **No owner.** [#40](https://github.com/cjd721/Rimworld-Archinity/issues/40) is the Chronicle's implementation surface and *"nothing else"* **[V]** — a different chain, `hitl` + `wayfinder:grilling`, deliberately last in its own chain. Widening it is Conrad's call, not this document's. |
