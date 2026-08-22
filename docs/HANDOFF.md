# Handoff — read this first

State of the Archinity project at the end of session 3.

## Reading order

1. **[`VISION.md`](VISION.md)** — what this playthrough is *for*. The premise,
   the arc, the altar, and the design principles that drove nearly every
   decision. **This is the part that cannot be recovered from the code.** If
   you read nothing else, read this.
2. **[`../CLAUDE.md`](../CLAUDE.md)** — the failures that produce no error
   message. Short, and every entry has already cost someone an evening.
3. **[`QUESTLINE.md`](QUESTLINE.md)** — the sixteen-beat outline: what each
   beat gates on, what it gives, and what every reward mechanically does.
4. **[`technical-findings.md`](technical-findings.md)** — every fact verified
   against decompiled source. Re-deriving it is expensive and the wiki is wrong
   about several of them.

This document is build status and next actions.

---

## Two decisions waiting on Conrad

Do not resolve either unilaterally.

**1. The Medieval route.** See
[`DECISION-medieval-route.md`](DECISION-medieval-route.md) — enable Medieval
Overhaul and strip it (Route A), or hand-port selected content into our own
module (Route B). The Medieval era is 22 projects and 15,500 research points
against an intended 180–240 day era. That doc carries the verified facts for
both routes, the gameplay walkthrough and the obsolescence audit.

**2. Quest cadence, then the gene split.** Conrad wants the questline's rhythm
settled *before* deciding how many archite genes leave the starting xenotype.
His last word was that he'd keep "a few more upfront" than the split proposed
to him. Fix the beats first; the gene list follows from them.

---

## What this is

A suite of RimWorld 1.6 mods for one long co-op playthrough on the
**Multiplayer** mod. Neolithic start, every tech era in order, endgame in orbit
aboard a gravship, ending in transcendence.

Almost everything is **XML defs only**, because def-only mods carry no
simulation code and are inherently multiplayer-safe.

**`Archinity.Altar` is the one deliberate exception** and ships a Harmony
assembly. Three things forced it, each verified impossible in XML:

- Granting a **named** gene. Nothing in vanilla represents a specific gene as an
  item — `Genepack.PostMake()` unconditionally calls `GenerateGeneSet()`, so
  even a hand-placed genepack has random contents.
- Charging a machine with **a life** rather than an item. `CompRefuelable`
  accepts anything matching its filter, which would let hemogen packs stand in
  for a sacrifice.
- Rebinding VRE-Archon's equipment gate, a hardcoded `HashSet<ThingDef>` checked
  against `HasActiveGene(VRE_Transcendent)`.

Do not start a second assembly without an explicit decision.

---

## Build status

| Mod | Status | Verified how |
|---|---|---|
| `Archinity.Origins` | Built | Loaded in game; scenario appears, 2 archonians + 2 baseliners confirmed |
| `Archinity.Pacing` | Built | Loads clean; all four xpaths resolved |
| `Archinity.Drifters` | Built | Loads clean. **Never been through worldgen.** |
| `Archinity.Glitterites` | Built | Loads clean. **Never been through worldgen.** |
| `Archinity.Altar` | Built | Compiles clean, all four checks pass. **Never loaded in game.** |
| `Archinity.Chronicle` | **Not started** | — |

### Verification backlog — nothing below has run in game

1. **Fresh worldgen.** Drifters and Glitterites have never been placed. Confirm
   both appear at world creation, that their settlements generate **in orbit**
   not on the surface, that names read correctly (`Longwake Drydock`,
   `Threshold-17 Overlook`), and that orbit is visibly denser (subdivisions were
   raised 5→6). Note worldgen duration — it decides whether 6→7 is worth trying.
   The view-orbit button only exists **in game**, not at world creation
   (`GetGizmos` bails on `ProgramState.Entry`). In colony → world map → **`B`**.
2. **A glitterheart actually drops.** Never confirmed.
3. **The altar loads and works.** Specifically: does its texture resolve from VQE
   Ancients' folder; do the twelve facilities link; does a prisoner get hauled in
   and drained; does a vector grant its gene.
4. **Does `VQEA_Electromagnetized` keep the archoplate's shield up through an
   EMP?** This is an assumption, not a finding. The entire "archon gear becomes
   usable in the Ultra era" reward rests on it.

---

## Archinity.Altar — what was built

Read *The altar* in `VISION.md` for why it is shaped this way. This is how it
works.

### The mechanism

