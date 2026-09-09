# Factions and worldgen

How the faction roster is built, how many settlements each faction gets, what is
authorable as defs, and what happens when a faction changes tier mid-campaign.

Verified against decompiled RimWorld 1.6.4566 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

Worldgen material is from
[How the world starts, and how it changes](https://github.com/cjd721/Rimworld-Archinity/issues/8),
decompiled from `Assembly-CSharp.dll` (1.6.4566).

---

## The roster must be final before world creation

**Adding a `FactionDef` to an already-generated world does nothing, and says
nothing** — see `docs/TRAPS.md` T-07 for the mechanism and evidence. For a single
long co-op run this is a **one-time hard gate**, and it is the most consequential
silent failure in the project: a roster mistake is not a patch, it is a new world.

There is a C# escape hatch — `FactionGenerator.CreateFactionAndAddToManager(layer, def)`
is public static — but it is a repair, not a plan.

Recorded here because it is load-bearing for the world-roster decision and
previously lived only in `docs/archive/sys/05-factions.md`, which is archived
prose rather than the fact store.

⚠️ **One shipped mod breaks the freeze from inside the game.**
`VFET_OpportunitySite_WildMen` generates and adds a faction at runtime, only for a
Neolithic player — which is precisely our Neolithic — and with no reuse guard, so
it can fire more than once (`docs/TRAPS.md` T-15). A frozen roster cannot survive
it.

`requiredCountAtGameStart` is dead code in 1.6 and must not be used as a lever
(`docs/TRAPS.md` T-09). The live levers are in *The roster is authorable as defs*
below.

---

## How many settlements a faction gets

### The algorithm

`FactionGenerator.GenerateFactionsIntoWorldLayer`, called once per planet layer
from `WorldGenStep_Factions.GenerateFresh`:

1. **Instance creation.** `InitializeFactions` walks
   `Current.CreatingWorld.info.factions` and creates one `Faction` per **admissible**
   entry — entries failing `CanExistOnLayer` (`layerWhitelist` / `layerBlacklist`)
   are skipped (`:66-72`).
2. **One free settlement per instance.** `NewGeneratedFaction` (`:175`) places a
   settlement for every created faction where `!faction.Hidden && !def.isPlayer`.
   (`Faction.Hidden => hidden ?? def.hidden`.)
3. **The bulk pool.**
   `RoundRandom(TilesCount / 100000f * settlementsPer100kTiles * populationScale * viewAngleFactor)`
   (`:36`), **minus `Find.WorldObjects.AllSettlementsOnLayer(layer).Count`** (`:37`)
   — which is *every* settlement on the layer, not only step 2's. Identical at
   worldgen; not identical if a mod's gen step places settlements first.
4. **Distribution.** Each remaining settlement independently picks a faction via
   `RandomElementByWeight(x => x.def.settlementGenerationWeight)` (`:40`) **over
   faction instances**, filtered by
   `!def.isPlayer && !Hidden && !temporary && CanExistOnLayer` (`:52-59`). That
   `:40` is `settlementGenerationWeight`'s **only** use site in the assembly
   outside its declaration.

**Surface declares neither `settlementsPer100kTiles` nor
`viewAngleSettlementsFactorCurve` in XML**, so the C# defaults apply:
`FloatRange(75, 85)` per 100k tiles and a flat 1.0 curve. Orbit declares
`1000~1000` and a curve falling to 0.5 at full view angle.
`OverallPopulation` scale factors: AlmostNone 0.1 / Little 0.4 / LittleBitLess
0.7 / Normal 1 / LittleBitMore 1.5 / High 2 / VeryHigh 2.75.

Per-layer behaviour, including which layers exist, is in
`docs/engine/world-time-and-layers.md`.

### The consequence that matters for design

**Total settlement count scales with planet coverage and population, never with
faction count.** More factions on a fixed planet means each gets a thinner slice.
Share is `(instances × weight) / total` — linear in both — **but only over the
remainder left after every non-hidden faction's freebie.** With a large roster the
freebies consume the pool and weight stops being a usable size dial.

Measured default rosters (non-hidden instances, with the `replacesFaction` prune
applied as `ResetFactionCounts` does it): **DLC floor 9; DLC + every
faction-bearing mod on disk 33; same minus the declined mods 26.** Vanilla lands
at 9, which is why Ludeon never needed to clamp the defaults.

**Hidden factions are free.** Both the settlement-lottery `Validator` and the
freebie are gated on `!Hidden`, so hidden ambient factions cost no map presence.

---

## The roster is authorable as defs

`Page_CreateWorldParams.ResetFactionCounts()` reads **only**
`maxConfigurableAtWorldCreation`, `startingCountAtWorldCreation`,
`configurationListOrderPriority` and `replacesFaction`. So a `PatchOperation`
fully authors the default roster:

| Field | Effect |
|---|---|
| `startingCountAtWorldCreation: N` | N instances on the page by default |
| `startingCountAtWorldCreation: 0` | dropped from defaults, still addable |
| `maxConfigurableAtWorldCreation: 0` | removed from defaults *and* the Add menu |
| `displayInFactionSelection: false` | row hidden **and removed from the Add… menu** (`WorldFactionsUIUtility.cs:64`), faction still generates |

⚠️ The `replacesFaction` prune (`Page_CreateWorldParams.cs:81-87`) runs over
**every** configurable def, including ones at `startingCountAtWorldCreation: 0`
that never entered the list — so a def we exclude can still delete a def we kept
(`docs/TRAPS.md` T-10).

An example of the second row in the wild: **VFEM2 ships `VFEM2_KingdomRough`,
`KingdomSavage`, `ClanSavage` and `CivilClan` at `startingCountAtWorldCreation =
0`**, so a default world gets only two visible Medieval factions. All have
`maxConfigurableAtWorldCreation 9999`, so add them by hand at world creation.

**No ScenPart route exists.** All **43** `ScenPart_*` classes in 1.6 were
enumerated; **none touches the world-creation faction list.** Two scenario hooks
are faction-aware and neither helps: `ScenPartDef.preventRemovalOfFaction`, read
at one site (`WorldFactionsUIUtility.DoRow`) where it hides a delete button; and
`ScenPart_PlayerFaction` (`ScenPart_PlayerFaction.cs:10,48,53-54`), which holds a
`FactionDef` and *does* create a faction in `PostWorldGenerate` — but it sets the
**player** faction and never touches the roster.

**VEF supplies a removal lock.** `VEF.Factions.FactionDefExtension.forcedFactionData`
→ `preventRemovalAtWorldGeneration` + `requiredFactionCountAtWorldGeneration`
re-inserts a deleted entry at the same index. Safe: it runs in the world-creation
UI, before any save exists.

> ⚠️ **`forcedFactionData`'s gameplay-backfill half stays forbidden.**
> `requiredFactionCountDuringGameplay` / `forceAddFactionIfMissing` /
> `forcePlayerToAddFactionIfMissing` run from a `GameComponentUtility.LoadedGame`
> postfix — per client, outside any synced command, consuming `Rand` while
> mutating `FactionManager` and `WorldObjects`. Never set them.

### Faction Customizer cannot remove factions

Verified against 1.6.4871. `azravos.factioncustomizer`'s entire Harmony surface is
eight UI patches. `FactionManager.Remove` / `defeated` / `deactivated` appear zero
times. It can add, rename, recolour and move settlements, and nothing else. Zero
MP sync and `Rand`-heavy mutations, so it is **pre-landing use only**. Its
settings file is missing from `config/ModSettings/`.

### The 12-faction cap is a UI guard only

`WorldFactionsUIUtility` declares `private const int MaxVisibleFactions = 12`.
The constant is inlined at **three** sites — the tooltip (`:32`), the guard
(`:147`) and its message (`:149`) — but **only `:147` enforces anything**, inside
a local `CanAddFaction` called from the `"Add..."` float-menu loop.
`ResetFactionCounts`, `CanDoNext` and `WorldGenerator.GenerateWorld` are
unchecked, so defaults may exceed 12 and the game generates all of them.

**VEF transpiles the constant to 99**, unconditionally and with no settings gate
(`VEF.Planet.…CanAddFaction_Patch:100-105`, a blind `ldc.i4.s 12 → ldc.i4 99`
sweep). ⚠️ It is scoped to the `CanAddFaction` local function only, **so the
tooltip at `:32` still says 12** — a UI that contradicts the live cap. World Tech
Level patches this same UI too (`Patch_WorldFactionsUIUtility.cs:35`).

---

## Climbing a faction by swapping `Faction.def`

**The mechanism is sound.** `Faction.def` is `public FactionDef def;`
(`Faction.cs:14`), scribed via `Scribe_Defs.Look(ref def, "def")`
(`:272`), so a swap persists across save/load. Vanilla writes it exactly once, at
`FactionGenerator.cs:135` — **there is no engine-blessed swap path and no
invalidation hook**, which is the source of every leak below.

Swapping the *def reference* is the supported move. Writing `FactionDef.techLevel`
in place is not: it silently reverts on load and mutates every faction sharing the
def (`docs/TRAPS.md` T-11).

### What survives a swap

- **`Faction.relations` is instance-keyed.** `FactionRelation.other` is a
  `Scribe_References` to a `Faction`, compared by reference in
  `Faction.RelationWith`. Every relationship survives.
- **`Faction.Name` and `Settlement.nameInt`** are set once and never re-derived.
- **Layout selection reads the current def at map-generation time**, and
  settlement maps generate on first visit (`SettlementUtility.cs:47`,
  `GetOrGenerateMapUtility.GetOrGenerateMap`, guarded on `!settlement.HasMap`) —
  so a faction that climbed unseen builds its new tier's base when you arrive.
  Three distinct sites:
  - `KCSG.Postfix_Settlement_MapGeneratorDef` patches the `Settlement.MapGeneratorDef`
    getter and reads `__instance.Faction.def` (`:19,21`) — **no null guard on `.def`**.
  - `KCSG.GenStep_Settlement.ScatterAt` reads **`map.ParentFaction.def`**, not the
    settlement's, and hard-NREs if the `CustomGenOption` extension is missing.
  - **Vanilla `RimWorld.GenStep_Settlement.ScatterAt` does not dereference
    `Faction.def` at all** — it passes the live `Faction` into `ResolveParams`, and
    the deref happens downstream in `SymbolResolver_Settlement.cs:23,70`. VEF
    separately transpiles that vanilla method to read `faction.def` for
    `settlementGenerationSymbol`.

  The KCSG side of this is covered in `docs/engine/mods/kcsg.md`.
- **`TraderKind`** is computed live per access from `def.baseTraderKinds` and
  `HashOffset()`. Deterministic, no `Rand`.
- **Defenders** are generated at map-gen from the current `def.pawnGroupMakers`.
- **`Faction.Hidden`** is `hidden ?? def.hidden`, and `hidden` is null on the
  standard worldgen path — so a swap can unhide a faction.

### What breaks, and the fix

| Leak | Detail | Fix |
|---|---|---|
| `Settlement.cachedMat` | caches texture **and** colour from the def on first draw (`Settlement.cs:20,68-78`); **never nulled anywhere in the assembly**, not scribed (`docs/TRAPS.md` T-12) | null by reflection |
| `Faction.Color` | retained `colorFromSpectrum` resamples the **new** def's `colorSpectrum` | same spectrum per tier, or set `color` |
| `Faction.allegianceColor` | lazily computed **and scribed** (`"mechColor"`) | null it in the command |
| `Faction.leader` | never regenerated; `TryGenerateNewLeader` only fires on leader death/loss | regenerate — costs `Rand` |
| Trade stock | `RegenerateStock` only on null/empty or a 30-day boundary | `TryDestroyStock()` |
| Hostility | `TryMakeInitialRelationsWith` runs only at creation. Afterwards `CanChangeGoodwillFor` (`Faction.cs:533-548`) consults the **new** def — so goodwill **freezes where it stood** if that def sets `permanentEnemy`, `permanentEnemyToEveryoneExceptPlayer`, or a `permanentEnemyToEveryoneExcept` list omitting the other party. **Only for permanent-enemy defs**, not as a general consequence of a swap | write goodwill explicitly when climbing into hostility |
| `FactionUtility.DefaultFactionFrom` | resolves `AllFactions.Where(x => x.def == ft)`, falling back to `replacesFaction`, else **null** — orphans any `PawnKindDef.defaultFactionDef` (`docs/TRAPS.md` T-13) | set `replacesFaction` on higher tiers pointing down the chain |
| `Faction.ideos` | created only if `humanlikeFaction`, from the **worldgen** def; never regenerated, so later defs' `fixedIdeo`/`forcedMemes` are ignored | not a bug — but **author creeds on the worldgen def** |
| `FactionManager` singletons | `Faction.OfEmpire`/`OfPirates`/… recache via a **private** `RecacheFactions()` reachable from `Add`/`Remove`, and `Add` early-returns for an existing faction | only bites if a climb def *is* a `FactionDefOf` def |

⚠️ **`Faction.leader` regeneration has a landmine:** `Faction.cs:1185` reads
`ideos.PrimaryIdeo.SupremeGender` with no null guard. Swapping a non-humanlike
faction to a humanlike def leaves `ideos` null and this NREs.

**No `[Unsaved]` fields exist on `Faction` at all.** The seven `[Unsaved]` fields
in this area are on `FactionDef` and are therefore per-def — they follow the new
def correctly.

### `WorldObject.SetFaction` is a bare field write

```csharp
public virtual void SetFaction(Faction newFaction) { ...warn if !def.canHaveFaction...; else factionInt = newFaction; }
```

That is the whole method, and `Settlement` does not override it. A transferred
settlement keeps its name, its stock and (if the map already exists) its pawns.
**Nothing notifies** `FactionManager`, `Map.events`, `attackTargetsCache` or
`LordManager` — compare `Faction.Notify_RelationKindChanged`, which does all of
it. **`Settlement.previouslyGeneratedInhabitants` is a non-hazard in 1.6.** The
read path (`PawnGenerator.cs:209-219`) is real, but the **only add site**
(`:235-237`) is
`if (request.Inhabitant && !request.Tile.Valid) Find.WorldObjects.WorldObjectAt<Settlement>(request.Tile)?...Add(result)`
— with an invalid tile the lookup returns null and `?.` no-ops, so **the list is
never populated** (a vanilla inversion bug). Old-tier pawns cannot resurface in a
climbed settlement unless the save is legacy or a mod populates the list.

### Multiplayer

**Nothing is covered for free.** `Multiplayer.dll` registers **no `SyncMethod`
for `WorldObject.SetFaction` and no sync of any `FactionDef` mutation**; only
`allowRoyalFavorRewards` and `allowGoodwillRewards` are synced on `Faction`.
Arguments serialize fine — `Faction` has an explicit sync worker keyed on
`loadID`, and all `Def` subclasses are handled generically.

**The minimal command consumes no `Rand`** (a def write plus a `SetFaction`).
`Rand` enters with leader regeneration, name generation, colour-from-spectrum,
stock regeneration, `new Faction()` and `DefaultFactionFrom` — each of which must
therefore sit inside the same synced command.

The general model — what desyncs, and why `Rand` is the axis — is in
`docs/engine/determinism.md`.

---

## Raid faction selection

Verified against 1.6.4871.

**Raid faction choice has no tech weighting.**
`UsableFactions(...).TryRandomElementByWeight(f => RaidCommonalityFromPoints(points) * (lastRaidFaction ? 0.4 : 1))`.
Ignorance Is Bliss gates via a postfix on `FactionCanBeGroupSource`.

Empty-pool behaviour is **fail-open and fail-quiet** (`docs/TRAPS.md` T-17).

Two further constraints on anything authored here: `RaidStrategyDef` has no
`minTechLevel` field, so every tech gate is worker code (`docs/TRAPS.md` T-16);
and any `RaidStrategyDef` we author is silently excluded from the VFE Empire
deserter faction (`docs/TRAPS.md` T-14).

---

## Faction composition and containment

Neither VRE Starjack nor VRE Archon injects xenotypes into vanilla factions.
Starjack has zero `xenotypeChances` anywhere; Archon ships its own hidden
faction. The only Starjacks on the planet come from Odyssey's own Traders Guild
(25%) and Salvagers (10%) defs, which is vanilla intent.

`Archinity_ArchonianSanguophage` sets `canGenerateAsCombatant: false` and
`factionlessGenerationWeight: 0` so it can never spawn on anyone but the player.

---

## Smaller faction facts

- **`VFET_WildMen` is a *player* faction** (`isPlayer true`). The NPC def is
  `VFET_WildMenGroup`, hidden, `techLevel Animal`. It never enters the roster
  because `maxConfigurableAtWorldCreation` is left at the **C# default of `-1`**
  (`FactionDef.cs:140`) — neither the def nor its parent authors it. Its *authored*
  gates are `canMakeRandomly false` and `maxCountAtGameStart 0`, **both of which
  are the obsolete no-ops of `docs/TRAPS.md` T-08** — so it stays out by accident,
  not by design.
- **`BTG_IndependentTraders` is also a player faction.** Better Traders Guild
  ships no non-player FactionDef; it patches Odyssey's `TradersGuild` (**two
  operations**, three `PatchOperation` elements counting one nested inside a
  conditional; none count-related) and Royalty's `Empire`.
</content>
</invoke>
