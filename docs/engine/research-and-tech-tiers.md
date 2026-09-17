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

## Cost and completion, in the engine

Vanilla, 1.6.4871, and the whole enforcement — and the whole failure mode — of a
tiered arc. Every claim [V].

- **`ResearchManager.FinishProject` recursively completes `prerequisites`** before
  it does anything else, and **never `hiddenPrerequisites`**. One free Spacer
  project therefore completes that project's Theory lock and every Theory lock
  beneath it. A single grant shatters several eras at once; the recursion, not
  the grant, is the ranking criterion for how bad a research bypass is.
- **`ResearchProjectDef.Cost` is `baseCost` only when `baseCost > 0`** — otherwise
  it is `knowledgeCost`. **`CostFactor` is display-only**: four readers, one of
  them `MainTabWindow_Research`. It never moves `Cost` and never moves
  `IsFinished`, so a completion test read off a displayed number is wrong by
  exactly that factor.
- **`ResearchManager.progress` is scribed**
  `Scribe_Collections.Look(ref progress, "progress", LookMode.Def, LookMode.Value)`,
  and **no patch can retract a granted project.** Completion is a saved dictionary
  entry, not derived state. Once a bypass has written it the only cure is to have
  prevented the write — which is why the bypass census is a load-time question
  rather than a runtime one.

## TechBlock

TechBlock is settings-driven, and mod settings are part of the Multiplayer sync
surface — see `docs/TRAPS.md` T-18.

### The era lock is an ordinary `prerequisites` injection

There is no special gating mechanism. `TechBlocker.BlockTechs` walks every
`ResearchProjectDef` and **appends `GetBlock(allDef.techLevel)` to its
`prerequisites`** — creating the list when null, skipping only a project that
already carries a prerequisite at its own `techLevel` [V]. Everything vanilla
does with a prerequisite it therefore also does with the lock, including the
recursive completion in § *Cost and completion, in the engine* above.

**`GetBlock` returns a `TB_<Era>Theory` def** — the six tabulated under *Quests can
be gated on tech tier* above, held internally as `neo`/`med`/`ind`/`spa`/`ult`/`arc`
`Theory` [V]. **The `TB_*TechLock`
defs are never the prerequisite of anything.** They are prerequisites *of* the
Theory defs, and TechBlock only rewrites their cost. Anything gating on the arc
— `requiredResearch` above included — must key on the **Theory** def.

**The injection is indexed `techLevel - 2`, so Animal-tier projects get no lock
at all** [V]. Never write "every project".

### Two projects per tier, and the defNames are era-shifted

- `TB_<Era>TechLock` — `baseCost = SnapToMult(tierTotal × requiredPoints<Era> −
  alreadyResearched, 100)`. Shrinks as you research normally.
- `TB_<Era>Theory` — cost = the flat `<era>BaseCost` setting.

So advancing a tier costs a *fraction of the tier's value* plus a flat toll. It
is **not** "complete X% of the tree." Currently set to 0.75 across all tiers.

**Each `TB_*` defName sits one era above the era it is actually about**, which is
the reading trap. `TB_SpacerTechLock` is labelled *"Industrial Understanding"*
and declares `<techLevel>Industrial</techLevel>` [V]. Confirmed in
`BlockTechs()`, where `switch (techLevel - 1)` puts **Medieval** costs into
`indCount`.

| Def | Era it is about | Label |
|---|---|---|
| `TB_MedievalTechLock` | **Neolithic** | "Neolithic Understanding" |
| `TB_IndustrialTechLock` | **Medieval** | "Medieval Understanding" |
| `TB_SpacerTechLock` | **Industrial** | "Industrial Understanding" |

`TB_MedievalTheory` is `baseCost` 500 with `CostFactor` 1.5, which the research
tab draws as **750**. The 500 is the number that decides completion — see
§ *Cost and completion, in the engine*.

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
(`randomInsightProgressBlock 1`). **The pool is filtered on `CanStartNow`** —
`GetPossibleTechs` is `!IsFinished && !IsHidden && CanStartNow && techLevel ==
<current tier> && !IsBlockTech` [V] — so the draw cannot cross a tier lock and
cannot reach an analysis-gated project.

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