- **Charge is measured in lives.** A prisoner or slave hauled in is drained over
  ~2 in-game hours and dies. Yield scales with `BodySize`, so an adult is worth
  about 1 and an animal a fraction — which is what makes "fifty people, or
  several hundred animals" a real shape rather than a number pulled from air.
- **Charge lives in the building**, so it never spoils and never needs
  refrigeration. That was the specific problem with storing blood as items.
- **A free colonist who walks in willingly** spends charge plus a vector and
  comes out changed. The recipient is never the one who dies.
- **Fuel vs. recipient is read from the pawn's own status** —
  `IsPrisonerOfColony || IsSlaveOfColony` is fuel, a free colonist is a
  recipient. This is why the building needs **no mode toggle and no custom
  gizmos**, which is the main reason it should be multiplayer-safe.

### Why entry is safe in multiplayer

Both entry paths are **vanilla jobs**. Willing entry uses `JobDefOf.EnterBuilding`
via `Building_Enterable.SelectPawn`. Unwilling entry uses
`JobDefOf.CarryToBuilding` via `WorkGiver_CarryToBuilding`, which
`WorkGiver_CarryToAltar` subclasses in about four lines — reservation,
reachability, the prisoner check and the job itself are all inherited. That is
the same path the vanilla gene extractor and growth vat use, so Multiplayer syncs
it natively and we never touch its API.

The only job of our own is hauling a vector in, and it is a plain haul.

### Gene vectors

The primitive that forced the assembly. `GeneVectorExtension` on a ThingDef makes
that item mean exactly one gene. Because it is an ordinary item, deterministic
delivery stops being a quest-system problem — a vector works in a hand-authored
ruin, a quest stash, a loot table or a trader's stock.

Two worked examples ship (`Archinity_Vector_PerfectVision`,
`Archinity_Vector_PlasteelSkin`). The rest get authored alongside the beats that
deliver them, because cost and gate belong to the beat.

Vectors are quest-only: no recipe, no trade tags, `thingSetMakerTags` cleared so
nothing generates them as loot.

### The draw table

[`Archinity.Altar/Defs/GenePoolDefs/GenePool_Archite.xml`](../Archinity.Altar/Defs/GenePoolDefs/GenePool_Archite.xml)
— all 50 archite genes, hand-tiered 1–5 and categorised.

**Ranked by hand because the game's own numbers cannot separate them.**
`biostatMet` is 0 for 49 of 50; `biostatCpx` is 3 for 35 of them. `Deathless`
(cpx 7) and a cosmetic gene (cpx 3) are indistinguishable to any automatic rule.
Distribution is in [`archite-gene-pool.md`](archite-gene-pool.md); regenerate
with `python tools/survey_archite.py` after any mod change.

Reserved out of the lottery entirely: `Deathless`, `Ageless`, `VRE_Transcendent`,
`VQEA_Genius`, `VQEA_Serene`, `VQEA_Electromagnetized`, `VacuumResistance_Total`,
`XenogermReimplanter`, and `VREH_ChemicalDependency_Luciferium` (kept listed
because it is useful later as a curse).

### Patches shipped

- **Reimplant postfix** strips `Deathless`/`Ageless` from converts and *adds*
  `Deathrest`. The endogene/xenogene trick does **not** work —
  `ReimplantXenogerm` calls `SetXenotype` first, which copies the whole
  XenotypeDef gene list onto the recipient, so stripping afterwards is the only
  honest fix.
- **Archon equipment gate** rebound off `VRE_Transcendent` onto whatever
  `archonEquipmentGene` names (currently `VQEA_Electromagnetized`). Implemented
  by reflecting on VRE-Archon's public static `blockedWeapons` HashSet, emptying
  it, and re-gating in our own postfix. Wrapped in try/catch — it must never
  become a hard dependency.
- **Hunger offset.** `Archinity_ArchiteSustenance` cancels the metabolic cost of
  implanted genes.

### Starting xenotype changes

`Deathrest` and `XenogermReimplanter` are both **removed**. Both removals are
load-bearing and are explained in `VISION.md`. Do not restore either without
reading that section first.

---

## Archinity.Chronicle — designed, not built

### Gating: use research, not timers

The key finding of session 3, and it replaces the earlier day-gate plan.

`QuestChainExtension.requiredResearch` takes **any single `ResearchProjectDef`**,
and VEF postfixes `ResearchManager.FinishProject` to reschedule — so a quest
fires **the instant that research completes**. No reload lag.

