# Technical findings

Verified facts underpinning the Archinity design. Everything here was confirmed
against game defs or decompiled source — not documentation, not the wiki, not
assumption. Recorded so we never re-litigate it.

Game version 1.6.4871. Verify again after any major RimWorld update.

---

## Pacing and gating

### Quests can be gated on tech tier

`VEF.Storyteller.QuestChainExtension` has a `requiredResearch` field, unused by
any mod in our load order. `GameComponent_QuestChains.TryScheduleQuest`:

```csharp
QuestChainExtension ext = quest.GetModExtension<QuestChainExtension>();
if (ext.requiredResearch != null && !ext.requiredResearch.IsFinished)
    return false;
```

TechBlock's tier locks are `ResearchProjectDef`s, so they plug straight in:

| Def | Meaning |
|---|---|
| `TB_NeolithicTheory` | entered Neolithic |
| `TB_MedievalTheory` | entered Medieval |
| `TB_IndustrialTheory` | entered Industrial |
| `TB_SpacerTheory` | entered Spacer |
| `TB_UltraTheory` | entered Ultra |
| `TB_ArchoTheory` | entered Archotech |

### `rootMinProgressScore` is NOT a tech gate

`StorytellerUtility.GetProgressScore` is:

```csharp
return freeColonistCount * 1f + target.PlayerWealthForStoryteller * 0.0001f;
```

Colonists plus wealth/10000. Ignores research entirely. Vanilla gates sit at
3–10, which a wealthy neolithic colony clears in year one. Do not use.

### TechBlock's two projects per tier

- `TB_<Era>TechLock` — cost = `(tier's total research points × requiredPoints<Era>) − points already researched in that tier`. Shrinks as you research normally.
- `TB_<Era>Theory` — cost = the flat `<era>BaseCost` setting.

So advancing a tier costs a *fraction of the tier's value* plus a flat toll. It
is **not** "complete X% of the tree." Currently set to 0.75 across all tiers.

### Ignorance Is Bliss scope

`changeQuests` does **not** stop quests firing. It substitutes the faction in a
quest's threat for a tech-appropriate one ("Will not change the quest
description, but an appropriate faction will arrive").

Division of labour: **IIB controls who shows up, `requiredResearch` controls
when the quest appears.** Both needed; neither replaces the other.

`useActualTechLevel: true` is correct for us — its own tooltip says it is only
appropriate with a mod that drives colony tech level, which TechBlock does.

---

## Archite injection (VQE Ancients)

### Gene pool

`GetFilteredGenes(pawn, g => g.biostatArc > 0)` — every archite gene in the
loaded def database, minus `InjectionBlacklistDef`, minus genes the pawn has,
minus genes whose prerequisite is unmet. ~50 genes with our load order,
including `VRE_Transcendent` (now blacklisted in `Archinity.Pacing`).

`blacklistedGenes` is `List<string>` — plain defName strings, not
cross-referenced. Naming an absent gene is silently ignored, so the patch is
safe to over-specify.

### Outcome table

| Outcome | `baseWeight` |
|---|---|
| Success | 50 |
| Rejection | 35 |
| Spliceling | 8 |
| Splicehulk | 5 |
| Splicefiend | 2 |

All patchable. Optional looted facilities modify results — `VQEA_TraitSelectionPrism`
gives a choice of two archite genes instead of one random.

### Three independent gates

1. **The machine.** `VQEA_ArchogenInjector` inherits `neverBuildable: true`, but
   its base sets `minifiedDef: MinifiedThing` and `claimable: true`. You cannot
   build one — you find it in a vault, claim it, uninstall it, haul it home.
   Same for every support facility.
2. **Power.** 400 W running, 50 W idle. Hard requirement — see below.
3. **Ammo.** One `ArchiteCapsule` per injection. Not craftable by anyone at any
   tech level; the item description says so. Trade-only (outlander bases and
   caravans, orbital traders, Empire bases) plus ancient crate loot.

### Blood cannot gate it without C#

`Building_PawnProcessor.PowerOn` dereferences the power comp unguarded:

```csharp
public bool PowerOn => TryGetComp<CompPowerTrader>(this).PowerOn;
```

Read every tick via `ShouldProcessTick()`. Removing `CompProperties_Power`
causes a continuous NullReferenceException.

