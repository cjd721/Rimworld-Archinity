# VEF Outposts (`Outposts.dll`)

The outpost engine ships inside Vanilla Expanded Framework (`2023507013/1.6/Assemblies/Outposts.dll`),
not in Vanilla Outposts Expanded. Content carriers: VOE (`2688941031`, 13 defs on 1.6) and VFE
Classical (`2787850474`, 4 defs, same defNames as VOE's Farming/Hunting/Logging/Mining). Multiplayer
defects and the harness: `specs/TERRITORY.md` §2. Cost and staffing routes: § *What an outpost
costs*. Upkeep as events: § *An outpost's upkeep arrives as events*.

## Who is committed
- Founding validates over `Utils.HumanColonists` = `Pawn.IsFreeColonist` — **slaves count, prisoners do
  not** (1.6: a slave's host faction is null and it is secure off-map).
- The founding commit (`Dialog_CreateCamp.DoOutpostDisplay`) calls `AddPawn` on **every** caravan pawn —
  prisoners and animals included.
- `Utils.CanAddPawn` is the only per-pawn gate, and it checks only the ideology `Event`.
- `Outpost.IsCapable` = humanlike, has skills, no relevant skill totally disabled. Prisoners and slaves
  produce; animals are occupants that produce nothing.
- Entry paths: founding, the caravan "Add" gizmo, `TransportPodsArrivalAction_AddToOutpost`. All go
  through `AddPawn`.

## What they get
- The outpost ticks rest (night), food from `ProvidedFood` (conjured, free), chemical needs (pinned full; addictions
  and dependencies zeroed), hediffs, and tending from its own medicine. Mood, suppression and every other need are not ticked;
  occupants are not world pawns. No rebellion, escape or mental break at an outpost.

## An occupant's life at a VEF outpost — what already ticks

VEF `Outposts.Outpost` [V]:

- `Tick()` runs every tick. At `PawnCount == 0` it sends *"Abandoned"* and destroys the outpost.
  While `Map == null` it runs `SatisfyNeeds` → `OutpostHealthTick`. The per-tick `Hediff.Tick` is
  mostly empty in 1.6.
- `TickInterval(delta)` counts down packing (`ConvertToCaravan` at zero) **or** production, never
  both, and runs `SatisfyNeedsInterval` → `OutpostHealthTickInterval`: disease progression, injuries,
  bleeding, tending, healing, aging, rest and food all live on this path.
- **Tending spends whole stacks.** It picks the healthy humanlike with the best Medicine skill;
  `OutpostHealthTickInterval` pulls every "best so far" medicine stack out of `containedItems` with
  `TakeItem`, and `TendUtility.DoTend` decrements the last one, which is never returned. A delivery
  of N medicine buys about one tend per stack [V].
- **Only a death on the per-tick path is cleaned up.** `SatisfyNeeds` removes a pawn that died inside
  its own `OutpostHealthTick` and stores the corpse. A death from disease or bleeding happens on the
  interval path, so the dead pawn stays in `occupants`, still counts and still produces, and the
  outpost is never abandoned (T-152) [V code; in play I].
- Food comes from `ProvidedFood`, conjured free with no stock.
- Mood and other needs are not ticked (per #170).

So disease, injury and a medicine shortage are live mechanics at an outpost. Hunger is not, and
death needs handling of ours.

## Limits and floors
- No count cap. `CanSpawnOnWithExt` rejects only a tile at/adjacent to a settlement base or next to
  another outpost.
- `MinPawns` / `RequiredSkills` are founding checks. Afterwards Remove is disabled only at one occupant
  and `Tick()` abandons only at zero.
- `MinPawns`, `Range`, `TicksPerProduction`, `TicksToPack` are `[PostToSetings]` (mod settings, T-18).
- `TicksToSetUp` is declared and never read: there is no build time.
- `CostToMake` is charged once, when the caravan's last humanlike joins (T-149).
- A second founding gate is available without Harmony: after `CanSpawnOnWithExt` passes, the dialog
  reflects for `public static string CanSpawnOnWith(PlanetTile, List<Pawn>)` on the def's
  `worldObjectClass`.
- Occupants drop out of the storyteller's population (T-148).
- An outpost has no map; a map generated on its tile is adopted (`Encounter` fallback) and never
  removed (T-150).
- `Outpost.Destroy()` on a staffed outpost discards its living pawns; `OutpostsMod.Notify_Removed` is
  empty (T-151).

*[#170](https://github.com/cjd721/Rimworld-Archinity/issues/170),
[#171](https://github.com/cjd721/Rimworld-Archinity/issues/171). `2023507013/1.6/Assemblies/Outposts.dll`;
1.6 `Assembly-CSharp.dll`.*