So pace beats on *research*, not clocks: beat 1 of an era on `TB_<Era>Theory`,
later beats on specific mid- and late-tier projects. Pacing then tracks how fast
Conrad actually plays, with no dead air either way. It also buys precision — the
Descent Engine beat gates on `Xenogermination` itself, so the fiction and the
mechanism become the same thing.

Constraints, all verified in `GameComponent_QuestChains.TryScheduleQuest`:

- `conditionSucceedQuests` and `conditionMinDaysSinceStart` are **mutually
  exclusive** — the succeed branch returns early. You cannot say "after beat 4
  *and* after day 200."
- `requiredResearch` combines with everything, and is checked first.
- `ticksSinceSucceed` measures from **completion**, not acceptance. There is no
  "days since received" field. This is exactly the dead-time problem Conrad
  raised, and gating on research sidesteps it entirely.
- Chain quests call `CreateQuest()` directly, **bypassing the storyteller**, so
  `rootMinPoints` and `rootMinProgressScore` do nothing on them.

### The spine — ~16 beats over ~700 days

Roughly one every 40 days, which is quiet by RimWorld standards. Most beats give
a bundle: an augment plus a vector, or two small augments together.

| Era | Beats | Gives |
|---|---|---|
| — | Scenario text | Simulation, gift, a path forward |
| Neolithic | **You find the Altar** | The altar. Obviously important, obviously wants blood, nothing explains it. |
| Neolithic | **First vector** | The dots connect. You go home and pay. |
| Medieval | 4 beats | Chorus Stones, Recovery Shroud, Reliquary Sump, **Rendering Vat + Galvanic Coil together**, vectors |
| Industrial | 4 beats | Rapid Infusion Pump, Rejection Buffer, **the Descent Engine**, vectors |
| Spacer | 3 beats | Prism, `VacuumResistance_Total`, the Glitterites revealed as the gate |
| Ultra | 2 beats | Attenuator, Redirector, Harmonizer, the archon-gear gene |
| Archotech | 1 beat | Pathing Array, `VRE_Transcendent` |

The vat and the coil **must arrive together**. Neither does anything alone — the
vat makes charge, the coil makes charge go further. An earlier draft split them
across eras and the vat did nothing for 200 days; Conrad caught it.

The vat produces **altar charge, not electricity**. That was the fix to "the
moment I get a windmill it's useless" — no generator can substitute for it.

### Facility reskins

VQE Ancients' twelve facilities get repointed by `AltarFacilityExtension`
(charge discount, duration, outcome bonus, category bias, extra options) rather
than rebuilt. The altar already declares all twelve as `linkableFacilities`.

Several stack natively — 10 neurostabilizers, 6 recovery arrays, 9 pumps, 5
buffer coils — so mid-era beats can award *more of the same building* and the
effect escalates with no new defs. The single-copy ones are the real milestones.

### Not built: the lottery

Named vectors work end to end. The archite-capsule path — roll a tier band, offer
four options — needs a **selection window**, and a custom UI is a player command
Multiplayer has to sync. That is the one genuinely desync-prone part of this
design, and it cannot be verified without running the game.

Everything it needs already exists: tiers, categories, `biasCategory` /
`biasStrength`, `extraOptions`, `outcomeBonus`.

Design agreed with Conrad, for whoever builds it:

| Result | What happens |
|---|---|
| Critical failure | Capsule returned, blood spent, **the pawn** is comatose for days. The altar is never what breaks. |
| Poor | Four options, all weak — the best merely neutral |
| Standard | Four options, mixed |
| Strong | Four options, all worth having |
| Perfect | Four excellent options |

Vanilla `ArchiteCapsule` is the lottery ammo, **unchanged and unpatched** —
Conrad explicitly ruled out new capsule types. Capsules work from day one on the
founders, which is what stops them being useless for the first 400 days.

---

## The archoplate

Its stat block is deceptive, and the obvious buff is impossible.

`ArmorRatingBase` has `<maxValue>2</maxValue>`. Legendary quality is ×1.80, so
legendary cataphract is 1.20 × 1.80 = 2.16 → **clamped to 2.00**. It already
sits on the ceiling. Nothing can be 20% better on sharp.

Current archoplate: Sharp 1.15, Blunt 0.60, Heat 0.86, Mass 10. Its real power is
`CompProperties_ShieldField` — `activeAlways`, radius 2, 5.6 energy — which does
not block the wearer shooting and covers nearby allies.

