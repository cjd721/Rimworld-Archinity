# World time and planet layers

The engine's calendar arithmetic, and the Odyssey orbit layer's geometry,
settlement density and faction placement controls.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Time

`GenDate.DaysPerYear = 60`. A RimWorld year is **60 days**, four 15-day
quadrums. Any gate expressed in years must be multiplied by 60, not 365.

Conrad's target era lengths, converted:

| Era | Years | Days | Era ends ~day |
|---|---|---|---|
| Neolithic | 1–2 | 60–120 | 60–120 |
| Medieval | 3–4 | 180–240 | 240–360 |
| Industrial | 2–4 | 120–240 | 360–600 |
| Spacer | 1–2 | 60–120 | 420–720 |

The era lengths above are campaign design input, not an engine fact: what
becomes available when is owned by `docs/progression/`. The 60-day year and the
conversion arithmetic are the engine facts this file carries.

Day-based gates much above ~700 are effectively "never" for this campaign.

**Gating principle:** set day gates to the EARLIEST plausible entry into the
target era, and let `rootMinPoints` (which tracks colony strength) hold the
line. An available quest can be ignored; an absent one cannot be summoned.

## Odyssey space layer

| Layer | radius | subdivisions |
|---|---|---|
| Surface (Core) | 100 | 10 |
| Orbit (Odyssey) | 130 | **5** |

Tile count is exactly **`12 + 10 × (3^subdivisions − 1)`** — it scales with
**~3^subdivisions, not ~4^**. `PlanetLayer.Subdivide` emits one new vertex per
triangle and one triangle per (vertex, adjacent-triangle) pair, so triangles
triple each pass and the surviving degree-5/6 vertices are the tiles. That gives
**2,432 tiles at subdivisions 5 and 7,292 at 6**. Orbit therefore has orders of
magnitude fewer tiles than the surface. `PlanetLayerDef.Orbit` sets
`settlementsPer100kTiles` to `1000~1000` (one per ~100 tiles), so few tiles also
means few settlements, asteroids and sites — roughly 9 at subdivisions 5 and 27
at 6.

