# Traps: multiplayer and determinism

Divergence that survives identical mod lists. The model these rest on is
`docs/engine/determinism.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Multiplayer and determinism

### T-18 — Mod settings are part of the sync surface

Both players need identical mods, identical load order (`config/ModsConfig.xml`)
**and** identical mod settings (`config/ModSettings/`). The third is the one people
miss — TechBlock, Ignorance Is Bliss and Medieval Overhaul are all settings-driven,
and settings reach runtime as well as def-load. A diff that changes settings must
re-snapshot them.

Compare **parsed values, not bytes**: `Scribe_Values.Look` omits values equal to
their default, so a fresh config and an explicitly-defaulted one are byte-different
with identical meaning.

*`docs/engine/determinism.md`; T-19 and T-20 are the worked cases. MP 0.11.5.*

### T-19 — Medieval Overhaul forces a setting from a draw method

The force lives inside the **Map-Gen tab's draw method** — not `ExposeData`, not a
constructor:

```csharp
if (!metalChain) { vanillaMine = true; }
```

Uncheck `metalChain` on the Production tab, close without visiting Map Gen, and the
force never runs. **Two players clicking identical settings produce different
files.** Copy the settings file between machines; never re-click it.

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-20 — Medieval Overhaul's schematic cache is a live desync bug

Both schematic patches carry `private static bool? cachedSchematicCheck` and
`cacheStaleAfterTicks` with a 250-tick window and **no key** — not the project, not
the bench, not the schematic —
so whichever call lands first decides the answer for every gated project on every
bench. `CanBeResearchedAt` is called from `WorkGiver_Researcher` (simulation)
**and** the research tab UI (client-local), so the player with the tab open poisons
the shared cache on a schedule the other client does not share, and one client's
`WorkGiver_Researcher` refuses jobs the other accepts.

Separately, both patches' `Prepare()` returns `!settings.biotechSchematic`, and
`Prepare()` decides whether the patch is applied at all — so a settings mismatch
changes which code exists. Mitigation needs no assembly: strip the
`RequiredSchematic` extension from the 14 gated projects and the postfix returns
immediately.

*`docs/engine/mods/medieval-overhaul.md`. MO 1.6.*

### T-21 — Filter at draw time, never at list-membership time

`Letter.CanCullArchivedNow` culls the Archive by **stack membership**, so filtering
at receive makes two clients cull different sets and synced `ChoiceLetter` commands
then deserialize to null — Multiplayer ships this bug with a TODO admitting it. The
same shape is worse upstream: patching `MapPawns.FreeColonists`, `PawnsFinder` or
`Pawn.IsColonist` diverges **~15 ticked readers**, equally silently.

Any per-player presentational layer filters at **draw** time only.
`ColonistBar.cachedEntries` is never serialised and nothing in the tick path reads
it, which is why the colonist bar is tractable and the pawn lists are not.

*`docs/engine/determinism.md` § *Presentational separation*. MP 0.11.5.*

### T-22 — 77 workshop mods have a second copy on disk

**77 workshop mods carry a full second copy** under
`steamapps/common/RimWorld/Mods/`, declaring the same `packageId` — measured today
as the id-overlap between the two roots: 145 folders under
`workshop/content/294100`, 83 under `Mods/`, of which 77 collide and 6 are ours
(the five `Archinity.*` mods plus Steam's placeholder file).

These are real copies, not junctions — VEF (`2023507013`) is 13 MB in both. Five
were diffed and are byte-identical; the rest were not. Which one loads is not
something the mod list tells you, and byte-identity between machines is not
established by matching workshop IDs.

**Resolve this before the mod set is pinned**; the vendoring decision in
[#3](https://github.com/cjd721/Rimworld-Archinity/issues/3) has to say which root
wins. The same hazard applies inside a mod: TechBlock ships both a `1.6/` and a
`1.0/` assembly, and decompiling the wrong one yields different code and a wrong
conclusion.

*Disk survey 2026-09; overlap re-counted against both roots 2026-09-08.*

---