Agreed plan, **not yet applied**: Sharp to 2.00, Blunt ~1.20, Heat ~1.50, and put
the god-tier into the shield (energy 5.6 → ~20, roughly double recharge). Keep
`disarmedByEmpForTicks` — the EMP weakness is the counterplay, and
`VQEA_Electromagnetized` is the answer to it.

`thingSetMakerTags: VREA_None` means it never generates as loot. It has to be
placed deliberately.

---

## Deferred, not forgotten

- **Diplomacy / ideology pass** across the faction map. Needs both new factions to
  exist first — do it after fresh worldgen.
- **Orbit subdivisions 6 → 7** — only after worldgen time at 6 is known.
- **More Realistic Research era curve.** Wants playtest data. Note
  `audit_research.py` currently reports **36 deadlock risks**; these predate the
  altar work and have not been investigated.
- **Faction art** — both icons are generated placeholders.
- **Archon ruin loot tables and set dressing.** ~230 candidates catalogued in
  [`archon-asset-inventory.md`](archon-asset-inventory.md). Caveat: it was built
  by scanning the workshop folder, not the load order, so anything from Medieval
  Overhaul depends on decision 1 above.
- **Lore readables.** Almost none exist in the load order. Cheapest fix is
  authoring our own `Book`-parented defs.

## Planned: the content and presentation pass

**Conrad asked for this to be written down so it is not forgotten. It is
explicitly a LATER review** — it should happen once the full content set is
known and settled, not before. Nothing here blocks anything.

He loaded a game and found the modded content is not curated: *"there's a lot
of little odds and ends I can build randomly, and some things that show up in
the architect menu (like disassemble chemfuel pipes and paste pipes) as
standalones that clearly smell."*

Four related jobs, all sweeping the whole modded content set:

**1. Architect menu discipline.** Nothing should be visible before it is
appropriate. The observed symptoms are orphaned or oddly-scoped entries —
pipe-disassembly designators and similar appearing as top-level standalones
rather than nested where they belong. The likely levers are `designationCategory`,
`researchPrerequisites` and `menuHidden` on the offending `ThingDef`s, plus
whichever mod is contributing the pipe designators (PipeSystem via VEF is the
first place to look). **Diagnose before patching** — the specific defs behind
those entries have not been identified yet.

**2. Research placement.** Confirm every modded item unlocks at the tier we
actually want, not wherever its author happened to put it. This overlaps the
Medieval route decision and the More Realistic Research curve, and should
probably wait until both have landed.

**3. Art and model consistency.** Compare all Neolithic and Medieval mods
against each other and overhaul textures where they clash. Conrad wants the
models used for every item to be deliberate choices rather than defaults. This
is the largest and least mechanical part of the job.

**4. Cull the odds and ends.** Buildables that exist only because a mod happened
to ship them, and which nobody will ever want, should not be in the menu at all.

Sequencing note: do this **after** the Medieval route is chosen, because Route A
(enable Medieval Overhaul and strip it) would change both the art baseline and
the menu contents substantially. Doing the pass first would mean doing it twice.

## Explicitly decided against

- **Two machines.** VQE's injector as a rival path to the altar. Killed — one
  machine, one philosophy.
- **New capsule types.** Vanilla `ArchiteCapsule` only.
- **Vanilla Psycasts Expanded.** Conrad does not like psycasts. This leaves
  VRE-Archon's `VREA_Transcendent` psycaster path dormant; that is accepted, not
  an oversight.
- **The recipient ever dying at the altar.** Non-negotiable.
- Relocating Ushanka's glittertech sites to orbit — KCSG cannot floor a space map
  (34–100% of layout tiles are `.`, and `GenStep_Space` makes unwritten cells
  impassable vacuum).
- Patching Odyssey's `OpportunitySite_MechanoidPlatform` "Insect" check — it looks
  like a bug but `Insect` has `requiredCountAtGameStart: 1`, so it always passes.
- `naturalEnemy` for the Glitterites — `permanentEnemy` locks goodwill at −100;
  `naturalEnemy` only offsets by −130 and could soften.

---

## How the orbital gate works

The least obvious part of the earlier work. Read before touching it.

Ushanka's glittertech research is gated only by craftable vanilla benches, and it
gates some *building* on `USH_Glitterheart` — but hearts came from surface sites,
so nothing required going to orbit.

**Do not reinvent the heart.** An earlier session created a duplicate and it was
deleted. `USH_Glitterheart` is the real item: uncraftable, sell-only,
`stackLimit 3`, already a crafting ingredient.

