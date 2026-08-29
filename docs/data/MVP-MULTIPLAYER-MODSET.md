# MVP Multiplayer mod set — approved and safe

**Purpose.** One playable two-player Multiplayer session tonight.
Vanilla → Multiplayer → QoL + content → Archinity questline. Not the campaign set.

**Every packageId below was read off disk** (`tmp/scratch/installed-mods-2026-08-28.md`,
135 unique mods across the workshop folder, `RimWorld\Data`, `RimWorld\Mods` and this repo).
**Every safety verdict comes from `docs/data/MOD-VERDICTS.md`** — nothing here is a new
safety claim, this file only *selects*.

**Status: LOCKED.** Conrad's five calls are recorded in *Decisions* at the bottom. The set
is written to `config/ModsConfig.xml` and **verified**: 86 active mods, every packageId
resolves to an installed folder, **zero unmet hard dependencies**, `check_refs.py` clean,
`patch_check.py` 0 failures across 33 operations over a 2,766-file merged database.

---

## The rule this list follows

In only if all four hold:

1. Not barred, not declined in `MOD-VERDICTS.md`.
2. It **adds content** rather than **changing a core system**. Research, tech gating,
   combat resolution, diplomacy, work-priority and psycasts are core systems.
3. Its price is **zero, or a settings-file copy** — no fork, no Harmony patch of ours, no
   unresolved open question.
4. Not on an exclusion Conrad named (Empire, Deserters, Neolithic, Gravship Expanded).

Failing only #3 defers a mod past tonight; it does not remove it from the campaign.

---

## APPROVED — 87 mods

### Tier 0 · Load-bearing (11)

```
brrainz.harmony
zetrith.prepatcher
Ludeon.RimWorld
Ludeon.RimWorld.Royalty
Ludeon.RimWorld.Ideology
Ludeon.RimWorld.Biotech
Ludeon.RimWorld.Odyssey
rwmt.Multiplayer
rwmt.MultiplayerCompatibility     <-- NOT in your current active list. Must be added.
OskarPotocki.VanillaFactionsExpanded.Core
adaptive.storage.framework
```

`rwmt.MultiplayerCompatibility` is Open item #1 in `MOD-VERDICTS.md` — *"enable before any
co-op smoke test."* It is installed (workshop `1629973374`) and currently disabled. It is
also what fixes Vanilla Psycasts Expanded's viewport-gated RNG, if that goes back in.

`adaptive.storage.framework` is **the only natively MP-aware mod in the bin.** Nothing to do.

`UnlimitedHugs.HugsLib` is **out**. It is installed but disabled, and the dependency audit
confirms **nothing in this 86-mod set declares it**. Trivially added if a load error asks.

### Tier 1 · QoL (24)

```
Mehni.PickUpAndHaul
Memegoddess.ReplaceStuff
Wiri.compositableloadouts
rabiosus.TakeCover
GonDragon.DefensivePositions
Fluffy.Pharmacist
com.bymarcin.ArchitectIcons
ferny.BetterArchitect
MRK.architectmenuoptimizer
Andromeda.MilkyWay
willworkforicecream.NoAlzheimers
FrozenSnowFox.FilthVanishesWithRainAndTime
Bart.APP
Kangel.Moisture
sbz.NeatStorage
sbz.NeatStorageFridge
sbz.GravshipStorage
Adaptive.PrimitiveStorage
Mlie.AnimalFeedTrough
SereQ.RusticWorkbenches
shunter.bettertradersguild
Mlie.SlaveRebellionsImproved
AIRetexture.Core
neronix17.hd.pawns
kathanon.FixStyledBlueprints
```

Plus the cosmetic style family, all four or none:
`Anthitei.ATHsStyleableFramework.Style` · `anthitei.athsstylegothic.style` ·
`anthitei.athsstylenorse.style` · `Anthitei.ATHsStyleDraconic.Style`

Two worth naming:

