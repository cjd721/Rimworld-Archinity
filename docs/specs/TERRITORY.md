# Territory

## Purpose and scope

How the world map carries **places that are not the colony and are not a settlement** —
sites the player founds and runs, and sites where something happens whether or not the
player attends.

It satisfies [`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md) § *Trade and Logistics* —
*"Outposts, allies and subordinate territories must provide meaningful resources, people or
logistics rather than token vanilla outputs"* — and
[`docs/requirements/POLITICS.md`](../requirements/POLITICS.md)'s ally-aid beat, the battle
between two NPC powers at a tile the player may travel to.

This document owns **the world-site lifecycle**: what creates a world object, what advances
it on a clock, what resolves it, what it scribes, and what has to be a synced command. Two
capabilities land here —
[#92](https://github.com/cjd721/Rimworld-Archinity/issues/92) (the ally-aid battle) and
[#81](https://github.com/cjd721/Rimworld-Archinity/issues/81) (player-founded outposts with
real yields) — because they are one machine with two payloads.

It does **not** own:

- **Roads and vehicles** — [`WORLD-INFRASTRUCTURE.md`](WORLD-INFRASTRUCTURE.md) owns the
  world-map mobility ladder outright. Nothing here re-derives a road fact.
- **Vassalage and tithe** — [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35).
  §3 states the boundary.
- **The territory model itself** — which tiles a faction claims.
  [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2 settled that it is
  *"a claimed tile is one within a small radius of a visible settlement or outpost"*, and
  explicitly **not** a Dijkstra flood fill. §1's authored trigger names its factions directly
  and therefore does not consult it.
- **Settlement ownership and the era rite** — [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8).
- **Faction goodwill mechanics** — [`POLITICS.md`](POLITICS.md).

---

## The build

**Both capabilities are already-solved problems with worked reference implementations in the
corpus, and in neither case do we ship the mod that solved them.** #81's engine is a module
of a framework we already take, and needs a synchronization harness. #92's reference mod is
**declined by Conrad** ([#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2,
recorded in `docs/data/MOD-VERDICTS.md` § *Declined*), with the decline text stating that the
design *"is reimplemented in `Archinity.Core`"* — so #92 is a build, and the reference mod's
value is that we get to copy a design that is known to work rather than invent one.

### 0. The shared pattern

Five verified engine facts. **P1 and P3 are the rule for anything new we write; neither
selected build happens to use them** (§1 clocks off a `GameComponent`/`WorldComponent` tick,
§2's carrier clocks off `MapParent.TickInterval`). They are stated first because P2 is only
survivable *because* of how the selected carriers happen to be written, and a reader needs
the rule before the exception.

**P1 — `WorldObject.Tick()` runs every tick for every spawned world object, with or without a
map.** `WorldObjectsHolder.WorldObjectsHolderTick` copies `worldObjects` and calls `DoTick()`
on each; `DoTick()` calls `Tick()` unconditionally before anything else [V]
(`RimWorld.Planet.WorldObjectsHolder.WorldObjectsHolderTick`, `RimWorld.Planet.WorldObject.DoTick`).
`Tick()` in turn calls `CompTick()` on every `WorldObjectComp` [V]. **This is the clock of
choice for new code**: it has no rate to diverge.

**P2 — `WorldObject.TickInterval(delta)` is a gated path, and the gate is viewport-derived in
vanilla.** `DoTick` accumulates `tickDelta` and calls `TickInterval(tickDelta)` when
`tickDelta > UpdateRateTicks` or on a hash-offset interval, where

```csharp
protected virtual int UpdateRateTicks =>
    !WorldRendererUtility.WorldSelected ? 15 : 1;
```

[V], and `WorldRendererUtility.WorldSelected` resolves through `Find.CurrentMap` and
`Find.World.renderer.wantedMode` [V] — client-local viewport state.

**Multiplayer repairs it.** `Multiplayer.Client.Patches.VtrSyncWorldObjectPatch` prefixes
`WorldObject.UpdateRateTicks` and returns `Multiplayer.AsyncWorldTime.VTR` [V]
(`294100/2606448745/1.6/AssembliesCustom/Multiplayer.dll`). `VTR` is `1` when
`CurrentPlayerCount > 0` and `15` otherwise, and `CurrentPlayerCount` is mutated **only** from
the synced `CommandType.PlayerCount` world command [V]. So under Multiplayer the cadence is
identical on every client.

**Elapsed ticks are conserved either way** — `DoTick` passes the accumulated `tickDelta` into
`TickInterval(delta)` and consumers decrement by `delta` [V], so a timer does **not drift**. What
diverges without the patch is the **phase and granularity** at which the timer crosses zero —
which still means `Produce()` fires on a different tick on each client, taking any `Rand` inside
it with it. See *Failure and recovery*.

**§2's selected carrier is on the gated path, and that is fine for a stated reason.**
`Outposts.Outpost.TickInterval(int delta)` is where production lives [V]. `Outpost` does **not**
override `UpdateRateTicks`, so MP's prefix on the base declaration governs it and the cadence is
synced. The question arises and is answered; it would stop being answered the moment any subclass
of ours overrode the property.

**P3 — the tick gate for new code is `IsHashIntervalTick`.**
`Gen.IsHashIntervalTick(this WorldObject o, int interval)` resolves to
`Find.TickManager.TicksGame + o.ID.HashOffset()` [V] (`Verse.Gen.HashOffsetTicks`) — pure,
deterministic, staggered per object. `SitePartWorker_RaidSource.SitePartWorkerTick` is the worked
vanilla example: ticks every tick with no map, self-gates on
`sitePart.site.IsHashIntervalTick(2500)`, draws `Rand.MTBEventOccurs` inside that gate, writes
scribed state and fires a real consequence [V]. **Neither donor uses it** — both scan a global
list on a fixed `TicksGame % N` cadence — which is correct for them (a handful of objects) and
wrong for anything that could exist in the dozens.

**P4 — the outcome roll is seeded off the stream, not drawn from it.** Verbatim [V]
(`FactionTerritories.Invasions.Utility.RollWinner`,
`294100/3626725895/Assemblies/FactionTerritories.dll`):

```csharp
int num2 = Gen.HashCombineInt(tile, attacker.loadID);
num2 = Gen.HashCombineInt(num2, defender.loadID);
num2 = Gen.HashCombineInt(num2, (Find.TickManager != null) ? Find.TickManager.TicksGame : 0);
Rand.PushState(num2);
try { if (Rand.Value < attackerWeight / num) return attacker; return defender; }
finally { Rand.PopState(); }
```

The winner is a pure function of tile, both faction load IDs and the tick — independent of where
the shared stream sits, and the `finally` puts the stream back. `CODING_STANDARDS.md` § *The two
gates* rules `Rand` on a synced tick safe anyway; this shape is stronger and free. **Every
in-absentia outcome in this document uses it.**

**P5 — a `FloatMenuOption` on a world object is synced; a gizmo or a dialog is not.**
`Multiplayer.Client.SyncActions.Init` registers one `SyncAction` over
`WorldObject.GetFloatMenuOptions(Caravan)` and calls `SyncWorldObjCaravanMenus.PatchAll("GetFloatMenuOptions")`
[V]. `SyncAction.PatchAll` iterates `typeof(A).AllSubtypesAndSelf()` and patches each type's
**declared** method — MP deliberately enumerates subtypes rather than trusting one
base-declaration patch [V].

In `SyncAction.DoSync`, for each yielded option [V]:

```csharp
CS$<>8__locals0.original = syncAction.actionGetter(current);
Action action  = delegate { ActualSync(target, arg0, arg1, original); };
Action action2 = syncAction.actionWrapper(current, target, arg0, arg1, original, action);
syncAction.actionGetter(current) = action2 ?? action;
```

and the default `actionWrapper`, when the registration supplies none, is
`(…) => (Action)null` [V]. **So a `null` wrapper falls through to the sync path** — `ActualSync`
writes the sync command. `WorldObjectCaravanMenuWrapper` returning `null` for an option that did
not come from `CaravanArrivalActionUtility` therefore means *sync it normally*, not *do not sync
it*; its **non-null** branch is the special case, which swaps the closure's action to `sync` and
calls `original()` so the command is deferred behind the confirmation dialog. **Every option
yielded from `WorldObject.GetFloatMenuOptions(Caravan)` is synced, hand-rolled or not.**

What is outside the net is everything that is not a float-menu option on a world object:

| Commit shape | Synced by this registration? |
|---|---|
| Any `FloatMenuOption` from `WorldObject.GetFloatMenuOptions(Caravan)` | **yes**, via `ActualSync` |
| — the `CaravanArrivalActionUtility` subset | yes, and additionally deferred behind its confirmation dialog |
| A `Command_Action` gizmo on a `Caravan` | **no** — not a float-menu option; outside the registration entirely |
| A `Window` / `Dialog_*` button | **no** — same reason |

§1's attendance path is a float-menu option and is covered. §2's founding path is a
`Caravan.GetGizmos` postfix opening a `Window`, and is not. Both conclusions stand; the reason is
the shape of the commit, not a property of how the option was constructed.

**One mechanism, two world-object classes, and the reason is map ownership.** State, persistence,
clock, roll and sync are the same. What differs:

| | #92 — ally-aid battle | #81 — outpost |
|---|---|---|
| Lifetime | transient, days | permanent until packed up |
| Class | a bare `WorldObject` overlaying an existing `Settlement` | a `MapParent` that owns its own map |
| Why | the settlement underneath already generates the map, so no site map generation is involved | colonists live there; it needs a map to enter |
| Consequence | goodwill, ownership of the settlement underneath | items delivered to a home map |

Because #92 never generates a site map, **it does not touch
[#88](https://github.com/cjd721/Rimworld-Archinity/issues/88)** (closed) — by design, not by
deferral.

### 1. The ally-aid battle — build it, against a read reference

**Selection.** Faction Territories and Vassalage (`jaeger972.factionterritories`,
`294100/3626725895`) is a **verified available mechanism and is not selected.** It is
**declined by Conrad** in [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2
and sits in `docs/data/MOD-VERDICTS.md` § *Declined*; the decline is *"as a dependency, with its
ideas kept"*, and its text says the design it carried *"is **reimplemented in `Archinity.Core`**"*.
**That is Build B, and Build B is the plan of record.** Build A — shipping FT&V — is live only if
Conrad **reverses** that decline, which is #8's call and not
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s.

**What the reference supplies, and therefore what Build B copies** [V]:

| Piece | What it is |
|---|---|
| `Invasions.Invasion : WorldObject` | 209 lines. Scribes attacker/defender/map-defender faction load IDs, `settlementId`, `vassalOutpostId`, `tempSettlementId`, `createdTick`, `timeoutTick`, `initialPoints`, `enteredMap`, `attackerRaidSpawned`, `resolved`, `winningFactionLoadId`, `rewardGoodwillOnExit`/`rewardFactionLoadId`/`rewardAmount`. |
| `Invasions.Component : GameComponent` | 225 lines. `GameComponentTick` → `TickActiveInvasions` every tick, plus a `nextInvasionTick` scheduler. |
| `Invasions.Utility` | **1,337 lines, nine methods Build B must reproduce**: `TryCreateForSettlement`, `EnsureAttackerRaid`, `TryResolveOnMap`, `ResolveFromMapClosure`, `ResolveOffMap`, `RollWinner`, `ResolveWithWinner`, `ApplyWinnerToSettlement`, `ApplyPendingExitReward`. Plus `Enter`, `GetTechWeight`, `GetCurrentFactionStrength`, `FindAttackerEntryCell` and the resolve/lookup helpers. |
| `Invasions.ArrivalAction_JoinFight : CaravanArrivalAction` | 569 lines, ~150 non-boilerplate. Built through `CaravanArrivalActionUtility.GetFloatMenuOptions<T>`. |
| `Invasions.Patches_GetFloatMenuOptions` | 39 lines. Strips the vanilla "Attack" option while an invasion is live, adds "Join fight". |
| `Invasions.Patches_CheckDefeated` | Blocks vanilla `SettlementDefeatUtility.CheckDefeated` so an NPC-versus-NPC fight is not miscounted as a player conquest. **Easy to miss and required.** |

**`Utility.TryCreateForSettlement(Settlement, Faction attacker, int now)` is the shape the
authored trigger wants** — it takes both factions explicitly and does not consult the territory
cache. Only FT&V's *scheduler*路 routes through `FindEligibleAttackers`, which requires the
attacker to claim the defender's tile via `TerritoryOwnershipCache.TryGetClaimingFactions` [V].
Build B's authored trigger names the pair and skips that entirely, which is why Build B does not
need a territory model.

**Two premises in #92's ticket were wrong.**

*"The machinery that lets a pawn target a non-player faction, which vanilla AI cannot do."*
**Vanilla AI can do it.** `Verse.AI.AttackTargetsCache.GetPotentialTargetsFor(IAttackTargetSearcher)`
keys entirely on `thing.Faction` and `thing.HostileTo(item.Thing)` and contains **no reference to
`Faction.OfPlayer`** [V]; `RimWorld.LordToil_AssaultColony.UpdateAllDuties` assigns
`DutyDefOf.AssaultColony` and nothing else [V]. FT&V proves it in the shipped case:
`EnsureAttackerRaid` makes a stock `LordJob_AssaultColony(attacker, …)` for an NPC-versus-NPC
fight, with no custom LordJob, DutyDef or JobGiver [V].

*"A `Site` with a `TimeoutComp`, or something longer-lived."* Neither. `TimeoutComp.CompTickInterval`
only calls `parent.Destroy()` [V] — it deletes, it does not decide. The overlay design is selected
instead.

**The `Trigger_BecameNonHostileToPlayer` hazard, stated precisely.** In
`LordJob_AssaultColony.CreateGraph`, `Trigger_TicksPassed` and `Trigger_FractionColonyDamageTaken`
sit on **two separate transitions**, both inside `if (canTimeoutOrFlee)`; `Trigger_BecameNonHostileToPlayer`
sits on a **third transition gated only on `assaulterFaction != null`**, so it is added
unconditionally [V]. Both FT&V and Worksites Expanded pass `canTimeoutOrFlee: false`, which removes
the first two and leaves the third — **the one that actually bites.**

It is **narrower than "any relation moves"**, and the earlier draft of this document overstated it:

- `Trigger_BecameNonHostileToPlayer.ActivateOn` requires `signal.previousRelationKind == FactionRelationKind.Hostile`
  before it evaluates `!lord.faction.HostileTo(Faction.OfPlayer)` [V].
- The signal is raised from `Faction.Notify_RelationKindChanged` — only on a **relation *kind*
  change**, not on every goodwill tick — and the loop reaches a lord only when `lord.faction` is
  one of the two factions in the changed pair [V].

**It is still real, and the earlier draft's exculpation of FT&V was wrong.** FT&V makes a lord for
the **attacker**, via `EnsureAttackerRaid`; the defender is the settlement's resident garrison and
has no lord of ours. So the hazard binds **whenever the side we give a lord to is not hostile to
the player** — under this architecture, whenever the *attacker* is the player's friend. In #92's
stated fiction the ally is the one under attack, so the attacker is an enemy and the trigger stays
quiet; in the general two-NPC case, and in any variant where the ally attacks, FT&V is on the wrong
side of it too. **Build B strips the transition unconditionally**, the way Worksites Expanded does
[V] (`MiningOutpost.LordJob_WorksiteGarrisonAssault.CreateGraph` walks `StateGraph.transitions` and
removes the one carrying the trigger). ~10 lines, and it is **priced in the cost table**, which an
earlier draft omitted.

**[SR]Factional War: recommended against, and not currently declined.**
`docs/data/MOD-VERDICTS.md` § *Explicitly NOT declined* has it **in and undecided**, as a
*duplication* question against whatever #8 lands on. This document's contribution to that question
is that it duplicates a capability vanilla already has. Its AI layer *is* liftable — 7 LordJobs,
7 LordToils, 4 Triggers, 6 `DutyDef`s, 8 JobGivers, one JobDef plus driver, with
`LordJobFactionPairBase.TargetFaction` as the only seam and no coupling to its settings, incident
workers, `PawnGroupMakerUtility` or any component [V] — and lifting it buys nothing. Two things for
the record: its site half carries a 90,000-tick (1.5-day) `TimeoutComp` on all three world objects
[V]; and `LordJobAssaultFactionFirst` does **not** derive from `LordJobFactionPairBase` while four
JobGivers type-test against it, so handing a Lord a bare `LordJobAssaultFactionFirst` gives **no
jobs, silently** [V] — which is what a naive lift would do.

**State.** Build B: one `WorldObject` subclass in `Archinity.Core` with the field set above, plus a
`WorldComponent` holding `nextBattleTick`. Nothing else.

**Change.** The authored trigger fires the battle; the world-component tick advances and resolves it.

**Display.** Build B reproduces what the reference shows [V]: `Label` (*"<ally> under attack"*),
`ExpandingIcon` tinted to the attacker's colour, and `GetInspectString` printing defender, attacker,
*"Expires in: <period>"* and, once resolved, *"Winner: <faction>"*. Plus a creation letter naming
the ally who asked and a resolution letter.

**Multiplayer, Build B.** The three `ModSettings` prefixes Build A would need **drop out entirely** —
we write no settings. What remains: the resolution roll uses P4; the world object is created from the
world tick or from a synced incident, never from a UI handler; the attendance option is a
`FloatMenuOption` on a `WorldObject` and is covered by P5.

**If Build A is ever revived, the settings defect is not a posture problem.**
`FactionTerritoriesSettings.enableInvasions` is a **public bool field**, read inline in
`Invasions.Component.GameComponentTick` [V] — **a field read cannot be Harmony-prefixed**, so the
earlier draft's "three prefixes" was not buildable as written. The buildable retarget is a prefix on
the private `Component.TryCreateInvasion` (returns `bool`) or a transpiler over `GameComponentTick`
— and **not** a blanket prefix on `GameComponentTick`, which also runs `TickActiveInvasions`, the
resolution clock. The consequence is also worse than a differing scribed value:
`RollNextInvasionTick` draws `Rand.Range(num4, num5)` off the **shared stream**, with both bounds
derived from per-client settings [V], so a client with the setting false never takes the draw at all.
That is a shared-stream desync.

### 2. Outposts with real yields — the engine ships inside VEF

**Correction the build rests on.** #81 asks what *Vanilla Outposts Expanded* does. VOE
(`vanillaexpanded.outposts`, `294100/2688941031`) contains **no outpost engine**: **10** `Outpost_*`
subclasses, `OutpostExtension_Mining : OutpostExtension_Choose`, `Resource`, `TexDefensive`, and
`TravellingArtilleryStrike : WorldObject` — a world object of its own with its own `Tick` and
`ExposeData`, which "no engine" should not be read to deny. Its **14** `WorldObjectDef`s are 13
outposts plus `VOE_TravellingArtilleryStrike`, and **three outpost defs have no VOE class at all**:
`Outpost_Logging` and `Outpost_Trading` declare no `worldObjectClass` (so they run base
`Outposts.Outpost`) and `Outpost_Production` uses `Outposts.Outpost_ChooseResult` [V].

The engine is **`Outposts.dll`, shipped inside Vanilla Expanded Framework**
(`2023507013/1.6/Assemblies/Outposts.dll`), with the abstract `WorldObjectDef` `OutpostBase` also
VEF's [V]. **`VEF.dll` itself contains zero `Outpost` types**, so a sweep of `VEF.dll` for outposts
returns a false negative [V].

**This changes the sourcing question.** VEF is already a donor in
[`WORLD-INFRASTRUCTURE.md`](WORLD-INFRASTRUCTURE.md) §2. **The engine costs nothing extra.**

**Mechanism** [V], all in `Outposts.dll`:

| Piece | What it is |
|---|---|
| `Outposts.Outpost : MapParent, IRenameable` | `occupants` (`List<Pawn>`), `containedItems`, `ticksTillProduction`, `ticksTillPacked`, `costPaid`, `deliveryMap`, `raidFaction`/`raidPoints`. |
| `Outposts.OutpostExtension : DefModExtension` | Per-type config, XML: `AllowedBiomes`/`DisallowedBiomes`, `CostToMake`, `MinPawns`, `RequiredSkills`, `Range`, `Event`, `TicksPerProduction` (default 900,000), `TicksToPack` (default 420,000), `ResultOptions`. |
| `Outposts.ResultOption` | `Thing`, `BaseAmount`, `AmountPerPawn`, `AmountsPerSkills`, `MinSkills`. |
| `Outpost.TickInterval(delta)` → `Produce()` → `Deliver(ProducedThings())` | Clock and payout. See P2 for why the gated path is safe here. |
| `Outpost.Deliver` | Five methods — `Teleport` (default: a `VEF_OutpostDeliverySpot` building, else a random reachable edge cell), `PackAnimal`, `ForcePods`, `PackOrPods`, `Store` — each ending in a summary letter. |
| `Outpost.ExposeData` | `occupants` and `containedItems` (both `LookMode.Deep`), `ticksTillProduction`, `ticksTillPacked`, `name`, `costPaid`, `raidFaction`, `raidPoints`, `deliveryMap`. |
| `Outposts.Utils.CanSpawnOnWithExt` | The founding gate: `CanAddPawn` per pawn (which carries the ideology `Event` willingness check), biome allow/disallow, **proximity** (`AnySettlementBaseAtOrAdjacent`, or a neighbouring `Outpost`), `MinPawns`, `RequiredSkills`, `CostToMake`. **Six gates, and no research or era gate.** |

#### 2a. Yields are XML — for 7 defs of 13, and the carve-out matters

The base path is data:

```csharp
// Outposts.ResultOption.Amount(List<Pawn> pawns)
Mathf.RoundToInt((BaseAmount + AmountPerPawn * pawns.Count
    + (AmountsPerSkills?.Sum(x => x.Amount(pawns)) ?? 0))
    * OutpostsMod.Settings.ProductionMultiplier)
```

and `Outpost.ProducedThings()` is `ResultOptions.SelectMany(ro => ro.Make(CapablePawns.ToList()))` [V].
For an outpost that takes that path, restatting a yield is one xpath into its
`modExtensions/li/ResultOptions`.

**Six of the ten VOE subclasses compute yield in C#, and two of them ignore the XML entirely** [V]:

| Subclass | What it does | Restat by xpath? |
|---|---|---|
| `Outpost_Scavenging` | `ProducedThings()` ignores `ResultOptions` and calls `ThingSetMakerDefOf.Reward_ItemsStandard` with a `totalMarketValueRange` | **No** |
| `Outpost_Town` | overrides `Produce()` and yields **pawns**; never calls `ProducedThings()` | **No** |
| `Outpost_Hunting` | overrides `ResultOptions`, rebuilds the list in code from `LeatherAmount`/`MeatAmount` stats and its own `[PostToSetings] float ProductionMultiplier = 0.5f`, and can discard the XML option | **Partial** |
| `Outpost_Farming`, `Outpost_Mining` | synthesize options in `GetExtraOptions()`; `Outpost_ChooseResult.ResultOptions` **concatenates** `Ext.ResultOptions.OrEmpty()` with them | **Partial** |
| `Outpost_Drilling` | gates the XML options on a C# `workDone` counter | **Partial (gate is code)** |
| `Outpost_Artillery`, `Outpost_Defensive`, `Outpost_Encampment`, `Outpost_Science` | no yield override | Yes |

Add the three classless defs (`Outpost_Logging`, `Outpost_Trading`, `Outpost_Production`) and the
tally is **7 of 13 restattable by xpath alone, 4 partial, 2 not at all**. Several subclasses also
carry their own `[PostToSetings]` float fields feeding the maths — a second settings surface on top
of `OutpostsMod.Settings`, closed by the same patch as B2/B3 below.

**So "the shape is settled" holds for the base path only.** Scavenging and Town need a C# override
of ours or need dropping from the shipped set; that is a content call, not a mechanism gap. Three
def-patching traps apply to the XML half: **T-06** (`GetModExtension` returns the *first* match —
replace the existing extension's contents, never add a second `li`), **T-02** (patches run before
`ParentName` resolves, and these defs inherit VEF's `OutpostBase`, so target the child's own nodes),
**T-05** (`XmlInheritance` appends list children rather than replacing them). The numbers belong to
the balance deferral in
[map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2).

#### 2b. What blocks it — five defects, all multiplayer

| # | Defect | Where |
|---|---|---|
| **B1** | Unsynced `WorldObjectMaker.MakeWorldObject` + `NameGenerator.GenerateName` + `Find.WorldObjects.Add` + `AddPawn`, **inline inside a `Widgets.ButtonText` branch** | `Outposts.Dialog_CreateCamp.DoOutpostDisplay` |
| **B2** | Reflection writes per-client `ModSettings` onto live instances, from `Outpost.SpawnSetup` — **every world load** — and again from `WriteSettings()` over every live outpost when the settings window closes | `Outposts.OutpostsMod.Setup(Outpost)` via `OutpostsMod.Notify_Spawned` |
| **B3** | The second loop in the same method writes onto `outpost.Ext` — the **`DefModExtension` instance shared by every outpost of that def** — so a per-outpost setting mutates global def state | `Outposts.OutpostsMod.Setup(Outpost)` |
| **B4** | `Settings.ProductionMultiplier` and `Settings.TimeMultiplier` read directly, plus the per-subclass `[PostToSetings]` multipliers | `ResultOption.Amount`, `Outpost.PostAdd`, `Outpost.TickInterval`, `Outpost_Hunting`, `Outpost_Farming` |
| **B5** | Pack / stop-pack / abandon gizmos write `ticksTillPacked` client-locally; `Dialog_TakeItems` / `Dialog_GiveItems` / `Dialog_RenameOutpost` / the delivery-map picker likewise | `Outpost.GetGizmos` and the dialogs |

All [V]. `Outposts.dll` references `Multiplayer.API` nowhere [V] — VEF 1.6 no longer ships
`0MultiplayerAPI.dll`.

**B1 is outside P5's net** because a `Caravan.GetGizmos` postfix yielding a `Command_Action` that
opens a `Window` is not a float-menu option on a world object. And `WorldObjectMaker.MakeWorldObject`
calls `Find.UniqueIDsManager.GetNextWorldObjectID()` [V], while MP's `UniqueIdsPatch` prefixes
`UniqueIDsManager.GetNextID` to return **negative, decreasing, client-local IDs** whenever
`Multiplayer.InInterface` is true [V]. The outpost gets a negative ID on the client that clicked and
does not exist on the other.

**Multiplayer Compatibility does not cover this.** The entire
`Multiplayer.Compat.VanillaOutpostsExpanded` late-patch is [V]:

```csharp
MP.RegisterSyncMethod(AccessTools.TypeByName("VOE.Outpost_Artillery"), "Fire", null);
MpCompat.RegisterLambdaDelegate("VOE.Outpost_Defensive", "GetGizmos", 3);
```

Founding, occupants, production, delivery, packing and every dialog are uncovered.

#### 2c. The harness, in `Archinity.Core`

1. **One prefix on `OutpostsMod.Setup(Outpost)` returning `false` when `MP.IsInMultiplayer`.**
   Closes **B2 and B3 together** and is the highest-value line in the build: with `Setup` never
   running, every `[PostToSetings]` field — including the per-subclass multipliers — keeps its XML
   value identically on both clients, and the shared `DefModExtension` is never written.
2. **Two prefixes forcing `Settings.ProductionMultiplier` and `Settings.TimeMultiplier` to `1f`**
   under the same gate. Closes the part of **B4** that `Setup` does not reach.
3. **Closing B1 is a transpiler, or a prefix that reimplements the row.** There is **no commit
   method to wrap** — `MakeWorldObject`, `NameGenerator.GenerateName`, `Tile`, `SetFaction`,
   `Find.WorldObjects.Add` and the `AddPawn` loop are inline in a `Widgets.ButtonText` branch of
   `DoOutpostDisplay` [V]. Either transpile that branch to call our
   `[SyncMethod] FoundOutpost(Caravan, WorldObjectDef)`, or prefix `DoOutpostDisplay` and redraw the
   row ourselves. The dialog stays client-local; the commit is the synced write — the shape
   [`WORLD-INFRASTRUCTURE.md`](WORLD-INFRASTRUCTURE.md) §3 records MP Compat using for VFE
   Classical's road targeter.
4. **`MP.RegisterSyncMethod` on `Outpost.AddPawn` / `RemovePawn`, the pack and stop-pack gizmo
   lambdas, the item-transfer dialogs' commit and the delivery-map setter.** Closes **B5**.

**Era gating is the one thing neither mod supplies**, per the six gates above — contrast VFE
Classical's `RoadBuildingDef`, research-gated by construction. One `DefModExtension` of ours plus a
filter in the same `DoOutpostDisplay` prefix, the `ReachRungExtension` shape
[`CHARTING.md`](CHARTING.md) §4 already uses.

**Display.** Already there [V]: the world-map draw from the `WorldObjectDef`, four `inspectorTabs`
(`WITab_Outpost_Items` / `_Gear` / `_Health` / `_Needs`, declared on `OutpostBase`), production
progress in the inspect string, and a delivery letter on every payout.

**Build B, if VEF's Outposts module is declined.** There is **no second outpost engine among the
assemblies read**. A `MapParent` subclass, a `DefModExtension`, a production tick and five delivery
methods: ~400 lines. **Not recommended** — the harness is a third of that against a module VEF
already gives us.

### 3. The boundary with vassalage — [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)

**The line is who supplies the labour.**

- **An outpost consumes your colonists.** Pawns leave the colony, live at the tile, and their count
  and skills *are* the yield formula. A logistics decision with an opportunity cost. **#81, and this
  document.**
- **A vassal consumes nobody.** Tribute accrues per outpost per day against the vassal's tech level,
  and the vassal can then be invaded. A political relationship with a political cost. **#35's, and
  `POLITICS.md`'s.**

Different verbs; shipping both is not duplication. They share §0's pattern, and **#35 should be
built against it rather than inventing a second one.** Note that #8 already declined FT&V's
vassalage *as designed* — `scratch/recon-vassalage-territory.md` records it as one-directional,
without obligations or an end state, with an exploitable purchase path. **That FT&V would also
supply #35's half is an argument for reversing the #8 decline, not a benefit currently in hand**,
and on the recon's reading it is a weak one.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| **§1 — Build B (plan of record).** World object + `WorldComponent` clock + nine `Utility` methods + `CaravanArrivalAction` + `Settlement.GetFloatMenuOptions` postfix + a `SettlementDefeatUtility.CheckDefeated` block | new C# | **350–500 lean, 450–700 faithful** | `Archinity.Core` |
| **§1** `Trigger_BecameNonHostileToPlayer` transition surgery on the attacker's lord | new C# | ~10 lines | `Archinity.Core` |
| **§1** authored trigger (`IncidentWorker` naming both factions) | new C# | ~50 lines | `Archinity.Core` |
| **§1** `IncidentDef` and letter text | XML | ~25 lines | `Defs/IncidentDefs/Territory.xml` |
| **§1** multiplayer harness under Build B | **none** — no settings of ours; P4 for the roll; P5 covers the attendance option | 0 | — |
| **§1** [SR]Factional War AI lift | **not needed** — vanilla targeting is faction-relative | 0 | — |
| — *§1 Build A, only if #8's FT&V decline is reversed:* mod ships the above; we add the authored trigger, the transition surgery, **and** a settings neutraliser that must be a prefix on `Component.TryCreateInvasion` or a transpiler, **not** a field-read prefix | new C# | ~90 lines total | `Archinity.Core` |
| **§2** engine, production, delivery, packing, tabs | **none** — VEF's `Outposts.dll` ships it | 0 | — |
| **§2** `OutpostsMod.Setup` prefix (B2 + B3, incl. per-subclass multipliers) | new C# | ~12 lines | `Archinity.Core` |
| **§2** two `Settings` multiplier prefixes (rest of B4) | new C# | ~15 lines | `Archinity.Core` |
| **§2** B1: transpiler over `DoOutpostDisplay`'s button branch, or a prefix redrawing the row, plus `[SyncMethod] FoundOutpost` | new C# | **80–120 lines** | `Archinity.Core` |
| **§2** five sync registrations (B5) | new C# | ~30 lines | `Archinity.Core` |
| **§2** era gate: one `DefModExtension` + a filter in the same prefix | new C# | ~20 lines | `Archinity.Core` |
| **§2** yield restat, base-path defs | XML, 1 `PatchOperationReplace` per def | ~15 lines each, **7 of 13 defs** | `Patches/Outposts_Yields.xml` |
| **§2** yield restat, `Farming` / `Mining` / `Hunting` / `Drilling` | XML for the declared options, but the generated half is code | partial | as above |
| **§2** `Outpost_Scavenging`, `Outpost_Town` | **XML cannot reach them** — a C# override of ours, or drop them from the set | ~40 lines each if kept | `Archinity.Core` |
| **§2** era-gate rows | XML, one `<modExtensions>` block per def | ~6 lines each | `Patches/Outposts_Gating.xml` |
| — *§2 Build B, if VEF's Outposts module is declined* | new C# | ~400 lines | `Archinity.Core` |
| **§3** vassalage and tithe | **[#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)'s** | — | — |

**Total new C# on the plan of record: roughly 560–760 lines**, of which §1's reimplementation is
the bulk and §2's is harness.

---

## Persistence and multiplayer

- **Both world objects scribe themselves.** `WorldObject.ExposeData` writes `def`, `tile`, `ID`,
  `creationGameTicks`, `destroyed`, `tickDelta`, `isGeneratedLocation`, `faction` and `questTags`,
  then calls `PostExposeData` on every comp [V]. Each subclass adds its own fields on top.
- **A comp added to an existing `WorldObjectDef` migrates cleanly forward.** `ExposeData` calls
  `InitializeComps()` during `LoadSaveMode.LoadingVars`, from `def.comps`, *before* any comp data is
  read [V]. A save that predates the comp constructs it with defaults. Removing a comp drops its
  scribed data silently.
- **`WorldObjectComp.PostExposeData` writes into the parent's flat scribe node.** Comps do not push
  a sub-node, so two comps on one def sharing a `Scribe` key collide silently. Vanilla has a near
  miss: `TimedDetectionRaids` scribes `ticksLeftToSendRaid` under the key
  `"ticksLeftToForceExitAndRemoveMap"`, which the obsolete `TimedForcedExit` uses for a different
  field [V]. Prefix every key on a comp of ours.
- **Creating a world object from an unsynced path produces a client-local object.**
  `MakeWorldObject` → `GetNextWorldObjectID()`, and MP's `UniqueIdsPatch` hands out negative
  client-local IDs while `Multiplayer.InInterface` [V]. Creation must be inside a `SyncMethod` —
  §2's B1, and §1 gets it free by creating from the world tick or a synced incident.
- **`WorldObjectsHolder.Add` is partly patched, and not in a way that helps.**
  `Multiplayer.Client.Patches.WorldObjectAdd.Prefix` defers through a `[SyncMethod]` only when
  `Multiplayer.MapContext != null`; from a world-level context it returns `true` and the add
  proceeds unsynced [V].
- **`UpdateRateTicks` is MP's to patch and not ours to override.** See P2, and *Failure and
  recovery*.
- **Every outcome roll uses P4's seeded form.**
- **`ModSettings` are the live divergence surface in both donors.** Under the plan of record §1 has
  none (we write the code) and §2's are closed by one prefix. Both are **T-18** in origin.
- **A save that predates either capability loads normally**, and **there is no freeze item** —
  unlike [`WORLD-INFRASTRUCTURE.md`](WORLD-INFRASTRUCTURE.md) § *The freeze*, nothing here is read
  at world creation.
- **Faction consequences work, subject to the full gate list.** `Faction.CanChangeGoodwillFor`
  returns false when **any** of these holds [V]:
  `!HasGoodwill`, `!other.HasGoodwill`, `def.permanentEnemy`, `other.def.permanentEnemy`,
  `defeated`, `other.defeated`, `other == this`,
  `def.permanentEnemyToEveryoneExceptPlayer && !other.IsPlayer`,
  `other.def.permanentEnemyToEveryoneExceptPlayer && !IsPlayer`,
  `def.permanentEnemyToEveryoneExcept != null && !…Contains(other.def)`,
  the mirrored form of the same, or `QuestUtility.IsGoodwillLockedByQuest(this, other)`. **And one
  more that is live for §1**: a **positive** `goodwillChange` is blocked when
  `IsPlayer && SettlementUtility.IsPlayerAttackingAnySettlementOf(other)` (or the mirror) [V].
  A player attending an ally-aid battle is on a settlement map with hostiles present, so **the
  reward write can be blocked by the very battle that earned it.** That is why the reference defers
  it: `rewardGoodwillOnExit` is scribed on the world object and paid by `ApplyPendingExitReward` on
  map exit [V]. **Build B must keep the deferral, not simplify it away.**
  `Faction.defeated` is a plain scribed bool and setting it is cheap [V].

---

## Failure and recovery

- **Overriding `WorldObject.UpdateRateTicks` escapes Multiplayer's VTR prefix.** Proposed as a trap.
  MP patches `RimWorld.Planet.WorldObject.UpdateRateTicks` and, separately,
  `Verse.Projectile.UpdateRateTicks` [V], and `SyncAction.PatchAll` elsewhere in the same assembly
  iterates `AllSubtypesAndSelf()` and patches each type's **declared** method [V] — MP evidently
  does not trust a base-declaration patch to reach overrides. A subclass of ours that overrides the
  property is covered by neither patch. **The symptom is not drift**: `DoTick` passes the accumulated
  `tickDelta` and consumers decrement by `delta`, so elapsed ticks are conserved. The symptom is a
  different **phase and granularity** per client — the timer crosses zero on a different tick on each
  machine, so `Produce()` and any `Rand` inside it run at different stream positions. Silent until
  the desync trace names something unrelated.
- **A `Command_Action` gizmo or a `Window` button is outside Multiplayer's float-menu sync, and
  nothing says so.** Proposed as a trap. MP's `SyncActions` registration covers
  `WorldObject.GetFloatMenuOptions(Caravan)` and **syncs every option it yields** — a `null` return
  from `WorldObjectCaravanMenuWrapper` falls through to the default `ActualSync` path, and the
  non-null branch is the *deferred-confirmation* special case, not the sync case [V]. The
  registration never sees anything else on a caravan: a `Gizmo` from `Caravan.GetGizmos`, including
  one added by a postfix, and any button inside a `Window` / `Dialog_*` are outside it entirely and
  are never synced. VEF's `Dialog_CreateCamp` founds an outpost from a `Window` reached through a
  `Caravan.GetGizmos` postfix, and is uncovered.
- **The reward goodwill write can be blocked by the battle that earned it.** See *Persistence*;
  keep the deferred-on-exit payment.
- **A lord we make for a faction friendly to the player leaves the map on the first relation-kind
  change out of Hostile.** `Trigger_BecameNonHostileToPlayer`, on a transition added unconditionally
  [V]. Strip the transition; do not rely on `canTimeoutOrFlee: false`, which removes the other two
  and not this one.
- **An NPC-versus-NPC fight can be miscounted as a player conquest** unless
  `SettlementDefeatUtility.CheckDefeated` is blocked while the battle is live [V].
- **Arriving at an ally's site can be read as an attack.** `SitePartDef.considerEnteringAsAttack`
  defaults `true`, and `CaravanArrivalAction_VisitSite.DoEnter` calls
  `SettlementUtility.AffectRelationsOnAttacked` when any part carries it [V]. The overlay design
  never generates a site; any variant that does must set the field false.
- **Two `WorldObjectComp`s on one def sharing a `Scribe` key overwrite each other silently.**
- **Removing VEF's Outposts module from a live save deletes the outposts and the colonists in
  them** [V] — `occupants` is scribed `LookMode.Deep` on the world object. A sourcing constraint:
  once §2 ships, the module is load-bearing for the rest of the campaign.
- **§2's B2 prefix failing is silent and looks like a balance problem.** Two clients with different
  settings get different production intervals and yields from the same outpost. The prefix itself is
  loud — a renamed target throws at startup — which is why it beats asking both players to copy a
  settings file.
- **An outpost with zero occupants divides by zero in a public property.**
  `Outpost.TicksToPack => (Ext?.TicksToPack ?? 420000) / occupants.Count`, no guard [V]. `Tick()`
  destroys an empty outpost before `TickInterval` normally reaches it, so it is latent [I] — but any
  UI of ours reading the property reopens it.
- **No campaign softlock exists here.** The worst outcome of everything above except the desyncs is
  a missing letter or a wrong number.

---

## Status

**Evidence class: READ.** Settled from `Core` defs and decompiled 1.6 assemblies —
`RimWorldWin64_Data/Managed/Assembly-CSharp.dll`,
`294100/3626725895/Assemblies/FactionTerritories.dll`,
`294100/2023507013/1.6/Assemblies/Outposts.dll`,
`294100/2688941031/1.6/Assemblies/VOE.dll`,
`294100/3687071198/Assemblies/MiningOutpost.dll`,
`294100/3423264477/Assemblies/ModRimworldFactionalWar.dll`,
`294100/3684587591/1.6/Assemblies/BetterTradersGuild.dll`,
`294100/3762723122/Assemblies/RimPacts.dll`,
`294100/2606448745/1.6/AssembliesCustom/Multiplayer.dll` and all 18
`Multiplayer_Compat*.dll` builds under `1629973374`.

§1 established by [#92](https://github.com/cjd721/Rimworld-Archinity/issues/92), §2 by
[#81](https://github.com/cjd721/Rimworld-Archinity/issues/81), both revised after an adversarial
audit. No source tree was read as 1.6 fact: VOE ships 1.3-era source, [SR]Factional War's `Source/`
calls a `TileFinder.TryFindNewSiteTile` overload absent from 1.6, and VEF ships none.

`scratch/recon-vassalage-territory.md` is a prior 1,252-line recon of FT&V and Map Mode Framework.
It is **gitignored** — readable to a local agent, invisible to a sandboxed one — so per
`docs/agents/capability-research.md` § *Inherited claims* its content is **[I]** except where
re-derived here. Its `RollWinner` quotation, its invasion description and its "no dependency in the
co-op save" verdict were re-derived and hold [V]. Its estimate that a **stripped, off-map-only**
invasion would cost ~200 lines is consistent with this document's 350–500, which additionally buys
the player-joinable half #92 explicitly asks for.

**Verified available mechanisms** — not selected:

- FT&V's `Invasions` module end to end, including `Utility.TryCreateForSettlement` as an authored
  entry point. **Declined as a dependency by Conrad in #8 session 2.**
- VEF's `Outposts.Outpost` / `OutpostExtension` / `ResultOption` and its five delivery methods —
  **selected**, subject to §2c's harness.
- `WorldObject.Tick` / `WorldObjectComp.CompTick` as an unconditional clock, and
  `Gen.IsHashIntervalTick(WorldObject, int)` as its stagger.
- `SitePartWorker.SitePartWorkerTick`, with `SitePartWorker_RaidSource` as the shipped worked
  example. **One mod in the corpus uses it** (`Nyar.NCLvsTW`), on a validated sweep.
- `Rand.PushState(Gen.HashCombineInt(...))` with a `finally { Rand.PopState(); }`.
- Multiplayer's `VtrSyncWorldObjectPatch`, `UniqueIdsPatch` and `SyncActions` registration.
- Vanilla `LordJob_AssaultColony` for an NPC-versus-NPC fight, with the
  `Trigger_BecameNonHostileToPlayer` transition stripped.

**Proposed, marked [I] by construction:** §1's Build B in full, its authored `IncidentWorker` and
the transition surgery; §2's patches, sync registrations and era-gate extension; the yield and gate
numbers; §3's boundary rule. The mechanisms each composes are [V]; the composition is [I] until built.

**Premises corrected:**

1. **#92's ticket**, quoting `scratch/recon-factional-war.md`: *"vanilla AI cannot [target a
   non-player faction]."* **Wrong** — `AttackTargetsCache` is faction-relative with no player
   reference, and FT&V uses a stock `LordJob_AssaultColony` [V].
2. **#92's ticket** proposes a `Site` + `TimeoutComp`. `TimeoutComp` has no outcome [V]; the overlay
   design is selected and removes the #88 dependency entirely.
3. **#81's ticket** attributes the engine to VOE. It is `Outposts.dll` inside VEF [V].
4. **`PARTS-BIN.md` § 7.6**, VOE row: *"(It **is** covered by the compat layer…)"* — it is not [V].
   Same row: **10** subclasses, not 11; **14** `WorldObjectDef`s of which 13 are outposts; three
   outpost defs have no VOE class; `OutpostExtension_Mining : OutpostExtension_Choose`; and VOE also
   ships `TravellingArtilleryStrike : WorldObject`.
5. **`scratch/recon-factional-war.md`'s** *"no `[HarmonyPatch]` attributes anywhere"* is literally
   true and materially misleading — `HarmonyPatches` is `[StaticConstructorOnStartup]` and runs
   `new Harmony(...).PatchAll()`, and `About.xml` hard-declares `brrainz.harmony` for 1.5 and 1.6 [V].
6. **This document's own first draft** stated P5 inverted — that an option not built through
   `CaravanArrivalActionUtility` was silently unsynced. The opposite is true: `null` from the
   wrapper falls through to `ActualSync` [V]. Corrected in place; the trap proposed in *Failure and
   recovery* is the corrected one, and both build conclusions were unaffected.
7. **This document's own first draft** exculpated FT&V from the
   `Trigger_BecameNonHostileToPlayer` hazard on the grounds that the defender is a resident
   garrison. FT&V gives a lord to the **attacker**, so it is exposed whenever the attacker is
   friendly to the player [V]. Struck.
8. **This document's own first draft** proposed three Harmony prefixes for FT&V's settings.
   `enableInvasions` is a **public field** and a field read cannot be prefixed [V]. Retargeted.

---

## Available mechanisms

### Vanilla and DLC — the site layer, and what it does not do

`WorldObject` → `MapParent` → `Site`, with `SitePart` (per-instance, scribed) and
`SitePartDef.Worker` — a **singleton per def**, lazily constructed into an `[Unsaved]` field [V].
**That singleton is why neither capability puts state on a `SitePartWorker`**: per-instance state
must live on `SitePart`, whose fields are a fixed vanilla list (`SitePartParams` has 17 named fields
and no extension point [V]), or on a `WorldObjectComp`, which is per-instance and scribes freely.

`SiteMaker.MakeSite(…, Faction faction, …)` takes a faction directly; only the *finder* path gates
on hostility, via `SiteMakerHelper.FactionCanOwn`'s `disallowNonHostileFactions` [V]. **So an
ally-owned site is constructible** — pass the faction and skip `TryMakeSite_*`.

The vanilla site timeout is **not** `TimeoutComp` in practice:
`Site.WorldObjectTimeoutTicksLeft` walks the quest manager for a `QuestPart_WorldObjectTimeout` [V],
whose `DelayFinished` removes the object and completes the part. Both are outcome-free.

**Odyssey changed the world-object layer additively.** `PlanetTile` replaces the bare int tile id;
`MapParent` gained `GravShipCanLandOn` and `wasSpawnedViaGravShipLanding` handling; `Site` gained
`preventGravshipLanding`; `SitePartDef` gained `gravShipsCanLandOn` and `lootTable` [V]. Nothing was
removed. Odyssey also added the **work site** family — `StorytellerComp_WorkSite`, four
`SitePartWorker_WorkSite_*`, `GenStep_WorkSitePawns` / `GenStep_WorkSiteStash` — which is the
nearest vanilla thing to §2 and is not it: `SitePartWorker_WorkSite.Init` generates a fixed loot
pile into `sitePart.things` once, at creation, and nothing ticks to add more [V]. **Vanilla ships a
world site that holds goods; it ships none that produces them.**

### Faction Territories and Vassalage — read in full, declined as a dependency

`jaeger972.factionterritories` (`294100/3626725895`), 1.6-only, one copy on disk (T-22 clear),
depends on Map Mode Framework. Two rows already exist in `docs/data/MOD-VERDICTS.md` — the Declined
table and the cheap-plus-settings tier — and nothing here asks for a third. Covered under §1. Two
things worth recording beyond it:

- **`CaravanIncidentEntryDef`** is a def-driven, era-gated encounter table keyed to whose territory
  the caravan is standing in. Not this document's, and unclaimed by any ticket.
- **Territory is derived and never saved** — a multi-source Dijkstra flood fill rendered through Map
  Mode Framework. #8 chose a radius model instead, so §1's authored trigger does not depend on
  either.

### VEF's Outposts module — §2's carrier

`Outposts.dll` in `2023507013/1.6/Assemblies/`, with VOE supplying content. Covered under §2. Two
constraints:

- **VOE's 1.6 content is smaller than its 1.5 content.** `loadFolders.xml` loads `/` and `1.6` only;
  the conditional `1.6/Fishing` folder **does not exist on disk** and `1.6/Factory` exists with its
  `<li>` commented out [V]. Thirteen outpost defs on 1.6 against fifteen on 1.5 — and the two missing
  ones are moot, since `oskarpotocki.vfe.mechanoid` is not in the corpus.
- **`VEF.dll` contains zero `Outpost` types** [V].

### Worksites Expanded — read, not selected

`godsfathermixtape.worksitesexpanded` (`294100/3687071198`), 1.6-only, VEF-dependent, **undecided**
in `MOD-VERDICTS.md`. Its `WorkSiteDefenseTracker : GameComponent` is a second complete worked
example of §1's behaviour — a scribed `List<WorkSiteDefense>`, a `GameComponentTick` gated on
`TicksGame % 2500`, and `Resolve(def, 0.7f)` rolling whether the unattended worksite is overrun
(`WorldObject.Destroy()`, quest failed, letter) or holds (its `QuestPart_WorldObjectTimeout`
prolonged 5–7 days), then settling goodwill [V].

**Not selected**: its roll is a bare `Rand.Chance` off the shared stream rather than P4's seeded
form, and `CreateTemporaryAttackerFaction` generates a `Faction` at runtime — the **T-15** shape, a
standing hazard for a campaign whose roster is frozen at world creation (**T-07**). It is cited
because it confirms §1's architecture in a second assembly, and because
`Patch_WorksiteDefense_FriendlyFire`, `Patch_AttackTargetFinder_WidenRangeDuringDefense` and
`LordJob_WorksiteGarrisonAssault.CreateGraph`'s transition surgery are the concrete list of rough
edges a three-way fight has under any build.

### [SR]Factional War — read, recommended against, currently undecided

`SR.ModRimWorld.FactionalWarContinued` (`294100/3423264477`). 1.6 loads the **mod root**
(`<v1.6>/</v1.6>`), so the live assembly is `Assemblies/ModRimworldFactionalWar.dll` — a flat folder
with no version subdirectory [V]. Covered under §1. **One defect if anyone reopens the lift**:
`LordJobAssaultFactionFirst` does not derive from `LordJobFactionPairBase`, yet four JobGivers gate
on `LordUtility.GetLord(pawn).LordJob is LordJobFactionPairBase` [V]. It works today only because
the outer pair-base LordJobs `AttachSubgraph` its graph. Hand a Lord a bare
`LordJobAssaultFactionFirst` and the whole `SrAssaultFactionFirst` duty gives no jobs, silently.

### The two nearest false positives, read and cleared

- **Better Traders Guild** (`shunter.bettertradersguild`, `3684587591`) — has a `SitePartDef`
  worker, `BetterTradersGuild.SitePartWorkers.SitePartWorker_SmugglersDen`, which is **an empty
  subclass**: no `SitePartWorkerTick`, no production [V]. A quest-created trade site, not a yield
  engine.
- **RimPacts** (`3762723122`) — `RimPacts.RptEesOutpostApi` is a pure reflection interop shim
  (`MethodInfo` soft-binding into another mod's outposts) plus three
  `WorldObject.GetInspectTabs` patches [V]. Not an engine.

---

## Verification

**Sweeps, with the form that actually produced each result.** ASCII (`-a`) over the `#Strings` and
`#Blob` heaps; both roots; `-g '*.dll' -g '!**/obj/**'` throughout. **A packageId is an attribute
argument living in `#Blob`, not a type name** — an earlier draft justified skipping the `#US` pass
with "every question was a type or member name", which does not cover the packageId sweep. It
worked because `#Blob` attribute strings are ASCII, which is the correct reason.

| Sweep | Form | Result |
|---|---|---|
| Validator for the compat sweep | `rg -a -l -e "vanillaexpanded.outposts" <both 1629973374 roots> -g '*.dll' -g '!**/obj/**'` | 8 hits across 1.3–1.6 in both roots — the form finds a packageId that is known present |
| MP Compat coverage | `rg -a -l -e "factionterritories" -e "worksitesexpanded" -e "jaeger972" -e "godsfathermixtape" <same>` | **zero**, across all 18 `Multiplayer_Compat*.dll` builds |
| `SitePartWorkerTick` users | `rg -a -l -e "SitePartWorkerTick" <both roots> …` | 1 mod (`Nyar.NCLvsTW`) |
| `WorldObjectMaker` callers | `rg -a -l -e "WorldObjectMaker" <both roots> …`, attributed per mod | **20 mods** — listed below |

> **An earlier draft printed `rg -a -l "factionterritories\|worksitesexpanded"`.** In ripgrep's Rust
> regex `\|` is an **escaped literal pipe**, so that sweep searched for the literal string
> `factionterritories|worksitesexpanded` and could only ever return zero. It also dropped
> `-g '!**/obj/**'` and searched one root, and it was **not validated** — the validator run was a
> different sweep, which is precisely the hole `docs/agents/capability-research.md` warns about. The
> answer was right; the stated construction was not, and the construction is part of the result.

**The `WorldObjectMaker` hit list in full**, since the negative below is scoped to it:
`1629973374` (MP Compat), `1845154007` (VFE Security), `2023507013` (VEF — `KCSG.dll`,
`Outposts.dll`, `VEF.dll`, `VFECore.dll`), `2222935097` (Rim War), `2606448745` (Multiplayer),
`2688941031` (VOE), `2723801948` (VFE Pirates), `3014915404` (Vehicle Framework), `3309003431`
(VFE Insectoids), `3336572602` (Faction Customizer), `3414187030` (World Tech Level), `3423264477`
([SR]Factional War), `3444347874` (VFE Medieval), `3555799437` (Mechanoids: Total Warfare),
`3609835606` (Vanilla Gravship Expanded), `3626725895` (FT&V), `3684587591` (Better Traders Guild),
`3687071198` (Worksites Expanded), `3762723122` (RimPacts), `818773962` (HugsLib).

**Scope of the negatives, honestly.** *"No second player-founded yielding-site engine"* and *"no
third NPC-battle system"* are **[V] over the eight assemblies depth-read** (`Outposts.dll`,
`VOE.dll`, `FactionTerritories.dll`, `MiningOutpost.dll`, `ModRimworldFactionalWar.dll`,
`BetterTradersGuild.dll`, `RimPacts.dll`, `Assembly-CSharp.dll`) and **[I] over the remaining
twelve**, which were attributed by metadata hit and not decompiled: Rim War, Vehicle Framework,
World Tech Level, Faction Customizer, VFE Security / Pirates / Insectoids / Medieval, Vanilla
Gravship Expanded, Mechanoids: Total Warfare, KCSG and HugsLib. A metadata-name hit is [I]; none of
these twelve is a plausible outpost or invasion engine on its name and role, but that is an
inference. A second residual gap stands regardless: a `Dictionary<Faction, float>`-shaped field
lives in `#Blob` as a signature and no grep finds it, so "does some mod hold a per-faction yield
ledger" is bounded by what was read, not proven empty.