All in `Archinity.Glitterites`:

1. **Research gate** — 10 of 18 projects require hearts to reverse-engineer.
   Fabrication 3, seven production/deep 2, two entry 1. Telepad, teeth, overclock,
   skin and the four skilltrainers are deliberately free.
2. **Orbital garrisons** — repoints `factionDef` on `Opportunity_AbandonedPlatform`
   and `Opportunity_OrbitalWreck` to the Glitterites. One field each. No new
   locations, no new quests — Odyssey's `OrbitalScanner` was already the discovery
   loop.
3. **Chunks in orbit** — a `USH_GlittershipChunk` prefab on those platforms. 20000
   work, 3 hearts on deconstruct. The richest single source.
4. **Loose drops** — hearts added to `Reward_GravshipUpgrade` at weights 3/5/2
   (~30/50/20 for 1/2/3). Additive; Odyssey and VGE progression untouched.
5. **Earth closed off** — glittercrate heart roll set to weight 0, and the one
   layout row placing a surface chunk rewritten to slag.

**Economy.** ~25 hearts total demand, ~3–4 per orbital raid, so roughly 7 raids —
slightly generous against the "closer to 10" target. To tighten it, lower the
weight-2 and weight-3 options in `Ascension_OrbitalLoot.xml` first, never the
chunk. The chunk is what makes a raid feel like a haul.

### Traps found the hard way here

- `Opportunity_OrbitalWreck` uses `GenStep_OrbitalWreck` with `<prefabs>`
  (weights). `Opportunity_AbandonedPlatform` uses `GenStep_OrbitalPlatform` with
  `<exteriorPrefabs>` (count ranges). **Different classes, different field
  names.** Do not assume symmetry.
- `USH_GlittershipChunk_North` is not a def — KCSG generates rotation variants at
  runtime, so only the base symbol is patchable.

---

## Tooling

```bash
python tools/check_refs.py          # parses all XML, then validates cross-mod defNames
python tools/audit_research.py      # research gated on unobtainable items
python tools/check_availability.py  # planned MRR materials have 2+ sources
python tools/survey_archite.py      # regenerate the archite gene pool table
python tools/make_faction_icons.py  # placeholder faction icons
./setup.ps1 -SyncConfig             # junction mods into RimWorld + sync config
```

`setup.ps1` auto-discovers every `Archinity.*` folder, so new mods need no
registration.

Building the assembly:

```bash
cd Archinity.Altar/Source && dotnet build
```

Output goes straight to `Archinity.Altar/Assemblies/`. The built `.dll` **is
committed** so the other player can sync and play without a .NET SDK installed.
Game and Harmony assemblies are referenced in place, never copied — shipping a
stale duplicate of the game's own code is the classic way to break on an update.

`check_refs.py` now parses every shipped XML **before** checking names. A file
that fails to parse is dropped silently by RimWorld, and `check_refs` used to
pass on it happily. `ilspycmd` is pinned to `8.2.0.7535`; the latest is broken on
.NET 8.

### Multiplayer requirements

Both players need identical mods, identical load order (`config/ModsConfig.xml`)
**and identical mod settings** (`config/ModSettings/`). The third is the one
people miss — TechBlock, Ignorance Is Bliss and Medieval Overhaul are all
settings-driven.

Conrad intends to set IIB to `NumTechsAhead = 0`, `NumTechsBehind = 1`. If he
does, **re-snapshot** into `config/ModSettings/` — the current snapshot predates
that change.

`ModsConfig.xml` lists `ludeon.rimworld.odyssey` twice. Harmless in practice, but
worth cleaning up given configs must match byte-for-byte.

---

## Working style that works

- **Verify against decompiled source, never memory or the wiki.** Session 3
  killed four confident assumptions this way: that a gene could be granted by an
  XML quest node, that an endogene/xenogene split would stop reimplantation from
  copying genes, that `biostatMet` could rank archite genes, and that armour
  could be pushed past legendary cataphract on sharp.
- **Run all four checks before claiming def work is done.** `check_refs.py` alone
  passes on files that do not parse and on fields that do not exist.
- **Prefer additive patches.** `PatchOperationAdd` onto an options list beats
  `PatchOperationReplace` on someone else's reward.
- **Conrad checks the work and finds real errors** by asking why something seems
  too convenient or too neat. The duplicated glitterheart, the biobattery that
  did nothing, and the capsule dead zone all surfaced that way. He would rather
  have a correction than a confident answer.
