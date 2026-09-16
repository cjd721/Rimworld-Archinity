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

Tile count scales ~4^subdivisions, so orbit has orders of magnitude fewer tiles
than the surface. `PlanetLayerDef.Orbit` sets `settlementsPer100kTiles` to
`1000~1000` (one per ~100 tiles), so few tiles also means few settlements,
asteroids and sites.

**Our change, not vanilla:** `Archinity.Pacing` raises the orbit layer's
subdivisions to 6. Vanilla Odyssey ships 5, as tabled above.

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
