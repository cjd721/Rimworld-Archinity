# Recon: VFE-Tribals / TechBlock / research-requirements mods

All findings [CONFIRMED IN SOURCE] against decompiled 1.6 assemblies + shipped XML.
Generated 2026-08-22.

## Q2 (the load-bearing one) — gathering-research is PER-PROJECT, not a locked colony mode

**There is no "gathering research mode" flag anywhere.**

Gathering is the only available research path early purely because of two gates:
1. The `Intellectual` work tag is **disabled until `VFET_Culture` is finished** (`unlocksWorkTags`).
2. `SimpleResearchBench` is patched to require `ComplexFurniture`.

Once `VFET_Culture` completes, `Utils.IsUnlocked()` returns true forever and bench
research works normally. Separately, `Precept_Ritual_ShouldShowGizmo_Patch` **hard-hides**
the gathering ritual once `Faction.OfPlayer.def.techLevel > Neolithic`.

**Consequence: the mode turns itself off.** Author later projects as ordinary
`ResearchProjectDef` at Medieval+ and they are bench-only automatically. Conrad's
stated desire — gatherings for the first ~20 projects, then normal bench research
forever — is the mod's *default behaviour*. No work required.

## Q1 — it is a RitualDef, not a research mode

- `PreceptDef VFET_TribalGathering` -> `VFET_TribalGathering_Pattern` -> outcome worker
  `VFETribals.RitualOutcomeEffectWorker_TribalGathering`, which dumps points into
  `Find.ResearchManager.progress[...]`.
- Project def type is **`VFETribals.TribalResearchProjectDef : ResearchProjectDef`**.
  Added fields are only `unlocksWorkTypes`, `unlocksWorkTags`, `unlocksDesignators` —
  nothing about gathering.
- Eligibility is **hardcoded in C#** to `techLevel == Animal(1) || Neolithic(2)`.

## Q3 — cornerstones: the hook already exists, and TechBlock already fires it

- `EraAdvancementDef` (fields `newTechLevel`, `cornerstonePoint`) + `CornerstoneDef`.
- `GameComponent_Tribals.GameComponentTick()` polls `Faction.OfPlayer.def.techLevel`.
  Any *increase from any source* calls `AdvanceTechLevel()` -> `AdvanceToEra()` ->
  `OffsetAvailableCornerstonePoints()`.
- TechBlock writes `Find.CurrentMap.ParentFaction.def.techLevel = val3` on tier-up.

**So TechBlock tier-ups already award VFET cornerstone points automatically.**
Conrad's "keep the cornerstone system throughout the game, triggered by TechBlock
tier-ups" requires **zero C#** — just add `EraAdvancementDef` entries in XML.
Archotech is currently missing an entry.

## Q4 — TechBlock mechanics

- `TB_<Era>TechLock` / `TB_<Era>Theory` research pairs in `TechLocks.xml`.
- `TechBlocker.BlockTechs()` runs at `[StaticConstructorOnStartup]`, iterates **every**
  `ResearchProjectDef` and injects the matching Theory as a prerequisite if none at the
  same techLevel exists. It reads `ResearchProjectDef.techLevel`, **not a curated list**.
- Lock cost = `sum(baseCost of that tier) x requiredPoints`.
- **No Harmony patches at all** — it is def mutation at load + polling.
- Completion detected by polling `Theory.IsFinished` in `RecalculateBlockValues`.
  A *direct* completion hook would need a Harmony postfix on `ResearchManager.FinishProject`
  — [NEEDS C#], and only if the techLevel side-channel is insufficient.

## Q5 — VFET x TechBlock interaction

Both drive `Faction.OfPlayer.def.techLevel`, and each force-completes the other's gate
(VFET `ResearchAllAnimalProjects()`; TechBlock `FinishProject(theory)` when
`def.techLevel > val3`). Mutually-reinforcing ratchet — mostly beneficial.

**Real bug risk:** VFET's `RitualObligationTargetWorker_AnyGatherSpotForAdvancement`
requires that *no* project at the current techLevel be `CanStartNow`. TechBlock's
injected prerequisites make projects not-startable, so **the advancement ritual can
unlock prematurely.**

## Q6 — settings-driven def changes (multiplayer relevant)

**VFE-Tribals has zero mod settings.** TechBlock only:
- `requiredPoints` / `requiredPointsOverride` + six per-era multipliers set every
  `*TechLock.baseCost`.
- `neolithic...archotechBaseCost` set every `*Theory.baseCost`.
- `BlockTechs()` mutates `prerequisites` on **every** ResearchProjectDef.

### MULTIPLAYER RED FLAG — live in our current config
`TechBlock_Component.GameComponentUpdate()` is **frame-based, not tick-based**, and calls
`Rand`-driven `AddRandomProgress()` when `randomInsights` is on.
**Guaranteed desync.** Our snapshot has random-insight rate = 1 (ON). Must be turned off.

Also: `DoSettingsWindowContents` calls `RecalculateBlockValues` live in-game — never
re-click settings, copy the files.

## Mod identity correction

**"More Research Requirements" (MRR) is NOT installed** — not in workshop, not in
`RimWorld\Mods`, not under Archinity. The docs' references to "MRR" actually mean
`sae.ResearchMod` = **"More Realistic Research"** (workshop `3771646847`), a different mod.

Its schema: `ResearchMakesSense.ManualAnalysisDef` with fields `researchProject`,
`experimental` / `reverseEngineering` / `theoreticalMaterials` and matching
`...PointsRequired`. It **auto-generates requirements by techLevel** for any project
not explicitly listed.

## Source locations

| Finding | File |
|---|---|
| `TribalResearchProjectDef` | `workshop\294100\3079786283\1.6\Assemblies\VFETribals.dll` (readable C# at `\1.5\Source\`) |
| Gathering-only gate (`unlocksWorkTags: Intellectual`) | `3079786283\1.6\Defs\ResearchProjectDefs\ResearchProjects.xml` (`VFET_Culture`, ~line 352) |
| Research bench behind `ComplexFurniture` | `3079786283\1.6\Patches\Core.xml` lines 46-70 |
| Ritual defs | `3079786283\1.6\Defs\PreceptDefs\Precepts_Ritual.xml`, `RitualPatterns.xml` |
| Cornerstone / era system | `3079786283\1.6\Defs\EraAdvancementDefs\EraAdvancements.xml`, `Defs\CornerstoneDefs\Cornerstones.xml` |
| TechBlock tier defs + patch | `294100\1970774610\Defs\ResearchProjectDef\TechLocks.xml`, `Patches\TechBlock.xml` |
| TechBlock runtime | `294100\1970774610\1.6\Assemblies\TechBlock 1.2.1.dll` |
| More Realistic Research | `294100\3771646847` |

**Load order note:** `fridgebaron.techblock` currently loads after all VFE mods and before
`archinity.*` — correct. `BlockTechs()` must see final `techLevel` values.

**VFE-Tribals is at workshop `3079786283` but is NOT in `ModsConfig.xml`.** It is
downloaded but not enabled.
