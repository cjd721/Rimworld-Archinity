# Archinity — system map

The spine. Every system we must build, in dependency order, with who can start now
and what is blocked. One row per system; the detail lives in `docs/sys/`.

**How to use this:** hand a session one row. It reads this file's conventions section,
then its one brief, then starts. It should not need to read any other brief.

**Exception:** `sys/06` and `sys/07` also require `QUESTLINE.md`. They depend on its
vocabulary — beats, acts, the thirteen buildings, the power curve — and are not startable
without it.

Last updated 2026-08-22.

---

## Status of the project, honestly

**Medieval Overhaul and VFE Tribals are now enabled** (Conrad enabled both and booted a
game; `config/ModsConfig.xml` in the repo predates that and must be re-snapshotted after
the game is closed).

The content design is still ahead of the foundation. This map exists to put the foundation
in dependency order.

Last boot: **one config error**, ours —

> `Config error in Archinity_GL_Technician: Cheapest weapon with one of my weaponTags costs
> 1010 but weaponMoney min is 400, so could end up weaponless.`

Fix in `sys/05`. It is also a clean demonstration of how gear selection actually works:
tags intersected with a money ceiling, no techLevel anywhere.

---

## The systems

| # | System | Brief | Blocked by | State |
|---|---|---|---|---|
| 01 | **Mod set & load order** | `sys/01-modset.md` | Conrad decisions D1, D2 | **Blocking everything** |
| 02 | **Research tree** | `sys/02-research.md` | 01 | Designed, not built |
| 03 | **Benches & production** | `sys/03-benches.md` | 01, 02 | Mechanic proven, unbuilt |
| 04 | **Items & resources** | `sys/04-items.md` | 01 | Policy set, ledger unbuilt |
| 05 | **Factions & world** | `sys/05-factions.md` | 01 | Partly built, never worldgen'd |
| 06 | **Quests & rewards** | `sys/06-quests.md` | 05 | Mechanism known, unbuilt |
| 07 | **Balance** | `sys/07-balance.md` | 02, 03, 04 | Last pass, do not start early |
| — | **The Altar / Chronicle** | `QUESTLINE.md` | 06 | Best-documented system we have |

**01 blocks everything.** Every other brief authors defs against a def database whose
contents depend on which mods are enabled. Building 02–07 before 01 is settled means
authoring against a database that does not exist yet.

02 and 04 can run in parallel once 01 lands. 05 and 06 can run in parallel with those.
07 runs last, by construction.

---

## Decisions only Conrad can make

These are blocking. Nothing downstream is safe to build until they land.

| ID | Decision | Why it blocks | Options |
|---|---|---|---|
| ~~D1~~ | ~~Is VFE Tribals in?~~ | — | **RESOLVED: in.** Its own tech-advancement ritual is disabled; TechBlock is the sole advancement lever. **Note: it is not actually enabled in the live `ModsConfig.xml` — see `INVENTORY.md`. Conrad reconfirmed 2026-08-22 that it should be; switching it on is an open action, not an open decision.** |
| ~~D2~~ | ~~Is Medieval Overhaul in?~~ | — | **RESOLVED: in, and gutted.** Enabled for the assets; the systems in `sys/04`'s kill list get stripped. |
| **D3** | **Founder access model** | Blocks the lottery, which blocks beat placement. | Two altars / one altar split by ammunition — `QUESTLINE.md` §3 |
| **D4** | **Capsule timing** | Same. | Neolithic / Industrial — `QUESTLINE.md` §4 |
| **D5** | **Can the player decline all four lottery options?** | Decides whether the bad-gene band has teeth. | `QUESTLINE.md` §5 |

D1 and D2 are resolved, which unblocks 02–07. D3–D5 are content decisions already framed
in `QUESTLINE.md` and are not repeated in the `sys/` briefs.

### Settled this session — do not reopen

- **TechBlock `randomInsights` is off.** Not just for the desync — Conrad does not want RNG
  research progress at all. Disable the feature outright.
- **VFE Tribals' tech-advancement ritual is disabled.** TechBlock is the only advancement
  lever. This also resolves the premature-advancement conflict between the two mods.
- **Recipe gating on a linked facility is acceptable via research** — you research the
  augment, which unlocks a band of recipes, and keep researching more advanced ones until
  the next augment. A stricter mechanism also exists (`RecipeWorker`, `sys/03`) and is
  worth using where it fits, but nothing depends on it.
- **QoL items need a *guaranteed* route, not a *quest* route.** Luck into one early from
  trade or loot and that is fine. What must never happen is a required item with no
  reliable way to get it.

### Decisions a session may make on its own

Consequential but not Conrad-only. Make the call, record it in the brief, move on.

