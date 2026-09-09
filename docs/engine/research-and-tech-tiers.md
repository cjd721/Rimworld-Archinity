# Research and tech tiers

How research pacing, tier gating and the tech-gating mod stack (TechBlock,
Ignorance Is Bliss, World Tech Level, More Realistic Research) actually behave.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Quests can be gated on tech tier

The quest machinery itself is in `docs/engine/quests.md`; this is only the tech
gate on it.

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

This is the only tech gate on quests — `QuestScriptDef` has no `minTechLevel`
(see `docs/TRAPS.md` T-16).

## `rootMinProgressScore` is NOT a tech gate

`StorytellerUtility.GetProgressScore` is:

```csharp
return freeColonistCount * 1f + target.PlayerWealthForStoryteller * 0.0001f;
```

Colonists plus wealth/10000. Ignores research entirely. Vanilla gates sit at
3–10, which a wealthy neolithic colony clears in year one. Do not use.
(Also registered as `docs/TRAPS.md` T-16.)

---

## TechBlock

TechBlock is settings-driven, and mod settings are part of the Multiplayer sync
surface — see `docs/TRAPS.md` T-18.

### Two projects per tier

- `TB_<Era>TechLock` — cost = `(tier's total research points × requiredPoints<Era>) − points already researched in that tier`. Shrinks as you research normally.
- `TB_<Era>Theory` — cost = the flat `<era>BaseCost` setting.

So advancing a tier costs a *fraction of the tier's value* plus a flat toll. It
is **not** "complete X% of the tree." Currently set to 0.75 across all tiers.

### The def names are offset one tier from the settings names

Confirmed in `BlockTechs()`: `switch (techLevel - 1)` puts **Medieval** costs
into `indCount`.

| Def | Actually gates | Label |
|---|---|---|
| `TB_NeolithicTechLock` | Animal | costs **1**, since we have no Animal research |
| `TB_MedievalTechLock` | **Neolithic** | "Neolithic Understanding" |
| `TB_IndustrialTechLock` | **Medieval** | "Medieval Understanding" |

`baseCost = SnapToMult(tierTotal x requiredPoints<Era> - alreadyResearched, 100)`.
`TB_MedievalTheory` is 500 baseCost x `CostFactor` 1.5 = **750 effective**.

### It writes the player faction's techLevel, but only on load

`RecalculateBlockValues` sets `Find.CurrentMap.ParentFaction.def.techLevel`. So
Ignorance Is Bliss's `useActualTechLevel` **does** track your tier. It just lags
until the next save-load. There is no `FinishProject` patch, so hand-finished
research does not shrink the lock until reload either.

This is a runtime write to a `FactionDef.techLevel` — related to, but distinct
from, the silent revert-on-load trap in `docs/TRAPS.md` T-11.

> **Unresolved.** Two agents disagreed. One read
> `IgnoranceBase.GetPlayerTech()` returning `Faction.OfPlayer.def.techLevel` and
> concluded the window was frozen at Neolithic for the whole run. The write
> above is the more specific finding and is probably correct, but it has **not
> been observed in game**. `useHighestResearched` sidesteps the question.

### The random-insight mechanic cancels visible progress

While researching a block tech, every 25 points grants 25 (`randomInsightRate 1`)
to a random unfinished same-tier project **and adds 25 back to the block's cost**
(`randomInsightProgressBlock 1`).

> **Net spend = tierTotal x requiredPoints - alreadyFinished.**

Two consequences: roughly 75% of a tier arrives free without being chosen, and
**the lock bar appears frozen**, because cost and progress rise together 1:1.
Setting both values to about 0.5 gives identical total spend with visible
movement. Must be edited in XML; the settings window forcibly re-couples the
sliders.

### Multiplayer determinism

The random-insight draw is also TechBlock's Multiplayer determinism defect; the
worked example lives in `docs/engine/determinism.md`. Note when checking it
yourself: verification must be against `1.6/Assemblies/TechBlock 1.2.1.dll`,
which is what loads. (The folder also ships a `1.0/Assemblies/TechBlock.dll`;
reading that one gives different code and a wrong conclusion. See
`docs/TRAPS.md` T-22.)

---

## Research rate, reconstructed

The documented 213/day reproduces exactly with one unstated assumption:
**46.64% researcher uptime, about 11.2 h/day**.

```
pts/day = N x (0.08 + 0.115*Skill) x benchFactor x 0.00825 x 60000 x 0.4664
```

**213/day is ONE Intellectual-10 researcher, not a colony rate.** Two
multipliers the earlier tables omit: `difficulty.researchSpeedFactor` (Rough
1.0, Hard 0.95, Extreme 0.90) and the bench's own StatParts, which are **x0.75
outdoors** plus a room-cleanliness curve from 0.75 to 1.15.