Adding `CompProperties_Refuelable` with a `HemogenPack` filter is crash-free and
gives a real fuel bar, but **does not gate** — VQEA's code never reads
`CompRefuelable`. Cosmetic only.

The capsule requirement is also not def-driven: `ThingDefOf.ArchiteCapsule` is
hardcoded in seven places, so hemogen cannot be added as a second ingredient.

Real gating requires ~10 lines of Harmony postfixing
`Building_PawnProcessor.get_PowerOn`. Deterministic, no RNG, reads only synced
state — assessed multiplayer-safe, but it means shipping an assembly.

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

## Decay — what survives being acquired centuries early

| Thing | Decays? | Notes |
|---|---|---|
| `ArchiteCapsule` | **No** | No `DeteriorationRate`, no ticker, no `CompRottable`, `Flammability 0`. Safe anywhere, forever. No shelter needed. |
| Minified buildings | **No** | `MinifiedThing` has no `statBases` ⇒ rate 0; inner building is `category=Building` ⇒ `CanEverDeteriorate` false. A crated `VQEA_ArchogenInjector` keeps indefinitely, indoors or out. |
| `Genepack` | **Yes — 20 days** | `DeteriorationRate 5`/day vs 100 max HP. No grace period. `deteriorateFromEnvironmentalEffects: false`, so roofs, rooms and shelves give **zero** protection. |

**Consequence:** capsules and the crated god machine can be looted in the
Neolithic and stored for a decade with no special handling. **Genepacks cannot
be an early-game reward** — they are dust in 20 days.

The only thing that stops genepack decay is a powered `GeneBank` — research
`Xenogermination` (Industrial, cost 1000, itself gated behind Electricity),
40 W constant. Unpowered banks do not protect.

Genepack rewards are therefore viable **only from Industrial onward**, which is
fine: that is exactly when guaranteed-specific-gene rewards are wanted anyway.

> Do **not** patch `Genepack`'s `DeteriorationRate` to 0 to work around this.
> Genepacks are a single ThingDef with dynamic contents, so it is all-or-nothing
> and would strip gene banks of their entire purpose.

---

## Time

`GenDate.DaysPerYear = 60`. A RimWorld year is **60 days**, four 15-day
quadrums. Any gate expressed in years must be multiplied by 60, not 365.

Conrad's target era lengths, converted:

| Era | Years | Days | Cumulative day |
|---|---|---|---|
| Neolithic | 1–1.5 | 60–90 | ~90 |
| Medieval | 2–4 | 120–240 | ~330 |
| Industrial | 1–2 | 60–120 | ~450 |
| Spacer | 1–2 | 60–120 | ~570 |

So the whole planned arc through Spacer lands around **day 570**, not day
3000. Day-based gates above ~600 are effectively "never" for this campaign.

---

## Odyssey space layer

| Layer | radius | subdivisions |
|---|---|---|
| Surface (Core) | 100 | 10 |
| Orbit (Odyssey) | 130 | **5** |

Tile count scales ~4^subdivisions, so orbit has orders of magnitude fewer tiles
than the surface. `PlanetLayerDef.Orbit` sets `settlementsPer100kTiles` to
`1000~1000` (one per ~100 tiles), so few tiles also means few settlements,
asteroids and sites. Raised to 6 in `Archinity.Pacing`.

Faction placement on the orbit layer is controlled by `FactionDef.layerWhitelist`
/ `arrivalLayerWhitelist` / `neutralArrivalLayerBlacklist`. Odyssey's own
`TradersGuild` and `Salvagers` are the working templates.

`settlementWorldObjectDef` lives on `PlanetLayerDef`, not `FactionDef`, so all
orbit factions share one base type by default. Better Traders Guild works around
this with a `PatchOperationSequence` on `SpaceSettlement` — same approach
available to us.

---

## Race containment

Neither VRE Starjack nor VRE Archon injects xenotypes into vanilla factions.
Starjack has zero `xenotypeChances` anywhere; Archon ships its own hidden
faction. The only Starjacks on the planet come from Odyssey's own Traders Guild
(25%) and Salvagers (10%) defs, which is vanilla intent.

`Archinity_ArchonianSanguophage` sets `canGenerateAsCombatant: false` and
`factionlessGenerationWeight: 0` so it can never spawn on anyone but the player.