**Observable checks, once built:**

1. **§1 in-absentia.** Fire the authored incident, do not travel, wait past `timeoutTick`. The
   inspect string should go from *"Expires in: …"* to *"Winner: <faction>"*, a resolution letter
   should arrive, and the settlement should change hands if the attacker won. Because the roll is
   P4-seeded, the winner can be **computed from the world object's own fields before the tick
   arrives** — that prediction is the actual test.
2. **§1 attendance.** Travel and take *"Join fight"*. Expect the attacking group under a
   `LordJob_AssaultColony` fighting the settlement's residents with no player involvement required;
   confirm the attacker's lord does **not** leave when a relation kind changes; confirm the
   settlement is not credited to the player as a conquest; confirm the goodwill reward pays **on map
   exit**, not on resolution.
3. **§2 yields.** Found an outpost, patch `TicksPerProduction` low, and confirm the delivery letter's
   counts equal `BaseAmount + AmountPerPawn × N + Σ AmountsPerSkills` exactly — i.e. that the
   multiplier is pinned to 1. Use a base-path def (`Outpost_Encampment` or `Outpost_Science`), not
   Scavenging or Town.
4. **The one genuine RUN item, and it is narrow.** Everything above is single-client. **Two
   Multiplayer clients, one with the world map open and one on a colony map**, founding an outpost
   and letting one production cycle complete: confirm identical `ticksTillProduction` on both and no
   desync. It is the only claim reading cannot settle, because it exercises P2's VTR sync over
   `Outpost.TickInterval` and §2's B1 `SyncMethod` together. Hand it back rather than reasoning
   around it.

