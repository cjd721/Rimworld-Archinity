# Handoff — read this first

State of the Archinity project as of the end of session 1.

**Read [`technical-findings.md`](technical-findings.md) before doing anything.**
It holds every fact verified against decompiled source across ~600k tokens of
research. Re-deriving it is expensive; trusting the wiki instead will be wrong.

---

## What this is

A suite of RimWorld 1.6 mods for one long co-op playthrough. Neolithic start,
slow climb through every tech era, endgame in orbit, ending in transcendence
via the `VRE_Transcendent` gene.

Two players (Conrad and a friend) on the **Multiplayer** mod. Everything is
**XML defs only** — no C#, no Harmony. That is a deliberate constraint: def-only
mods carry no simulation code and are inherently multiplayer-safe. Do not break
it without an explicit decision.

---

## Build status

| Mod | Status | Verified how |
|---|---|---|
| `Archinity.Origins` | Built | Loaded in game; scenario appears, 2 archonians + 2 baseliners confirmed on the pawn screen |
| `Archinity.Pacing` | Built | Loads clean; all four xpaths resolved |
| `Archinity.Drifters` | Built | Loads clean. **Never been through worldgen.** |
| `Archinity.Glitterites` | Built | Loads clean. **Never been through worldgen.** |
| `Archinity.Chronicle` | **Not started** | — |

### FIRST TASK: fresh-world verification

Drifters and Glitterites have never been placed by worldgen. Generate a new
world and confirm:

1. Both factions appear at world creation
2. Their settlements generate **in orbit**, not on the surface
3. Names read correctly (`Longwake Drydock`, `Threshold-17 Overlook`)
4. Orbit is visibly denser than vanilla (subdivisions were raised 5→6)
5. Note worldgen duration — decides whether 6→7 is worth trying

The view-orbit button only exists **in game**, not during world creation
(`GetGizmos` bails on `ProgramState.Entry`). In colony → world map → hotkey
**`B`**.

---

## What remains: Archinity.Chronicle

The quest chain. Everything it needs is verified as XML-expressible.

### The spine

```
sanguophage origin  →  archite injection loop  →  glitterheart hunt in orbit
                                               →  Archon contact → transcendence
```

### Verified mechanisms to build on

| Need | Mechanism |
|---|---|
| Gate a quest chain on tech tier | `VEF.Storyteller.QuestChainExtension` → `requiredResearch` → TechBlock's `TB_<Era>Theory` defs |
| Fixed, guaranteed rewards | `QuestNode_SetItemStashContents` (shipped precedent: `Royalty/Script_Intro_Deserter.xml:90-96`) |
| Threats attached to the same site | `Util_Raid` node, see directly above that precedent |
| Reserve a gene from the random pool | `InjectionBlacklistDef.blacklistedGenes` — already used for `VRE_Transcendent` |

### Design decisions already made

- **Archons** appear only when a quest summons them. 1–2 encounters in a whole
  playthrough. `permanentEnemy` stays true; "joining them" means acquiring
  `VRE_Transcendent`, not an alliance.
- **`VRE_Transcendent` is blacklisted** from random archite injection, so it can
  only arrive through the Chronicle chain.
- **Archite capsules and the crated Archogen Injector never decay** — the design
  of finding them in the Neolithic and using them in the Industrial era works
  with no special handling. Genepacks do NOT survive (20 days); never use them
  as an early reward.
- **Time:** a RimWorld year is **60 days**. The whole campaign fits under ~600
  days. See the era table in technical-findings.

### Open question for Conrad

Whether to strip the starting xenotype down. `Archinity_ArchonianSanguophage`
currently has all 33 genes including 13 archite ones. Splitting ~11 out and
delivering them through the Chronicle chain was proposed and **not decided**.
Every archite gene is annotated `<!-- [ARCHITE] -->` in the def, so the split is
mechanical if he says yes.

---

## Deferred, not forgotten

- **Diplomacy / ideology pass** across the whole faction map. Conrad flagged it
  at world creation. Needs both new factions to exist first — do it after
  fresh-world verification.
