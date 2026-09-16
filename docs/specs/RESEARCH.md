# Research

## Purpose and scope

> **Authority correction — 2026-09-13.** This document's `requiredAnalyzed` mechanism is
> the campaign's **Exemplar** route: studying a physical likeness unlocks a project and
> the item survives. It does not add research progress, produce Intel or consume the
> item. **Glitterite analysis** is a separate, destructive, long-running activity that
> consumes a one-use artifact, produces Intel and raises Trace. Any section below that
> prices this exemplar gate in Intel or treats the two activities as one is superseded.
> [#115](https://github.com/cjd721/Rimworld-Archinity/issues/115) owns the destructive carrier.

How research is *earned* in this campaign. `CONTEXT.md` settles three routes to knowledge —
**Practice** (resource cost alone), **Instruction** (a techprint, a book, a teacher) and
**Exemplar** (a surviving physical example that the colony studies). Practice is the vanilla
default and needs no spec. Instruction is solved and shipped: techprints are vanilla Royalty, and
`QuestNode_GiveTechprints` with `fixedProject` is pure XML.

This document owns the **Exemplar gate**: what forces a research project to require that the
colony physically studied a named item, and what happens to the item
([#67](https://github.com/cjd721/Rimworld-Archinity/issues/67)). It is the mechanism behind
the Glitterite loop in
[`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md). Destructive Glitterite
analysis is a different activity owned by [#115](https://github.com/cjd721/Rimworld-Archinity/issues/115).

It also owns **research bypasses** — every route in the bin that advances or completes a
research project without the colony spending research points at a bench, and the shutoff for
each ([#83](https://github.com/cjd721/Rimworld-Archinity/issues/83)). That half starts at
[*Bypasses — the build*](#bypasses--the-build); a reader who came for it should jump there
rather than read the Analysis gate first. The two halves meet in one place: a bypass that
ignores `CanStartNow` also ignores `requiredAnalyzed`, and one such route ships in **Core**.

And it owns **granted capability** — what lets a research project unlock a *verb* rather than a
recipe: a work type, a work tag, a designator
([#72](https://github.com/cjd721/Rimworld-Archinity/issues/72)). That third half starts at
[*Granted capability — the build*](#granted-capability--the-build). It is the shape of the
Neolithic on-ramp, and it meets the other two halves at the same seam they do: every one of
them is keyed on `ResearchProjectDef.IsFinished`, so a bypass that finishes a project also
hands over the verbs it grants.

It does **not** own the Intel balance or exchange surface
([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)) — the interface between the two
is stated in *The build* § **The seam with Intel** and nothing more. The Exemplar gate is not
priced in Intel. It does not own the
exemplar **catalogue** — which artifact gates which branch is authoring work and belongs to
[Act V](https://github.com/cjd721/Rimworld-Archinity/issues/47). It does not own research
**pacing**, tier totals or the era ladder
([`docs/engine/research-and-tech-tiers.md`](../engine/research-and-tech-tiers.md); **#5 and #7
are closed and pacing has no owning ticket today**), the research **menu surface**
([#96](https://github.com/cjd721/Rimworld-Archinity/issues/96)), or **the era clock** that the
capstones move ([`ERA.md`](ERA.md)). It does not own **which** verbs the Neolithic gates —
that is the grid's ([#41](https://github.com/cjd721/Rimworld-Archinity/issues/41),
[#37](https://github.com/cjd721/Rimworld-Archinity/issues/37)) — only what makes gating one
possible at all.

---

## The build

**Vanilla already carries the Analysis gate, in pure XML, and we are not writing any code for
it.** `ResearchProjectDef.requiredAnalyzed` plus `CompProperties_CompAnalyzableUnlockResearch`
on the exemplar item is the whole mechanism: the project cannot be started until a colonist
has physically analysed the named thing at a research bench, and with
`destroyedOnAnalyzed: false` the player keeps the trophy afterwards. It is base
`Assembly-CSharp` code, so no DLC assembly is involved, but the field is switched off without
**Biotech** — which is in the floor ([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6)).

**More Realistic Research (`sae.researchmod`) is declined** — a recommendation to
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14), which owns the verdict.
Everything it uniquely contributes is either this vanilla mechanism with extra steps, or the
auto-generation engine that is the sole cause of the recorded deadlocks. Nothing is
reimplemented in `Archinity.Core`.

### 1. The gate — `ResearchProjectDef.requiredAnalyzed`

**Mechanism.** `Verse.ResearchProjectDef` ships `public List<ThingDef> requiredAnalyzed` [V].
`ResearchProjectDef.CanStartNow` conjoins `AnalyzedThingsRequirementsMet` alongside
`PrerequisitesCompleted`, `TechprintRequirementMet`, `PlayerMechanitorRequirementMet`,
`!IsHidden`, `InspectionRequirementsMet` and — **only when `requiredResearchBuilding` is
non-null** — `PlayerHasAnyAppropriateResearchBench` [V]. An earlier draft listed the bench test
as unconditional and omitted `!IsHidden`; the corrected conjunction is
`!IsFinished && PrerequisitesCompleted && TechprintRequirementMet && (requiredResearchBuilding ==
null || PlayerHasAnyAppropriateResearchBench) && PlayerMechanitorRequirementMet &&
AnalyzedThingsRequirementsMet && !IsHidden && InspectionRequirementsMet` [V].
`AnalyzedThingsRequirementsMet` is `AnalyzedThingsCompleted >= RequiredAnalyzedThingCount`,
and `AnalyzedThingsCompleted` walks `requiredAnalyzed`, reads each entry's
`CompProperties_CompAnalyzableUnlockResearch.analysisID`, and counts the ones whose
`AnalysisDetails.Satisfied` is true [V].

**There is no tech-level filter anywhere on this path** — not in `PostLoad`, not in
`ConfigErrors`, not in `CanStartNow` [V]. Analysis is available at every tier, Neolithic and
Archotech included. Vanilla demonstrates this itself rather than merely permitting it: the
Ultra-flavoured `NanostructuringChip` gates the **Industrial**-tier `WastepackAtomizer` [V].
See *Available mechanisms* for why that sentence is load-bearing.

**Enforcement is at project selection, not at the bench.** `WorkGiver_Researcher.HasJobOnThing`
never consults `CanStartNow`; `MainTabWindow_Research` does, refusing to start the project and
naming the reason [V]. That is the right place: a colonist is never sent to a bench to do
nothing. It is enforcement against the *player choosing the project*, not against every route
that can advance a project — see *Failure and recovery* § **`AddProgress` does not consult the
gate**.

**Loud on authoring error.** `ResearchProjectDef.ConfigErrors` emits
*"requires analyzing X but X cannot be analyzed"* when a `requiredAnalyzed` entry lacks an
assignable `CompAnalyzable` [V]. This gate is not on the silent list — **in a load order that
has Biotech**. Without Biotech that error can never fire, because `PostLoad` has already nulled
the list before `ConfigErrors` runs [V]; see **T-40**.

### 2. The exemplar — `CompProperties_CompAnalyzableUnlockResearch`

**Mechanism.** One comp on the item's `ThingDef`, all XML. Fields that matter to us [V]:

| Field | Our value | What it does |
|---|---|---|
| `analysisID` | a large unique int | the key into `AnalysisManager`. See **T-41** below |
| `destroyedOnAnalyzed` | `false` | **the trophy survives**. `OnAnalyzed` destroys the parent only when true |
| `analysisRequiredRange` | `n~n` (min == max) | how many analyses satisfy the gate. Equal bounds take `Rand.RangeInclusive`'s early return and draw **no** random number [V] |
| `analysisDurationHours` | authoring dial | wait is `ceil(ceil(hours × 2500) / pawn ResearchSpeed)` ticks [V] |
| `canStudyInPlace` | `false` | forces the work to a research bench via `StudyUtility.TryFindResearchBench` [V] |
| `requiresMechanitor` | `false` | Biotech's own chips set this true; third-party use sets it false [V] |
| `showProgress`, `allowRepeatAnalysis` | `true`, `false` | progress letters; one-way latch |
| `completedLetterLabel` / `completedLetter` | authored | `{RESEARCH}` resolves to the projects this unlocks, via `CompAnalyzableUnlockResearch.ExtraNamedArg` [V] |
| `completedLetterDef` | **mandatory whenever the two above are set** | `CompProperties_Analyzable.ConfigErrors` requires it; omitting it is a config error, not a default [V] |
| `progressedLetterLabel` / `progressedLetters` / `progressedLetterDef` | **mandatory whenever `analysisRequiredRange` exceeds 1** | see *Failure and recovery* — an unauthored `progressedLetters` throws on the **first** analysis [V] |

**The act itself.** `CompAnalyzable` derives from `CompInteractable`, which is an
`ITargetingSource`. The player gets an **"Analyze…" gizmo** on the selected item and a
right-click float-menu option on a colonist; both funnel through
`CompAnalyzable.OrderForceTarget`, which issues `JobDefOf.AnalyzeItem`.
`JobDriver_AnalyzeItem.GetStudyToils` is one `Toils_General.Wait` with a progress bar and
`activeSkill = Intellectual`, then `Toils_General.DoAtomic(OnAnalyzed)` [V].

**No `WorkGiver` exists for it.** Analysis never happens on its own — it is always a player
order naming a specific colonist. For a campaign beat that is the behaviour we want, and it is
stated here so nobody later files a bug against it.

### 3. Where the state lives — `Game.analysisManager`

`RimWorld.AnalysisManager` holds `Dictionary<int, AnalysisDetails>`; `AnalysisDetails` is
`{ int id; int required; int timesDone; bool Satisfied => timesDone >= required; }` [V]. Keyed
by `analysisID`, **not** by item, def or map — the record is colony-global and one-way.

The entry is created by `CompAnalyzable.PostSpawnSetup`, whose condition is
`!respawningAfterLoad && !Find.AnalysisManager.HasAnalysisWithID(AnalysisID)`, via
`AnalysisManager.AddAnalysisTask(AnalysisID, Props.analysisRequiredRange.RandomInRange)` [V].
**Both halves matter.** The first is the one hazard in the design (see *Failure and recovery*).
The second is what freezes `required` at the value drawn by the *first* exemplar ever to spawn:
a later spawn of the same def finds the id present and adds nothing, so re-authoring
`analysisRequiredRange` on a live save changes nothing.

### 4. What changes it

- `CompAnalyzable.OnAnalyzed` → `AnalysisManager.TryIncrementAnalysisProgress(id, out details)`,
  then a progress or completion letter [V].
- `ResearchManager.FinishProject` walks the project's `requiredAnalyzed` and calls
  `AnalysisManager.ForceCompleteAnalysisProgress(analysisID)` for each [V]. So a project granted
  by quest reward, dev mode or a campaign script never strands the player behind an analysis they
  no longer need.

Nothing else in vanilla or in the corpus writes it — see *Available mechanisms* § *The wide pass*.

### 5. Where the player sees it

All vanilla, all free [V]:

| Surface | What it shows |
|---|---|
| `MainTabWindow_Research.DrawStudyRequirements` | a **"Study requirements"** block on the detail pane listing each required item |
| project node | a `StudyRequirementTex` (`UI/Icons/Study`) badge and an `analyzed / required` counter, beside the techprint counter |
| prerequisite text | coloured by `AnalyzedThingsRequirementsMet` — fulfilled vs missing |
| locked reasons | `"NotStudied".Translate(item.LabelCap)` per unsatisfied entry |
| `ResearchProjectDef.GetTip` | appends `"StudyRequirementTip"` + the item list to the cached description |
| the item | its own `inspectString`, the "Analyze…" gizmo, and a disabled float-menu entry carrying the refusal reason |
| on success | a letter naming the colonist and the projects unlocked |

**There is no display half left to build, and no UI ticket to defer to.**

### 6. The seam with Intel ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54))

> **Corrected seam.** Research never calls `CanAfford` or `TrySpend` on Intel. Accumulated
> Intel is exchanged elsewhere for a techprint or other unlocking item; the resulting
> item then uses the ordinary Instruction path. The exemplar gate remains independent.

What this gate needs to know about a recovered exemplar, stated as a contract so #54 can build
against it:

1. **The gate's entire input is a `ThingDef` on a colony map.** It cannot read a balance and
   does not need to.
2. **Intel exchange and studying an exemplar are different acts.** Studying spends
   nothing and leaves the item intact. It flips one colony-global boolean per
   `analysisID`, permanently. Intel is an accumulated scalar exchanged elsewhere for
   an Instruction item; do not model one on the other.
3. **The clean split.** The exemplar answers *may this branch be researched at all* —
   binary, per branch, irreversible. Intel answers *which instruction can the colony
   obtain now*. One `requiredAnalyzed` entry may sit at a branch root; a techprint or
   authored unlock item may gate a different node. Destructive analysis belongs to
   [#115](https://github.com/cjd721/Rimworld-Archinity/issues/115), not this manager.
4. **What #54 may rely on.** `Find.AnalysisManager.TryGetAnalysisProgress(id, out details)` and
   `details.Satisfied` are public, scribed and multiplayer-safe, callable from any C# #54 writes.
   That is the supported "this branch is unlocked" read, and it costs nothing.
5. **What #54 must not do.** Do not store Intel in `AnalysisManager`. Its dictionary is keyed by
   a hand-chosen int with no uniqueness check (**T-41**), and `required` is frozen at first
   spawn. It is a latch, not a ledger.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| Add the analyzable comp to each exemplar ThingDef | `PatchOperationAdd` (`USH_Glitterheart` has no `<comps>` node, so the operation adds one) | ~25 lines per exemplar, including the mandatory `completedLetterDef` and — at `required > 1` — the three `progressedLetter*` fields | `Archinity.Glitterites/Patches/Analysis_Exemplars.xml` |
| Add `requiredAnalyzed` to each branch-root project | `PatchOperationAdd` | ~6 lines per project | `Archinity.Glitterites/Patches/Analysis_GlittertechGate.xml` |
| Retire `Analysis_Glittertech.xml`, `Analysis_Unblock.xml`, `Fix_MoreRealisticResearch.xml` | deletion | −3 files, ~250 lines | `Archinity.Glitterites`, `Archinity.Pacing` |
| Recommend dropping `sae.researchmod` | sourcing input | — | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) owns the verdict |
| **New C#** | **none — conditional on Analysis staying unpriced (the Analysis-pricing question in [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2))** | **0 under the default.** If Analysis is ever priced, the completion path needs a `TrySpend` call and the gizmo needs a `CanAfford` disable reason — a Harmony postfix on `CompAnalyzable.OnAnalyzed` and one on `CompInteractable.CanInteract`, neither of which exists today | — |

---

## Bypasses — the build

**One XML lockout file and one corpus-wide audit script. No C#, no Harmony, nothing in
`Archinity.Core`.** The era arc is not defended by writing code; it is defended by deleting the
player's access to seventeen specific things, in the pattern
[`Archinity.Pacing/Patches/Lockout_AlphaMechs.xml`](../../Archinity.Pacing/Patches/Lockout_AlphaMechs.xml)
already establishes — keep the def, remove the route to it.

### 0. The test that sorts the bin

**The era arc is enforced by `ResearchProjectDef.prerequisites`.** TechBlock's
`TechBlocker.BlockTechs` walks every `ResearchProjectDef` at def-load and appends
`GetBlock(allDef.techLevel)` to `prerequisites` **wherever that lookup yields a def** — creating
the list if it is null, and skipping projects that already carry a prerequisite at their own
`techLevel` [V,
`1970774610/1.6/Assemblies/TechBlock 1.2.1.dll`]. **The def it appends is `TB_<Era>Theory`**, not
`TB_<Era>TechLock`: `GetBlock` returns one of `neoTheory` / `medTheory` / `indTheory` /
`spaTheory` / `ultTheory` / `arcTheory` [V]. The injected Theory def is therefore an ordinary
prerequisite, and the whole ladder reduces to one predicate.

**Two precisions, because an earlier draft of this section named the wrong def and overstated the
reach.**

- **The `TB_*TechLock` defs are never a prerequisite of anything.** They are prerequisites *of*
  the `TB_*Theory` defs, and TechBlock only rewrites their cost [V]. Their naming is also
  era-shifted and must not be read as a tier label: `TB_SpacerTechLock` carries
  `<label>Industrial Understanding</label>` and `<techLevel>Industrial</techLevel>` [V]. Cite the
  Theory def whenever you mean the lock a project actually carries.
- **Not "every project" receives one.** `GetBlock` indexes at **`techLevel - 2`**, so `Undefined`
  and **`Animal`** fall off the bottom of the table and get no injected prerequisite at all [V].
  The ladder starts at Neolithic; an Animal-tier project is outside it by construction, which is
  why VFE Tribals' Animal-tier catch-up (below) is not an era breach.

**So a bypass breaks the era arc if and only if it can advance a project whose
`PrerequisitesCompleted` is false.** Everything else is a pacing question, not an era question.
That single test does more work than a mod-by-mod survey, and it is why the shutoff list below is
seventeen entries long rather than three.

Two vanilla facts make it sharp, and both are load-bearing [V, decompiled 1.6
`Assembly-CSharp`]:

- **`ResearchManager.FinishProject` recursively finishes every unfinished prerequisite** before
  doing anything else. One free Spacer project therefore completes the Spacer `TB_*Theory` def
  and every Theory def beneath it, free, in one call. **This is the mechanism by which a single
  grant shatters several eras**, and it is why the `FinishProject` callers below rank above the
  `AddProgress` ones. **The recursion walks `prerequisites` only — it never touches
  `hiddenPrerequisites`** [V], so hidden prerequisites survive a cascade that completes every
  visible one.
- **`ResearchProjectDef.IsFinished` is `ProgressReal >= Cost`, and `Cost` is `baseCost` only when
  `baseCost > 0`** — otherwise it returns `knowledgeCost` [V], which is the anomaly-knowledge
  path. `CostFactor` is not one of `Cost`'s inputs at all: it has four readers — `CostApparent`,
  `ProgressApparent`, the divisor inside `ResearchPerformed`, and a fourth, **display-only** read
  in `MainTabWindow_Research` [V]. A mod that writes `progress[proj] = proj.baseCost` by
  reflection has finished the project outright, prerequisites unread, and `ReapplyAllMods` then
  applies its unlocks. No `FinishProject` call is needed and none happens.

### 1. Mechanism — one lockout file

`Archinity.Pacing/Patches/Lockout_ResearchBypasses.xml`, one `PatchOperationFindMod` block per
mod so every clause is inert when its mod is not in the final set, and the vanilla clauses
unguarded. Ordered the way `Lockout_AlphaMechs.xml` is ordered — neuter the referencing def
first, delete last — for the same reason: an unresolved cross-reference is **omitted**, not
nulled.

**Class A — advances a project whose prerequisites are unmet. These break the arc.**

| Carrier | Anchor | Shutoff |
|---|---|---|
| **VPE `VPE_ReverseEngineer`** | `VanillaPsycastsExpanded.Technomancer.Ability_ReverseEngineer.Cast` | `PatchOperationRemove` the `VEF.Abilities.AbilityDef` `VPE_ReverseEngineer` **and** its `AbilityExtension_Psycast` slot on the `VPE_Technomancer` path. Coordinate with [#33](https://github.com/cjd721/Rimworld-Archinity/issues/33), which owns the surviving path set |
| **Mechanoids: Total Warfare, on vanilla `CerebrexCore`** | `NCL.CompUnlockResearch.UnlockResearch` | `PatchOperationRemove` `/Defs/ThingDef[defName="CerebrexCore"]/comps/li[@Class="NCL.CompProperties_UnlockResearch"]`. **Archinity.Pacing must load after MTW** or the node is not there to remove |
| **VFE Classical senator favours** | `VFEC.Senators.WorldComponent_Senators.GainFavorOf` | `PatchOperationReplace` the `senatorResearch` entries and `finalResearch` with projects already inside the era. **Do not remove them** — `FactionExtension_SenatorInfo.ConfigErrors` requires `senatorResearch.Count == numSenators` and a non-null `finalResearch` and `finalPerk` [V] |
| **VFE Classical `Profectus` perk** | `VFEC.Perks.Workers.Profectus.DoResearch` | `PatchOperationReplace` `finalPerk` with any other `PerkDef`. It is Class B on the era test (below); it is listed here because the disposition lands in the same file |
| **VFE Tribals one-shot catch-up** | `VFETribals.GameComponent_Tribals.ResearchAllAnimalProjects` | none needed — it completes only the mod's own `TribalResearchProjectDef`s at techLevel Animal [V] |
| **RimPacts tech-steal** | `RimPacts.WorldComponent_RimPacts.ResolveSpyOpSuccess` | **no def to remove** — the grant lives in a `WorldComponent` reached from the mod's spy system, throttled only by a **30-day per-faction cooldown** [V], which bounds the rate and not the tier. If RimPacts ships, the spy op has to go or the mod does; the verdict is [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s |
| **Vanilla `Schematic` book** | `ReadingOutcomeDoerGainResearch.OnReadingTick` | § *The `Schematic` book* below — one XML line |

**Class B — picks only from a `CanStartNow` pool. Cannot cross a tier lock; accelerates inside
one.** Left alone unless pacing wants them gone, and none of them is an era-arc question:
`VFEC.Perks.Workers.Profectus.CanResearch` [V], `TechBlock_Component.GetPossibleTechs` [V],
`VFEInsectoids.HordeModeManager.CompleteWave` [V, gated on storyteller `VFEI_HanHordeMode`],
`VFETribals.RitualOutcomeEffectWorker_TribalGathering.Apply` [V, Animal/Neolithic only].

**Class C — produces research points into the player-selected project from a non-bench source.**
A rate breach, not a gate breach: the project had to pass `CanStartNow` to be selected. These
belong to pacing, and **pacing currently has no owning ticket** — #5 and #7, the two this survey
was written to hand them to, are both closed and nothing has replaced them. The gap is stated
here and left to be routed; the top two rows are large enough that whoever picks pacing up needs
to see them.

| Def | Anchor | Rate |
|---|---|---|
| `MAG_AutoResearcher`, `ArchoDecipherAI` | `MoreArchotechGarbage.CompSpawnerResearchMK2.AddResearchPoints1` | 5,000–15,000 points per 30k–90k ticks, per building, stacking [V] |
| a Vanilla Quests Expanded – Ancients gene | `VEF.AnimalBehaviours.HediffComp_PassiveResearch.CompPostTickInterval` — the comp ships in VEF with **no VEF def using it**; the only corpus consumer is VQE-Ancients, at 50 points / 6000 ticks [V] | **500/day** per carrier |
| `USH_ResearchProbe` | `USH_GE.CompPassiveRes.ConductResearch` | ≈180/day [V]. **Keep** — it is the Glittertech tree's own facility and this document already leans on it |
| `Outpost_Science` | `VOE.Outpost_Science.Tick` | one garrison's research speed, in-game hours 9–15 [V] |
| `Joy_ModernComputer` | `VanillaFurnitureEC.JobDriver_ExtendedSitFacingBuilding.ModifyPlayToil` | 10 points per completed joy session [V] |
| `USH_Cyberdata`, `USH_AdvancedCyberdata`, `USH_BrokenExecData` | `USH_HE.JobDriver_ApplyResearchGiver.MakeNewToils` | 15 / 100 / 150 points per item consumed [V] |
| vanilla `TechprofSubpersonaCore` | `CompUseEffect_FinishRandomResearchProject.DoEffect` | finishes the **current** project instantly [V]. `tradeability Sellable` and `thingSetMakerTags: RewardStandardCore`, so acquisition is quest rewards and loot. Strip `thingSetMakerTags` — exactly `Lockout_AlphaMechs.xml` § 3 |

**Class D — currency substitution, not a bypass.** Vanilla Gravship Expanded reroutes **11**
projects (4 Odyssey + 7 of its own) into a gravdata track:
`VanillaGravshipExpanded.MainTabWindow_Research_DoBeginResearch_Patch.Prefix` swallows the click
and `GravshipResearchUtility.ResearchPerformed` feeds them from `JobDriver_CollectGravdata`
instead [V]. It is **not** a free-research route — `MainTabWindow_Research.DrawStartButton` gates
the button on `CanStartNow` before `DoBeginResearch` is ever reached [V], and
`SetGravshipResearch` re-checks `PrerequisitesCompleted` [V]. It does force
`PlayerHasAnyAppropriateResearchBench` true and `CostFactor` to 1 for those 11 [V]. Leave it; see
*Bypasses — available mechanisms* § *The census* for why the ticket's framing of it is withdrawn.

### 2. The `Schematic` book

The one shutoff the Analysis gate itself depends on, and the only one in **Core**.

`ReadingOutcomeDoerGainResearch.OnBookGenerated` picks one project — two with 25 % chance — from
projects that are `PrerequisitesCompleted && !IsFinished && TechprintCount == 0 &&
generalRules != null` and sit in an allowed `ResearchTabDef`; vanilla's `Schematic` allows `Main`
and excludes the three gravtech and four mechtech projects by name [V].

**Two paths through that picker drop the `PrerequisitesCompleted` test entirely** [V]: the
`Props.include` path, which takes an authored list as given, and the fallback taken when the
filtered list comes back empty. Either can name a project whose prerequisites — and so whose
injected TechBlock Theory def — are unpaid. **The `usesHiddenProjects` remedy below is unaffected
by both**: its xpath resolves to exactly one node, and the gate it restores applies at
`OnReadingTick`, which is where the progress actually lands.

`OnReadingTick` then
calls `AddProgress` for each at 0.008–0.032 points per tick by book quality — **20–80 points per
hour of reading** [V, `BookUtility.QualityResearchExpTick`]. Nothing on that path consults
`CanStartNow`. `IsProjectVisible` does, but **only when `Props.usesHiddenProjects` is true, and
it defaults false** [V].

**The fix is one line:**

```xml
<Operation Class="PatchOperationAdd">
  <xpath>/Defs/ThingDef[defName="Schematic"]/comps/li[@Class="CompProperties_Book"]/doers/li[@Class="BookOutcomeProperties_GainResearch"]</xpath>
  <value><usesHiddenProjects>true</usesHiddenProjects></value>
</Operation>
```

That routes `IsProjectVisible` through `CanStartNow`, restoring the techprint, mechanitor, bench,
hidden **and `requiredAnalyzed`** gates on the book's grant, while leaving books tradeable and
useful. The display half is free: `GetBenefitsString` already prints a greyed
*"(when discovered)"* for a project the reader cannot currently advance [V]. Removing the doer
outright is the alternative and is worse — it deletes the item's entire purpose.

**Five mods widen the pool by adding their own tabs to the same doer** — Medieval Overhaul,
Vanilla Cooking Expanded, VFE Tribals, Vanilla Vehicles Expanded, and VEF, whose
`VEF.Research.ResearchProjectUtility.AutoAssignRules` adds the `VanillaExpanded` tab to vanilla
`Schematic` at startup [V]. The one-line fix covers all five, because it changes the *test*, not
the pool.

### 3. State, persistence and change

**We own no state.** Every bypass writes vanilla `ResearchManager.progress` / `techprints`, which
this document does not touch. The lockout is def-load-time `PatchOperation`s: no runtime hook, no
`GameComponent`, nothing to scribe.

**The one persistence consequence is a hard ordering constraint.** `ResearchManager.progress`
persists across loads and no `PatchOperation` can retract a project already granted. **The
lockout must be in before world creation** ([#18](https://github.com/cjd721/Rimworld-Archinity/issues/18),
**T-07**); applied to a live save it stops future grants and leaves past ones standing.

**Multiplayer:** nothing here is a sync surface of ours. Three carriers are worth noting rather
than acting on — RimPacts' spy resolution and TechBlock's random-insight draw both consume `Rand`
off paths this repo has already flagged (`docs/engine/determinism.md`), and
`Ability_ReverseEngineer.Cast` opens a `Dialog_NodeTree` directly, which is client-local UI
raised from a synced cast.

### 4. Where the player sees it

Nowhere, deliberately — a removed reward pool, a missing comp and a psycast that is not on the
path are all invisible, which is correct for a lockout and is exactly why § 5 exists instead. Two
exceptions are vanilla and free: the `Schematic` benefits string greys out projects the reader
cannot advance [V], and `TechprofSubpersonaCore` keeps its `CompProperties_Usable` gizmo and its
own *"no active research project to finish"* refusal [V].

### 5. The standing check — `tools/audit_bypasses.py`

This class of breach reappears whenever the mod set moves, and the re-run must not be another
active-set tool. `defdb.py`, `patch_check.py`, `audit_research.py` and `inventory.py` all narrow
to `config/ModsConfig.xml` before they start, and a bypass sitting in an inactive mod is exactly
the false negative that costs months.

Build it on `tools/corpus.py` instead — both roots, `Data/` included, `-g '!**/obj/**'` — with
two passes and a committed baseline, the idiom `tools/audit_research_baseline.txt` already
establishes:

1. **Assemblies.** ASCII `.dll` sweep for `FinishProject`, `AddProgress`, `ResearchPerformed`,
   `ApplyTechprint`, `ApplyKnowledge`; attributed with `corpus.py --which`.
2. **XML-only carriers**, which pass 1 cannot see because they ride vanilla code:
   `CompUseEffect_FinishRandomResearchProject`, `BookOutcomeProperties_GainResearch`,
   `ScenPart_StartingResearch`.

Diff against `tools/audit_bypasses_baseline.txt`; a new row is a new carrier to classify by the
§ 0 test. ~120 lines of Python.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| The per-mod shutoffs, each inside a `PatchOperationFindMod` | XML patch | ~130 lines | `Archinity.Pacing/Patches/Lockout_ResearchBypasses.xml` |
| The `Schematic` one-liner | XML patch, unguarded (Core) | 4 lines | same file |
| Corpus-wide bypass audit plus its baseline | Python | ~120 lines and a generated baseline | `tools/audit_bypasses.py`, `tools/audit_bypasses_baseline.txt` |
| **New C#** | **none** | **0** | — |

**[I] on the composition.** Every mechanism above was read [V]; the claim that these operations
leave the era arc intact is inferred until the lockout is written and `patch_check.py` confirms
every xpath matches.

---

## Granted capability — the build

**Keep the mechanism, drop the mod: one `DefModExtension`, six Harmony patches and one cache
invalidation, all reading vanilla's already-scribed `ResearchProjectDef.IsFinished`. We own no
new saved state.** Roughly **250–300 lines** of C# in the assembly we already ship, plus XML per
gated verb — see *Cost*, which shows the donor's measured line counts and why an earlier
estimate of ~155 was too low. And **before any of that — where a whole architect category can be
gated, vanilla already does it in pure XML** (§ 1), which is free and should be preferred
wherever it fits.

The named carrier, **VFE Tribals**, does carry it. `VFETribals.TribalResearchProjectDef :
ResearchProjectDef` declares exactly the three fields the ticket names —
`public List<WorkTypeDef> unlocksWorkTypes`, `public WorkTags unlocksWorkTags`,
`public List<Type> unlocksDesignators` [V,
`…/294100/3079786283/1.6/Assemblies/VFETribals.dll`]. **The ticket's premise is confirmed**, which
is worth saying out loud because premises in this repo have not always survived
([`docs/agents/capability-research.md`](../agents/capability-research.md) § *Inherited claims*).

But [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) ruled the mod out on **T-15**
(`VFET_OpportunitySite_WildMen` registers a faction at runtime against the frozen roster), and
`docs/data/PARTS-BIN.md` § 5.3 independently files it **RESTAT leaning REBUILD** on a hard
co-op desync and a twelve-building retier collision. **So we take the shape and write the code.**
The whole of it fits in this document because — read end to end — the mod's mechanism turns out
to be **stateless**: it holds nothing, scribes nothing and asks nothing of the save.

### 0. The shape, read out of the donor

Seven of VFE Tribals' pre-Neolithic projects carry a grant, and this is the entire authored
surface [V, `…/1.6/Defs/ResearchProjectDefs/ResearchProjects.xml`]:

| Project | `techLevel` | work types | work tags | designators |
|---|---|---|---|---|
| `VFET_Fire` | Animal | `Firefighter` | `Firefighting` | — |
| `VFET_Agriculture` | Animal | `Growing` | — | `Designator_ZoneAdd_Growing` |
| `VFET_AnimalHandling` | Animal | `Handling` | — | `Designator_Tame`, `Designator_Slaughter` |
| `VFET_Mining` | Animal | `Mining` | — | `Designator_Mine`, `Designator_SmoothSurface` |
| `VFET_Hunting` | Animal | `Hunting` | — | `Designator_Hunt` |
| `VFET_Construction` | Animal | — | — | `Designator_AreaBuildRoof`, `Designator_RemoveFloor`, `Designator_RemoveFoundation` |
| `VFET_Culture` | Animal | — | `Intellectual` | — |

Five grants of work types, two of work tags, five of designators — **twelve rows of XML** is
what "the entire Neolithic on-ramp" amounts to as data. Note the tier: all seven are
`techLevel Animal`, which falls **below** TechBlock's injected era ladder — `GetBlock` indexes at
`techLevel - 2`, so `Undefined` and `Animal` receive no injected prerequisite [V, *Bypasses —
the build* § 0]. An on-ramp authored at `Animal` is outside the era arc by construction, which is
why VFE Tribals' own Animal-tier catch-up is not a breach and why ours would not be either.

### 1. Take the free half first — `DesignationCategoryDef.researchPrerequisites`

**Vanilla already gates an entire architect category on research, in pure XML, and nobody in the
repo has written it down.** `Verse.DesignationCategoryDef` ships
`public List<ResearchProjectDef> researchPrerequisites`, and its `Visible` property returns false
while any of them is unfinished [V]. `MainTabWindow_Architect` passes `panel.Visible` to
`DoCategoryButton` as the button's `enabled` flag and refuses `ClickedCategory` outright when it
is false [V].

Two properties make it better than anything we would write:

- **It is evaluated live, every frame.** `CacheDesPanels` caches the *tab objects*, not their
  visibility [V]. So a category becomes reachable the instant the project finishes, with **no
  invalidation of any kind** — which answers the ticket's "does a mid-game designator appearing
  need a UI invalidation" with *not for this route*.
- **`DebugSettings.godMode` short-circuits it to true** [V], so dev mode is not locked out of
  its own content.

**Know what the player actually sees, because it is not a hidden tab.** `DoWindowContents`
iterates **every** `desPanelsCached` entry unconditionally and `DoCategoryRow` passes
`panel.Visible` to `DoCategoryButton` as its `enabled` flag [V]. When that flag is false,
`DoCategoryButton` sets `labelColor` and `GUI.color` to `InactiveColor` and **still calls
`Widgets.ButtonTextSubtle`** — so the button is drawn, greyed, and remains clickable; clicking
routes to `ClickedCategory`, whose first statement is
`if (!Pan.Visible) { Messages.Message("NothingAvailableInCategory".Translate() + ": " +
Pan.def.LabelCap, MessageTypeDefOf.RejectInput, historical: false); return; }` [V]. **The
observable is greyed, clickable, and refused with a message — not absent.** That is arguably
better for an on-ramp (the player can see what is coming), but it is a different thing from
hiding, and a check written against "the tab is absent" will fail.

Use it wherever the unit being gated is a whole category. It does not reach an individual
designator inside a category, and it does not touch work types — which is what § 2 is for.

### 2. Mechanism — `ResearchGrantExtension`, and six patches

**A `DefModExtension` on the vanilla `ResearchProjectDef`, not a subclass.** VFE Tribals
subclasses, which forces every gated project to be authored as `<VFETribals.TribalResearchProjectDef>`
and makes it impossible to gate a def somebody else already shipped. A `DefModExtension` is
`PatchOperationAdd`-able onto **any** existing project [V, the mechanism `docs/engine/` already
relies on throughout], which is what a campaign patching vanilla and mod research needs.

```
public class ResearchGrantExtension : DefModExtension
{
    public List<WorkTypeDef> unlocksWorkTypes;
    public WorkTags          unlocksWorkTags;
    public List<Type>        unlocksDesignators;
}
```

with three lookup indexes — `WorkTypeDef → projects`, `WorkTags → projects`, `Type → project` —
because the enforcement patches run per pawn and per gizmo draw and cannot afford a `DefDatabase`
scan. **`VFETribals.Utils` builds its three in two different ways, which is worth copying
deliberately rather than by halves** [V]: `researchProjectsWithDesignators` is a static field
initialiser on a `[StaticConstructorOnStartup]` class, so it is built **eagerly at startup**,
while `cachedResearchProjectsForWorkTypes` and `cachedResearchProjectsForWorkTags` are
`Dictionary` caches filled **lazily on first use** inside `GetCachedResearchProjectsFor`. Eager
is right for the designator index (it is iterated by every gizmo draw); lazy is right for the two
keyed dictionaries (they are sparse). Build ours the same way, and note that a lazy index must be
cleared if defs are ever reloaded mid-session.

**The six patches, each read off the donor and each verified against the vanilla member it
targets:**

| # | Target | Kind | What it does |
|---|---|---|---|
| 1 | `Pawn.GetDisabledWorkTypes`'s local `FillList` | postfix | appends every locked `WorkTypeDef` for player-faction pawns |
| 2 | `Pawn.CombinedDisabledWorkTags` | postfix | ORs in every locked `WorkTags` flag for player-faction pawns |
| 3 | `Pawn.GetReasonsForDisabledWorkType` | postfix | the *"requires research: X"* line on the work tab |
| 4 | `CharacterCardUtility.GetWorkTypeDisabledCausedBy` | postfix | the same line on the character card |
| 5 | `Designator.GizmoOnGUI` | postfix | `Gizmo.Disable(reason)` on a locked designator — **and re-enables it when the reason matches ours, so we never strand a gizmo another mod disabled** |
| 6 | `DesignationManager.AddDesignation` | prefix | hard refusal plus a `Messages.Message`, so no other route can place the designation |

Patch 1 is the one with a wrinkle. `Pawn.GetDisabledWorkTypes(bool permanentOnly = false)` fills
`cachedDisabledWorkTypes` **or** `cachedDisabledWorkTypesPermanent` through a **C# local
function** `FillList`, not a named method [V, `Verse.Pawn.GetDisabledWorkTypes`]. VFE Tribals
reaches it by scanning `AccessTools.GetDeclaredMethods(typeof(Pawn))` for a name containing both
`GetDisabledWorkTypes` and `FillList` [V]. **Target `GetDisabledWorkTypes` itself instead**,
postfixed on `__result`. Two reasons, and neither is the one an earlier draft gave:

1. **A public method is a stable anchor; a compiler-generated name is not.** The donor's search
   survives a recompile of the same source but not a refactor, and it is unciteable — there is no
   `Type.Method` to write down.
2. **Only the public postfix can read `permanentOnly`, and that is a correctness bug in the
   donor, not a preference.** `GetDisabledWorkTypes(true)` fills the *permanent* cache — the one
   that answers "is this pawn incapable of X for good", read by backstory and trait UI. A
   `FillList` postfix receives only the `List<WorkTypeDef>` and **cannot tell which cache it is
   filling**, so VFE Tribals adds research-gated work types to `cachedDisabledWorkTypesPermanent`
   as well [V — `DisableWorkTypes` takes only `(Pawn, List<WorkTypeDef>)` and adds
   unconditionally]. A work type you have not researched yet is not a *permanent* incapability.
   The public postfix gets `permanentOnly` as a parameter and can skip the permanent call.

The one thing to get right is that the returned list **is the cache**, so a postfix must add to
it idempotently (`Contains` first) or it grows on every non-cached rebuild.

> **The Loudness argument an earlier draft made for this choice was wrong and is withdrawn.** It
> claimed a missing local function gives Harmony a silent null target while a missing public
> method throws. **Both are loud.** `PatchClassProcessor.GetBulkMethods()` invokes
> `[HarmonyTargetMethod]` through `RunMethod` with a `failOnResult` delegate
> `method => method != null ? null : "null"`; a non-null result throws
> `"Method … returned an unexpected result: null"`, which `ReportException` rethrows as
> `HarmonyException` [V, `0Harmony.dll` **2.4.1.0**, `…/294100/2009463077/Current/Assemblies/`].
> The recommendation is unchanged; the two reasons above are what actually support it.

Patches 5 and 6 are why **no designator cache has to be rebuilt**. VFE Tribals never removes a
designator from its category; it lets the category resolve normally and **disables the gizmo in
place**, every frame [V]. `DesignationCategoryDef.resolvedDesignators` is built once at
`ResolveReferences` under `LongEventHandler.ExecuteWhenFinished` [V] and is not rebuildable at
runtime without re-resolving the def — so *not touching it* is the design, not an omission. The
donor also patches `Designator.CreateReverseDesignationGizmo`, `Designator.DesignateThing` (over
a computed set of subclasses) and `PawnColumnWorker_Designator.SetValue` [V]; patch 6 covers all
three routes at the one chokepoint they share, `DesignationManager.AddDesignation`, and the
extra three are belt-and-braces that can be added if a hole shows up in play.

### 3. State — **none of ours**, and that is the load-bearing part

**The capability is derived, not stored.** "Is this verb unlocked" is
`extension.project.IsFinished`, and that is `ResearchManager.progress`, which vanilla already
scribes, already synchronises, and already migrates. This document adds **zero** saved fields,
**zero** `Scribe` calls and **zero** migration.

This is deliberately the opposite answer to [`ERA.md`](ERA.md) § 1, and the two come from one
rule: **scribe only what nothing else scribes; derive everything else.** The era clock owes a
store because nothing in the game records when an era began. Granted capability owes none,
because `ResearchManager` already holds the only fact it needs. Building a `GameComponent` here
would be a second store for a number vanilla keeps, and it would drift the first time anything
finished a project by a route we did not write — which, per *Bypasses — the build*, is seventeen
routes.

**VFE Tribals does store something, and it is worth saying why we do not copy it.**
`GameComponent_Tribals` scribes `HashSet<ResearchProjectDef> finishedResearchProjects`, kept in
step by a `ResearchManager.FinishProject` postfix and self-pruned on every read
(`finishedResearchProjects.RemoveWhere(x => !x.IsFinished)`) [V]. It exists to make
*"was this newly finished"* answerable inside that postfix, for the mod's ideology letter and
its storyteller's back-to-back-research raid — not for the unlock check, which reads `IsFinished`
directly [V, `VFETribals.Utils.IsUnlocked`]. We need neither consumer, so we need neither field.

### 4. Persistence, change, and what a legacy save sees

- **Persistence: nothing to persist.** Adding this to an existing save changes what the work tab
  and the architect menu report on the next frame and writes nothing. There is no migration and
  no version gate.
- **Change: one postfix on `ResearchManager.FinishProject`**, and it exists for exactly one
  reason — **`Pawn` caches its disabled work types and nothing else will invalidate that cache
  when a project finishes.** `Pawn.Notify_DisabledWorkTypesChanged()` is **the only invalidation
  call**: it nulls `cachedDisabledWorkTypes` and `cachedDisabledWorkTypesPermanent`, clears
  `cachedReasonsForDisabledWorkTypes`, and calls `workSettings?.Notify_DisabledWorkTypesChanged()`
  and `skills?.Notify_SkillDisablesChanged()` [V, `Verse.Pawn`]. (The caches are *also* dropped
  inside `GetDisabledWorkTypes` itself whenever `Scribe.mode != Inactive` [V] — that is a
  save/load guard, not an invalidation anything can trigger, which is exactly why the symptom
  below disappears after a reload and never before one.) Without the call, **a research
  project finishes and no colonist can do the new work until something else happens to
  invalidate the cache** — no error, no message. VFE Tribals makes exactly this call, over
  `PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive`, and only when the finished
  project actually grants a work type or tag [V]. Copy it verbatim, including the guard.
  > **This is a silent failure.** The full proposed `docs/TRAPS.md` entry is written out verbatim
  > in the resolution on [#72](https://github.com/cjd721/Rimworld-Archinity/issues/72); the
  > orchestrator applies it, since this session may not edit the register.
- **Designators need no invalidation** (§ 2), and work *tags* need none beyond the same call,
  because `Pawn.CombinedDisabledWorkTags` is computed fresh on every read [V].

### 5. Where the player sees it

| Surface | What it shows | Cost |
|---|---|---|
| research tab, project detail | the granted verb listed among *Unlocks*, with its icon | one transpiler or postfix on `ResearchProjectDef.UnlockedDefs`, ~35 lines |
| work tab cell | greyed, with *"requires research: fire"* on hover | patch 3, free once written |
| character card | the same reason under the disabled work tag | patch 4 |
| the designator | drawn, greyed, with the reason in its tooltip | patch 5 |
| an attempt anyway | a `Messages.Message` naming the project | patch 6 |
| a gated architect category | the category button **greyed and still clickable**; clicking it produces *"nothing available in category: X"* as a `RejectInput` message | vanilla, free (§ 1) |

The research-tab half needs the same trick the donor uses, and it is worth knowing before
someone tries something cleverer. `ResearchProjectDef.UnlockedDefs` builds
`cachedUnlockedDefs` from six `DefDatabase` queries over recipes, things, plants, terrain,
surgeries and psychic rituals [V] — it is a list of `Def`, and a `WorkTypeDef` is a `Def` but a
`Designator` is a `Type`. VFE Tribals therefore synthesises a `FakeDef` carrying the designator's
`LabelCap`, `Desc` and icon, appends it, and patches `Widgets.DefIcon` to render it [V]. That is
three small classes, and it is the only way to get a designator into a list typed as `Def`.
Work types need no fake — append the `WorkTypeDef` itself.

### 6. Multiplayer

**Nothing here is a sync surface of ours, and the one hook rides a path Multiplayer already
covers.**

- `ResearchManager.FinishProject` is reached from `JobDriver_Research`'s toil on the synced tick,
  and Multiplayer registers `MainTabWindow_Research.DoBeginResearch` and
  `ResearchManager.StopProject` as sync methods [V, *Persistence and multiplayer* below]. Both
  clients run the postfix on the same tick with the same result.
- The enforcement patches are **pure reads** — `IsFinished` against a static index — inside UI
  draw and cache-fill paths. They write no simulation state and draw no random number.
- `Notify_DisabledWorkTypesChanged()` mutates only client-local caches; running it on both
  clients from the same synced tick is the deterministic case, and running it on one would
  desync nothing because the caches are derived.
- **The donor's own defect is not inherited.** PARTS-BIN § 5.3 records that
  `GameComponent_Tribals.AddCornerstone` mutates saved state from `DoWindowContents` with no
  `[SyncMethod]` [V]. That is the cornerstone system, not the unlock system, and § 3 does not
  copy it — but it is the reason a *restat* of VFE Tribals would have to be audited window by
  window while a rebuild does not.

### 7. The cornerstone system — drop it

The ticket asks. **Recommend dropping it**, and the recommendation is narrow: the mechanism is a
stat-offset shop (`CornerstoneDef` → `StatWorker_GetValueUnfinalized` / `GetExplanationUnfinalized`
postfixes, spent from `availableCornerstonePoints`, 88 authored defs) [V], it is the one piece of
the mod carrying the unsynced-write defect, and the campaign already owns a register for
permanent colony-wide boons — **the altar** ([`ALTAR.md`](ALTAR.md)), which #7 § 7 makes the
home of era advancement anyway. Two registers doing one job is the thing `CODING_STANDARDS.md` §
*The bar for a change* rejects.

**The missing Archotech `EraAdvancementDef` entry does not matter**, and for a sharper reason
than "Archotech is never researched": `EraAdvancementDef` is looked up by
`FirstOrDefault(x => x.newTechLevel == newTechLevel)` and a null result is simply skipped [V,
`GameComponent_Tribals.AdvanceTechLevel`] — the absence is inert, not a hole. It is moot for us
regardless, since `AdvanceEra()` ([`ERA.md`](ERA.md) § 3) does not read `EraAdvancementDef` at
all. The verdict on the mod remains
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s; this document recommends
**REBUILD**, agreeing with PARTS-BIN § 5.3.

### Cost

| Piece | Kind | Donor, measured | Ours | Lands in |
|---|---|---|---|---|
| `ResearchGrantExtension` + the three indexes (§ 2) | C# | ~45 | **~45** | the assembly we already ship |
| Patches 1–4 — work types, work tags, both reason strings | C# | **119** | **~70** | same |
| Patches 5–6 — designator gizmo disable and the `AddDesignation` refusal | C# | **69** | **~55** | same |
| `FinishProject` postfix — the `Notify_DisabledWorkTypesChanged` sweep | C# | ~12 | **~12** | same |
| `UnlockedDefs` display + `FakeDef` + `Widgets.DefIcon` postfix | C# | **240** | **~70** | same |
| Per gated project: the extension block | XML `PatchOperationAdd` | — | ~6 lines each | `Archinity.Pacing/Patches/` |
| Per gated architect category: `researchPrerequisites` | XML `PatchOperationAdd`, **no code** | — | ~5 lines each | same |

**~250–300 lines of C# in the assembly we already ship, and ~6 lines of XML per verb. No new
assembly, no new saved state, no recompiled third-party DLL.**

**An earlier draft of this section said ~155, and the correction is worth keeping visible.** The
*Donor, measured* column is VFE Tribals' decompiled line count for the equivalent piece. Our
column discounts decompiler verbosity (`//IL_` comments, explicit interface casts) and takes a
postfix where the donor uses a transpiler — but four of the five rows still land above the first
estimate, and the display stack lands far above it. **The same sentence this document applies to
the ticket's ~30-line guess — low by roughly 5× — applies to ~155 at roughly 1.7×.** Estimating
a rebuild without counting the thing being rebuilt is how both numbers went wrong.

**[I] on the composition.** Every mechanism above was read [V]; the claim that they compose into
a working on-ramp is inferred until it is built and a colonist is watched failing to mine.

---

## Persistence and multiplayer

**Persistence.** `Game.ExposeData` does `Scribe_Deep.Look(ref analysisManager, "analysisManager")`
followed by a `LoadingVars` null-guard that reconstructs an empty manager [V].
`AnalysisManager.ExposeData` is `Scribe_Collections.Look(ref analysisDetails, "analysisDetails",
LookMode.Value, LookMode.Deep)` with a null-guard of its own — a **`PostLoadInit`** guard, not
the `LoadingVars` one `Game.ExposeData` uses; they are two different guards at two different
scribe stages, and describing them as one is imprecise [V]. Every RimWorld 1.5+ save already
carries the node, so adding our defs to an existing save loads cleanly — with the one caveat in
*Failure and recovery*.

**Multiplayer — safe, and already covered without a line from us.** Multiplayer registers
`OrderForceTarget` as a `SyncMethod` for **every `ITargetingSource` implementor in
`Assembly-CSharp`**, excluding only `CompInteractableRocketswarmLauncher` and `CompNociosphere`
[V]. `CompAnalyzable` declares its own `OrderForceTarget` override, so both the gizmo route and
the float-menu route are synced. `ResearchManager.StopProject` and
`MainTabWindow_Research.DoBeginResearch` are registered too [V].

**Determinism.** The only `Rand` draw on the whole path is
`Props.analysisRequiredRange.RandomInRange` in `PostSpawnSetup`.
`Rand.RangeInclusive(min, max)` returns `min` unchanged when `max <= min` [V], so authoring
`n~n` removes the draw entirely rather than merely making it deterministic. **Every exemplar
comp we author must use equal bounds**; this is a rule, not a preference. Nothing else in
`CompInteractable`, `CompAnalyzable`, `JobDriver_AnalyzeItem` or `AnalysisManager` touches
`Rand` [V].

---

## Failure and recovery

**An exemplar already on the map when its def gains the comp can never satisfy the gate, and
fails silently — with no feedback at all.** `AnalysisManager.AddAnalysisTask` is called only
from `CompAnalyzable.PostSpawnSetup`, and only when `!respawningAfterLoad` [V]. On a save where
the item predates our patch, no `AnalysisDetails` entry is ever created; `AnalyzedThingsCompleted`
then cannot count it, and `OnAnalyzed` takes the `IsAnalysisComplete` branch — which returns
**true** for an absent key [V].

The symptom is quieter than an earlier draft of this spec claimed. That branch routes to
`SendLetter(Props.repeatCompletedLetterLabel, …)`, and `SendLetter` no-ops on an empty label —
which Biotech's chips have, and which any exemplar we author will have unless we go out of our
way [V]. So there is no "already analysed" letter and no error: the **"Analyze…" gizmo stays
live, the colonist walks over, the job runs to completion, and nothing happens**. The player can
repeat it indefinitely while the project stays locked. A wrong-but-visible letter would have been
kinder.

Not a live risk for this campaign: the world is created once, after the freeze
([#18](https://github.com/cjd721/Rimworld-Archinity/issues/18)), with the defs already in.
Recovery if it ever bites: spawn a fresh exemplar, or dev-mode
`AnalysisManager.ForceCompleteAnalysisProgress`. It was offered for the trap register and not
taken — the freeze rules out the situation — so it is documented here and nowhere else.

**`analysisRequiredRange` above 1 with no authored progress letters throws on the *first*
analysis.** `CompAnalyzable.SendAppropriateProgressLetter` indexes
`Props.progressedLetters[timesDone - 1]`, falling back to `Props.progressedLetters.Last()` [V].
Both are exceptions on an empty list. Biotech's three chips are all `1~1` and author no progress
letters, so the completion path is the only one vanilla ever walks and the bug has never shipped
a repro. **Our *Outstanding decisions* explicitly floats `2~2` for a campaign-central exemplar**,
which walks straight into it. **Rule: any exemplar we author with `analysisRequiredRange` above
`1~1` must author `progressedLetterLabel`, `progressedLetters` and `progressedLetterDef`, and
`progressedLetters` must hold at least `required - 1` entries.** Loud when it fires, so not a
trap — but the spec invites it, so the spec states the guard.

**Duplicate `analysisID` silently merges two gates — T-41.** The dictionary is keyed by a
hand-picked int with no uniqueness check and no `ConfigErrors` coverage. Medieval Overhaul ships
two live collisions today. Our own IDs must be drawn from a reserved block and recorded here when
authored.

**`requiredAnalyzed` is nulled without Biotech — T-40.** `ResearchProjectDef.PostLoad` does
`if (!ModLister.BiotechInstalled) requiredAnalyzed = null;` [V] — no error, no warning, the gate
simply ceases to exist and the project becomes free. Two precisions worth stating exactly:

- **`ModLister.BiotechInstalled` tests *owned and present on disk*, not *active*.** It reads
  `modsByPackageId.ContainsKey("ludeon.rimworld.biotech")`, set in
  `ModLister.RecacheExpansionsInstalled` [V], from a `modsByPackageId` that
  `ModLister.RebuildModList` fills via `TryAddMod` across every mod on disk. Deactivating
  Biotech in `ModsConfig.xml` does **not**
  null the field; only not owning the DLC does. This repo's rule is that the active mod set is
  an output of the last playtest and not a design input, so the distinction is the useful one:
  the floor dependency is on the *purchase*, and a player who owns Biotech but has it switched
  off still gets a working gate.
- **`ConfigErrors`' "requires analyzing X but X cannot be analyzed" can never fire in the
  no-Biotech state**, and it is unreachable twice over [V]. `PostLoad` fires at
  deserialisation, from `DirectXmlToObject.TryDoPostLoad`, and has already emptied the list
  long before `ErrorCheckAllDefs` runs inside `PlayDataLoader` — and `ErrorCheckAllDefs` runs
  **only under `Prefs.DevMode`**. So the loud-on-authoring-error property §1 leans on is not
  merely Biotech-conditional, it is dev-mode-conditional: a player without dev mode gets no
  authoring diagnostics at all, and the Royalty/techprint ConfigError at the same site is dead
  for the same reason. Author with dev mode on, or the check is not there.

Biotech is in the floor ([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6)), so this is
a floor dependency to record rather than a bug to fix.

**`AddProgress` does not consult the gate — and the mod this spec accused of exploiting that
does not.** `ResearchManager.AddProgress` checks `PrerequisitesCompleted` before auto-finishing
and never checks `CanStartNow` [V], so the §1 claim that "enforcement is at project selection"
is a claim about the *player's* route, not about every route. **An earlier draft named
TechBlock's random-insight mechanic as the route that takes the other one. That is wrong and is
withdrawn.** `TechBlock_Component.GetPossibleTechs` builds its candidate pool from
`!IsFinished && !IsHidden && CanStartNow && techLevel == <current tier> && !IsBlockTech` [V,
`1970774610/1.6/Assemblies/TechBlock 1.2.1.dll`], and `CanStartNow` carries
`AnalyzedThingsRequirementsMet` [V]. **TechBlock cannot touch an analysis-gated project**, the
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) "keep the Glittertech roots out of
its tier pool" caveat is retired, and the *Outstanding decisions* row that carried it is struck.

**Two routes in the bin genuinely do it, and one of them is vanilla.** `Find.ResearchManager`
`.AddProgress` is reached with no `CanStartNow` test by `ReadingOutcomeDoerGainResearch`
`.OnReadingTick` — the **`Schematic`** book, `Core/Defs/Books/BookDefs.xml` — and by RimPacts'
tech-steal spy operation. The book's project pool excludes techprint projects but **not**
`requiredAnalyzed` ones [V]. So a schematic bought from a trader can carry a Glittertech branch
root to full progress behind the exemplar gate. The shutoff is one XML line and is specified at
[*Bypasses — the build*](#bypasses--the-build) § *The `Schematic` book*.

**`ResearchManager.FinishProject` dereferences the comp props without a null check** when
force-completing analysis [V]. A `requiredAnalyzed` entry carrying some *other* `CompAnalyzable`
subclass passes `ConfigErrors` and then throws on any force-finish. Loud, so not a trap — but
every entry we author must use `CompProperties_CompAnalyzableUnlockResearch` specifically.

**Campaign softlock check.** The gate is only as safe as the exemplar's obtainability.
`tools/check_availability.py` scores a candidate material on six independent acquisition routes
and is the standing guard here; its docstring is framed around More Realistic Research and needs
repointing at `requiredAnalyzed`, but its logic is mechanism-agnostic and survives this verdict
intact.

---

## Status

**Evidence class: READ.** Settled by vanilla defs and the decompiled 1.6 `Assembly-CSharp`, the
decompiled `ModResearchRimworld.dll`, and `Multiplayer.dll`. No stub and no launch needed.

**Verified available mechanism; selection and the MRR verdict sit with
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14).** `requiredAnalyzed` +
`CompProperties_CompAnalyzableUnlockResearch` is verified [V] end to end — gate, state,
persistence, change, display, multiplayer. This document recommends it as the carrier and
recommends declining `sae.ResearchMod`; neither is a decision this document is entitled to make.
`docs/data/MOD-VERDICTS.md` currently files `sae.ResearchMod` under *Cheap* and
`docs/data/PARTS-BIN.md` §5.4 files it as REBUILD; both are the orchestrator's to move, and
*Declined* is Conrad's with no justification owed. The claim that our particular composition of
the vanilla mechanism delivers the Glitterite loop is **[I]** until something is built and played.

- [#67](https://github.com/cjd721/Rimworld-Archinity/issues/67) — this gate (absorbed the
  exemplar half of [#55](https://github.com/cjd721/Rimworld-Archinity/issues/55)).
- [#6](https://github.com/cjd721/Rimworld-Archinity/issues/6) — the DLC floor Biotech sits in.
- [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) — owns the `sae.researchmod`
  verdict and the TechBlock question.
- [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) — the Intel side of the seam.
  **Resolved: Analysis is never priced in Intel.** Research and hacking never debit it; Intel is
  exchanged for Instruction items ([`CURRENCIES.md`](CURRENCIES.md) § *The Intel exchange*). The
  cost line above is unconditional.
- [#53](https://github.com/cjd721/Rimworld-Archinity/issues/53) / [`RELIGION.md`](RELIGION.md) —
  Instruction *supply* for Empire-tagged techprints. The Church keeps `categoryTag Empire`, so its
  trader route stays open only while the Church is non-hostile and a colonist holds Knight (Baron
  for its orbital trader). Orbital trade ships generate stock with no faction and bypass
  `heldByFactionCategoryTags` altogether (**T-99**).

**Open parameters, not mechanisms:** how many analyses per exemplar, the duration, which branch
roots carry a gate and which artifact gates which branch. Named in *Outstanding decisions*.

### Bypasses ([#83](https://github.com/cjd721/Rimworld-Archinity/issues/83))

**Evidence class: READ.** Settled by decompiled 1.6 assemblies — `Assembly-CSharp`, `VFEC.dll`,
`VanillaPsycastsExpanded.dll`, `VanillaGravshipExpanded.dll`, `TechBlock 1.2.1.dll`, `NCLvsTW.dll`,
`VEF.dll`, `VFETribals.dll`, `VFEInsectoids.dll`, `RimPacts.dll`, `HackingExpansion.dll`,
`GlittertechExpansion.dll`, `VanillaFurnitureEC.dll`, and the More Archotech Garbage and Vanilla
Outposts assemblies — plus vanilla and mod XML. No stub and no launch.

**Verified survey; the disposition is [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s.**
Every carrier in *Bypasses — available mechanisms* § *The census* is [V], and each row implies a
per-mod verdict — *restat*, *art only*, *block* — which this document does not make. Two rows
carry a recommendation and nothing more: `USH_ResearchProbe` should be **kept** and restatted
because the Glittertech tree needs it, and the vanilla `Schematic` one-liner should be **taken**
because the Analysis gate in the first half of this document is otherwise open.

**Three of the ticket's own claims are corrected** in *Bypasses — available mechanisms* § *Three
claims on the ticket that the assemblies contradict*, and two of this document's own claims about
`Profectus` and TechBlock are withdrawn in place.

- [#83](https://github.com/cjd721/Rimworld-Archinity/issues/83) — this survey and the lockout.
- [#33](https://github.com/cjd721/Rimworld-Archinity/issues/33) — owns the surviving VPE path set;
  `VPE_ReverseEngineer` sits inside it.
- [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) — owns every per-mod verdict, and
  the revalidation cadence § 5's audit script serves.
- **The Class C rate question has no owner.** #5 and #7, the pacing tickets this survey was
  written against, are both closed and nothing has replaced them. Recorded as a gap, not handed
  off.
- [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) — the freeze the lockout must
  precede.

### Granted capability ([#72](https://github.com/cjd721/Rimworld-Archinity/issues/72))

**Evidence class: READ.** Settled against the 1.6 `Assembly-CSharp.dll` (`Verse.Pawn`,
`Verse.WorkTypeDef`, `Verse.DesignationCategoryDef`, `RimWorld.GameRules`,
`RimWorld.ResearchManager`, `Verse.ResearchProjectDef`, `RimWorld.MainTabWindow_Architect`),
`VFETribals.dll` 1.6 read end to end, `VEF.dll` 1.6, and both corpus roots for the wide pass. No
stub and no launch.

**Verified available mechanism; the carrier is ours to write.** The ticket's premise is
confirmed — `TribalResearchProjectDef.unlocksWorkTypes` / `unlocksWorkTags` /
`unlocksDesignators` exist and work [V] — and the mod stays ruled out on **T-15**
([#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)). Recommendation to
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14): **REBUILD**, agreeing with
`docs/data/PARTS-BIN.md` § 5.3, and **drop the cornerstone system** rather than restat it.

**Newly found and free:** `DesignationCategoryDef.researchPrerequisites` gates a whole architect
category on research in pure vanilla XML, evaluated live with no cache to rebuild [V]. It
appears in no repo document today.

**Selected: nothing.** The composition is **[I]** until it is built.

- [#72](https://github.com/cjd721/Rimworld-Archinity/issues/72) — this build and its survey.
- [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) — the T-15 ruling that puts VFE
  Tribals out, re-checked and upheld.
- [#41](https://github.com/cjd721/Rimworld-Archinity/issues/41),
  [#37](https://github.com/cjd721/Rimworld-Archinity/issues/37) — which verbs the Neolithic
  gates, and in what order. **Not settled here**, deliberately.
- [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) — the per-mod verdict.
- [`ERA.md`](ERA.md) — the clock these capstones move, and the opposite answer to the same
  state-ownership question.

---

## Available mechanisms

### Vanilla — the carrier

Biotech's mechanitor tree is the shipped working reference, read from
`Data/Biotech/Defs/ResearchProjectDefs/ResearchProjects_Mechanitor.xml` [V]:

| Project | `techLevel` | `requiredAnalyzed` |
|---|---|---|
| `BasicMechtech` | Industrial | **none** — the tree's entry project carries no analysis gate at all |
| `StandardMechtech` | Industrial | `SignalChip` |
| `HighMechtech` | Industrial | `PowerfocusChip` |
| `UltraMechtech` | **Ultra** | `NanostructuringChip` |
| `WastepackAtomizer` | **Industrial** | `NanostructuringChip` |

All five inherit `MechtechBase`, which sets `techLevel Industrial` and `requiresMechanitor true`;
`UltraMechtech` overrides the tier and `WastepackAtomizer` restates Industrial explicitly [V].
All three chips set `destroyedOnAnalyzed: false` — **vanilla's own design keeps the trophy** [V].
`requiresMechanitor: true` is a Biotech-flavour choice, not a requirement of the mechanism.

Two things in that table are load-bearing beyond the "it ships and it works" point.

**`WastepackAtomizer` is vanilla's own counter-example to a tech-tier filter.** It is an
**Industrial** project gated on `NanostructuringChip` — the same artifact that gates the Ultra
`UltraMechtech`, and an item whose whole flavour is above-Spacer. One chip gates two projects at
two different tiers, and the low-tier one is not special-cased. §1's "no tech-level filter
anywhere on this path" therefore rests on a shipped positive as well as on a negative code read,
which is the stronger footing for the *Outstanding decisions* row that wants Analysis at
Neolithic and Medieval.

**One chip can gate several projects, and a tree's entry project need not be gated.** The shape
Biotech chose — free entry, gate the branches — is exactly the shape §6's "one `requiredAnalyzed`
entry at each branch root" reaches for.

**Four third-party mods already author it in XML**, which proves it is moddable outside Biotech's
own content and outside the mechanitor fiction [V]:

| Mod | What it does |
|---|---|
| Medieval Overhaul `dankpyon.medieval.overhaul` | 16 `DankPyon_Schematic_*` items, `requiresMechanitor: false`, `destroyedOnAnalyzed: **true**`, patched onto 16 research projects — 14 of its own plus vanilla `LongBlades` and `Greatbow` |
| Alpha Mechs `sarg.alphamechs` | further chip-style items |
| Mechanoids: Total Warfare `nyar.nclvstw` | ditto |
| GravTech `als.gravtech` | ditto |

Medieval Overhaul is the useful one: it is the *opposite* choice on consumption, and the tell is
what it destroys. MO burns a **schematic** — a piece of paper. Biotech keeps a **chip** — an
artifact. Destroy documents; keep objects. Our exemplars are objects.

Two cautions that belong to Medieval Overhaul rather than to us, recorded because they touch
this mechanism and are easy to conflate with it. Its whole schematic block sits inside a
`MedievalOverhaul.PatchOperation_ToggleSettings` on the `biotechSchematic` setting — a mod
setting read inside a `PatchOperation`, which is **T-18**'s worst shape: mismatched settings
give the two clients different `ThingDef`s and different `ResearchProjectDef`s [V]. And the
**T-20** mitigation on `MOD-VERDICTS.md` — *strip the `RequiredSchematic` extension from the 14
projects* — does **not** remove the `requiredAnalyzed` gates, which are a separate patch
covering 16 projects [V]. That is fine, because the vanilla gate is the multiplayer-safe half;
it is written down so nobody assumes one removal did both jobs.

### `Profectus` cannot see this gate, and that is an argument for it

VFE Classical's **`Profectus`** (Eastern Republic capstone) completes a **random research
project** every `(5 + n) × 60000` ticks, forever, **excluding techprint, analysis, mechanitor and
anomaly projects** ([`docs/data/PARTS-BIN.md`](../data/PARTS-BIN.md) § 5.5) [V]. It filters on
the def's own fields, and `requiredAnalyzed` is one of the fields it filters on:
`VFEC.Perks.Workers.Profectus.CanResearch` rejects any project with `TechprintCount > 0`,
`RequiredAnalyzedThingCount > 0`, `requiresMechanitor`, or a non-null `knowledgeCategory` [V].

**Correction to an earlier draft of this section, which said *"it never consults
`CanStartNow`"*. It does** — `CanResearch`'s last statement is `return proj.CanStartNow;` [V],
read from `2787850474/1.6/Assemblies/VFEC.dll`. The conclusion above survives, and is now
belt-and-braces: an analysis-gated project is excluded by the explicit
`RequiredAnalyzedThingCount` test *and* by `CanStartNow`'s own
`AnalyzedThingsRequirementsMet`. But the withdrawn sentence mattered for a different reason —
it is what made `Profectus` look like an era-arc breach, and it is not one. See
[*Bypasses — the build*](#bypasses--the-build) § *The census*.

**That is the strongest in-repo argument for the vanilla carrier over More Realistic Research,
and it was not part of the original comparison.** A `requiredAnalyzed` gate is *structurally
invisible* to `Profectus` — the project is skipped. An MRR gate is not: MRR's requirements live
in `GameComponent_ResearchLegs.ProjectPoints`, not on the `ResearchProjectDef`, so a
`Profectus` draw sees an ordinary ungated project and hands it over free. Under MRR, the
Glittertech tree is one Eastern Republic capstone away from being given away; under
`requiredAnalyzed` it is not. VFE Classical is a BLOCK for Multiplayer reasons of its own
(§ 5.5), so this is a robustness argument rather than a live dependency — but it is the kind of
robustness a hand-rolled parallel system cannot buy.

The mirror image of this is in *Failure and recovery*: `ResearchManager.AddProgress` has no such
filter, and TechBlock calls it at random.

### Is recovery consumption? No.

`docs/requirements/GLITTERTECH.md` says *"Want their armor? Bring home armor."* It says bring
home, not burn. The exemplar is the proof you went; taking it apart and putting it back together
is what a researcher does, and destroying it converts a trophy into a receipt. The colony flies
to orbit for a glitterheart and Ushanka already charges hearts to *build* glittertech — charging
one again to *research* it is paying twice for one trip. `destroyedOnAnalyzed: false` [V].

### The nearest facility gate — Ushanka, corrected

`requiredResearchFacilities` is the adjacent lever: a building you must have standing.
Ushanka's Glittertech Expansion uses it, and the claim carried on #67 needed correcting —
**the probe gates 14 of 18 projects, not the tree** [V].
`3522676478/1.6/Defs/ResearchProjects/ResearchProjects.xml` holds one `ResearchTabDef` and 20
`ResearchProjectDef`s, of which **2 are abstract** — **18 concrete projects** [V], the same count
our own `Analysis_Glittertech.xml` header already carries. `USE_GE_ProjectBase`, which all 18
inherit, requires `HiTechResearchBench` plus facility `MultiAnalyzer`. Only
`USE_GE_ProbeProjectBase` — 14 children — adds `USH_ResearchProbe`, and by **T-05**
list-append it carries `MultiAnalyzer` as well. The probe is itself unlocked by
`USH_GlittertechUtilitiesRes`, a project inside the same tree.

The two levers are orthogonal and compose: `requiredResearchFacilities` is *a machine you keep
standing*; `requiredAnalyzed` is *an object you took apart once*. Only the second is a gate on
having gone somewhere.

### More Realistic Research `sae.researchmod` — read in full, declined

`3771646847`, one 32 KB assembly, `ResearchMakesSense` namespace, **twelve Harmony patches across
eleven patch classes** (`Patch_WorkGiver_Researcher` carries two). It implements a parallel
analysis system on top of `CompStudiable`, with three types: `reverseEngineering` (damages the
subject), `experimental` (consumes one item per point) and `theoretical` (pure delay). Points are
stored per project in `GameComponent_ResearchLegs.ProjectPoints` and scribed [V].
`Patch_WorkGiver_Researcher` postfixes `WorkGiver_Researcher.HasJobOnThing` to `false` and
prefixes `JobDriver_Research.MakeNewToils` with a fail condition, so unmet requirements stop
research at the bench rather than at selection [V].

**Three reasons it is declined, in order of weight.**

**1. Auto-generation is a deadlock engine, and it is the whole of what MRR uniquely adds.**
`VanillaResearchAnalysisSetup.BuildForProject` builds requirements for every project that is
*not* hand-listed [V]:

| `techLevel` | What it assigns |
|---|---|
| Undefined / Animal / Neolithic | `null` — exempt |
| Medieval | Experimental, on the **build materials** of the first unlocked thing |
| Industrial / Spacer | **ReverseEngineering on every thing the project unlocks**, plus Experimental on the last one's materials |
| Ultra | **Theoretical on every thing the project unlocks**, plus Experimental on the last one's materials |
| Archotech and anything else | `null` — exempt |

Reverse-engineering and theoretical both require you to *possess* the subject. The subjects are
the things the research unlocks. So any project whose unlocked defs are all player-built-only is
permanently unresearchable, silently. `tools/audit_research_baseline.txt` records **34 such
projects accepted as risks** in today's load order — the file is 36 lines, two of them comments,
and every one of the 34 entries is an `AUTO:` row [V]. Projects carrying techprints or
`requiredAnalyzed` are skipped [V], which is a small mercy and also the tell: the author knew
vanilla's mechanism existed.

**Correction to a claim carried in #67's own body and in
[`docs/data/RESEARCH-NEO-MED.md`](../data/RESEARCH-NEO-MED.md)'s *Devilstrand* row:
`Devilstrand` is not an auto-generation deadlock.** It is one of MRR's own hand-authored
`ManualAnalysisDef`s (`defName` `1`, `experimentalMaterials: DevilstrandCloth`, 9 points), and
`BuildRegistry` applies hand-authored defs **first and unconditionally**, before the tier filter
ever runs [V] — which is the only reason a Neolithic project has a live gate at all. Two
different failure modes were being attributed to one cause. Both die with the mod.
(`docs/engine/research-and-tech-tiers.md` does **not** make this error — it already states the
manual-before-filter ordering and the nine `DevilstrandCloth` studies correctly. An earlier draft
of this spec named it among the conflators; that was over-broad and is withdrawn.)

**2. Its reverse-engineering damage is not what the ticket believed.**
`AnalysisEngine.GetReverseEngineeringDamagePercent` reads the studier's Intellectual level and
then calls `Mathf.Clamp(num, 20, 0)` — arguments transposed. Unity's `Clamp` is
`if (value < min) value = min; else if (value > max) value = max`, so **every** level from 0 to
19 collapses to 20, giving `0.05 + 20/20 × 0.45` = **a flat 50 % of max hit points per study**;
only Intellectual exactly 20 yields 5 % [V]. It is not "5–50 % scaled by skill". With
`reverseEngineeringPointsRequired 2`, a normal item is destroyed on the second study. Only a
`useHitPoints: false` subject survives — which is the accident
`Analysis_Glittertech.xml` was leaning on when it chose `USH_Glitterheart`. The flavour this
ticket was going to pick does not do what it says.

**3. It re-implements, worse, what vanilla already has.** Points live in a mod `GameComponent`
rather than `Game.analysisManager`; the gate fires at the bench rather than at selection; the
display is a string appended to `ResearchProjectDef.Description` behind a hand-rolled cache
that `Patch_ResearchProjectDef_GetTip` busts by nulling `___cachedDescription` every tip draw
[V]; and the whole thing rides `CompStudiable` comps injected into vanilla `ThingDef`s at
`[StaticConstructorOnStartup]`. Set against vanilla: the same behaviour, in XML, with a
purpose-built UI already drawn — and, per § *`Profectus` cannot see this gate*, invisible to a
shipped free-research bypass that MRR's off-def storage walks straight into.

**The three patches on mandatory research targets, now read.** **#67's own body** carried these
as unverified — the attribution to `docs/data/MOD-VERDICTS.md` in an earlier draft of this spec
was wrong: that file holds exactly one MRR reference, a two-column name/packageId row under
*Cheap*, and says nothing about its patches. All three are live in today's load order and all
three are harmless in isolation — the harm is in the registry they consult, not the patch bodies:

| Patch class | Target | Body |
|---|---|---|
| `Patch_ResearchManager_SetCurrentProject` | `ResearchManager.SetCurrentProject`, postfix | if the newly selected project has a registry entry, calls `StudiableCacheRefresher.RefreshAllOurStudiableCaching()`, which walks every managed `ThingDef` on every map and calls `Find.StudyManager.UpdateStudiableCache(thing, map)`. An O(managed defs × maps × things) sweep on every research-tab click [V] |
| `Patch_ResearchManager_StopProject` | `ResearchManager.StopProject`, postfix | identical sweep [V] |
| `Patch_WorkGiver_Researcher` | two patches in one class: `WorkGiver_Researcher.HasJobOnThing` postfix and `JobDriver_Research.MakeNewToils` prefix | the postfix forces `__result = false` when the current project has a registry entry and `AnalysisEngine.AllRequirementsMet` is false; the prefix adds a job fail condition testing the same predicate, so a researcher already at the bench is kicked off [V] |

Those three classes account for **four** of the twelve patches. The remaining **eight** are on
`CompStudiable` (`Study`, `CurrentlyStudiable`, `EverStudiableCached` — three),
`WorkGiver_StudyBase.GetPriority` (a `+1e9` priority override),
`JobDriver_StudyItem.GetStudyToils` (a prefix that replaces the vanilla toils wholesale for
managed defs), `WorkGiver_StudyInteract.HasJobOnThing` (a full prefix replacement) and the two
`ResearchProjectDef` display patches (`get_Description` postfix, `GetTip` prefix) [V].
3 + 1 + 1 + 1 + 2 = 8; 8 + 4 = 12.

**And `PARTS-BIN.md` §5.4's "undeclared and unguarded Anomaly coupling" is wrong — there is no
Anomaly coupling.** Every type MRR's study loop touches is base game: `CompStudiable`,
`CompProperties_Studiable`, `CompAnalyzable`, `WorkGiver_StudyBase`, `WorkGiver_StudyInteract`,
`JobDriver_StudyItem` and `Find.StudyManager` are all in `Assembly-CSharp`, and the
`WorkGiverDef` that drives pawns to study — `StudyArchotechStructures`, `giverClass
WorkGiver_StudyInteract`, `workType Research` — ships in **Core**, not in Anomaly [V]. The study
loop therefore runs, today, in our Anomaly-free load order, and so do its 34 accepted deadlock
risks. The one genuine dependency is the opposite of the claimed one and is inert:
`AnalyzableHelper.CreateAnalyzableProps()` scans for a non-abstract `CompProperties_Analyzable`
subclass whose `compClass` is `CompAnalyzable` — and `CompAnalyzable` is **abstract**, so no
sane def can name it and nothing in vanilla does [V]. The method returns `null` and
`AttachStudyComp` adds a bare `CompProperties_Studiable`, which is all the loop actually needs.

This also answers `PARTS-BIN.md` §14's open item — *"verify whether More Realistic Research's
study loop functions without the Anomaly DLC"* — which was closed as moot rather than answered.
**It does function.** That makes the mod's live behaviour a reason to decline it, not a reason
to ignore it.

### The wide pass

Both roots, both encodings, `obj/` excluded throughout, attributed with `tools/corpus.py --which`.

- `requiredAnalyzed` in XML → **4 mods** (Medieval Overhaul, Mechanoids: Total Warfare, Alpha
  Mechs, GravTech). The four-mod headline is the finding; two further paths in the raw hit list
  are residue and were **not** additional consumers.
- `CompAnalyzableUnlockResearch` in XML → the same 4 mods.
- `AnalysisManager` in `.dll`, ASCII → **zero**. `requiredAnalyzed` / `analysisID` /
  `AnalyzedThingsRequirementsMet` in `.dll`, UTF-16LE → **zero**.

**On the residue.** An earlier draft described the two extra paths as *"the two vendored Biotech
copies"*, which misreads them. They are
`common/RimWorld/Mods/2973169158/1.5/Mods/Biotech/…` and `…/1.6/Mods/Biotech/…` — the **T-22**
second copy of **Alpha Mechs**, whose `Mods/Biotech/` is a perfectly ordinary `IfModActive` load
folder holding Alpha Mechs' own `AM_*` defs. No DLC is vendored anywhere in the corpus. Both
paths collapse into the Alpha Mechs row above, which is why the count is 4 and not 6.

**Sweep validated against known positives before the negative was trusted**: `CompStudiable`
ASCII returns More Realistic Research and Multiplayer across both roots; the UTF-16LE literal
`ResearchMakesSense` returns More Realistic Research. So the negative stands: **no assembly in
the 155-mod corpus Harmony-patches or extends the vanilla analysis system.** We are its only
non-XML consumer, and there is no conflict surface to patch around.

**One honest caveat on the method, not on this result.** The UTF-16LE half of the pass used
`rg -a --encoding utf-16le`, the form `docs/agents/capability-research.md` prescribes, which is
now known to miss strings provably present in the `#US` heap and to do so **non-uniformly**
([#103](https://github.com/cjd721/Rimworld-Archinity/issues/103); the reliable form is `-a` with
a null-interleaved pattern). That is a general reason to distrust a UTF-16LE negative. It is not
a reason to distrust *this* one: the validator run in the same encoding, on the same roots, with
the same flags — the literal `ResearchMakesSense` — **did fire**, and returned More Realistic
Research. The pass demonstrably worked here. The negative was re-run and reproduced exactly by an
adversarial audit on 2026-09-12, validators included.

`python tools/corpus.py --check` reported the corpus matching the snapshot at both the start and
the end of this investigation.

---

## Bypasses — available mechanisms

### The census

**Seventeen distinct mod carriers across fourteen mods, plus two in vanilla — not three.** The
table below has **nineteen** rows. Exactly two are **Core** —
`ReadingOutcomeDoerGainResearch.OnReadingTick` and
`CompUseEffect_FinishRandomResearchProject.DoEffect`; `RitualOutcomeEffectWorker_TribalGathering`
is VFE Tribals', not vanilla, and an earlier draft's count of three vanilla carriers contradicted
this document's own table. 19 − 2 = **17** mod carriers, resolving to **14** distinct mods. The
ticket's catalogue was one pass's worth, and the three it names are not the three that matter.
Classified by the § 0 test; every anchor read from the 1.6 assembly the game loads.

| Carrier | Class | What it does |
|---|---|---|
| `Ability_ReverseEngineer.Cast` (VPE) | **A** | `AccessTools.FieldRefAccess<ResearchManager, Dictionary<ResearchProjectDef,float>>("progress")`, then `progress[proj] = proj.baseCost` for every project that is a `researchPrerequisite` of the targeted thing or of a recipe producing it; then destroys the target [V] |
| `NCL.CompUnlockResearch.UnlockResearch` (MTW) | **A** | `FinishProject` the moment any awake colonist comes within 8 cells of vanilla Odyssey's `CerebrexCore` — no line of sight, no gizmo, no cost. Grants Spacer `NCL_CerebrexCore_Rebuild`, baseCost 5000 [V] |
| `WorldComponent_Senators.GainFavorOf` (VFEC) | **A** | `FinishProject` one named project per senator favoured, plus a `finalResearch` when a republic is complete — 18 named projects across three republics [V] |
| `GameComponent_Tribals.ResearchAllAnimalProjects` (VFE Tribals) | **A** | `FinishProject` over the mod's own Animal-tier defs, once [V] |
| `WorldComponent_RimPacts.ResolveSpyOpSuccess` (RimPacts) | **A** | `AddProgress` of `Cost`, or `Rand.RangeInclusive(300, Cost)`, on a random unfinished project at the target faction's tech level; 1500 silver a go, repeatable on a **30-day per-faction cooldown** [V] |
| `ReadingOutcomeDoerGainResearch.OnReadingTick` (**Core**) | **A** | 20–80 points/hour into one or two projects picked at book generation, with no `CanStartNow` test [V] |
| `Profectus.DoResearch` (VFEC) | **B** | `FinishProject` a random `CanStartNow` project every `(5 + n) × 60000` ticks, forever [V] |
| `TechBlock_Component.AddRandomProgress` | **B** | 25 × `randomInsightRate` into a random `CanStartNow` same-tier project per 25 real points [V] |
| `HordeModeManager.CompleteWave` (VFE Insectoids 2) | **B** | one whole `CanStartNow` project per wave, unbounded, under storyteller `VFEI_HanHordeMode` [V] |
| `RitualOutcomeEffectWorker_TribalGathering.Apply` (VFE Tribals) | **B** | 2/4/8/12 × participants into a `CanStartNow` Animal-or-Neolithic project, by outcome band [V] |
| `CompSpawnerResearchMK2.AddResearchPoints1` (More Archotech Garbage) | **C** | 5,000–15,000 points per 30k–90k ticks per building [V] |
| `HediffComp_PassiveResearch.CompPostTickInterval` (VEF) | **C** | 50 points / 6000 ticks via the VQE-Ancients gene [V] |
| `CompPassiveRes.ConductResearch` (Ushanka Glittertech) | **C** | ≈180/day from `USH_ResearchProbe` [V] |
| `Outpost_Science.Tick` (VOE) | **C** | off-map garrison research, hours 9–15 [V] |
| `JobDriver_ExtendedSitFacingBuilding.ModifyPlayToil` (VFE Core) | **C** | 10 points per joy session at `Joy_ModernComputer` [V] |
| `JobDriver_ApplyResearchGiver.MakeNewToils` (Ushanka Hacking) | **C** | 15/100/150 per consumed data item [V] |
| `CompUseEffect_FinishRandomResearchProject.DoEffect` (**Core**) | **C** | `TechprofSubpersonaCore` finishes the current project [V] |
| `TechBlocker.RecalculateBlockValues` (TechBlock) | **A**, by design | `FinishProject` the `TB_*Theory` defs when player faction techLevel outruns them [V]. This *is* the era ladder's catch-up; it becomes a bypass only if something else raises `FactionDef.techLevel` |
| `GravshipResearchUtility` (VGE) | **D** | currency substitution over 11 projects [V] |

**Ruled out on a read, listed so nobody re-reads them:** Vanilla Books Expanded (its
`FinishProject` hits are all in its **1.1, 1.3 and 1.4** assemblies and **1.6 ships none**, so
the build the game loads carries no research API at all), World Tech Level, Ignorance Is Bliss, Architect Menu Optimizer, Better Architect Menu
(all `FinishProject` postfixes that only invalidate caches or recompute a tech level), VFE
Medieval 2 (`ResearchManager_ResearchPerformed_Patch` *divides* the incoming amount), Tribal
Furniture (a reimplementation of the vanilla bench toil), Vanilla Landmarks Expanded (its
`AddProgress` is `CompSpawnSubplant`'s, unrelated), More Realistic Research (gates, does not
grant — read in full above) [all V].

### Three claims on the ticket that the assemblies contradict

1. **`VFEC_Profectus` does not "unilaterally destroy the era arc."** `PARTS-BIN.md` § 5.5, quoted
   in the ticket, says it "will hand you industrial and spacer research for free."
   `Profectus.CanResearch` ends `return proj.CanStartNow;` [V], so under TechBlock it cannot draw
   a project whose tier lock is unpaid. It is a fast in-era accelerator — roughly 40+ free
   projects over a twenty-year run, since the interval is `(5 + n)` **days** — and that is a real
   pacing problem, but it is not an era breach.
2. **`GravshipResearchUtility` is not an 18-project parallel track, and is not a bypass.** The
   track is **11** projects — `BasicGravtech`, `StandardGravtech`, `AdvancedGravtech`,
   `OrbitalTech` moved into the `VGE_Gravtech` tab by `1.6/Patches/ResearchProjects.xml`, plus VGE's
   own seven `VGE_*` defs [V]. And the Harmony prefix it names sits on `DoBeginResearch`, which
   `DrawStartButton` only reaches for a project that already passes `CanStartNow` [V].
3. **VPE's `Reverse Engineer` is def-removable, as the ticket says — but it is not "the single
   worst breach."** `NCL.CompUnlockResearch` is, because it goes through `FinishProject`, which
   **recursively completes every unfinished prerequisite** [V]; `Ability_ReverseEngineer` writes
   `progress` directly and so completes exactly the projects it names, with no cascade. The
   direct write has its own consequence: because `FinishProject` never runs, the
   `ResearchCompleted` signal never fires, `requiredAnalyzed` entries are never force-completed,
   and every mod postfixing `FinishProject` — TechBlock's lock recalculation, VEF's quest chains,
   both architect-menu caches — never learns the project finished [V].

### Bypasses — the wide pass

Both roots plus `common/RimWorld/Data/`, `obj/` excluded throughout, attributed with
`tools/corpus.py --which`. `python tools/corpus.py --check` reported the corpus matching the
snapshot at the start and the end.

- **`.dll`, ASCII** — `FinishProject` → 13 mods, `AddProgress` → 7, `ResearchPerformed` → 7,
  `ApplyTechprint` → **0**. Every one was depth-read; the results are the census table.
- **`.dll`, ASCII**, for two of `ResearchManager`'s private fields — `techprints` →
  **`NiceBillTab.dll` only**; `anomalyKnowledge` → **zero files**. **An earlier draft filed this
  row under the UTF-16LE pass**, and it is an ASCII result. Nothing is lost by the correction —
  `NiceBillTab.dll` references no research API — so the conclusion stands; the labelling did not.
- **`.dll`, UTF-16LE**, for reflection into `ResearchManager`'s private fields — `currentProj` →
  **TechBlock only**. `progress` intersected with an ASCII `ResearchManager` reference → 11 mods, of which
  six were not already read. **All six resolve to one shared library**, `AchievementsExpanded.dll`,
  redistributed byte-identically under `<mod>/1.4/Assemblies/`; its
  `AchievementsExpanded.ResearchTracker.Trigger` calls `AccessTools.Field(..., "progress")
  .GetValue(...)` and nothing in the assembly calls `SetValue`, `FieldRefAccess`, `Traverse` or
  `GetField` [V]. None of the six loads it under 1.6 at all.
- **XML**, for the three carriers that ride vanilla code and so are invisible to a `.dll` sweep —
  `CompUseEffect_FinishRandomResearchProject` → **Core only**;
  `BookOutcomeProperties_GainResearch` → Core plus five mods widening its tab list;
  `ScenPart_StartingResearch` → Core, Biotech, Odyssey, VRE-Android, Better Traders Guild.

**Method note, because it cost an hour and will cost the next agent one.** The UTF-16LE half was
first run by building the null-interleaved pattern in a command substitution. **Bash strips null
bytes from command substitution** — with a warning that scrolls past — so the pattern silently
degraded to plain ASCII and the "UTF-16" pass was an ASCII pass wearing its name. Both forms
return hits, which is what makes it invisible. Write the escape out literally
(`rg -a -l 'p\x00r\x00o\x00g\x00r\x00e\x00s\x00s\x00' …`) and never construct it in a
substitution. This is a second, distinct defect from the one
[#103](https://github.com/cjd721/Rimworld-Archinity/issues/103) records. **It did not become a
numbered trap** — it is a sweep-construction defect in our own method, not a silent game
behaviour, so it is folded into #103 and into
[`docs/agents/capability-research.md`](../agents/capability-research.md) instead. **None of
[#83](https://github.com/cjd721/Rimworld-Archinity/issues/83)'s trap proposals were allocated an
ID**, and this document cites none.

**Sweep validated before any negative was trusted.** `ResearchMakesSense` ASCII returned More
Realistic Research; `Profectus` ASCII returned VFE Classical across both roots; the UTF-16LE
literal `progress` returned Vanilla Psycasts Expanded, which is where it is known to be, and the
same pattern on the same roots returned zero in the mods reported clean.

---

## Granted capability — available mechanisms

### Vanilla carries one third of it, in XML, and nothing of the other two

**The positive.** `Verse.DesignationCategoryDef.researchPrerequisites` + its `Visible` property
[V], read by `MainTabWindow_Architect.DoCategoryButton` and `ClickedCategory` [V]. Whole
architect categories are research-gated in vanilla XML, live, with `DebugSettings.godMode` as an
escape hatch. *Granted capability — the build* § 1.

**The second vanilla mechanism, which is scribed and which is not what it looks like.**
`RimWorld.GameRules` holds `HashSet<Type> disallowedDesignatorTypes` and
`HashSet<ThingDef> disallowedBuildings`, scribes both through `Game.ExposeData`'s
`Scribe_Deep.Look(ref rules, "rules")`, and is consulted **live** by
`DesignationCategoryDef.ResolvedAllowedDesignators` via `GameRules.DesignatorAllowed(d)` [V].
`SetAllowDesignator(Type, bool)` even calls `Find.ReverseDesignatorDatabase.Reinit()` for you
[V] — the one place vanilla does the invalidation the ticket asks about.

It was surveyed carefully and **not taken**, for three reasons, all [V]:

1. **It is a deny-list with no default.** Research-gating with it means disallowing every gated
   designator at game start and removing entries as projects finish — an *applied* model, which
   needs an apply-once hook and breaks on a save where the project finished before our mod
   existed. The derived model in § 2 has no such state.
2. **`DesignatorAllowed` short-circuits for `Designator_Place`**: if the designator is a
   `Designator_Place`, it returns `!disallowedBuildings.Contains(PlacingDef)` and **never
   consults `disallowedDesignatorTypes` at all** [V]. Build designators cannot be blocked by
   type through this path.
3. **It does not touch work types.** Half the ticket is untouched either way.

**The negative, and it is complete.** Vanilla `ResearchProjectDef` has no field that grants a
work type, a work tag, or an individual designator. There is no `WorkTypeDef` gate other than
the def-level `visible` flag and `visibleOnlyWithChildrenInColony` [V] — `visible` is a **def**
field, so writing it at runtime is a def mutation, per-install rather than per-save, and the
same class of defect as **T-11**. `WorkTypeDef.VisibleCurrently` also caches its answer for **30
frames** [V], which would make any such write visibly laggy. Not a route.

**`Verse.ResearchMod` is vanilla's unused extension point, and it is worth knowing about even
though it is not taken.** `ResearchProjectDef.researchMods` is a `private List<ResearchMod>`
(private is not a bar — `DirectXmlToObject` sets it), and `ResearchManager.FinishProject` calls
`ReapplyAllMods()` → `ResearchProjectDef.ReapplyAllMods()` → `researchMods[i].Apply()` inside a
try/catch [V]. **Vanilla ships the abstract class and zero subclasses** [V]. It is the
XML-authored "do this when the project finishes" hook, and it is the natural carrier for an
*applied* design — which is precisely why the *derived* design in § 2 does not need it.

> **Correction to an earlier draft, which had this exactly backwards.** That draft said
> `ReapplyAllMods` has *"no load path"* and concluded that *"a `ResearchMod` that mutates state
> is not re-applied on load"*, and marked it [V]. **It is re-applied on load.** There are
> **three** callers, not two: `ResearchManager.FinishProject`,
> `ResearchManager.DebugSetAllProjectsFinished`, and **`Verse.Game.FinalizeInit()`**, which calls
> `researchManager.ReapplyAllMods()` two lines above `GameComponentUtility.FinalizeInit()` [V,
> `Verse.Game.FinalizeInit`]. So a `ResearchMod` is idempotently re-run for **every finished
> project on every load**, which makes it *more* attractive as an applied carrier, not less —
> and note it is the same hook [`ERA.md`](ERA.md) § 4 builds its post-load repairs on, firing
> immediately before them. The reason § 2 does not take it is unchanged and was never this: a
> derived design needs no apply step at all.

### VFE Tribals, read end to end

The mechanism is fifteen types and no saved state. Beyond the fields and the seven authored
projects already tabulated in *Granted capability — the build* § 0:

| Piece | Anchor | Note |
|---|---|---|
| the unlock test | `VFETribals.Utils.IsUnlocked(WorkTypeDef, out …)` / `(WorkTags, out …)` | reads `IsFinished` directly; two `Dictionary` indexes built lazily [V] |
| work types | `Pawn_GetDisabledWorkTypes_FillList_Patch` | targets the **compiler-generated local function** by name scan over `AccessTools.GetDeclaredMethods(typeof(Pawn))` [V] |
| work tags | `Pawn_CombinedDisabledWorkTags_Patch` | ORs locked flags for `Faction.OfPlayerSilentFail` pawns [V] |
| reasons | `Pawn_GetReasonsForDisabledWorkType_Patch`, `CharacterCardUtility_GetWorkTypeDisabledCausedBy_Patch` | two surfaces, same string [V] |
| designators | `Designator_GizmoOnGUI_Patch`, `Designator_CreateReverseDesignationGizmo_Patch`, `Designator_DesignateThing_Patch`, `PawnColumnWorker_Designator_SetValue_Patch`, `DesignationManager_AddDesignation_Patch` | **disable in place; never remove from the category** [V] |
| display | `ResearchProjectDef_UnlockedDefs_Patch` (transpiler + `AddUnlockedDefs`), `VFETribals.FakeDef`, `Widgets_DefIcon_Patch` | synthesises a `Def` for a `Type` [V] |
| invalidation | `ResearchManager_FinishProject_Patch` | `Notify_DisabledWorkTypesChanged()` over all live pawns, guarded on the project actually granting something [V] |

Two details that a summary would lose and that the build depends on:

- **`Designator_GizmoOnGUI_Patch` re-enables as well as disables.** If the gizmo's
  `disabledReason` equals *our* reason and the project is now finished, it clears `disabled` and
  `disabledReason` [V]. Without that, a gizmo disabled once stays disabled, because
  `Gizmo.Disable` is sticky across frames for a cached command.
- **`DesignationManager_AddDesignation_Patch` guards against off-thread access**: it skips when
  `Find.ReverseDesignatorDatabase.desList == null && !UnityData.IsInMainThread` [V]. The
  designator lookup touches a lazily-built UI database; a patch on this method that ignores the
  thread can deadlock or throw during map generation.

### Wide pass

Both corpus roots plus `common/RimWorld/Data`, `-g '*.dll' -g '!**/obj/**'`, ASCII
(`#Strings`-heap identifiers), attributed with `python tools/corpus.py --which -`:

| Symbol | Mods | Read |
|---|---|---|
| `unlocksWorkTypes` | **1** — VFE Tribals (its 1.4 / 1.5 / 1.6 copies) | yes |
| `SetAllowDesignator` | **0 mods**; vanilla `Assembly-CSharp.dll` only | sweep validated against that known hit |
| `GetReasonsForDisabledWorkType` | **1** — VFE Tribals | yes |
| `Notify_DisabledWorkTypesChanged` | 7 — VFE Deserters, VFE Tribals, VPE Puppeteer, VRE Android, MedPod, VEF, EdB Prepare Carefully | VFE Tribals and VEF read; the rest are hediff-, xenotype- and apparel-driven work disabling, **not research-driven** [I] |
| `CombinedDisabledWorkTags` | 4 — VFE Empire, VFE Tribals, VEF, EdB Prepare Carefully | same |

**How the sweeps were built, because a null-interleaved negative is only worth the bytes that
reached ripgrep.** The ASCII passes are `rg -a -l "<symbol>" <workshop> <common/Mods>
<common/RimWorld/Data> -g '*.dll' -g '!**/obj/**'`. A `#US`-heap pass was run once for
confirmation with the escapes **typed literally** into the pattern
(`rg -a -l "u\x00n\x00l\x00o\x00c\x00k\x00s\x00W\x00o\x00r\x00k\x00"`, never through `$(…)`,
never `--encoding utf-16le` — **#103**) and returned nothing, which is the correct result: a
field or type *name* lives in `#Strings` as ASCII, not in `#US`. `corpus.py --which` attributed
five `EdBPrepareCarefully.dll` / `VFECore.dll` paths under `common/RimWorld/Mods` to no mod —
**T-22** second copies whose `About.xml` the tool does not index, not a broken sweep.

**Nothing else in the corpus grants a capability from research.** The nearest thing is **VEF**,
and it is not one: `VEF.Buildings.HiddenDesignatorsDef` carries a flat `List<BuildableDef>`
consumed by `VanillaExpandedFramework_DesignationCategoryDef_ResolvedAllowedDesignators_Patch`,
which filters out `Designator_Build` entries whose `PlacingDef` is on a **static** hidden list
[V] — permanent, build-designators-only, and unconditioned by research.
`VEF.Apparels.VanillaExpandedFramework_Pawn_GetDisabledWorkTypes_Patch` disables work types from
**worn apparel** [V]. Both are the right seams, neither is keyed on a project.

So the verdict is the ticket's own guess, confirmed by reading rather than by absence: **VFE
Tribals is the only donor, and we reimplement it.** The ticket's ~30-line estimate is low by
roughly a factor of five once display and invalidation are included; the build's table says
where the rest goes.

---

## Verification

**Settled by reading** [V]: the gate chain (`CanStartNow` → `AnalyzedThingsRequirementsMet` →
`AnalysisDetails.Satisfied`); the comp and its XML surface; `Game.analysisManager` and its
scribe path; `OnAnalyzed` and `FinishProject` as the only writers; all six display surfaces in
`MainTabWindow_Research`; Multiplayer's blanket `ITargetingSource.OrderForceTarget` registration;
`Rand.RangeInclusive`'s early return; and Biotech's four gated mechanitor projects as a shipped
working instance.

**Needs a prototype or an in-game check** [I]:

1. **One end-to-end pass on a throwaway save.** Patch the comp onto `USH_Glitterheart` and
   `requiredAnalyzed` onto `USH_GlittertechFabrication`; confirm the project shows "Study
   requirements" and refuses to start, that the "Analyze…" gizmo appears on a spawned
   glitterheart, that a colonist walks to a bench and completes it, that the letter fires, that
   the project becomes startable, **and that the glitterheart is still in the stockpile.**
2. **A stack check.** `USH_Glitterheart` has `stackLimit 3`. Confirm the gizmo and job behave on
   a stack of more than one; nothing read suggests otherwise, but Biotech's chips are the only
   shipped instance and no test covers a stack.
3. **One two-client pass**, observing that a client-issued "Analyze…" order completes on both
   machines and that `AnalysisDetails.timesDone` matches. The sync registration is verified;
   that it *behaves* is not.
4. **If any exemplar ends up at `required > 1`, one deliberate first-analysis check** with the
   `progressedLetter*` fields authored, and one without, confirming the empty-list throw. Nothing
   in vanilla exercises this path.

**Observable checks that demonstrate the requirement.** From
`docs/requirements/GLITTERTECH.md` — *"the colony cannot reason its way into post-vanilla
technology from nothing"*: with no glitterheart ever recovered,
`USH_GlittertechFabrication` cannot be selected in the research tab and the tab says why; after
one analysis it can; and the heart is still owned and still spendable on building the fabricator.

### Bypasses

**Settled by reading** [V]: `TechBlocker.BlockTechs`'s injection of the `TB_<Era>Theory` def into
`prerequisites` at `techLevel - 2`; `FinishProject`'s recursive prerequisite completion, over
`prerequisites` and never `hiddenPrerequisites`; `Cost == baseCost` whenever `baseCost > 0` —
`knowledgeCost` otherwise — and so `IsFinished` from a bare `progress` write; `DrawStartButton`'s `CanStartNow` gate ahead of
`DoBeginResearch`; and every anchor in the census table.

**Needs a prototype or an in-game check** [I]:

1. **`patch_check.py` on the written lockout.** Every xpath must match a non-zero node count. A
   `PatchOperation` matching nothing is loud under the tool and **silent in game** — which is the
   whole failure mode this lockout exists to prevent, so the check is not optional.
2. **Load-order proof for the `CerebrexCore` clause.** `Archinity.Pacing` must resolve after
   Mechanoids: Total Warfare or the comp is not yet on the def. Confirm with `xpath.py` against
   the merged tree, not by reading `ModsConfig.xml`.
3. **One reading pass on a schematic** after the `usesHiddenProjects` line, confirming the
   benefits string greys an analysis-gated project and that reading it adds no progress.
4. **One `Profectus` interval measurement**, if VFE Classical survives sourcing. `(5 + n) × 60000`
   ticks was read, not observed, and the free-project count over a campaign follows from it.

**Observable check that demonstrates the requirement.** With the lockout in and TechBlock's
Neolithic lock unpaid, no route in the load order completes or fills a Medieval project: no
schematic advances one, no reward pool offers a `TechprofSubpersonaCore`, and no psycast, perk,
wave, ritual or proximity trigger finishes one.

### Granted capability

**Settled by reading** [V]: `Pawn`'s two disabled-work-type caches and the single method that
nulls them; `Pawn.CombinedDisabledWorkTags` as an uncached computation;
`DesignationCategoryDef.researchPrerequisites` → `Visible` → `MainTabWindow_Architect`;
`resolvedDesignators` built once under `LongEventHandler` and never rebuilt;
`GameRules`'s scribe path, its live read and its `Designator_Place` short-circuit;
`ResearchProjectDef.researchMods` → `ReapplyAllMods` and its **three** callers, including
`Verse.Game.FinalizeInit`; `MainTabWindow_Architect.DoCategoryButton` / `ClickedCategory` and
what a gated category actually looks like; `0Harmony` 2.4.1's `GetBulkMethods` `failOnResult`
throw; `Game.FillComponents`; and every VFE Tribals anchor tabulated above.

**Needs a prototype or an in-game check** [I]:

1. **The invalidation, deliberately broken first.** Finish a granting project with the
   `FinishProject` postfix commented out and confirm the work type stays disabled on every
   colonist until a save/load. That is the silent failure the postfix exists for, and seeing it
   once is the only way anyone will remember it is there.
2. **The idempotence of patch 1.** `GetDisabledWorkTypes` returns the cache itself; confirm over
   a few hundred ticks that the returned list does not accumulate duplicate entries.
3. **A designator mid-game.** Finish `Mining`'s analogue and confirm `Designator_Mine` goes from
   greyed-with-reason to live **without a save/load and without reopening the architect menu** —
   the claim that no cache needs rebuilding.
4. **A gated architect category.** Author `researchPrerequisites` on one `DesignationCategoryDef`
   and confirm the category button is **drawn, greyed, and clickable** before the project
   finishes, that clicking it produces the *"nothing available in category"* `RejectInput`
   message, and that both revert after — with no code at all. **An earlier draft of this check
   read "confirm the whole tab is absent before and present after" and would have failed**:
   `DoWindowContents` iterates every cached panel unconditionally and `DoCategoryButton` only
   greys it.
5. **One two-client pass.** Finish a granting project on one client; both work tabs must change
   on the same tick and no desync.

**Observable check that demonstrates the requirement.** From `docs/plot/NEOLITHIC.md` —
*"establish the first verbs of civilization"*: on a fresh colony with the on-ramp authored, a
colonist cannot be assigned to Mining, the Mine designator is greyed and names the project, and
the research tab's entry for that project lists **Mining** and **Mine** under *Unlocks*. After
the project finishes, all three change, in that order, without a reload.

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| **Which branch roots carry a gate, and which artifact gates each** | The whole shape of the Glitterite loop. The mechanism is settled; the catalogue is authoring. `GLITTERTECH.md` says only "every major Glittertech branch" and defers the catalogue itself | [Act V #47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| **Does analysis consume the exemplar** — as a stated rule, not an implementation default | Recommended here as **no**, on `GLITTERTECH.md`'s own "bring home armor" and on the double-charge argument. It is a gameplay rule and belongs in `docs/requirements/GLITTERTECH.md` as one line rather than living only in a spec | requirements gap, → [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| **Resolved: does the Exemplar gate cost Intel?** | No. Studying a surviving exemplar and exchanging accumulated Intel for an Instruction item are different acts. Destructive analysis produces Intel and Trace; it does not satisfy `requiredAnalyzed` | [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54), [#115](https://github.com/cjd721/Rimworld-Archinity/issues/115) and [#117](https://github.com/cjd721/Rimworld-Archinity/issues/117) |
| **`analysisRequiredRange` per exemplar, and `analysisDurationHours`** | Pacing dials only. Default `1~1` and 0.5 h match Biotech. A campaign-central exemplar may want `2~2` — **if it does, the three `progressedLetter*` fields become mandatory** (see *Failure and recovery*), which is a real authoring cost, not a dial | [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) / [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30) |
| **Our reserved `analysisID` block** | Collision with a third-party mod is silent (**T-41**). Pick a block, record it here when the first exemplar is authored | this document |
| **Whether `requiredResearchFacilities` also gates the Glittertech tree** | Ushanka already imposes `MultiAnalyzer` on all 18 and `USH_ResearchProbe` on 14. Composing a second facility gate on top is a pacing choice, not a capability question | [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| **Analysis at Neolithic and Medieval** | Newly available: vanilla's gate has no tier filter — demonstrated, not merely permitted, by Industrial `WastepackAtomizer` on `NanostructuringChip` — where More Realistic Research exempted everything at or below Neolithic. *"Study the sword you took off a dead marauder"* is now buildable in the early campaign if the leaps want it | [#41](https://github.com/cjd721/Rimworld-Archinity/issues/41), [#42](https://github.com/cjd721/Rimworld-Archinity/issues/42) |
| ~~**Whether TechBlock stays in the load order**~~ — **struck**. TechBlock's random-insight pool filters on `CanStartNow` [V], so it cannot touch an analysis-gated project. The risk was misattributed; see *Failure and recovery* | none | — |
| **Whether the `Schematic` book's doer gets `usesHiddenProjects`** | Vanilla's schematic feeds `AddProgress` with no `CanStartNow` test, so it can carry an exemplar-gated branch root to full progress. One XML line closes it, and it is the only shutoff in this document that the Analysis gate itself depends on | [#83](https://github.com/cjd721/Rimworld-Archinity/issues/83), this document |
| **Does any bypass survive as an authored reward** | The ticket asks, and it is a gameplay rule, not a mechanism. A one-off free project as a Church title privilege is legitimate; an infinite generator is not. The lockout above assumes **none survives**; if one should, the cheapest carrier is vanilla `TechprofSubpersonaCore` with its `thingSetMakerTags` kept and a hand-placed quest reward instead | requirements gap, → [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) for the ledger, and the owning requirements ticket for the rule |
| **Per-mod disposition for the seventeen mod carriers** | *restat*, *art only*, *block* — each row of the census implies one and this document makes none of them. Two recommendations only: keep and restat `USH_ResearchProbe`; take the vanilla `Schematic` one-liner | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) |
| **Whether the Class C rate producers are a pacing problem** | `MAG_AutoResearcher` at 5,000–15,000 points a cycle and the VQE-Ancients gene at **500/day** both outrun the 213/day single-researcher baseline in [`docs/engine/research-and-tech-tiers.md`](../engine/research-and-tech-tiers.md) § *Research rate, reconstructed*. They cannot skip an era; they can collapse one | **no owner** — #5 and #7 are closed; the gap is stated and awaits routing |
| **Whether `ScenPart_StartingResearch` is in scope** | Our own scenario grants starting research through the same vanilla `FinishProject` path, with its recursive prerequisite completion. Harmless if the grant is Neolithic; an era breach if anything above it is ever listed | [#18](https://github.com/cjd721/Rimworld-Archinity/issues/18) |
| **Which verbs the Neolithic actually gates, and in what order** | The ticket asks and this document deliberately does not answer. The mechanism supports any `WorkTypeDef`, any `WorkTags` flag and any `Designator` subclass; which of them start locked is a progression decision with a real cost — a colony that cannot haul or cook on day one is a different game from one that cannot mine. VFE Tribals' seven-project shape is tabulated in *Granted capability — the build* § 0 as a worked reference, not as a recommendation | [#41](https://github.com/cjd721/Rimworld-Archinity/issues/41), [#37](https://github.com/cjd721/Rimworld-Archinity/issues/37), grid at [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30) |
| **What tier the on-ramp projects are authored at** | `Animal` puts them outside TechBlock's injected era ladder entirely (`GetBlock` indexes at `techLevel - 2`), which is what VFE Tribals does and is almost certainly right — an on-ramp that is itself era-locked is circular. Recorded because it is a one-word XML decision with a silent consequence | [#41](https://github.com/cjd721/Rimworld-Archinity/issues/41) |
| **Patch 1's target — public `GetDisabledWorkTypes` or the local `FillList`** | Recommended: **the public method**, on two grounds — a public member is a citeable, refactor-stable anchor, and **only it can read `permanentOnly`**, so only it can avoid writing research gates into `cachedDisabledWorkTypesPermanent` the way the donor does. The cost is having to add idempotently to a list that *is* the cache. (The Loudness argument an earlier draft gave is withdrawn: both targets throw — `0Harmony` 2.4.1 `GetBulkMethods` fails on a null `[HarmonyTargetMethod]`) | this document |
| **Whether the cornerstone system is rebuilt anywhere** | Recommended **dropped**: the altar is already the campaign's register for permanent colony-wide boons and #7 § 7 puts era advancement there. If a "what this era made us" mechanic is wanted, it belongs in [`ALTAR.md`](ALTAR.md), not here | design call → [`ALTAR.md`](ALTAR.md) / [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) |
