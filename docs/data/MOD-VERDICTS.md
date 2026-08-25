# Mod verdicts

The bar from [#3](https://github.com/cjd721/Rimworld-Archinity/issues/3), applied to
every mod on disk. Issue [#17](https://github.com/cjd721/Rimworld-Archinity/issues/17).

**The instrument, restated so this file stands alone:**

- **Barred** — we *cannot* use it. Only when fixing it would mean owning their
  assembly: a parallel world simulation, or background threads. Nothing else bars.
- **Declined** — we *can* use it and choose not to. No justification owed.
- Everything else is **Free** (enable it), **Cheap** (enable plus a
  `PatchOperation`) or **Real** (a fork we re-merge, or a Harmony patch in our
  assembly).
- Barred and declined mods **stay on disk as reference.**

**113 mods scanned** — 108 in `workshop/`, the rest local. `config/ModsConfig.xml`
enables **57**. Per the map's standing note, enabled/disabled carries **zero
weight** as a verdict; it is recorded only as evidence of prior intent.

---

## Method, and what it can and cannot prove

A byte-marker scan of every 1.6 assembly (`tools/` scratch script, not committed —
regenerate from this file's method if needed), then targeted `ilspycmd` decompiles
where a marker was load-bearing.

**What the scan proves.** Absence of `ThreadStart` / `ThreadPool` / `new Thread` in
an assembly is strong evidence the mod starts no background threads. Presence of
an assembly at all, and of a `ModSettings` surface, is exact.

**What it does not prove.** `System.Threading` in an assembly means almost nothing
on its own — `Interlocked`, `Monitor` and `ConcurrentDictionary` all pull it in
without a thread ever being created, and 18 mods trip it for exactly that reason.
`WorldComponent` likewise does not imply a parallel world model; VEF's quest-chain
component is a `WorldComponent` and ticks inside the synced tick. **Every verdict
below marked `[M]` is marker-level only.** `[V]` means decompiled and read.

One methodological trap worth recording, because it cost a pass: reading
`<packageId>` with a regex over `About.xml` returns the first match in the file,
which for many mods is a **dependency's** id inside `<modDependencies>`. The first
run reported eight separate mods as `brrainz.harmony`. Parse the XML and take the
direct child of `ModMetaData`.

---

## Barred

**Two mods. Both already known, both already mined, and the pass found no third.**

| Mod | Evidence | Status |
|---|---|---|
| `Torann.RimWar` | `ThreadStart` present **[V]**, plus a 30-field settings ref constructed inside `WorldComponentTick`. Runs a genuine parallel world simulation on real background threads, on by default. | Barred. Already mined for the faction-tension shape. |
| `SR.ModRimworld.FactionalWarContinued` | Faction-vs-faction combat resolution outside the synced path; uncovered by the compat layer **[M]**. | Barred. Already mined. |

**That the barred list is this short is the headline result, and it is the bar
working as designed.** With licence struck and the set pinned, nearly every defect
that used to read as disqualifying is now something we can simply fix.

### The one that looked barred and is not

**`SmashPhil.VehicleFramework` — Real tier, not barred. [V]**

The only *enabled* mod carrying real thread-creation machinery.
`SmashTools.Performance.DedicatedThread` does
`new Thread(Execute) { IsBackground = true }` then `thread.Start()`, and
`Vehicles.DeferredGridGeneration` enqueues **vehicle pathing-grid and region
generation** onto it — simulation state computed off the synced tick, which is
exactly the shape the bar exists to catch.

It is saved by a switch. `Vehicles.SectionDebug.debugUseMultithreading` is a
scribed bool defaulting to `true`; when false, `RevalidateAllMapThreads()` calls
`ReleaseThread()` instead of `InitThread()`, `ThreadAvailable` goes false, and
every enqueue site takes its synchronous fallback (`threadAvailable ? … : null`).

**Price: set `debugUseMultithreading = false` and treat that settings file as
save-critical.** Residual risks, both unverified: the synchronous fallback path has
not been confirmed deterministic, and single-threaded grid generation will cost
frame time on large maps. `SmashPhil.VehicleFramework` *is* covered by the compat
layer, which is mild evidence the netcode authors already looked at this.

This one matters beyond itself: it is what decides whether vehicles are available
to the campaign at all, and the answer is yes, at a stated price.

---

## Enabled (57) — tiers

**12 are Free** — no assembly, nothing to go wrong beyond XML: the five Archinity
mods, `VanillaExpanded.VFEProduction`, `OskarPotocki.VanillaVehiclesExpandedUpgrades`,
`sbz.NeatStorage`, `sbz.GravshipStorage`, `Bart.APP`, `Kangel.Moisture`,
`FrozenSnowFox.FilthVanishesWithRainAndTime`, `willworkforicecream.NoAlzheimers`.

**14 are Cheap** — an assembly with no settings surface. `OskarPotocki.VFE.Classical`,
`VanillaExpanded.VFECore` (Furniture), `VFESecurity`, `VFESpacer`, `VFEFarming`,
`VFEMedical`, `VAEAccessories`, `VChemfuelE`, `vanillaquestsexpanded.ancients`,
`sae.ResearchMod`, `sbz.NeatStorageFridge`, `EdB.PrepareCarefully` (pre-game only),
`rwmt.Multiplayer`, `vanillaracesexpanded.waster`.

**31 are Cheap with a settings surface**, i.e. Cheap *plus a managed condition*.
Per `CODING_STANDARDS.md`, `config/ModSettings/` is part of the sync surface: copy
the file, never re-click it. This is not a defect to fix; it is a rule to follow.
Includes VEF Core, VFE Medieval 2, VFE Pirates, Settlers, VFE Power, TechBlock,
Ignorance Is Bliss, all four enabled VRE races, both gravship mods, Better Traders
Guild, Alpha Mechs, Glittertech, Adaptive Storage, Prepatcher, Replace Stuff.

**Named prices already known**, carried from `PARTS-BIN.md` rather than re-derived:

| Mod | Price |
|---|---|
| `SmashPhil.VehicleFramework` | **Real** — see above. |
| `fridgeBaron.TechBlock` | **Real** — `GameComponentUpdate()` writes research progress **per frame**, so clients at different frame rates diverge continuously and no settings file fixes it. Fork-and-recompile, or a Harmony prefix. Owned by [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7). |
| `vanillaracesexpanded.starjack` | Cheap — `starjackGenesAmount` drives the number of `Rand` draws per pawn. Settings file must match. |
| `vanillaracesexpanded.hussar` | Cheap — settings determine the **GeneDef count at load**. Settings file must match. |
| `azravos.factioncustomizer` | Cheap, **pre-worldgen use only** — `Rand`-heavy mutations, zero MP sync. Cannot remove factions; eight UI patches is its whole surface. |

**Three enabled mods are already-decided ejections**, and none is expensive:

- `vanillaracesexpanded.saurid` — `replacesFaction` deletes a vanilla faction.
- `vanillaracesexpanded.waster` — rewrites the vanilla Waster xenotype.
- Together they cost **two `MayRequire` gene lines** in `Archinity.Origins`
  (`VRESaurids_Pheromones`, `VRE_Instability_Extreme`) and one over-declared
  `<modDependencies>` block. Build-backlog item.

---

## Disabled (56)

Disabled is not a verdict. Three buckets.

### Fence — routed to the tickets that own them, not decided here

| Mod | Routed to | Note |
|---|---|---|
| `OskarPotocki.VFE.Empire` | [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) | Distinct from the Royalty DLC, which is not in question. Supporting antagonist? |
| `OskarPotocki.VFE.Deserters` | [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) | **Also the parts bin's recommended authoring pattern for the entire Chronicle** (§7.4). Can be *declined as content and kept as reference* without losing what we want from it. |
| `vanillaracesexpanded.android` | [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) | Late-game potential; patches the abstract outlander and pirate bases, so it bleeds unless patched. Its `AndroidSettings.xml` is a model for Def-based tunables. |
| `DankPyon.Medieval.Overhaul` | [#5](https://github.com/cjd721/Rimworld-Archinity/issues/5), [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) | **See the flag below — this one is urgent.** |
| `OskarPotocki.VFE.Tribals` | [#5](https://github.com/cjd721/Rimworld-Archinity/issues/5) | Ships an era ladder already (`PARTS-BIN.md` §5.3). |
| `VanillaExpanded.VPsycastsE` | [#10](https://github.com/cjd721/Rimworld-Archinity/issues/10) | The second power track lives or dies here. |
| `m00nl1ght.WorldTechLevel` | [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) | ~45 `[HarmonyPrepare]` settings toggles ⇒ clients get *different patched methods*. Cheap only if the settings file is treated as save-critical. |
| `rwmt.MultiplayerCompatibility` | — | **In. Floor assumption.** Downloaded, not yet enabled. Enable before any co-op test. |

### Declined

`ICC.FOV.ELVES` and `bean.customxenotypes.dwarvesoftherim` — flat out, Conrad's
call, no justification owed. `Torann.RimWar` and
`SR.ModRimworld.FactionalWarContinued` are declined *and* barred; the barred
verdict is the operative one. `jaeger972.factionterritories` and
`godsfathermixtape.worksitesexpanded` are declined as the same family — the
faction-tension shape is settled without them **[M]**; neither shows thread-creation
markers, so neither is *barred*, and the distinction is deliberate.

### Not assessed

The remaining ~40 disabled mods — art libraries, QoL, architect-menu tooling, the
VWE and VAE families, the Dark Ages set, Processor Framework, Outposts, Insectoids 2.
**No verdict, by choice.** Nothing has asked for them yet, and a verdict written
before a design ticket wants the mod is a verdict written blind. They are declined
by default and assessable on request. Listing this explicitly rather than implying
coverage: **this pass did not verdict every one of the 113.**

---

## What this pass changes

1. **The bar barred nothing new.** Across 113 mods, the only barred entries are the
   two already known and already mined. The instrument from #3 is not a filter that
   removes work; it is a filter that turns out to remove almost nothing, which is
   itself the finding.
2. **Vehicles are available**, at the price of one settings flag and a performance
   cost. Previously this looked like a hard block.
3. **The real cost of the mod set is not safety, it is the settings surface.** 31 of
   57 enabled mods carry one. Under our own doctrine that is a managed condition,
   but it means `config/ModSettings/` is save-critical for more than half the set,
   and the pre-worldgen freeze ([#18](https://github.com/cjd721/Rimworld-Archinity/issues/18))
   must snapshot it as a single artifact.
4. **Medieval Overhaul is currently disabled, and so is VFE Tribals.** Flagged below.

## Flag — the Medieval tier currently rests on VFEM2 alone

`DankPyon.Medieval.Overhaul` (679 defs, 165 patches) and
`Sierra.RF.MedievalOverhaul` are both **disabled** in the repo's `ModsConfig.xml`
snapshot, as is `OskarPotocki.VFE.Tribals`. `OskarPotocki.VFE.Medieval2` is enabled.

This matters because a large block of `PARTS-BIN.md` and of
`docs/technical-findings.md` reasons about the Medieval era *assuming MO is present*
— the ingot chains, the `metalChain` / `vanillaMine` settings analysis, the
iron-locked weapons, the measured tier totals (Medieval 18,000 baseline vs 57,900
with MO), the schematic-cache desync, and the `component_replace` blast radius
across 395 ThingDefs. **None of that is currently live.**

Per the map's standing premise the mod set is an output, so this is not a
contradiction — but [What the six eras are for](https://github.com/cjd721/Rimworld-Archinity/issues/5)
and [The era-gating mechanism](https://github.com/cjd721/Rimworld-Archinity/issues/7)
should both know that MO is a *proposal*, not a baseline, before they design against it.

## Open, for the freeze

- Enable `rwmt.MultiplayerCompatibility` before any co-op smoke test.
- Confirm Vehicle Framework's synchronous fallback is deterministic, if vehicles ship.
- Decompile `[WG] RimPacts` (`3762723122`) — not installed; carried from `PARTS-BIN.md` §14.
