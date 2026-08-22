# 01 — Mod set & load order

**Blocks every other system.** Every brief authors defs against a def database whose
contents depend on what is enabled here.

## What this system must do

Produce a final, frozen mod list and load order that both players run byte-for-byte
identically, containing exactly the content the design needs and nothing that dilutes it.

## Current state

62 entries in `config/ModsConfig.xml` (v1.6.4871). Full list in
`scratch/recon-inventory-and-tech.md`.

**Four defects, all confirmed:**

1. **`archinity.altar` is not in the load order.** It has never loaded in game. Everything
   in `QUESTLINE.md` depends on it.
2. **Medieval Overhaul is not installed.** No `DankPyon.*` entry exists. "Route A: enable
   MO and strip it" was decided in session 4 and never executed.
3. **VFE Tribals is not installed.** Downloaded at workshop `3079786283`, absent from
   `ModsConfig.xml`.
4. **All four DLCs are listed twice.** Harmless in play, but configs must match byte-for-byte
   between players — normalise it once and re-snapshot.

## Decisions this brief is blocked on

### D1 — Is VFE Tribals in?

`VISION.md` rejects it. `Player Progression Ideology.txt` opens by calling it "the perfect
start" and builds the entire Neolithic experience on its research-by-gathering, its work-tag
unlocks and its cornerstone system. **Both documents are live in the docs folder.**

Verified facts to decide on:

- It delivers what the Ideology describes: `TribalResearchProjectDef` with `unlocksWorkTypes`
  / `unlocksWorkTags` / `unlocksDesignators` — research that grants *jobs and gizmos*, which
  is the specific thing the Ideology praises.
- **The tribal mode ends itself.** No work needed. See `sys/02`.
- **Cornerstones already chain to TechBlock tier-ups.** Free, XML-only.
- It has **zero mod settings** — no multiplayer settings-sync risk.
- One real conflict with TechBlock (premature advancement ritual) — see `sys/02`.

The technical objections that might have motivated VISION's rejection do not survive
contact with the source. If it is rejected it should be on taste, not mechanics.

### D2 — Is Medieval Overhaul in?

Without it the Medieval era is nearly empty: VFE Classical contributes **zero** Medieval
research projects (all 18 are Neolithic — `VISION.md` is wrong about this), and VFE
Medieval 2 alone does not carry an era.

With it: ~39,900 research points, the full cooking/flour economy, 60 buildings, 4 visible
Noble House factions, `MedievalSiege`, mine shaft, crane, carrier birds, beekeeping, brewing.

Cost: it also brings everything `Player Progression Ideology.txt` explicitly rejects —
the wood→plank→board chain, paper/cartography, textile spinning + linen, Mithril, ~30 extra
plants, ingredient bloat. Route A means enabling it and stripping those with
`PatchOperationRemove`. See `sys/04` for the kill ledger.

**Note:** `metalChain` must be OFF (a setting, not a patch). `woodChain` has never been
ruled on and should be decided with D2.

## Work items

- [ ] **Add `archinity.altar` to `ModsConfig.xml`.** Highest-value single line in the project.
- [ ] Remove duplicate DLC entries; re-snapshot config.
- [ ] **Turn TechBlock `randomInsights` off.** Frame-based `Rand` = guaranteed MP desync,
      currently on at rate 1. Copy the settings file, never re-click — `RecalculateBlockValues`
      runs live from `DoSettingsWindowContents`.
- [ ] Resolve D1. If in: add `3079786283`, load before TechBlock.
- [ ] Resolve D2. If in: add MO + confirm Processor Framework (already subscribed), set
      `metalChain` off, rule on `woodChain`, then execute the `sys/04` strip.
- [ ] Apply the rest of the settings table: IIB `NumTechsAhead=0` / `NumTechsBehind=1`,
      `useHighestResearched` on, `EmpireIsAlwaysEligible` false, `ChangeQuests` true.
      Faction Customizer's settings file is missing.
- [ ] Re-snapshot `config/ModSettings/` after every settings change.
- [ ] Re-run all four `CLAUDE.md` checks with the final set (~2,930 new defs if MO lands).
- [ ] Run the 6-item MP desync checklist. Dark Forest tile first — reported hard failure,
      possibly one `PatchOperationRemove` away.

## Undecided, lower stakes

Rule on these when convenient; none block downstream work.

- **RimFantasy** — enable minus the 4 temperature pylons + `RF_ArcaneTemperatureRegulation`?
  `RF_FrostPylon` is -22 heat/s at no power cost and would kill Electricity's value.
- **Faction - Elves** — subscribed, unassessed. Test against the no-race-bleeding principle.
- **Dark Ages: Medieval Tools** — recommended skip. Zero research points; MO ships better
  versions of its 3 best tools; 4 of 5 buildings are stacking tool-cabinet clones.
- **Anomaly DLC** — unpurchased. Only "simulation/void" content is reachable without it.
- **Neolithic storage** — author one (`sbzCrateBase` template, workshop `3416243474`) vs
  subscribe "Adaptive Primitive Storage".
- **Two grape plants / two wine chains** if MO lands (`DankPyon_Plant_Grape` vs
  `VFEM2_Plant_Grape`) — no compat patch exists anywhere.

## Load order rules that matter

- `fridgebaron.techblock` must load **after** all content mods and **before** `archinity.*`.
  `BlockTechs()` iterates every `ResearchProjectDef` at startup and must see final
  `techLevel` values.
- `sae.ResearchMod` (More Realistic Research) auto-generates requirements at startup for
  every project not explicitly listed — see `sys/02`.
- `archinity.altar` needs `brrainz.harmony` + Biotech; loads after VQE-Ancients,
  VRE-Archon, VFE Core.