---

## Outstanding decisions

- **The numbers.** Yield amounts per outpost def, `TicksPerProduction` per era, the battle's
  frequency and its goodwill swing. Balance, owned by the deferral in
  [map #2's *Not yet specified*](https://github.com/cjd721/Rimworld-Archinity/issues/2).
- **Which era unlocks an outpost.** The era gate is a mechanism with no key. `docs/progression/` is
  where the key would live and it is **empty** — the same gap
  [#87](https://github.com/cjd721/Rimworld-Archinity/issues/87) found for research menu legibility.
  **No requirements document currently owns outpost availability.**
- **Whether `Outpost_Scavenging` and `Outpost_Town` ship.** XML cannot restat either. Keep them with
  a C# override of ours, or drop them from the set. A content call.
- **Whether the #8 decline of FT&V is reversed.** That is
  [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)'s and Conrad's, **not
  [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s** — #14 decides what ships from
  the *undecided* set, and this one is already decided. §1 is priced both ways so nothing blocks.
  The arguments for reversing are the ~400 lines Build B costs and FT&V also carrying #35's half;
  the arguments against are #8's original reasoning plus `recon-vassalage-territory.md`'s six named
  desync vectors and its verdict that vassalage as designed is one-directional and exploitable.
- **Which named pair fights, and when** — `docs/plot/` and
  [`docs/requirements/POLITICS.md`](../requirements/POLITICS.md), which already links #92.
- **`CaravanIncidentEntryDef`** — a def-driven, era-gated, territory-keyed encounter table sitting
  unclaimed by any ticket. Not a gap in this document.