Both founders have `Neversleep`, about 75% uptime, so **x1.6 per pawn**.

| Int | pts/day | with Neversleep |
|---|---|---|
| 5 | 113 | 182 |
| 10 | 213 | 343 |
| 12 | 253 | 407 |

---

## More Realistic Research

`BuildForProject` returns null for `techLevel <= Neolithic` **and for
Archotech**, which was not previously recorded.

`BuildRegistry` applies hand-authored `ManualAnalysisDef`s *before* the tier
filter, so MRR's three Neolithic entries still apply. **`Devilstrand` demands 9
studies of `DevilstrandCloth`** — circular, since sowing needs the research, and
no Neolithic trader stocks `Fabric`.

---

## Tier totals, measured

`audit_research.py` does not apply PatchOperations, so these are hand-corrected
for `Retier_Medieval.xml` (+2,500 Medieval) and MO's four research baseCost
changes (`LongBlades` 400 to 1,000; `PlateArmor` 600 to 2,000; `Cocoa` 500 to
600; `TreeSowing` a no-op), which are +2,000 Medieval and -1,000 Neolithic.
MO's wider def changes are in `docs/engine/mods/medieval-overhaul.md`.

| Tier | Baseline | plus MO/PF | plus VCE/Stews |
|---|---:|---:|---:|
| Neolithic | 27,500 | 28,600 | 29,100 |
| **Medieval** | **18,000** | **57,900** | **59,350** |
| Industrial | 144,800 | 144,800 | 146,400 |

Medieval by source under full Route A: MO 45 projects / 37,900, Core 12 / 8,800,
VFEM2 7 / 7,400, Royalty 4 / 1,800, VCE 2 / 1,150, others 4 / 2,300.

**VFE Classical contributes ZERO Medieval projects.** All 18 are `techLevel
Neolithic` at 1,200 each, which is 74% of that tier. `docs/archive/VISION.md` says "VFE
Classical and Medieval 2 carry it" about the Medieval era; that is wrong.

**MO adds zero MRR deadlocks**, structurally, since all 45 of its projects are
Medieval and MRR gives Medieval "Experimental only" with no study subject.
**VCE adds three real ones**: `VCE_Canning`, `VCE_DeepFrying` and
`VCE_SoupCooking` each unlock exactly one bench that is `tradeability: None`
with no loot, mapgen or trade route — research needs the bench, the bench needs
the research. The benches themselves are in
`docs/engine/facilities-and-recipes.md`.

---

## World Tech Level

Faction defs and worldgen are in `docs/engine/factions-and-worldgen.md`; this is
WTL's reading of them.

**World Tech Level does not track a per-faction climb.**
`TechLevelUtility.CurrentFilterLevel(FactionDef)` (`:125-136`) returns the
**global** `WorldTechLevel.Current`, never the faction's own `techLevel` — it
reads the def only to test its `defName` against `Settings.FactionsExcluded`,
where an excluded faction returns `Archotech`. The sibling
`TechLevelClamped(FactionDef)` (`:111-117`) *does* read `techLevel`, returning
`min(techLevel, CurrentFilterLevel())`, and is used in five places including
`Patch_BaseGen.cs:36`. It snapshots `techLevel` **twice** at startup —
`DefTechLevels.cs:51` for `FactionDef` and `:45` for `PawnKindDef` — and both
are re-initialised only when the def *count* changes
(`TechLevelDatabase.cs:109-116`).

---

## Ignorance Is Bliss

**Ignorance Is Bliss is fully live** — `IgnoranceBase` reads `f.def.techLevel`
on the live `Faction` inside call-time predicates at `:192, 204, 211, 225, 234,
243, 252, 261, 270` and `:320`, with no snapshot. It holds five static caches
(`:12,14,16,18,20`) and **none of them holds faction tech data**; `techLevel`
appears in exactly one file in the whole assembly.

Its substitutions ride on raid faction selection, which is fail-open and
fail-quiet (`docs/TRAPS.md` T-17), and it is settings-driven, so its settings
are part of the Multiplayer sync surface (`docs/TRAPS.md` T-18).

### Scope

`changeQuests` does **not** stop quests firing. It substitutes the faction in a
quest's threat for a tech-appropriate one ("Will not change the quest
description, but an appropriate faction will arrive").

Division of labour: **IIB controls who shows up, `requiredResearch` controls
when the quest appears.** Both needed; neither replaces the other.

`useActualTechLevel: true` is correct for us — its own tooltip says it is only
appropriate with a mod that drives colony tech level, which TechBlock does.