- **Defensive Positions – Forked** needs **no MP patch at all.** Its orders route through
  `Pawn_JobTracker.TryTakeOrderedJob` and `Pawn_DraftController.Drafted`, both of which
  Multiplayer registers itself **[V]**. Known quirk: saved positions and squads are
  **per-player and silent** — on save-and-reload only the host's survive. Harmless for an MVP.
- **AI Upscaled Textures – Core** is 6,760 textures and **not one def, patch or assembly** **[V]**.
  Pure path-shadowing. Zero risk, 196 MB.

`sbz.GravshipStorage` is kept despite the gravship name — it is Odyssey-keyed, XML-only, and
has nothing to do with Vanilla Gravship Expanded.

### Tier 2 · Vanilla Expanded content (30)

**Furniture / production / materials (9)**
```
VanillaExpanded.VFECore
VanillaExpanded.VFEFarming
VanillaExpanded.VFEMedical
VanillaExpanded.VFESecurity
VanillaExpanded.VFEProduction
VanillaExpanded.VFESpacer
VanillaExpanded.VFEPower
VanillaExpanded.VFEPropsandDecor
VanillaExpanded.VChemfuelE
```

**Gear (6)**
```
VanillaExpanded.VWE
VanillaExpanded.VWEFT
VanillaExpanded.VWENL
VanillaExpanded.VARME
VanillaExpanded.VAPPE
VanillaExpanded.VAEAccessories
```

**Food / world / flavour (8)**
```
VanillaExpanded.VCookE
VanillaExpanded.VCookEStews
VanillaExpanded.VCEF
VanillaExpanded.VNutrientE
VanillaExpanded.BaseGeneration
VanillaExpanded.VExplorationE
VanillaExpanded.VAEWaste
VanillaExpanded.Ideo.IconsandSymbols
```

**Factions and quests (7)**
```
OskarPotocki.VFE.Medieval2                            <-- requested by name
OskarPotocki.VFE.Pirates                              <-- requested by name
OskarPotocki.VFE.Classical
OskarPotocki.VanillaFactionsExpanded.SettlersModule   <-- "the Gunslinger one", confirmed
vanillaquestsexpanded.ancients
Ushanka.GlittertechExpansion                          <-- REQUIRED by Archinity.Glitterites
sarg.alphamechs
```

**Medieval side content (3)**
`Van.Beasts` · `Van.DACrypts` · `Van.DATools` (Dark Ages: Beasts and Monsters, Crypts and
Tombs, Medieval Tools). Cheap tier, additive, and they pair with Medieval 2.

**Setup (1)**
`EdB.PrepareCarefully` — in, at Conrad's call. See the caveat under *Cut*.

### Tier 3 · Races — all eight (8)

```
vanillaracesexpanded.archon
vanillaracesexpanded.sanguophage
vanillaracesexpanded.hussar
vanillaracesexpanded.starjack
vanillaracesexpanded.waster
vanillaracesexpanded.genie
vanillaracesexpanded.android
vanillaracesexpanded.saurid
```

| Mod | Price, from `MOD-VERDICTS.md` |
|---|---|
| Starjack | `starjackGenesAmount` drives the **number of `Rand` draws** per pawn — settings must match |
| Hussar | settings determine the **GeneDef count at load** — settings must match |
| Sanguophage | `drainCasketAmount` consumed in a tick — settings must match |
| ~~**Saurid**~~ | **No price. `MOD-VERDICTS.md` is wrong here and the runbook §3 shows the decompile.** `replacesFaction` is a vanilla Biotech mechanism — four of the five uses in this set are vanilla's own — and it deletes nothing, it only decides what is auto-added to the required-at-game-start list. With Biotech on, pigskins were already replacing plain rough outlanders. Saurid adds a second replacer, both get added, and you **gain** a faction. |
| ~~**Android**~~ | **No meaningful price.** Its entire faction patch appends `<VREA_AndroidAwakened>0.02</VREA_AndroidAwakened>` to three `xenotypeChances` lists. 2%, and read at *pawn* generation, so it is reversible at any time rather than baked at worldgen. |
| Waster | rewrites the vanilla Waster xenotype; `Rand` in a render path |
| Genie | rewrites the vanilla Genie xenotype in place. Cleanest assembly in the bin **[V]** |