- **Orbit subdivisions 6 → 7** — only after worldgen time at 6 is known.
- **Blood-fuelled Archogen Injector** — needs ~10 lines of Harmony. Would be the
  only assembly in the project. Optional, deferred, Conrad's call. See
  technical-findings for why XML cannot do it.
- **More Realistic Research era curve** — general research pacing beyond the
  glittertech gate. Wants real playtest data.
- **Faction art** — both faction icons are generated placeholders
  (`tools/make_faction_icons.py`). Fine to ship, nice to replace.

### Explicitly decided AGAINST

- Relocating Ushanka's glittertech sites to orbit. KCSG cannot floor a space
  map — 34-100% of every layout tile is `.` (no terrain), and `GenStep_Space`
  makes every unwritten cell impassable vacuum. Would need ~1700 hand-authored
  cells plus a temperature fix. Solved differently — see below.
- Patching Odyssey's `OpportunitySite_MechanoidPlatform` "Insect" check. It
  looks like a bug but `Insect` has `requiredCountAtGameStart: 1`, so the check
  always passes. Harmless leftover.
- `naturalEnemy` for the Glitterites. `permanentEnemy` locks max goodwill at
  −100 permanently; `naturalEnemy` only offsets by −130 and could soften.

---

## How the orbital gate works (built this session)

Worth understanding because it is the least obvious part of the design.

**The problem:** Ushanka's glittertech tree is gated only by craftable vanilla
benches (`HiTechResearchBench` + `MultiAnalyzer`, plus `USH_ResearchProbe` at
100 steel / 10 plasteel / 1 spacer component). You could ignore every glitter
site in the game and still research all of it. Space had no purpose.

**The fix**, in `Archinity.Glitterites`:

1. `Archinity_Glitterheart` — a ThingDef that is uncraftable, `tradeability
   None`, and never decays.
2. It is added to Odyssey's `Reward_GravshipUpgrade` options list — an
   **additive** patch, so `FuelOptimizer` and `GravshipShieldGenerator` rewards
   are untouched. Two orbital quests draw from that maker
   (`OrbitalFugitivePlatform`, orbital survey sites). Also added to the
   Glitterite raid loot table.
3. 18 `ResearchMakesSense.ManualAnalysisDef` entries — one per glittertech
   project — each requiring glitterhearts to reverse-engineer.

Net: the glittertech tree cannot be finished without going to orbit, and
nothing was taken away from Odyssey or Vanilla Gravship Expanded.

**Untested.** Nobody has yet confirmed a glitterheart actually drops in game.
That is the second verification task after worldgen.

---

## Tooling

```bash
python tools/check_refs.py        # validate every cross-mod defName before launch
python tools/make_faction_icons.py # regenerate placeholder faction icons
./setup.ps1 -SyncConfig            # junction mods into RimWorld + sync config
```

`check_refs.py` harvests ~19,000 defNames from Core, all DLCs, all 68 workshop
mods and the repo, then verifies every cross-mod name Archinity relies on. It
has already caught three real bugs. **Run it before every launch.**

`ilspycmd` is installed for decompiling (`8.2.0.7535` — the latest is broken on
.NET 8). Full decompiles live in the session scratch dir, not the repo.

### Multiplayer requirements

Both players need identical mods, identical load order (`config/ModsConfig.xml`)
**and identical mod settings** (`config/ModSettings/`). The third is the one
people miss — Ignorance Is Bliss and TechBlock are entirely settings-driven with
no defs of their own.

Conrad intends to set IIB to `NumTechsAhead = 0`, `NumTechsBehind = 1`. If he
does, **re-snapshot the settings file into `config/ModSettings/`** — the current
snapshot predates that change.

---

## Working style that worked

- Verify against decompiled source, never memory or the wiki. Several confident
  assumptions turned out wrong: `Mech_Centipede` does not exist, RimWorld years
  are 60 days, Ignorance Is Bliss gates exactly one quest by name.
- Test xpaths with an lxml harness that merges the target mod's defs the way
  RimWorld does, before shipping a patch. This caught an xpath that would have
  rewritten `$siteFaction` from a variable reference into a literal.
- Prefer additive patches. `PatchOperationAdd` onto an options list beats
  `PatchOperationReplace` on someone else's reward.