### The scribed field and the volatile mirror are two different things

`WorldTechLevel.GameComponent_TechLevel` holds one field, scribed as
`Scribe_Values.Look<TechLevel>(ref _worldTechLevel, "WorldTechLevel", TechLevel.Archotech)` [V] —
the whole of WTL's saved state. The ~60 filter sites do **not** read it; they read the static
auto-property `WorldTechLevel.WorldTechLevel.Current`, which has no persistence of its own and is
restored from the component by `Patch_WorldGenerator.GenerateFromScribe_Prefix` and
`GenerateWithoutWorldData_Prefix` on every load [V]. **Anything raising the world tech level must
write both.** WTL's own planet-tab button does [V]; Lemmy Progression's
`LemProgress.Systems.WorldEraManager.SetWorldTechLevel` writes only the static and therefore
reverts on the next load [V]. `Current` is an auto-property, so `AccessTools.Field(type, "Current")`
returns null — reach it via `AccessTools.Property` or `<Current>k__BackingField`.

The assembly the game loads is `1.6/Lunar/Components/WorldTechLevel.dll`, **not**
`1.6/Assemblies/`, which holds only `LunarLoader.dll`.

That planet-tab button is not dev-gated and is a route around any era clock — `docs/TRAPS.md`
**T-85**; the window it opens registers factions at runtime — **T-86**. Established on
[#109](https://github.com/cjd721/Rimworld-Archinity/issues/109); the clock built on it is
`docs/specs/ERA.md`.

---

## Ignorance Is Bliss

**Ignorance Is Bliss is fully live** — `IgnoranceBase` reads `f.def.techLevel`
on the live `Faction` inside call-time predicates at `:192, 204, 211, 225, 234,
243, 252, 261, 270` and `:320`, with no snapshot. `techLevel` appears in exactly
one file in the whole assembly.

> **Correction — 2026-09-17, [#128](https://github.com/cjd721/Rimworld-Archinity/issues/128).**
> This section previously read *"it holds five static caches and **none of them holds faction
> tech data**."* That is wrong. `IgnoranceBase` holds a static `cachedTechLevel` carrying the
> resolved **player** tech level, invalidated only by `ResearchManager.FinishProject` and by
> `Settings.WriteAll` — **never on save load**. Loading a second colony in the same session
> runs on the first colony's band until a project finishes, and a client that joined without
> restarting can hold a different band from the host. The original claim is true only of the
> *faction-by-faction* predicates, which are indeed unsnapshotted. [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22)
> owns the fix.

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
appropriate with a mod that drives colony tech level.

> **The driver changed — 2026-09-17, [#128](https://github.com/cjd721/Rimworld-Archinity/issues/128).**
> This line originally justified the setting by *"which TechBlock does"*. TechBlock is decided
> **off** (#7, and [#84](https://github.com/cjd721/Rimworld-Archinity/issues/84) owns the config
> reconciliation), so it drives nothing. The replacement driver is
> [`docs/specs/ERA.md`](../specs/ERA.md) § *Change* — `AdvanceEra()`'s **write 3**,
> `Faction.OfPlayer.def.techLevel = next`, which exists for exactly this reader. The setting
> stays correct; its justification now points at our own code rather than a mod we disabled.

## Research can grant capability, and vanilla carries one third of it

- **`DesignationCategoryDef.researchPrerequisites`** is a vanilla `List<ResearchProjectDef>`; the
  def's `Visible` property returns false while any is unfinished [V]. `MainTabWindow_Architect`
  passes it to `DoCategoryButton` as the button's `enabled` flag and `ClickedCategory` refuses
  when it is false. **The category is not hidden**: `DoWindowContents` iterates every cached panel
  unconditionally and `DoCategoryButton` only greys it, so the observable is a greyed, still
  clickable button that answers a click with
  `Messages.Message("NothingAvailableInCategory".Translate() + ": " + …, RejectInput)` [V].
  `CacheDesPanels` caches the *tab objects*, not their visibility, so the gate is evaluated live
  every frame with no invalidation. `DebugSettings.godMode` short-circuits it true.
- **There is no vanilla field that grants a work type, a work tag, or an individual designator.**
  `WorkTypeDef.visible` is a def field (per-install, not per-save — the **T-11** class) and
  `VisibleCurrently` caches for 30 frames [V].
- **`Verse.ResearchMod` is vanilla's unused extension point.** `ResearchProjectDef.researchMods` is
  a `private List<ResearchMod>` (private is no bar to `DirectXmlToObject`), applied by
  `ResearchProjectDef.ReapplyAllMods()` → `Apply()` inside a try/catch. Vanilla ships the abstract
  class and **zero** subclasses [V]. **Three callers:** `ResearchManager.FinishProject`,
  `ResearchManager.DebugSetAllProjectsFinished`, and **`Verse.Game.FinalizeInit()`**, which calls
  `researchManager.ReapplyAllMods()` two lines above `GameComponentUtility.FinalizeInit()` [V] — so
  a `ResearchMod` is re-applied for every finished project on every load, and must be idempotent.
- **`RimWorld.GameRules`** holds `HashSet<Type> disallowedDesignatorTypes` and
  `HashSet<ThingDef> disallowedBuildings`, is scribed through `Game.ExposeData`'s
  `Scribe_Deep.Look(ref rules, "rules")`, is read live by
  `DesignationCategoryDef.ResolvedAllowedDesignators` via `DesignatorAllowed(d)`, and
  `SetAllowDesignator(Type, bool)` calls `Find.ReverseDesignatorDatabase.Reinit()` [V].
  **Quirk:** `DesignatorAllowed` short-circuits for `Designator_Place`, returning
  `!disallowedBuildings.Contains(PlacingDef)` and never consulting `disallowedDesignatorTypes` —
  build designators cannot be blocked by type. No mod in either corpus root calls
  `SetAllowDesignator`.
- **`Pawn.GetDisabledWorkTypes(bool permanentOnly)`** fills one of two caches through a C# local
  function. A postfix on the local function cannot read `permanentOnly` and therefore cannot avoid
  polluting `cachedDisabledWorkTypesPermanent`; postfix the public method instead [V]. Changing
  whether a work type is disabled without calling `Pawn.Notify_DisabledWorkTypesChanged()` is
  **T-79**.
- **`Game.FillComponents()`** instantiates every non-abstract `GameComponent` subclass absent from
  a loading save via `Activator.CreateInstance(type, this)` [V] — free, silent migration for a
  component added to an existing save, provided it declares a `(Game game)` constructor. It is
  called from `Game.ExposeSmallComponents()` on `LoadingVars`, which `ExposeData` calls [V].

Established on [#72](https://github.com/cjd721/Rimworld-Archinity/issues/72); the system built on it
is `docs/specs/RESEARCH.md` § *Granted capability — the build*. 1.6.4871.

## A `Designator_Build` can be disabled with a reason; vanilla just never does

The other half of the architect-menu story above: the *category* gate is
`DesignationCategoryDef.researchPrerequisites`, and this is the *individual designator*.

`Designator_Build : Designator_Place : Designator : Command : Gizmo`, and `Verse.Gizmo` declares
`protected bool disabled`, `public string disabledReason`, `public virtual bool Disabled` and
`public void Disable(string reason = null)`. `ArchitectCategoryTab.DesignationTabOnGUI` draws the
palette through `GizmoGridDrawer.DrawGizmoGrid`, and `Command.GizmoOnGUI` greys a disabled gizmo,
appends `"DisabledCommand".Translate() + ": " + disabledReason` to its tooltip colourised
`ColorLibrary.RedReadable`, and emits the same string as a `RejectInput` message on click. [V]

**Vanilla's own buildability gate is `Designator_Build.Visible`, which filters the designator out of
the list rather than disabling it** — god mode, `min`/`maxTechLevelToBuild` against the player
`FactionDef`'s static tech level, research, monolith level, difficulty, `PlaceWorker`, building and
discovery prerequisites, grav-engine inspection. So unbuildable content is **invisible**, and the
Architect menu never shows a threshold. [V]

That is a property of `Visible`, not a limit of the surface: a Harmony gate that calls
`Disable(reason)` instead of hiding produces a greyed entry with its requirement legible. Noted
because the opposite was asserted on
[#93](https://github.com/cjd721/Rimworld-Archinity/issues/93) and would have ruled the surface out
entirely. Established on [#93](https://github.com/cjd721/Rimworld-Archinity/issues/93). 1.6.4871.

## Faction-tagged techprint supply closes on hostility and reopens on neutrality

`ResearchProjectDef.heldByFactionCategoryTags` is matched against `faction.def.categoryTag` in
`TechprintUtility.GetResearchProjectsNeedingTechprintsNow` alone, which tests no tech level. In
vanilla + Royalty **13 projects carry the Empire tag** — the tag is declared once on abstract
`BaseBodyPartEmpire_TierA` and inherited by 11 concrete implants, plus `CataphractArmor` and
`JumpPack`; `JumpPack` also carries the Outlander tag, so 12 are Empire-only. [V]

**Hostility with the tagged faction closes the steerable supply.** `FactionUtility.CanTradeWith`
rejects on `faction.HostileTo` **before** the permit check;
`IncidentWorker_TraderCaravanArrival.TryExecuteWorker` returns false while hostile; and
`TraderKindCommonality` is 0 with no permit holder — the Empire's own permits being Knight for
`TradeSettlement` and `TradeCaravan`, Baron for `TradeOrbital`. Quest rewards close the same way:
`Reward_Items.InitFromValue` sets `makingFaction = parms.giverFaction`, and `QuestNode_GetFaction`
rejects a hostile faction unless `allowEnemy` is set, which Royalty's Empire scripts do not. [V]

**Faction-less generators bypass the tag test and are unaffected** — orbital trade ships
(`TradeShip.GenerateThings` builds `ThingSetMakerParams` with no `makingFaction`), the map-gen
setmakers `MapGen_AncientTempleContents` and `MapGen_AncientComplexRoomLoot_Default`, and
asker-less quest rewards. That bypass is **T-99**. Books are never a route in either state:
`ReadingOutcomeDoerGainResearch.IsValid` returns false when `project.TechprintCount == 0` and
`CanStartNow` requires `TechprintRequirementMet`. [V]

**Neutrality reopens it, and vanilla ships two ways back.** The Empire is not `permanentEnemy`, and
its `permanentEnemyToEveryoneExcept` lists `PlayerColony` and `PlayerTribe`, so
`CanChangeGoodwillFor` passes; hostile is ≤ −75 and neutral ≥ 0. Natural drift alone stalls at
natural − 50 (`CheckReachNaturalGoodwill`), but **gifts work** — `CanOfferGiftsTo` *requires*
hostility, and `Settlement_TraderTracker.CanTradeNow` has neither a hostility nor a permit gate
(~40 silver per goodwill point, +25 % amplified) — and **peace talks admit an enemy faction**
(`allowEnemy true`; success +60~70, triumph +100~110). [V]

**Titles survive hostility.** Neither `Notify_RelationKindChanged` nor `Pawn_RoyaltyTracker`
carries any royalty-stripping path for a relation change, so permits and titles persist and the
trade route reopens with the same pawns the moment goodwill is neutral. Applied techprints are not
faction state either: this is supply closure, never confiscation. [V]

Established on [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53). 1.6.4871.