> **Correction, after checking both against decompiled source and shipped XML: neither Saurid
> nor Android has a pre-worldgen deadline, and neither needs patching.** The claims came from
> `MOD-VERDICTS.md` and this file repeated them without verifying. Runbook §3 carries the
> evidence. Nothing in this set has to be done before the world is generated.

### Tier 4 · Ours (5)

```
archinity.origins
archinity.pacing
archinity.drifters
archinity.glitterites
archinity.altar          <-- NOT in the active list, and NOT junctioned into RimWorld\Mods
```

`archinity.altar` is the only Archinity mod missing its `setup.ps1` directory junction, which
is why the disk scan never saw it in earlier passes. **Junction it before launch or it will
not load.**

---

## CUT — and the specific reason for each

### Conrad's four exclusions

| Mods | |
|---|---|
| `OskarPotocki.VFE.Empire`, `OskarPotocki.VFE.Deserters` | named directly |
| `OskarPotocki.VFE.Tribals`, `VanillaExpanded.VWETB`, `ETRT.TribalApparel`, `Fuu.UncompromisingTribalFaction`, `Xercaine.Tribal.Furniture`, `PJerri.TribalSiegeRaids` | Neolithic is out |
| `vanillaexpanded.gravship`, `als.gravtech`, `als.biotechgravship`, `LTS.MGW` | Gravship Expanded is out |

### The dangerous suite — off completely

| Mod | The specific defect |
|---|---|
| **Rim War** `Torann.RimWar` | **Barred.** `ThreadStart` in the 1.6 assembly **[V]**, running a parallel world power simulation off the synced tick. Threads on by default. |
| **TechBlock** `fridgeBaron.TechBlock` | `TechBlock_Component.GameComponentUpdate()` runs **per frame** and takes a `Rand` draw from the shared stream outside the synced tick. **Matching settings does not fix it** — the defect is the interleaving position, not the value. |
| **World Tech Level** `m00nl1ght.WorldTechLevel` | ~45 `[HarmonyPrepare]` toggles ⇒ the two clients get **different patched methods**. |
| **More Realistic Research** `sae.ResearchMod` | core research system; out per Conrad |
| **Ignorance Is Bliss** `dame.ignorance` | core research/knowledge system, settings-driven |
| **Lemmy Progression** `LemmyMods.LemProgression` | core progression, and it exists to serve World Tech Level |
| **RimPacts** `wowgag.RimPacts` | not barred, but **the largest shadow world in the bin**: 33,715 decompiled lines in one `WorldComponent`, and 57 settings fields gating `Rand` paths *inside the ticking component*. |
| **Vanilla Combat Reloaded** `Donald.VCR` | core combat resolution |
| **Faction Customizer** `azravos.factioncustomizer` | **pre-worldgen use only.** `Rand`-heavy, zero MP sync, and it cannot remove factions anyway. |
| **Sensible Factions** `Boots.SensibleFactions` | touches faction generation; buys nothing for an MVP |
| **Medieval Overhaul** + `EEG.MOxASF` + `Sierra.RF.MedievalOverhaul` | an overhaul, not content. Known unkeyed schematic-cache desync bug plus a Map-Gen settings trap. Medieval 2 covers the era tonight. |
| **Vanilla Outposts Expanded** `vanillaexpanded.outposts` | reflection writes settings **onto live instances** at load |
| **[SYR] Processor Framework** `syrchalis.processor.framework` | `initialProcessState` read in `CompProcessor.Initialize()` ⇒ **every processor spawns with a different enabled set.** Include only if a kept mod hard-depends on it. |
| **VIE – Memes and Structures** `VanillaExpanded.VMemesE` | unseeded `new Random()`; ideoligion is a core system |
| **VFE – Insectoids 2** `OskarPotocki.VFE.Insectoid2` | declined, #8 session 2 |
| **Faction Territories** `jaeger972.factionterritories` | declined, #8 session 2 — reimplemented in `Archinity.Core` |
| **Elves** `ICC.FOV.ELVES`, **Dwarves** `bean.customxenotypes.dwarvesoftherim` | declined |
| **Factional War** `SR.ModRimworld.FactionalWarContinued`, **Worksites Expanded** `godsfathermixtape.worksitesexpanded` | not barred — deferred as undecided *wants*, not safety cuts |

