# Research

## Purpose and scope

How research is *earned* in this campaign. `CONTEXT.md` settles three routes to knowledge —
**Practice** (resource cost alone), **Instruction** (a techprint, a book, a teacher) and
**Analysis** (a physical example you took apart). Practice is the vanilla default and needs no
spec. Instruction is solved and shipped: techprints are vanilla Royalty, and
`QuestNode_GiveTechprints` with `fixedProject` is pure XML.

This document owns **Analysis**: what forces a research project to require that the colony
physically studied a named item, and what happens to the item
([#67](https://github.com/cjd721/Rimworld-Archinity/issues/67)). It is the mechanism behind
the Glitterite loop in
[`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md) § *Acquire → Analyze →
Research → Manufacture*.

It does **not** own the Intel balance
([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)) — the interface between the two
is stated in *The build* § **The seam with Intel** and nothing more. It does not own whether
Analysis is *priced* in Intel, which is a requirements question
([#101](https://github.com/cjd721/Rimworld-Archinity/issues/101)). It does not own the
exemplar **catalogue** — which artifact gates which branch is authoring work and belongs to
[Act V](https://github.com/cjd721/Rimworld-Archinity/issues/47). It does not own research
**pacing**, tier totals or the era ladder
([`docs/engine/research-and-tech-tiers.md`](../engine/research-and-tech-tiers.md),
[#5](https://github.com/cjd721/Rimworld-Archinity/issues/5),
[#7](https://github.com/cjd721/Rimworld-Archinity/issues/7)), the research **menu surface**
([#96](https://github.com/cjd721/Rimworld-Archinity/issues/96)), or research that unlocks work
types ([#72](https://github.com/cjd721/Rimworld-Archinity/issues/72)).

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
`PrerequisitesCompleted`, `TechprintRequirementMet`, `PlayerHasAnyAppropriateResearchBench`,
`PlayerMechanitorRequirementMet` and `InspectionRequirementsMet` [V].
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

What this gate needs to know about a recovered exemplar, stated as a contract so #54 can build
against it:

1. **The gate's entire input is a `ThingDef` on a colony map.** It cannot read a balance and
   does not need to.
2. **Spending Intel and consuming an exemplar are two different acts, and this gate performs
   neither *as built*.** Analysis spends nothing. It flips one colony-global boolean per
   `analysisID`, permanently. Intel is a fungible, decrementable scalar; an analysed exemplar is
   a one-way latch. Do not model one on the other.
   **Whether Analysis should *additionally* cost Intel is not decided here, and an earlier draft
   of this spec was wrong to decide it.** That draft ruled *"do not price analysis in Intel"*;
   **the ruling is withdrawn.** #67 is a capability ticket and pricing is a gameplay rule — an
   open **requirements parameter** owned by
   [`docs/requirements/GLITTERTECH.md`](../requirements/GLITTERTECH.md) and tracked as
   [**#101 — Does Analysis ever cost Intel**](https://github.com/cjd721/Rimworld-Archinity/issues/101).
   [`docs/specs/CURRENCIES.md`](CURRENCIES.md) has dropped the matching half of the interface —
   its expectation that this gate calls `CanAfford`/`TrySpend` — in the same pass. Everything
   below, and the cost table, assumes the **unpriced default**.
3. **The clean split** — *under the unpriced default.* The exemplar answers *may this branch be
   researched at all* — binary, per branch, irreversible. Intel answers *how much of this branch
   can you afford now* — scalar, spent, replenished. One `requiredAnalyzed` entry at each branch
   root; Intel priced across the projects beneath it. If #101 decides Analysis is priced, the
   split moves and this spec grows a C# leg (see *Cost*).
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
| **New C#** | **none — conditional on Analysis staying unpriced ([#101](https://github.com/cjd721/Rimworld-Archinity/issues/101))** | **0 under the default.** If #101 prices Analysis, the completion path needs a `TrySpend` call and the gizmo needs a `CanAfford` disable reason — a Harmony postfix on `CompAnalyzable.OnAnalyzed` and one on `CompInteractable.CanInteract`, neither of which exists today | — |

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

**`AddProgress` does not consult the gate, and one mod in the bin calls it at random.**
`ResearchManager.AddProgress` never checks `CanStartNow` — the §1 claim that "enforcement is at
project selection" is a claim about the *player's* route, not about every route. TechBlock's
random-insight mechanic takes the other one: while a block tech is being researched, every 25
points grants 25 to a **random unfinished same-tier project**
([`docs/engine/research-and-tech-tiers.md`](../engine/research-and-tech-tiers.md)
§ *The random-insight mechanic cancels visible progress*) [V]. A gated Glittertech project
sitting unfinished at the same tier can therefore accumulate progress and, with enough draws,
finish — and `ResearchManager.FinishProject` then force-completes its analyses, so the gate is
not merely bypassed but retroactively marked satisfied. Whether TechBlock is in the final load
order is [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s call; if it is, the
Glittertech roots must sit outside its tier pool or the gate is decorative. **[I]** on the
interaction — the two mechanisms were read separately and have not been observed together.

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
- [#101](https://github.com/cjd721/Rimworld-Archinity/issues/101) — whether Analysis is priced
  in Intel at all. The cost line above is conditional on its default.

**Open parameters, not mechanisms:** how many analyses per exemplar, the duration, which branch
roots carry a gate, which artifact gates which branch, and whether Analysis costs Intel. Named
in *Outstanding decisions*.

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
anomaly projects** ([`docs/data/PARTS-BIN.md`](../data/PARTS-BIN.md) § 5.5) [V]. It never
consults `CanStartNow`; it filters on the def's own fields, and `requiredAnalyzed` is one of the
fields it filters on.

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

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| **Which branch roots carry a gate, and which artifact gates each** | The whole shape of the Glitterite loop. The mechanism is settled; the catalogue is authoring. `GLITTERTECH.md` says only "every major Glittertech branch" and defers the catalogue itself | [Act V #47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| **Does analysis consume the exemplar** — as a stated rule, not an implementation default | Recommended here as **no**, on `GLITTERTECH.md`'s own "bring home armor" and on the double-charge argument. It is a gameplay rule and belongs in `docs/requirements/GLITTERTECH.md` as one line rather than living only in a spec | requirements gap, → [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| **Does Analysis cost Intel** | Not settled, and **not settleable here** — #67 is a capability ticket. The build, the seam in §6 and the "New C# = none" cost line all assume **unpriced**; a priced gate adds two Harmony postfixes and moves the split in §6.3 | [#101](https://github.com/cjd721/Rimworld-Archinity/issues/101), owned by `docs/requirements/GLITTERTECH.md` |
| **`analysisRequiredRange` per exemplar, and `analysisDurationHours`** | Pacing dials only. Default `1~1` and 0.5 h match Biotech. A campaign-central exemplar may want `2~2` — **if it does, the three `progressedLetter*` fields become mandatory** (see *Failure and recovery*), which is a real authoring cost, not a dial | [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) / [#30](https://github.com/cjd721/Rimworld-Archinity/issues/30) |
| **Our reserved `analysisID` block** | Collision with a third-party mod is silent (**T-41**). Pick a block, record it here when the first exemplar is authored | this document |
| **Whether `requiredResearchFacilities` also gates the Glittertech tree** | Ushanka already imposes `MultiAnalyzer` on all 18 and `USH_ResearchProbe` on 14. Composing a second facility gate on top is a pacing choice, not a capability question | [#47](https://github.com/cjd721/Rimworld-Archinity/issues/47) |
| **Analysis at Neolithic and Medieval** | Newly available: vanilla's gate has no tier filter — demonstrated, not merely permitted, by Industrial `WastepackAtomizer` on `NanostructuringChip` — where More Realistic Research exempted everything at or below Neolithic. *"Study the sword you took off a dead marauder"* is now buildable in the early campaign if the leaps want it | [#41](https://github.com/cjd721/Rimworld-Archinity/issues/41), [#42](https://github.com/cjd721/Rimworld-Archinity/issues/42) |
| **Whether TechBlock stays in the load order** | If it does, its random-insight `AddProgress` draws can complete a gated Glittertech project without the exemplar (*Failure and recovery*). Either keep the Glittertech roots out of its tier pool, or the gate is decorative | [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14) |