*This file previously stated ~4^, which was wrong; `docs/traps/world-creation.md`
T-45 and `Archinity.Pacing/Patches/Orbit_LayerSize.xml` both carried the correct
law. Corrected from [#150](https://github.com/cjd721/Rimworld-Archinity/issues/150).
Verified against 1.6.4871 rev590.*

**Our change, not vanilla:** `Archinity.Pacing` raises the orbit layer's
subdivisions to 6 — `Archinity.Pacing/Patches/Orbit_LayerSize.xml`, a
`PatchOperationReplace` on
`/Defs/PlanetLayerSettingsDef[defName="Orbit"]/settings/subdivisions` **[V]**.
Vanilla Odyssey ships 5, as tabled above. **This matters beyond tile count:** the
orbit grid is ~3× denser than the one Odyssey's own constants were chosen for, so
orbit tiles run roughly √3 finer, and **T-45** means the geometry is rebuilt from
scribed values — *which* grid a given save carries depends on when its world was
made. **A threshold derived from orbit grid geometry is not stable across our own
saves**; author it per layer instead of deriving it
([#150](https://github.com/cjd721/Rimworld-Archinity/issues/150)).

### Cross-layer budgets, gates and the selected layer

- **`PlanetLayerDef.rangeDistanceFactor` is vanilla's own tile-budget conversion
  between layers** — `Orbit` sets **20** — consumed by
  `CompPilotConsole.GetMaxLaunchDistance` as
  `MaxLaunchDistance / layer.Def.rangeDistanceFactor` **[V]**. It is the shipped
  precedent for the *shape* of a per-layer threshold, not a number to inherit:
  it was chosen against vanilla's subdivisions-5 grid, which `Archinity.Pacing`
  replaces (above).
  ([#150](https://github.com/cjd721/Rimworld-Archinity/issues/150))
- **`Orbit` carries four separate whitelist gates plus `isSpace true`** —
  `onlyAllowWhitelistedIncidents`, `onlyAllowWhitelistedGameConditions`,
  `onlyAllowWhitelistedArrivals`, `onlyAllowWhitelistedArrivalModes` — each with a
  different reader and a different XML key **[V]**. See **T-48** for what that
  collapses, and the entry below for the fifth, building-level gate.
  ([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147),
  [#150](https://github.com/cjd721/Rimworld-Archinity/issues/150))
- **`PlanetLayerDef.layerType` is XML-settable but pinned into the save**: the
  layer is scribed `LookMode.Deep`, so a changed `layerType` does not reach an
  existing world **[V]**. Same shape as **T-45**.
  ([#148](https://github.com/cjd721/Rimworld-Archinity/issues/148))
- **`PlanetLayer.CanReachLayer` is the engine's cross-layer flight gate and it is
  effectively unused** — `PlanetLayer.TryGetPath` is its only consumer **[V]**.
  Nothing in `CompPilotConsole`'s validator or `CompLaunchable.ChoseWorldTarget`
  consults a reveal or unlock state **[V]**, so greying the view-orbit gizmo does
  not close the flight path.
  ([#148](https://github.com/cjd721/Rimworld-Archinity/issues/148))
- **`WorldSelector.set_SelectedLayer` is the sole writer of the selected layer**,
  and therefore the single chokepoint for anything that wants to police which
  layer the player is looking at **[V]** — but see **T-133** for the bypass.
  ([#148](https://github.com/cjd721/Rimworld-Archinity/issues/148))
- **`LayerConnection.fuelCost` defaults to zero**, and the scenario-injected
  Surface↔Orbit pair sets none **[V]** — the layer hop itself is free; the
  chemfuel a launch costs is the launch, not the hop.
  ([#148](https://github.com/cjd721/Rimworld-Archinity/issues/148))
- **There is a fifth layer gate, at the building rather than the layer.**
  `CompProperties_Mannable.planetLayerWhitelist`, read twice in `CompMannable`
  (`CompInspectStringExtra`, `CompFloatMenuOptions`), both emitting
  `CannotFunctionOnLayer` **[V]**. Vanilla sets `Surface` on the abstract
  `BaseArtilleryBuilding`, whose only concrete child is **`Turret_Mortar`** — so
  **mortars cannot be manned in orbit**, loudly, with the reason in the float
  menu. Automatic turrets are unaffected. The lever is a `PatchOperationAdd` of
  `<li>Orbit</li>` to that comp — XML, Easy **[I]** that the patch alone
  suffices. ([#147](https://github.com/cjd721/Rimworld-Archinity/issues/147))

Faction placement on the orbit layer is controlled by `FactionDef.layerWhitelist`
/ `arrivalLayerWhitelist` / `neutralArrivalLayerBlacklist`. Odyssey's own
`TradersGuild` and `Salvagers` are the working templates.

`settlementWorldObjectDef` lives on `PlanetLayerDef`, not `FactionDef`, so all
orbit factions share one base type by default. Better Traders Guild works around
this with a `PatchOperationSequence` on `SpaceSettlement` — same approach
available to us.

## Road network — the runtime write, the pather and the redraw

Read for [#68](https://github.com/cjd721/Rimworld-Archinity/issues/68)'s second reopen; the build
that uses them is `docs/specs/WORLD-INFRASTRUCTURE.md` § 3.

- **`WorldPathing.FindPath(PlanetTile, PlanetTile, Caravan, Func<float, bool>)`** — one pather per
  layer (`PlanetLayer.Pather`). The A\* edge cost is
  `ticksPerMove × WorldPathGrid.layerMovementDifficulty[tile] × WorldGrid.GetRoadMovementDifficultyMultiplier(from, to)`,
  with 3300 for a null caravan, so **the live road multiplier is inside the cost** and new paths
  prefer existing roads. It rejects only `World.Impassable` tiles, draws **no `Rand`**, and returns a
  pooled `WorldPath` the caller must `ReleaseToPool()`.
- **`WorldGrid.OverlayRoad(from, to, def)`** is the only road writer: null def → `Log.ErrorOnce`;
  same def → return; existing `priority` ≥ new → **silent** return (**T-43**); otherwise both
  symmetric links are replaced. **It marks nothing dirty** — every caller redraws for itself.
- **`WorldPathGrid` has no road term**, and `Caravan_PathFollower.CostToMove` reads the multiplier
  live, so a road write leaves no cache to clear.
- **Redraw.** `WorldRenderer.SetDirty<T>(PlanetLayer)` flags one layer type
  (`WorldDrawLayer_Roads` for roads), regenerated on its next draw; there is no per-edge redraw.
  `SetAllLayersDirty()` also dirties `WorldDrawLayer_Terrain`, and the *"GeneratingPlanet"* long
  event is queued only from `WorldRenderer.DrawWorldLayers`, when a visible `WorldDrawLayer_Terrain`
  is dirty.

See also `docs/engine/factions-and-worldgen.md` for faction generation, and
`docs/engine/quests.md` for how day gates and `rootMinPoints` are consumed.