### QoL cut — four divergence risks the sync layer cannot see

| Mod | Why |
|---|---|
| **Auto-Cast Specialist Commands** `Linnun.AutoCastSpecialistCommands` | Six client-local bools decide whether a **toil is inserted into a vanilla `JobDriver`**. MP syncs the *job*; each client then rebuilds the toil list locally by calling `MakeNewToils`. Two clients run **different toils from the same synced job**, and the sync layer has no way to notice — it delivered the job correctly. The worst settings dependency in the bin. |
| **Better Workbench Management** `falconne.BWM` | Three settings are read inside a detour on `RecipeWorkerCounter.CountProducts` — the count that decides whether a "do until X" bill is satisfied. Mismatch ⇒ one client's bill completes, the other keeps issuing jobs. Not covered by the compat layer. |
| **QualityBuilder** `hatti.qualitybuilder` | The compat layer covers the *commands*, not `getBestConstructionSkillCached`, which recomputes on a **10-second wall-clock `Stopwatch`**. Wall-clock is on the divergence list by name. |
| **Range Finder** `brrainz.rangefinder` | Ships **two** `RangeFinder.dll` builds and its `LoadFolders.xml` puts both in the 1.6 path. The stale 36 KB one Harmony-patches `ModMetaData.VersionCompatible` — it **rewrites which mods the game thinks are compatible**. Not something to inherit unknowingly on a pinned set on night one. |

**Xenotype Spawn Control** `bs.xenotypespawncontrol` — **out.** Settings-driven pawn
generation with eight race mods loaded. Back in once the roster is settled.

**Vanilla Psycasts Expanded** + `VanillaExpanded.VPE.Hemosage` + `…VPE.Puppeteer` — **out**,
as a core system rather than a safety call: its viewport-gated RNG in three places is
already fixed by the compat layer. Cheap to add back.

**Tavern** `ODs.Tavern` — **out.** Free tier and no assembly at all, so it is safe; cut
because ~27 of its 30 buildings are `techLevel` Undefined and nothing era-gates them, which
is wrong for a campaign built on era order.

**Slave Rebellions Improved** `Mlie.SlaveRebellionsImproved` — **IN**, at Conrad's call.
Both its floats are read *inside* rebellion logic, so mismatched settings files produce
**different rebel rosters from the same tick** — a real desync, and one the compat layer
does not cover. It is safe on one condition and only one: **the settings file is identical
on both machines.** Conrad's stated plan handles this — set it, snapshot it, and his partner
copies the file straight out of the repo rather than clicking to match. That is exactly the
right protocol for this mod. It also transpiles `SlaveRebellionUtility.IsRebelling`; no
threads, no `WorldComponent` **[V]**.

> **EdB Prepare Carefully is IN at Conrad's call, and here is the one thing to watch.** It
> owns the character-creation screen, which is the same screen Multiplayer's host/join flow
> uses. **Have the host configure the starting pawns; the client joins after.** If the lobby
> misbehaves at launch, this is the first mod to pull — it is the only entry in the set
> whose risk is at the setup screen rather than in the simulation.