| Decision | Brief | Note |
|---|---|---|
| `requiredPointsMedieval` 0.75 (~88 bench days) vs 1.0 (~117) | `sys/02`, `sys/07` | Changes every research cost. Decide during the balance pass, not before. |
| Stale-bill behaviour when an augment is removed | `sys/03` | Sweep on `Notify_LinkRemoved`, or accept that existing bills keep running. Accepting is defensible. |
| VFET × TechBlock premature advancement ritual | `sys/02` | Accept, or patch the worker. |

---

## Verified mechanics ledger

Facts confirmed against decompiled 1.6 source this session. Do not re-derive these.
Full detail and source paths in `scratch/recon-*.md`.

### Answers to the questions that opened this session

- **Do we need a custom storyteller?** **No.** Chain quests call `CreateQuest()` and bypass
  the storyteller entirely. A storyteller would only suppress *competing* noise, and
  `rootSelectionWeight` patches do that more cheaply. Not worth a second assembly.
- **Can we stop the tribal research mode when we're done with it?** **It stops itself.**
  Gathering-research is not a mode — it is the `Intellectual` work tag being disabled until
  `VFET_Culture` completes, plus the bench being gated behind `ComplexFurniture`. The ritual
  hard-hides itself above Neolithic. Author later projects normally and they are bench-only.
- **Can we keep cornerstones for the whole game?** **Already works, free.** VFET awards
  cornerstone points on *any* faction techLevel increase; TechBlock writes faction techLevel
  on tier-up. They already connect. Add `EraAdvancementDef` entries in XML (Archotech is
  missing one).
- **Can an augment building expand a core bench's recipes?** **Yes, ~15 lines of C#, no
  Harmony.** `RecipeDef.workerClass` is XML-settable and `RecipeWorker.AvailableOnNow(thing)`
  receives the worktable. See `sys/03`.
- **Can we force factions into every world?** **Yes, but not via the field the docs name.**
  `requiredCountAtGameStart` is **dead code in 1.6**. Use `startingCountAtWorldCreation` —
  and note the roster must be final **before world creation**, because adding a faction to
  an existing save does nothing, silently.
- **Can the player reliably get a named item from a faction?** **Yes, by all three routes.**
  Trade: `StockGenerator_SingleDef` with `countRange` min ≥ 1 (a uniform draw, not a chance,
  and no techLevel filter). Raid: `PawnKindDef.fixedInventory`, which runs unconditionally.
  Quest: `QuestNode_SetItemStashContents`. See `sys/05`.
- **Does faction `techLevel` make a faction feel era-appropriate?** **No.** Vanilla achieves
  it by hand-authoring `weaponTags` on every PawnKindDef — there is no systemic filter, and
  no `Faction.def.techLevel` vs `ThingDef.techLevel` check exists anywhere in the 1.6 gear
  path. Proof: Core's `Tribal_ChiefMelee` carries `MedievalMeleeAdvanced`, so a Medieval
  longsword spawns on a Neolithic pawn in the base game. Era-appropriate factions are an
  authoring job on `PawnKindDef`s and `TraderKindDef`s — see `sys/05` for the 7-point
  minimum set.
- **Does Ignorance Is Bliss guarantee era-appropriate raids?** **Partly — it gates which
  *factions* can raid, never what they *carry*.** The two protections are complementary and
  we need both.
- **Can research require a specific item?** **Yes**, via More Realistic Research — but read
  the trap below.

### Traps — silent, currently live

1. **TechBlock `randomInsights` is a guaranteed multiplayer desync and is currently ON.**
   `TechBlock_Component.GameComponentUpdate()` is *frame-based, not tick-based*, and calls
   `Rand`-driven `AddRandomProgress()`. Our snapshot has rate = 1.
   **Decided: disable the feature entirely.** No RNG research progress, desync aside.
2. **Research Mod auto-generates material requirements, by techLevel, for every research
   project not explicitly listed.** Every Archinity project will silently acquire gates we
   did not author. Almost certainly the source of the recorded deadlocks. Declare an empty
   `ManualAnalysisDef` for anything we do not want gated.
3. ~~VFET's advancement ritual can fire prematurely against TechBlock's prerequisites.~~
   **Resolved: VFET's advancement ritual is disabled outright.** TechBlock is the sole
   advancement lever. Cornerstones still work — they key off any faction techLevel
   increase, which TechBlock provides.
4. **Deleting a `ResearchProjectDef` strips the prerequisite off its dependants**, leaving
   them buildable with *no* research. Neuter referencing defs first, delete research last.
5. **`--` inside an XML comment silently drops the entire file.**
6. **PatchOperations run before `ParentName` inheritance resolves** and apply to the whole
   merged database. Match on `@ParentName`.
