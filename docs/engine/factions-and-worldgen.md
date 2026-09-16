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

### Runtime faction *instances* are ordinary — vanilla makes and removes temporary ones

T-07 is about the **def roster**. It does not mean a faction instance cannot appear mid-game.
Vanilla creates them routinely and cleans them up itself. Verified against 1.6.4871.

- **Three quest roots create one each.** `QuestNode_Root_Beggars`, `QuestNode_Root_Bossgroup` and
  `QuestNode_Root_Hospitality_Refugee` each call `FactionGenerator.NewGeneratedFactionWithRelations`,
  set `faction.temporary = true` and call `Find.FactionManager.Add` [V].
- **Only temporary factions can be removed.** `FactionManager.Remove` logs an error for any other
  faction [V]. Removal is queued (`QueueForRemoval`) from `Notify_QuestCleanedUp`,
  `Notify_PawnKilled`, `Notify_PawnLeftMap`, `Notify_PawnLeftFaction` and
  `Notify_WorldObjectDestroyed`, whenever `FactionCanBeRemoved` holds [V]. `FactionCanBeRemoved`
  requires the faction to be temporary, reserved by no quest, and referenced by no spawned or
  caravan pawn and no world object [V]. The queue drains in `FactionManagerTick` [V].
- **Many consumers skip temporary factions.** Among them are raid sources
  (`FactionCanBeGroupSource`), the comms console list, and royal-favour and trader pickers [V].
- **`QuestPart_InnerFactionFight` splits a map's pawns into two sides** [V]. It sends every other
  pawn in a list into a freshly generated temporary faction and gives each side a
  `LordJob_AssaultThings` against the other. It completes when one side is all downed or destroyed.
  **Nothing in vanilla calls it**: only its `QuestGen` extension references it.
- **`QuestPart_SetFactionHidden` writes `Faction.hidden` at runtime** [V]. This is how a faction
  hidden at worldgen can be revealed from a quest. There is no XML node for it; the `quest.SetFactionHidden`
  extension is C#.

