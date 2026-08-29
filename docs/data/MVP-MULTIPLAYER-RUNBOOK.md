# MVP multiplayer runbook

How to get tonight's two-player session actually running. Companion to
`MVP-MULTIPLAYER-MODSET.md`, which decides *what* is in the set; this decides *how* it gets
onto both machines and what to do when something goes wrong.

---

## 0. The ladder — climb it in order, do not skip a rung

The goal you set is four rungs, and each one is a separate question. Testing them together
means a failure at rung 4 is indistinguishable from a failure at rung 2. Each rung is a
few minutes; the whole ladder is faster than debugging a mystery.

| Rung | Mod set | The question it answers | Pass looks like |
|---|---|---|---|
| **1** | Core + 4 DLCs only | Does the base game run on both machines? | Both launch, no red errors |
| **2** | + Prepatcher, Harmony, Multiplayer, Multiplayer Compatibility | Does co-op connect at all? | Client joins host, both tick, pawns move on both screens |
| **3** | The full 86 | Does the mod set load and stay synced? | No red errors at startup, no desync after ~1 in-game day at 3× |
| **4** | Same 86, Archinity content in play | Does the questline work? | Altar present, a pawn can enter it, facilities change the numbers |

Rung 3 is the one that will actually break, and the fastest bisect is by tier: pull all
of Tier 2 and 3 (content and races), confirm green, then add them back in two halves.

The three lists are already written, so a rung is a file copy rather than forty clicks in
the mod menu. On **both** machines:

```powershell
copy config\ladder\ModsConfig.rung1-vanilla.xml     "$env:LOCALAPPDATA\Low\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml"
copy config\ladder\ModsConfig.rung2-multiplayer.xml "$env:LOCALAPPDATA\Low\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml"
copy config\ladder\ModsConfig.rung3-full.xml        "$env:LOCALAPPDATA\Low\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml"
```

Rung 3 and rung 4 use the same list — rung 4 is the same build with the Archinity content
actually exercised. `.\setup.ps1 -SyncConfig` installs the rung-3 list, so the ladder only
matters if you want to bisect.

---

## 1. Host machine — set it up, then freeze it

**`setup.ps1` is a dev convenience and you only need half of it.** It does two unrelated
jobs:

- **Junctions** the five `Archinity.*` folders into `RimWorld\Mods`, so the repo *is* the
  installed mod and your edits are live in-game with no copy step. Useful to you. Useless
  to your co-op partner, who is not editing anything.
- **Copies config** into RimWorld's Config folder. That is just a file copy with a backup.

You already ran it, so the junctions exist. You will not need it again unless you add a
sixth Archinity mod.

The actual workflow, in the order you actually do it:

1. **Launch the game.** Open every mod's settings menu and set everything the way you want.
2. **Freeze it:**
   ```powershell
   .\tools\snapshot-config.ps1
   ```
   This pulls the live `ModsConfig.xml` (the mod list *and* its order) and every
   `Mod_*.xml` settings file back into `config\`. It skips settings for mods that are not
   in the active list and deletes stale ones, so the snapshot always describes exactly the
   build you are playing.
3. **Commit and push.**
   ```
   git add config
   git commit -m "config: freeze mod list and settings"
   git push
   ```

That is the whole protocol. Set, snapshot, push.

## 2. Your co-op partner — copy and paste, no scripts

He needs three things, and none of them involve running anything.

**a. The same mods.** 77 of the 87 come from the Steam Workshop; 5 are Core and the DLCs he
already owns, and 5 are ours. Two ways to give him the 77 — see §2b, it matters more than it
looks.

`docs/data/MVP-WORKSHOP-COLLECTION.md` lists all 77 with workshop IDs and links, in load
order, and ends with a bare ID list.

**b. The five Archinity mod folders.** Pull the repo, then copy these five folders:

```
Archinity.Altar
Archinity.Drifters
Archinity.Glitterites
Archinity.Origins
Archinity.Pacing
```

into:

```
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\
```

(Whole folders, as-is. If his RimWorld is on another drive, it is the `Mods` folder next to
`RimWorldWin64.exe`.)

**c. The config.** Copy `config\ModsConfig.xml` and everything inside `config\ModSettings\`
into:

```
%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\
```

Paste that path straight into the Explorer address bar — it expands. Overwrite what is
there. **Note `LocalLow`, not `Local`.** They are siblings, and picking the wrong one is the
single most common way this goes wrong; it is the exact bug `setup.ps1` had until today.

Repeat step (c) any time you re-freeze the settings. Repeat (b) any time the Archinity mods
change.

> **Why all three, every time.** Both players need identical mods, identical **load order**,
> and identical **mod settings**. The third is the one people miss, and `ModsConfig.xml`
> carries the second — which is why he copies the file rather than ticking boxes in the mod
> menu to match. **He should not enable anything by hand.** Subscribing (or copying) gets him
> the files; `ModsConfig.xml` is what enables them and puts them in order.

## 2b. Steam Collection, or freeze the folders?

Two ways to get him the 77 workshop mods. They differ in one thing that matters over a
six-hundred-day campaign.

### Option A — a Steam Collection (fast, do this tonight)

Make a Collection at `steamcommunity.com/workshop` → *Create Collection* → RimWorld, add the
77 items, set it Public or Friends-Only, send him the link. He clicks **Subscribe to all**.

`docs/data/MVP-WORKSHOP-COLLECTION.md` has every ID and link in load order to build it from.
Fastest path: open your own *Subscribed Items* list, which has an **Add to collection** control
per item, rather than visiting 77 mod pages.

**The catch: Steam auto-updates workshop mods.** If a mod updates on one machine and not the
other — different day, different launch time, Steam being Steam — your def databases no longer
match and the session will refuse to join or desync. Over months, that *will* happen.

### Option B — ship him the folders (safer, and cheaper than it sounds)

**The whole 77-mod set is 0.81 GB.** Zip
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\` filtered to the 77 IDs in the
manifest, and he drops them into:

```
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\
```

RimWorld loads local `Mods\` folders exactly like workshop ones — folder names are irrelevant,
`About.xml`'s packageId is what `ModsConfig.xml` matches on. **Steam then cannot touch them**,
and your two installs are pinned to the same bytes until you both deliberately change them.

> **Nobody has to unsubscribe. Verified in decompiled `Verse.ModLister.TryAddMod`:**
>
> ```csharp
> if (mod.OnSteamWorkshop != modWithIdentifier.OnSteamWorkshop)
> {
>     ModMetaData modMetaData = (mod.OnSteamWorkshop ? mod : modWithIdentifier);
>     if (!modMetaData.appendPackageIdSteamPostfix)
>     {
>         modMetaData.appendPackageIdSteamPostfix = true;
>         return TryAddMod(mod);
>     }
> }
> ```
>
> When a packageId exists once locally and once on the workshop, the **Steam** copy is the one
> flagged, and `ModMetaData.PackageId` then returns `packageId + ModMetaData.SteamModPostfix`
> (`"_steam"`). The local copy keeps the clean id, `ModsConfig.xml` lists clean ids, and
> `GetModWithIdentifier` resolves them out of `modsByPackageId` — which is keyed on the
> postfixed `PackageId`. **So every entry resolves to the local copy and the Steam copy is
> simply not in the active list.**
>
> The `"Tried loading mod with the same packageId multiple times"` error only fires when both
> copies are on the *same* side — both local, or both workshop. Not this case.
>
> Costs of leaving the subscriptions: the set is duplicated on disk (~0.8 GB), and the in-game
> mod list shows both entries. Steam may keep updating its copies forever; the game will not
> load them.

Largest items, if you want to trim the transfer: AI Upscaled Textures 178 MB, ATH Norse 88 MB,
ATH Draconic 80 MB, Rustic Workbenches 76 MB, Landmarks 57 MB. The first four are purely
cosmetic — but cutting them means cutting them on both machines and re-snapshotting, not just
skipping the download.

### Recommendation — and this is done

**Option B, and it is already applied on the host.** `tools\freeze-workshop-mods.ps1` copied
all 77 workshop mods into `RimWorld\Mods\`; `-Check` confirms all 82 non-DLC entries resolve
locally. The subscriptions were left in place, because per the box above they do not need
removing.

`tools\export-for-partner.ps1 -Zip` builds the handover pack — 82 mod folders, `ModsConfig.xml`,
32 settings files and a `READ ME FIRST.txt`, about 0.6 GB zipped, roughly two and a half
minutes.

> **Use `ZipFile.CreateFromDirectory`, never `Compress-Archive`.** `Compress-Archive` is
> implemented in PowerShell and adds entries one at a time; on this set — thousands of small
> texture and def files — it produced about 13 KB per minute, which is hours. The .NET call
> does the same job in 144 seconds. The script uses the fast one.

**Re-run the export after any change to `Archinity.Altar`'s assembly**, or your partner gets
a stale DLL.

In this set the settings that actually reach synced simulation are **Starjack, Hussar,
Sanguophage and Ushanka's Glittertech Expansion**. Those four are the ones that will
desync you if they drift. The rest are cosmetic or inert.

**Right now `config/ModSettings/` holds 10 files, and those four are not all among them.**
RimWorld only writes a settings file once something in that menu changes, so Starjack,
Hussar and Sanguophage have none yet. Both machines therefore run identical defaults, which
is safe — but it is safe by accident, not by design.

**Since you are going to open all 87 menus and set everything anyway, that resolves itself.**
Do that pass, run `.\tools\snapshot-config.ps1`, push, and the four that matter are captured
along with everything else. After that the rule is simple: **any settings change on either
machine means re-snapshot, re-push, re-paste.**

> **`setup.ps1 -SyncConfig` never worked before today**, which is worth knowing because it
> means no settings have ever actually been synced between you two. It built the config path
> as `Join-Path $env:LOCALAPPDATA 'Low\...'` → `AppData\Local\Low\...`. RimWorld writes to
> `AppData\LocalLow\...`, a **sibling** of `AppData\Local`, not a child. The script took its
> "config folder not found" branch, printed a warning, and did nothing. Fixed; both it and
> `snapshot-config.ps1` now resolve from `$env:USERPROFILE`.

## 3. Before you generate the world — nothing, as it turns out

**An earlier revision of this file listed two pre-worldgen must-dos. Both were wrong, and
they are struck.** Recorded rather than deleted, because one of them is repeated in
`MOD-VERDICTS.md` and needs correcting there too.

### ~~Saurid's `replacesFaction` deletes a vanilla faction~~ — it does not

`replacesFaction` is **a vanilla Biotech mechanism**, not a Saurid quirk. The active set has
five uses of it and **four are vanilla**:

| Replacer | Replaces |
|---|---|
| `TribeRoughNeanderthal` | `TribeRough` |
| `TribeSavageImpid` | `TribeSavage` |
| `OutlanderRoughPig` | `OutlanderRough` |
| `PirateWaster` | `Pirate` |
| `VRESaurids_OutlanderRoughSaurid` | `OutlanderRough` |

And it deletes nothing. Decompiled `RimWorld.FactionGenerator`:

```csharp
if (!orderedEnumerable.Any(x => x.requiredCountAtGameStart > 0 && x.replacesFaction == facDef)
    && CanExistOnLayer(layer, facDef))
{
    for (int i = 0; i < facDef.requiredCountAtGameStart; i++)
        AddFactionToManager(layer, facDef);
}
```

It only decides whether a faction is **auto-added to the required-at-game-start list**. The
`FactionDef` still exists and can still be added by hand on the world-creation screen.

**So with Biotech enabled, vanilla was already replacing plain rough outlanders with
pigskins before Saurid was ever installed.** Saurid adds a *second* replacer for the same
slot, and since neither replacer is itself replaced, both get added. Net effect: you **gain**
a saurid outlander faction alongside the pigskin one. You lose nothing you would otherwise
have had.

> Note the resolution trap that made the original claim hard to check: every one of these
> inherits `requiredCountAtGameStart` from a **grandparent** (`OutlanderFactionBase`,
> `TribeBase`), so `tools/xpath.py` reports 0 matches on the concrete defs *and* on their
> immediate parents. Xpath runs before `ParentName` inheritance resolves, exactly as
> `CODING_STANDARDS.md` warns. Walk the chain.

### ~~Android's abstract-base patch bleeds into faction generation~~ — trivially, and reversibly

`.../2975771801/1.6/Patches/FactionPatches.xml` in full is three `PatchOperationAdd`s that
each append **one line**:

```xml
<VREA_AndroidAwakened>0.02</VREA_AndroidAwakened>
```

to the `xenotypeChances` of `OutlanderFactionBase`, `PirateBandBase` and `Empire`. A 2%
chance. The Empire operation no-ops here because Empire is not in the set.

That is the Waystone's *"a trace of the exotic is flavour"*, not its *"a world where everyone
is exotic is noise"* — and the Waystone's no-bleed rule names **Archons and Starjacks**
specifically, not androids.

It is also **not a worldgen decision at all**: `xenotypeChances` is read at *pawn*
generation, so patching it out later takes effect on the next pawn generated. Nothing is
baked in.

### What is actually permanent

The faction roster you pick on the world-creation screen, and the map you land on. That is
it. Faction Customizer stays out of the set because it is pre-worldgen-only *and* cannot
remove factions anyway — use RimWorld's own faction selector instead.

## 4. Starting the session

Host first, client joins. **EdB Prepare Carefully is in the set and it owns the
character-creation screen, which is the same screen Multiplayer's host/join flow uses.**
Have the host configure the starting pawns and open the lobby; the client joins after.
If the lobby misbehaves, Prepare Carefully is the first mod to pull — it is the only entry
in the set whose risk sits at the setup screen rather than in the simulation.

Turn on Dev Mode (Options → Gameplay) so def errors are visible.

## 5. Getting the altar

Three routes, in order of when they arrive:

1. **Scenario start.** `Archinity_SeedOfArchinity` in `Archinity.Origins` hands out the
   altar and a vector at game start. This is the intended path and matches the design:
   the altar is *given*, in the neolithic era, before you know what it is for.
   **If you start on a vanilla scenario instead of Seed of Archinity, you do not get it
   this way.**
2. **The VQE Ancients chain.** `Archinity.Altar/Patches/Quest_AncientLab_Grants.xml` adds
   the altar and all twelve of its lab facilities to the site maps that questline
   generates. Late, but it is the only route that hands over the full facility rack —
   the chain by itself gives roughly one facility per quest, and the altar links twelve.
3. **Dev-spawn.** `minifiedDef MinifiedThing` is set, so a dev-spawned altar uninstalls
   and re-installs normally.

The scenario route uses `ScenPart_StartingThing_Defined`, not a scatterer, and that is
deliberate: decompiled `GenerateThing` calls `thing.MakeMinified()` whenever
`ThingDef.Minifiable` is true, which the altar sets. So the 3×2 building arrives as a
haulable crate and no footprint has to be placed at map gen. Both entries are guarded
`MayRequire="archinity.altar,vanillaquestsexpanded.ancients"`; both are active, so both fire.

## 5b. What the facility rack actually does

`AltarFacilityExtension` was fully implemented in C# and carried by **zero defs** — the
twelve facilities linked, drew connection lines, and changed nothing, with no warning
anywhere. `Archinity.Altar/Patches/Facilities_AltarAugments.xml` now puts the extension on
all twelve, each with an identity read off its own VQEA description:

- **Duration** — rapid infusion pump, cognitive recovery array, archite pathing array
- **Charge cost** — archite recycler, genomic attenuator
- **Outcome** — neurostabilizer array, rejection buffer coil, spliceframe uplink, trait
  selection prism, aberration redirector
- **Trade-offs** — mutagen inhibitor core and complexity harmonizer buy blood or success and
  pay in hours

A full rack of one each totals `chargeCostFactor 0.446`, `durationFactor 0.640`,
`outcomeBonus +0.15` — so the rite's base 0.75 success becomes 0.90. Clear of the 0.25
charge floor `AltarModifiers.For()` enforces, and never certainty.

`biasCategory`, `biasStrength` and `extraOptions` are deliberately **omitted**. They are
computed and never read, because the gene lottery is dead code. Writing them would have
implied they work.

## 6. If something goes wrong

| Symptom | First thing to check |
|---|---|
| **Desync** | Compare `config/ModSettings/` between machines, byte for byte. Then check Starjack / Hussar / Sanguophage / Glittertech settings specifically. |
| **Client cannot join** | Mod list or load order mismatch. `ModsConfig.xml` must be identical, including order. |
| **Lobby screen misbehaves** | Pull EdB Prepare Carefully. |
| **A red error naming a def type** | Something needs `MayRequire` for a mod that is not loaded. Both known cases — 18 `ManualAnalysisDef`s in Glitterites and 1 in Pacing — are now gated on `sae.researchmod`. |
| **"MPCompat :: Exception loading &lt;mod&gt;"** | That mod is running with **no multiplayer sync patch**, even though Multiplayer Compatibility is enabled. Every other mod's patch still loads. Grep the boot log for `MPCompat ::` and check which lines say *Initialized* and which say *Exception*. |

### The first boot, and what it found

The 87-mod set booted. Four issues, three of them ours, all fixed:

- **11 dangling `AM_*` research references.** `Lockout_AlphaMechs.xml` deleted 8
  `ResearchProjectDef`s that 11 `ThingDef`s still named. Its own header described the correct
  order — neuter first, delete last — and the operations only neutered `designationCategory`,
  not `researchPrerequisites`. Fixed with one operation, verified to match exactly 11.
- **`ResearchMakesSense.ManualAnalysisDef` in `Archinity.Pacing`**, ungated. Fixed.
- **`Archinity_GL_Technician`** could generate weaponless: `weaponMoney` floor 400 against a
  cheapest `SpacerGun` of 580. Now 600~1200.
- **`Resurrect`** — not ours. Ludeon ships that **GeneDef commented out**; only the `AbilityDef`
  of that name is live, which is why `check_refs.py` passed on it. Removed from the pool.
| **Altar links to facilities but nothing changes** | That was the pre-existing bug: the twelve facilities were linked and carried no `AltarFacilityExtension`. Check `Archinity.Altar/Patches/Facilities_AltarAugments.xml` is present and that `patch_check.py` shows its operations matching. |

## 7. What is deliberately not in tonight's build

Recorded so nobody re-litigates it mid-session. Full reasoning in
`MVP-MULTIPLAYER-MODSET.md`.

- **Vehicles** — Vehicle Framework runs pathing-grid generation on a background thread; the
  single-threaded fallback exists but is **not confirmed deterministic**. In as soon as it
  is.
- **TechBlock, World Tech Level, More Realistic Research, Ignorance Is Bliss, Lemmy
  Progression** — the tech-gating suite. TechBlock in particular takes a `Rand` draw from a
  per-frame method, which matching settings cannot fix.
- **RimPacts, Rim War, Factional War, Faction Territories** — world simulation.
- **Medieval Overhaul, Vanilla Combat Reloaded, Vanilla Psycasts Expanded, VIE Memes** —
  core systems.
- **Auto-Cast Specialist Commands, Better Workbench Management, QualityBuilder, Range
  Finder** — QoL with settings that reach synced simulation invisibly.

## 8. Known rough edges in tonight's build

- The gene lottery is dead code. `GenePoolDef.Available` has no caller, and a vector with a
  null gene is consumed for its blood cost and grants nothing, silently. **Use named
  vectors.**
- `WorkGiver_CarryToBuilding` refuses an upright, mobile **slave** even though the altar's
  `IsFuel()` accepts one. Prisoners and downed pawns only.
- Site loot placement is crude: `CellFinder.RandomSpawnCellForPawnNear` validates pawn
  standability, not a building footprint. Four of the twelve lab facilities are 3×3 and the
  altar is 3×2, so one spawned against a vault wall will wipe what it overlaps. Expect the
  occasional hole in a wall. Cosmetic.
- **VQE Ancients has no Multiplayer Compatibility patch at all** — a UTF-16 string scan and
  class listing of `Multiplayer_Compat.dll` return only `VanillaQuestsTheGenerator`, a
  different module. `Window_ArchiteInjection` and the injector gizmos are unsynced surfaces.
  This is a pre-existing condition of running that mod in co-op, not something this work
  introduced, and it deserves its own ticket.