7. **`CompProperties_Facility.statFactors` is a silent no-op.** Offsets only.
8. **Adding a FactionDef to an already-generated world does nothing** — silent, no error,
   no reconcile path. The faction roster must be final before world creation.
9. **Trader stock is destroyed when you defeat a settlement.** You cannot raid a base for
   the things its trader was selling.
10. **A RimWorld year is 60 days.**

### Naming

The item-gating mod is `sae.ResearchMod` — **More Realistic Research**, workshop
`3771646847`. Call it **Research Mod**. Older docs call it "MRR" / "More Research
Requirements"; that mod is a different thing and is not installed, but the plans written
against the name still hold, because its `experimental` / `reverseEngineering` /
`theoretical` material levers are exactly the mechanism those plans wanted.

---

## Unresolved contradiction — resolve before working `sys/05`

**Has anything been through worldgen?** The corpus disagrees with itself.

- `scratch/recon-inventory-and-tech.md` and this file: Drifters and Glitterites "load clean,
  never been through worldgen."
- `scratch/recon-doc-extract.md`: worldgen was run and "Glitterites and Drifters both
  rendered correctly."

Both were produced this session from different sources. `sys/05` treats a
`layerWhitelist` / `layerBlacklist` misconfiguration as the likely reason the two orbit-only
factions have never generated — **that investigation is wasted if the second claim is
right.** Confirm which is true before spending time on it. Conrad can answer this in one
sentence.

## Confidence markers

Not all claims in these briefs were verified this session, and the briefs do not currently
distinguish them inline. Two tiers:

- **Verified this session** — anything traceable to `scratch/recon-factions.md`,
  `recon-augment-bench-feasibility.md`, `recon-tribal-techblock.md`, or the `[V]` entries in
  `recon-inventory-and-tech.md`. These carry code excerpts and source paths. Trust them.
- **Carried over** — anything traceable only to `scratch/recon-doc-extract.md`. That file is
  a mining of `HANDOFF.md` / `WORKLIST.md` / `DECISION-medieval-route.md`, which are stale
  and recommended for deletion. **Re-verify before acting.** Specifically includes: the
  "36 deadlocks" figure, the `VFEM2_LeatherBoilpot` and `PlateArmor` specifics, and the
  missing-research-gate list in `sys/02`.

## Conventions for every brief

- XML defs by default. **One assembly only** (`Archinity.Altar`). Additions to it must be
  deterministic across clients — see `CLAUDE.md`.
- Run all four checks in `CLAUDE.md` before claiming def work is done.
- Verify against decompiled source, not memory and not the wiki. `ilspycmd` is installed.
- Record new verified facts in `docs/technical-findings.md`, not in a brief.
- Multiplayer: mods, load order **and mod settings** must match byte-for-byte.

---

## Reference documents

| File | What it is |
|---|---|
| `INVENTORY.md` | Every item and research project in the live mod set, bucketed keep / change / fence / cut. Built by `tools/inventory.py`. Also records three defects in this map's own claims. |
| `PROGRESSION-MAP.md` | **The target design for the Neolithic and Medieval eras.** Narrative → capabilities → research nodes, across five milestones. Supersedes `RESEARCH-NEO-MED.md`. Read this before authoring anything in 02, 03, 04 or 07. |
| `RESEARCH-NEO-MED.md` | **Superseded — do not act on it.** Built on a wrong premise (it moved VFE Classical up an era and cut to an arithmetic budget). Kept for its per-project cost and dependency data, which is accurate; its verdicts are not. See `PROGRESSION-MAP.md` §9. |
| `QUESTLINE.md` | The Chronicle — beats, vectors, lottery, the 13 buildings. Current and good. |
| `Player Progression Ideology.txt` | Conrad's design philosophy for Neolithic->Medieval. The source of truth for *intent* on progression. Verbose but load-bearing. |
| `technical-findings.md` | Verified fact base. Append here. |
| `archon-asset-inventory.md` | Asset catalogue. Reference data. |
| `archite-gene-pool.md` | Gene tiering. Reference data. |
| `scratch/recon-*.md` | This session's raw research. Source paths and code excerpts. |

### Deleted

`HANDOFF.md`, `WORKLIST.md` and `DECISION-medieval-route.md` were mined into
`scratch/recon-doc-extract.md` and the briefs, then deleted. They are recoverable from
git history at commit `56b5c44` if anything turns out to be missing.

`VISION.md` was corrected rather than deleted — it holds intent unrecoverable from code.
Fixed: the Medieval Overhaul and VFE Tribals rejections are reversed with reasons, the
false "VFE Classical carries the Medieval era" claim is gone, and the founder-marker
section now names the custom gene instead of the rejected `Deathrest`-absence idea.