What forbids a new faction in the campaign is a **requirement**
(`docs/requirements/RELIGION.md` § *Revolt*), not the engine.
Established on [#131](https://github.com/cjd721/Rimworld-Archinity/issues/131).

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
>
> **VFE Empire sets the forbidden fields on a faction it ships.** `VFEE_Deserters`
> (`2938820380/1.6/Defs/FactionDefs/Factions_Hidden.xml`) carries `forcedFactionData` with
> `requiredFactionCountDuringGameplay 1` and `forceAddFactionIfMissing true`, under
> `MayRequire="OskarPotocki.VFE.Deserters"`. With VFE Deserters loaded, a world missing that
> faction — World Tech Level strips it (**T-54**) — gets it re-created by
> `VanillaExpandedFramework_GameComponentUtility_LoadedGame_Patch` on each client's load. A world
> that already holds it is untouched. ([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130))

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

### `AttackTargetsCache` indexes hostility at registration, not at query

The same shape one level down, on `Thing` rather than `WorldObject`, and reusable
well beyond a faction climb.

`Verse.AI.AttackTargetsCache.RegisterTarget` builds `targetsHostileToFaction` by
evaluating `thing.HostileTo(faction)` **once per faction as the target registers**,
and `GetPotentialTargetsFor` reads that dictionary back [V]. `UpdateTarget` is a
deregister/re-register pair and is the **only** thing that refreshes the index for a
live target.

**`Thing.SetFaction` calls `UpdateTarget`; `Thing.SetFactionDirect` does not** [V] —
`SetFaction` alone also raises the `ChangedFactionToPlayer` quest signal and
`Map.events.Notify_ThingFactionChanged`. So any mid-map faction flip that wants the
map's AI to notice must go through `SetFaction`, or call `UpdateTarget` itself. A
building seized through `SetFactionDirect` stays in its old hostility bucket until
something else refreshes it, and a save/load re-registers every target, so the symptom
disappears on reload. That failure is silent and is `docs/TRAPS.md` **T-68**.

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

**`IncidentWorker_PawnsArrive.MustHaveSettlementOnLayer` is dead in 1.6.** The base
`FactionCanBeGroupSource` does reject a non-hidden faction with no settlement on the map's layer
when the property is true. But it is `protected virtual bool … => false`, and **no class
overrides it**: not in `Assembly-CSharp.dll` 1.6.4871, and not in any corpus dll (both
encodings, `-i`). A landless, visible faction is therefore a valid arrival source. The one live
settlement-on-layer gate is `QuestNode_GetPawn.mustHaveSettlementOnLayer`, an XML field.
This corrects [#70](https://github.com/cjd721/Rimworld-Archinity/issues/70)'s resolution.
([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130))

---

## Faction composition and containment

Neither VRE Starjack nor VRE Archon injects xenotypes into vanilla factions.
Starjack has zero `xenotypeChances` anywhere; Archon ships its own hidden
faction. The only Starjacks on the planet come from Odyssey's own Traders Guild
(25%) and Salvagers (10%) defs, which is vanilla intent.

`Archinity_ArchonianSanguophage` sets `canGenerateAsCombatant: false` and
`factionlessGenerationWeight: 0` so it can never spawn on anyone but the player.

---

## Two faction UIs, and they are not the same one

Established on [Reverence, end to end](https://github.com/cjd721/Rimworld-Archinity/issues/98).
The names are close enough to swap by accident, and an earlier spec did — pointing a whole
display design at a screen that exists only before a game does.

- **`RimWorld.Planet.WorldFactionsUIUtility`** is the **world-creation faction-selection
  screen**. It takes a `List<FactionDef>`, offers Add and Delete buttons, and warns about
  disabled content [V]. Its `MaxVisibleFactions = 12` guard is the *UI* cap described under
  *The 12-faction cap is a UI guard only*, above — not an engine limit. VEF's three patches —
  `…_CanAddFaction_Patch`, `…_DoRow_Patch`, `…_DoWindowContents_Patch` — are all on this
  screen. It has no faction *instances* in scope, only defs.
- **`RimWorld.FactionUIUtility.DrawFactionRow`** is the **in-game Factions tab row**: icon,
  name, leader, info-card button, ideo icons, the goodwill number with its relation-kind label,
  the natural-goodwill column, and the enemy-faction icon strip [V]. It is `private static`, so
  a Harmony patch cannot reach it by `nameof`. Column widths are declared `private const` —
  basics 300, info 40, ideos 60, relations 70, natural goodwill 54, over a fixed 80px row — but
  **the method body uses inlined literals rather than the consts**, so a postfix must hardcode
  them too. **The ideo column is 0 wide when Ideology is inactive or
  `Find.IdeoManager.classicMode` is on** — any postfix computing an x-offset must replicate
  that branch or draw in the wrong place.

**The row is crowded, and three mods are already in it** [V]:

| Mod | What it does to the row |
|---|---|
| **VFE Classical** (`VFEC.dll`) | prefix `SenatorUIUtility.DoSenatorInfoButton`, registered from a **static constructor** via `AccessTools.Method` rather than an annotated patch class |
| **RimPacts** (`RimPacts.dll`) | `Patch_FactionTabWarRow` — prefix + finalizer resolving the method through `TargetMethod()`, paired with a postfix on `FactionRelationKindUtility.GetLabelCap` that **rewrites the relation-kind label** |
| **Faction Territories** (`FactionTerritories.dll`) | prefix shrinks `fillRect.width` by 80 and a postfix draws a vassalage button in the freed strip — **the right edge is taken** |

Two more **fork** it rather than patching it, so a postfix on vanilla never reaches them: **Rim
War** and **Faction Customizer** each copy the whole method into their own faction window [V].

**Vertical space inside the columns is not free either.** The relation-kind and goodwill labels
are drawn into two 80px-tall rects at `rowY - 10` and `rowY + 10` with
`TextAnchor.MiddleCenter`, so their glyphs land at `rowY + 30` and `rowY + 50`; and the natural
goodwill column draws a black rect at exactly `rowY + 30` [V]. Anything added to this row needs
its own horizontal strip, and the obvious one is already Faction Territories'.

**The faction info card cannot be extended through the def's stat hook.**
`StatsReportUtility.StatsToDraw(Faction)` yields exactly one entry —
`DescriptionEntry(faction)` — and it is the *caller*, `DrawStatsReport(Rect, Faction)`, that
adds `faction.def.SpecialDisplayStats(StatRequest.ForEmpty())` [V]. The faction instance is in
scope in both; what is def-level is `FactionDef.SpecialDisplayStats`, which is handed an empty
`StatRequest`. So a per-faction number cannot arrive through the def hook, but postfixing
`DrawStatsReport` before `FinalizeCachedDrawEntries` is a real patch point.

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

## What `Notify_RelationKindChanged` already does to faction-owned things

Verified against RimWorld 1.6 (`Assembly-CSharp.dll`, the build `docs/data/MOD-SNAPSHOT.md` pins).

`RimWorld.Faction.Notify_RelationKindChanged(Faction other, FactionRelationKind previousKind,
bool canSendLetter, string reason, GlobalTargetInfo lookTarget, out bool sentLetter)` is `public`,
and is vanilla's convergence point for *"the political situation with this faction changed"*. It is
an instance method on the faction whose relation changed; `other` is the counterparty. **Read
`__instance`, not `other`, for the faction the change is about.**

Two of its routines are the shipped pattern for anything the player holds *with* a faction:

- **Hostile edge** — `other == OfPlayer && this.HostileTo(OfPlayer)`: walks
  `Find.WorldObjects.AllWorldObjects`, and for every object of that faction fetches
  `TradeRequestComp` and calls `Disable()` on an active request; then, per map,
  `map.passingShipManager.RemoveAllShipsOfFaction(this)`. **A standing arrangement is disabled, not
  destroyed; a transient one is removed outright.**
- **Friendly edge** — `other == OfPlayer && !this.HostileTo(OfPlayer)`: collects every site where
  `factionMustRemainHostile && site.Faction == this && !site.HasMap` (a site the player is standing
  on is left alone), and if any remain sends `LetterLabelSiteNoLongerHostile` / `…Multi` — the multi
  form building a bulleted `"  - " + LabelCap` list with a parenthesised pawn name per entry, plus a
  `LookTargets` over the tiles — before destroying them.

**Two scoping facts that are easy to get backwards:**

- **Those two branches** are each guarded on `other == OfPlayer`. **The method is not** — its
  prisoner-status sweep (converting mutual guests to prisoners on a hostility flip) and its
  attack-target-cache / lord block run for any pair.
- The body consults `Current.ProgramState` **three times**: once to suppress letters, once bracketing
  the prisoner sweep, and once as an early `return` before the map-cache block.

**It does not fire during world generation**, and a patcher should not guard against that. Both
worldgen relation-seeding paths bypass it: `Faction.TryMakeInitialRelationsWith` hand-constructs both
`FactionRelation` objects and appends them to the two `relations` lists itself, and
`FactionGenerator.NewGeneratedFactionWithRelations` reaches `Faction.SetRelation(FactionRelation)`,
which mutates `relations` directly. The one route that could fire early —
`GoodwillSituationManager.CheckHostilityChanged` → `Notify_GoodwillSituationsChanged` →
`CheckKindThresholds` — is itself guarded on `Current.ProgramState != ProgramState.Playing`, and
worldgen runs at `ProgramState.Entry`.

**A postfix still needs a `ProgramState.Playing` guard**, because the hook does reach it at
`ProgramState.MapInitializing` — during map generation and during load — through
`SettlementUtility.AffectRelationsOnAttacked` and `GoodwillSituationManager.RecalculateAll`. That is
the window in which a `WorldComponent` may not yet hold its records.

Established on [#73](https://github.com/cjd721/Rimworld-Archinity/issues/73); the system built on it
is `docs/specs/RELIGION.md` § *The build — religious institutions inside foreign factions*.

---

## Hidden factions, alliances, and what holds a relation

Verified against RimWorld 1.6.4871 (`Assembly-CSharp.dll`), on
[#130](https://github.com/cjd721/Rimworld-Archinity/issues/130).

**A hidden faction has no goodwill.** `Faction.HasGoodwill => !Hidden && !temporary`. While a
faction is hidden:

- `CanChangeGoodwillFor` refuses every change, in both directions, so quest goodwill rewards
  no-op.
- `CheckReachNaturalGoodwill` returns early.
- `GoodwillSituationManager.RecalculateAll` skips the faction.
- `Faction.SetRelationDirect` is the only way to set its relation kind. It works only while
  one side has no goodwill; when both do, it `Log.Error`s and returns.

**Revealing a faction hands its relation back to goodwill.** The relation keeps the
`baseGoodwill` worldgen gave it. `TryMakeInitialRelationsWith` → `GetInitialGoodwill` gives
−100 for permanent-enemy defs, −80 for `naturalEnemy`, and otherwise 0. The next recalculation
runs `CheckKindThresholds` against that number, so **a kind set directly while the faction was
hidden is re-derived on reveal**. An Ally at goodwill 0 becomes Neutral. Write goodwill in the
same command as the reveal.

**The reveal part.** `QuestPart_SetFactionHidden` flips `faction.hidden` on a signal. Vanilla
uses it for mid-game reveals: beggars, refugees, reliquary pilgrims, the worshipped terminal. No
`QuestNode` wraps it. Its `hidden` flag is unscribed (**T-116**).

**Alliance hysteresis.** `FactionRelation.CheckKindThresholds`:

| From | To | When |
|---|---|---|
| any but Hostile | Hostile | goodwill ≤ −75 |
| any but Ally | Ally | goodwill ≥ 75 |
| Hostile | Neutral | goodwill ≥ 0 |
| Ally | Neutral | goodwill ≤ 0 |

`Faction.CheckReachNaturalGoodwill` (every `FactionTick`, i.e. every tick) counts a timer while
base goodwill sits outside `[natural − 50, natural + 50]`. At 3,000,000 it steps at most 10
toward the band. **So drift alone cannot end an alliance while natural goodwill is ≥ −49 and no
situation caps max goodwill at ≤ 0.** Losses that are not drift:

- `Notify_MemberDied` / `Notify_MemberCaptured` → `GoodwillToMakeHostile`
- `GoodwillSituationWorker_AttackingSettlement`: a cap of −80 while the player attacks
- `SettlementProximityGoodwillUtility`: −30/−20/−10 every 900,000 ticks for a player settlement
  within 2/3/4 tiles

Natural goodwill is the sum of situation offsets: `NaturalEnemy` −130, `SameIdeo` +10, meme
pairs from −50 to +10.

**`Faction.defeated` has one vanilla writer**, `SettlementDefeatUtility.CheckDefeated`, when the
last base falls on a map. A faction emptied by `SetFaction` transfers is not defeated.

## Vanilla saves who started the game

`Game.InitNewGame` copies `GameInitData.startingAndOptionalPawns` into
`GameInfo.startingAndOptionalPawns`. That happens after `GameInitData.PrepForMapGen` has trimmed the
list to `startingPawnCount` and passed the left-behind optional pawns to the world with
`wasLeftBehindStartingPawn`. `GameInfo.ExposeData` saves the list by reference and drops nulls on
load. Vanilla reads it during play (`Pawn_InfectionVectorTracker`). The same method then calls
`Scenario.PostGameStart` and `GameComponentUtility.StartedNewGame`, the two game-start hooks. [V]

`ScenPart_ConfigPage_ConfigureStartingPawns_Xenotypes` with `requiredAtStart` fills
`GameInitData.startingXenotypesRequired`. `Page_ConfigureStartingPawns.ExtraCanDoNextReport` refuses
unless each required xenotype's count among the starting pawns **equals** its `count`. Quick-test
play (`Root_Play.SetupForQuickTestPlay`) bypasses the page. [V] Multiplayer's multifaction path
writes none of this (**T-114**, § 1d).

Established on [#134](https://github.com/cjd721/Rimworld-Archinity/issues/134).

---

## A `WorldObjectComp` added by XML patch backfills into an existing save

Verified against RimWorld 1.6.

`WorldObject.ExposeData` calls `InitializeComps()` on `LoadingVars` **from `def.comps`**, then
`comps[i].PostExposeData()` for each. Comps are therefore **rebuilt from the def at load and never
scribed as a collection**, so a `WorldObjectCompProperties` added to an existing `WorldObjectDef` by
`PatchOperationAdd` appears on every existing instance in an existing save rather than erroring.

`WorldObjectDef Settlement` already declares a `<comps>` list with five entries
(`Abandon`, `TradeRequest`, `FormCaravan`, `TimedDetectionRaids`, `EnterCooldown`), so one patch
reaches every settlement in the game. `WorldObjectComp` then offers `CompTick`, `CompTickInterval`,
`GetGizmos`, `GetCaravanGizmos`, `GetFloatMenuOptions(Caravan)`, `IncidentTargetTags`,
`PostDrawExtraSelectionOverlays`, `CompInspectStringExtra`, `GetDescriptionPart` and
`PostExposeData`.

**Not a trap:** `InitializeComps` wraps each instantiation in a try/catch and emits
`Log.Error("Could not instantiate or initialize a WorldObjectComp: " + ex)`, so a bad comp class
fails loudly.

Established on [#73](https://github.com/cjd721/Rimworld-Archinity/issues/73).

## Subordination — what the engine has, and what it does not

Verified against RimWorld 1.6 (`Assembly-CSharp.dll`, the build `docs/data/MOD-SNAPSHOT.md` pins).
Established on [Vassals — can we, and by which routes](https://github.com/cjd721/Rimworld-Archinity/issues/120);
the routes are `docs/specs/TERRITORY.md` §3.

- **There is no vassal relation.** `RimWorld.FactionRelationKind` is `Hostile`, `Neutral`, `Ally` —
  nothing else. Any overlord/vassal state is stored by whoever builds it.
- **Conquering a faction's last settlement marks the faction defeated.**
  `SettlementDefeatUtility.CheckDefeated(Settlement)` replaces the settlement with a
  `DestroyedSettlement` of the same faction and destroys it; if `HasAnyOtherBase` is false it sets
  `Faction.defeated = true` (a plain public field) and appends the "faction destroyed" line to its
  letter. A defeated faction then fails `Faction.CanChangeGoodwillFor` for every counterparty. Code
  that replaces settlements itself does not pass through this method.
- **Vanilla's ally perks key on `PlayerRelationKind == Ally`.**
  `IncidentWorker_RaidFriendly.FactionCanBeGroupSource` admits only allies;
  `StorytellerComp_FactionInteraction.MakeIntervalIncidents` scales incident counts by
  `StorytellerUtility.AllyIncidentFraction(fullAlliesOnly)` and **passes no faction** — the incident
  worker chooses; `VisitorGiftForPlayerUtility.ChanceToLeaveGift` is `0.25 ×` a wealth curve `×` a
  goodwill curve, zero while hostile.
- **A quest cannot be routed to a named faction from XML.** `QuestNode_GetFaction.IsGoodFaction`
  filters on hidden, `ofPawn`, `exclude`, permanent-enemy, relation kind, attack state and
  goodwill-reward flags — never on `FactionDef` or on any stored record.