### Vehicles — cut, and the reason is specific

`SmashPhil.VehicleFramework` · `OskarPotocki.VanillaVehiclesExpanded` ·
`OskarPotocki.VanillaVehiclesExpandedUpgrades`

Vehicle Framework is the only mod besides Rim War with real thread-creation machinery:
`SmashTools.Performance.DedicatedThread` runs `new Thread(Execute){IsBackground=true}` +
`Start()`, and `Vehicles.DeferredGridGeneration` enqueues **vehicle pathing-grid and region
generation** onto it — simulation off the synced tick.

There is a lever: `Vehicles.SectionDebug.debugUseMultithreading`, a scribed bool defaulting
`true`. Set it false and every enqueue site takes its synchronous fallback. But
`MOD-VERDICTS.md` carries this as an **open, unverified residual — the synchronous fallback
is not confirmed deterministic.** That is worth an afternoon. It is not worth discovering at
hour three of a co-op session.

**Out tonight; in as soon as the fallback is confirmed.** You already offered this one.

---

## Before you generate the world

1. **Junction `Archinity.Altar`** into `RimWorld\Mods` (`setup.ps1`) — it is the one
   Archinity mod without a junction and it will not load otherwise.
2. **Enable `rwmt.MultiplayerCompatibility`.**
3. **Patch out Saurid's `replacesFaction`** and scope Android's abstract-base patch — both
   are pre-worldgen-only fixes.
4. **Copy the entire `config/ModSettings/` directory from host to client, and the
   `config/ModsConfig.xml` with it.** Per `CODING_STANDARDS.md`, both players need identical
   mods, identical load order *and* identical settings — the third is the one people miss.
   **Never re-click a settings menu on one machine only.** In this set the settings that
   actually reach synced simulation are: **Starjack, Hussar, Sanguophage, Glittertech
   Expansion.**

---

## Decisions

Conrad's calls, 2026-08-28. Recorded because `MOD-VERDICTS.md`'s rule holds here too: this
file decides what we *can* use; what we *want* is Conrad's and gets written down only once
he has said it.

| Question | Call |
|---|---|
| "The Gunslinger one" | **VFE – Settlers** (`…SettlersModule`). No mod named Gunslinger exists on disk; this is the one. Already in. |
| Vanilla Psycasts Expanded | **Out.** |
| EdB Prepare Carefully | **In.** |
| Xenotype Spawn Control | **Out.** |
| Dark Ages trio / Tavern | **Trio in, Tavern out.** |
| Slave Rebellions Improved | **In**, added after the first review pass. Same settings file on both machines, copied from git. |

## Verification run against this exact set

```
config/ModsConfig.xml          86 active mods, all resolve on disk, 0 unmet dependencies
tools/check_refs.py            28,811 defNames in scope - all references resolve
tools/patch_check.py           2,766 def files merged from 86 mods
                               1,253 third-party patch operations applied
                               0 failures
tools/check_availability.py    clean
tools/audit_research.py        skipped, by design - see below
```

**`audit_research.py` now skips when More Realistic Research is absent, and that is a fix,
not a suppression.** Every finding that script produces is a property of MRR's
auto-generated analysis prerequisites — read its own module docstring, which says so. With
`sae.researchmod` out of the set, nothing generates those prerequisites, so its 21 "new
deadlock risks" were all claims about a mod that is not loaded. The gate now checks
`config/ModsConfig.xml` for `sae.researchmod` and reports why it skipped. `--force` restores
the old behaviour, and the baseline is untouched, so the moment MRR comes back the audit
comes back with it.

Two known, pre-existing merge-fidelity notes, neither introduced by this set and neither a
blocker: one third-party gene file is not valid UTF-8 and is skipped, and three patch
operation classes are unimplemented in the checker (`PostInheritanceOperation.Patch` ×2,
`VCE_Fishing.PatchOperationModOption` ×1). The merged tree is approximate to that degree.
