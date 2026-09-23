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

Holdings and outposts are answered section by section, above *The build*:

- § *What a holding pays, and how the player takes it* — the form, schedule and taking of a holding's payment, and the rebuild debt ([#166](https://github.com/cjd721/Rimworld-Archinity/issues/166)).
- § *Taking a settlement must be hard* — what builds a settlement's map and garrison, and what survives the map ([#164](https://github.com/cjd721/Rimworld-Archinity/issues/164)).
- § *A settlement's specialty, and learning it before you commit* — the faction's and the settlement's specialty, and what reveals it ([#165](https://github.com/cjd721/Rimworld-Archinity/issues/165)).
- § *Showing what the player has learned about a settlement* — every surface a learned per-settlement fact can be drawn on, and whether both players see it ([#178](https://github.com/cjd721/Rimworld-Archinity/issues/178)).
- § *Paying to advance a holding to a later era* — where a holding's era lives, and paying to rewrite it ([#167](https://github.com/cjd721/Rimworld-Archinity/issues/167)).
- § *How a holding ends* — release, retaking, destruction and throwing off, each as a moment the player acts on ([#172](https://github.com/cjd721/Rimworld-Archinity/issues/172)).
- § *A caravan en route when its destination changes hands* — what an in-flight order does when its target changes owner ([#152](https://github.com/cjd721/Rimworld-Archinity/issues/152)).
- § *A sworn faction owes services* — what a sworn faction can owe, and whether the player asks or only receives ([#168](https://github.com/cjd721/Rimworld-Archinity/issues/168)).
- § *What an outpost costs* — materials, silver and committed pawns, and whether staffing bounds the count ([#170](https://github.com/cjd721/Rimworld-Archinity/issues/170)).
- § *An outpost's upkeep arrives as events* — upkeep, attack and decline as events, never a management surface ([#171](https://github.com/cjd721/Rimworld-Archinity/issues/171)).
- § *An outpost that consumes its pawns and runs on its own* — production without staff, the pawn sale and its kind rule, and the destroyed outpost as a lootable, rebuildable ruin ([#179](https://github.com/cjd721/Rimworld-Archinity/issues/179)).

It does **not** own:

- **Roads and vehicles** — [`WORLD-INFRASTRUCTURE.md`](WORLD-INFRASTRUCTURE.md) owns the
  world-map mobility ladder outright. Nothing here re-derives a road fact.
- **What a vassal must be** — [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35) states it;
  §3 answers what is possible for every shape ([#120](https://github.com/cjd721/Rimworld-Archinity/issues/120)).
- **The territory model itself** — which tiles a faction claims.
  [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2 settled that it is
  *"a claimed tile is one within a small radius of a visible settlement or outpost"*, and
  explicitly **not** a Dijkstra flood fill. §1's authored trigger names its factions directly
  and therefore does not consult it.
- **Settlement ownership and the era rite** — [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8).
- **Faction goodwill mechanics** — [`POLITICS.md`](POLITICS.md).

---

## What a holding pays, and how the player takes it

### Purpose and scope

**What this section answers:** the *form* a holding's payment can take, the schedule it can arrive
on, the act by which the player actually takes it, and whether the rebuild debt that gates it can
be expressed. It resolves
[#166](https://github.com/cjd721/Rimworld-Archinity/issues/166) against
[`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *A holding is a settlement taken by
force* — *"the form the payment takes is open and every shape is on the table"*.

*The build* §3 below answered **whether a holding can exist**; this section answers **what it does
once it does**. §3's R0/R1/R2 findings are cited here, not re-derived.

**What this section does not own:**

- **What a holding pays *characteristically*** — its faction's trade and its own specialty:
  [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165). The one seam that must land
  there is named under *Open questions*.
- **Taking the settlement** — [#164](https://github.com/cjd721/Rimworld-Archinity/issues/164).
- **Advancing a holding to a later era** —
  [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167).
- **What a sworn faction owes** — [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168).
  P3 below is the shipped *"the player asks"* shape and is #168's to reuse.
- **How a holding ends** — [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172).
- **Whether a caravan can reach orbit** —
  [#127](https://github.com/cjd721/Rimworld-Archinity/issues/127) and `SPACE`. *Where delivery
  lands* is answered here; *whether the tile is reachable* is not.

### Verdict

- **Possible? Yes — every form the requirement names is carried by something already read, and the
  hard part is shipped.** A basket on a clock, an accrual the player can see that keeps growing
  while undelivered, a cadence the player chooses, unprompted sends, a stockpile a caravan
  collects, a drop the player requests on a cooldown, and a payload of **generated people** all
  exist in 1.6 as read code. What has to be built is *who* pays and *what* they pay, because every
  shipped carrier hardcodes both.
- **Multiplayer? Yes for the shipped carriers; With work for anything of ours.** VFE Empire's whole
  tithe machine is synced by MP Compat today. Vanilla's `TradeRequestComp.Fulfill` and
  `RoyalTitlePermitWorker_DropResources.CallResourcesToCaravan` are synced by Multiplayer itself.
  Three named hazards under *Constraints*; none is a blocker.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **P1** Tithe engine, repointed | Payload + speed + cadence + daily accrual + delivery + legibility, all scribed. The whole of *what it pays and when* | VFE Empire `WorldComponent_Vassals` / `TitheInfo` / `TitheWorker` (+ MP Compat) | XML catalogue; patch C# to repoint | **Medium** (Easy left as the Empire's) | **Yes**, one ordering hazard |
| **P2** Outposts' delivery layer | Five ways payment physically arrives, including a pack animal that walks in and a stockpile on the tile | VEF `Outposts.Outpost.Deliver` | C# reuse/copy; XML yields | **Medium** | **With work** — T-18 |
| **P3** Royal permit as *"the player asks"* | A basket **or pawns** dropped where the player points, on a cooldown, priced in favour; XML-authored | vanilla Royalty `RoyalTitlePermitDef` / `RoyalTitlePermitWorker_DropResources` | XML (+ C# if per-holding) | **Easy → Medium** | **Yes**, one subclass caveat |
| **P4** Standing debt on the tile | The rebuild gate: a scribed demand on the settlement, legible in its inspect string, paid by a caravan standing there | vanilla `TradeRequestComp`; donor VEF `Outpost.costPaid` | patch C# + XML comp | **Easy → Medium** | **Yes** |
| **P5** Accrued credit spent on a menu | The holding's own restocking, priced list — *spend against what it can supply* | vanilla `Settlement_TraderTracker` + MP's `MpTradeSession` | XML if the credit is silver or favour; C# otherwise | **Easy** (silver/favour) · **Hard** (bespoke credit) | **Yes** for silver/favour |
| **P6** Unprompted sends | Gifts and ally traffic on the storyteller's own clock. §3 R5, not re-derived | vanilla | XML | **Easy** | **Yes** |

**Every route is [I] as a route.** The mechanisms each composes are [V]; the composition is
inferred until built. **P1 + P2 + P4 is the combination the requirement's prose describes**, and
they do not collide: P1 owns *what and when*, P2 owns *how it arrives*, P4 owns *whether it may
start at all*.

#### P1 — VFE Empire's tithe engine, repointed off the Empire

**Gets us** [V] (`294100/2938820380/1.6/Assemblies/VFEEmpire.dll`, `1.6/Defs/Misc/TitheTypeDefs.xml`):

- **A scribed per-settlement record.** `TitheInfo` holds `Type`, `Speed`, `Setting`, `Lord`,
  `Settlement` and `DaysSinceDelivery` (`VFEEmpire.TitheInfo.ExposeData`).
- **A payload catalogue in XML.** Seven `TitheTypeDef`s — steel 25, wood 40, gold 5, silver 50,
  2 survival meals, honor 5 every 5 days, 1 slave every 10 days. Each carries `item`, `count`,
  `deliveryDays`, `workerClass` and its labels. **A new payload is a def**, unless it needs a worker.
- **Four schedule shapes at once.** A per-def fixed interval (`TitheTypeDef.deliveryDays`); a
  player-chosen cadence (`VassalUtility.DeliveryDays` — `EveryWeek` 7, `EveryQuadrum` **15**,
  `EveryYear` **60**, `Never`); a per-instance random multiplier (`VassalUtility.Mult` /
  `Commonality` — 0.5× to 2.5×, weights 60/100/20/5/1); and a per-settlement modifier
  (`TitheWorker.AmountProducedBase` multiplies by every `Honor_Settlement.def.titheSpeedFactor`).
- **Accrual is shipped, including the case the player cannot collect.**
  `WorldComponent_Vassals.DoDay` runs on `TicksGame % 60000 == 0`, increments `DaysSinceDelivery`
  and delivers at the cadence; `TitheWorker.CreateDeliveryThings` makes **one stack per day
  accrued**. **When `Deliver` returns false — caravan over mass capacity, or the lord not on a
  player home map — `DaysSinceDelivery` is not reset**, so the debt grows and pays out whole later.
- **Legibility is shipped.** `RoyaltyTabWorker_Vassals.DoVassal` prints the per-delivery range, a
  `VFEE.InStockpile` line of `AmountProducedRange × DaysSinceDelivery`, and a progress bar of
  `DaysSinceDelivery / DeliveryDays` — *what is owed and when it is due*, in the requirement's words.
- **A non-goods payload is expressible.** `TitheWorker_Honor.DeliverInt` calls
  `Lord.royalty.GainFavor(...)` and delivers no `Thing`. The seam is `workerClass` in XML.

**Cannot** [V]:

- **Choose who pays.** `WorldComponent_Vassals.AllPossibleVassals` filters `Faction.OfEmpire`.
- **Choose what a settlement pays.** `WorldComponent_Vassals.GetTitheInfo` takes a random
  `TitheTypeDef` and a weighted-random `TitheSpeed`. The characteristic payload is a replacement of
  that method — **#165's**, not a def.
- **Deliver anywhere but the lord.** `TitheWorker.DeliverInt` reaches the lord's caravan or a drop
  beside the lord on a player home map, and returns false otherwise. No per-record target exists.
- **Gate on anything.** Nothing in `DoDay` consults a debt, a cooldown or a cap.

**Consequences.** Entry, cadence and release are the Royalty tab's, gated on Empire vassalage points
and 100-tile reach; taking the engine means keeping that tab or writing our own entry. **Multiplayer
[V]:** `Multiplayer.Compat.VanillaFactionsEmpire` registers `SyncedVassalizeSettlement`, the
`DoVassal` cadence lambdas (2, 3, 4), `ReleaseAllVassalsOf`, a `SyncWorker<TitheInfo>` keyed on
`Settlement`, and wraps `GetTitheInfo` in
`Rand.PushState(Gen.HashCombineInt(settlement.ID, settlement.Tile))` — **the payload draw is
deterministic under MP.**

#### P2 — VEF's Outposts delivery layer

**Five delivery surfaces**, all [V] (`Outposts.Outpost.Deliver`,
`294100/2023507013/1.6/Assemblies/Outposts.dll`):

| Method | What arrives |
|---|---|
| `Teleport` | Goods placed at a player-built `VEF_OutpostDeliverySpot`, else a reachable map-edge cell |
| `PackAnimal` | A biome-appropriate pack animal of the player's faction, generated loaded, spawned at the edge and walked in under `Outposts.LordJob_Deliver` → `LordToil_Drop` → `JobGiver_DropAll` |
| `ForcePods` | `TradeUtility.SpawnDropPod` at the delivery spot, else `DropCellFinder.TradeDropSpot(map)` |
| `PackOrPods` | Pods if `Outposts_DefOf.TransportPod.IsFinished`, pack animal otherwise — **era-appropriate delivery for free** |
| `Store` | Accrues into the world object's `containedItems`; the player brings a caravan and takes it through `Outposts.Dialog_TakeItems` (`Outpost.TakeItem` / `TakeItems` are the commits) |

Every branch ends in a consolidated delivery letter. `Outpost.deliveryMap` is a scribed,
player-settable `Map` defaulting in `SpawnSetup` to the nearest `IsPlayerHome` map. **The reverse
direction ships too** [V]: `Outposts.Dialog_GiveItems` and
`Outposts.TransportPodsArrivalAction_AddToOutpost` put goods *and pawns* into a player-held world
object from a caravan or by pod — which is how a rebuild cost could be paid from home rather than
by a caravan standing on the tile.

**Cannot** [V]: address a faction; pay anything that is not a `Thing`; vary the method per object —
the branch comes from `OutpostsMod.Settings.DeliveryMethod`, one global per-client setting.

**Consequences.** That settings read is **T-18 and is not in §2b's B4 list**, which names only
`ProductionMultiplier` and `TimeMultiplier`. It is worse than a differing number: the `PackAnimal`
branch calls `PawnGenerator.GeneratePawn` off the shared stream, so two clients with different
delivery settings take different draws at the same tick. Recorded here; **§2b is #81's and is not
edited from this ticket.**

#### P3 — vanilla's royal permit as *"the player asks and it arrives"*

[V], `Assembly-CSharp.dll`. `RoyalTitlePermitDef` is XML: `royalAid` (`itemsToDrop` as a
`List<ThingDefCountClass>`, `pawnKindDef` + `pawnCount`, `favorCost`, `aidDurationDays`),
`cooldownDays`, `minTitle`, `permitPointCost`, `faction`, `usableOnWorldMap`, and `layerBlacklist`
(a `List<PlanetLayerDef>`). `RoyalTitlePermitWorker_DropResources.OrderForceTarget` drops the basket
at a cell the player targets on a colony map; `CallResourcesToCaravan` drops it into a caravan on
the world map. `RoyalTitlePermitWorker.FillAidOption` reads
`pawn.royalty.GetPermit(def, faction).LastUsedTick` against `def.CooldownTicks` and offers the aid
free off cooldown, or for `royalAid.favorCost` favour while on it.

**Gets us** the requirement's *"the player must be able to ask, not only to receive"* in shipped,
XML-authored form, including a **pawn** payload — and a worked precedent that aid can be
blacklisted per planet layer.

**Cannot** [V]: be offered through the permits card, title-gated trade or the comms console
without a title — but a permit can be held and used without one
([#168](https://github.com/cjd721/Rimworld-Archinity/issues/168); § *A sworn faction owes services* OS-2b). Availability runs through
`RoyalTitlePermitDef.AvailableForPawn` (`permitPointCost`, `minTitle`, prerequisites) and
`Pawn_RoyaltyTracker`, and the currency is royal favour. Using the *shape* for holdings means
riding the royalty tracker or reimplementing the cooldown. `AidDisabled_NewTemp` blocks a hostile
faction and an underground map.

#### P4 — the rebuild gate as a standing debt

**It can be expressed, and vanilla ships the shape** [V]. `RimWorld.Planet.TradeRequestComp`
carries a scribed `requestThingDef`, `requestCount` and `expiration`; `CompInspectStringExtra`
prints the requested thing, its market value and the time left **in the world object's own inspect
string**; `GetCaravanGizmos` yields the fulfil command only while
`CaravanVisitUtility.SettlementVisitedNow(caravan) == parent`; `Fulfill` takes the goods with
`CaravanInventoryUtility.TakeThings`, pays goodwill and fires a quest signal. A comp added to an
existing `WorldObjectDef` backfills into a live save
([`engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md)).

VEF supplies the other half [V]: `Outpost.AddPawn` consumes `Ext.CostToMake` out of the absorbed
caravan's goods and sets a scribed `costPaid`. The charge fires only when the caravan's **last
humanlike** joins — the deduction sits inside
`if (!caravan.PawnsListForReading.Any(p => p.RaceProps.Humanlike))` [V]. A roster rule that rejects
a humanlike therefore leaves the caravan alive and the cost uncharged (#170 OC-K2, **T-149**).

**Correction, and it is load-bearing — stated precisely, because the imprecise form is dangerous.**
**`costPaid` is a real gate, and it is not on the production path** [V]. Its four occurrences in
`Outposts.Outpost` are the field declaration, its `Scribe_Values.Look` in `ExposeData`, and **a read
and a write both inside `Outpost.AddPawn`**, where `if (!costPaid)` gates the **one-time deduction
of `Ext.CostToMake` from the absorbed caravan's goods** and the flag is then set — scribed, so the
charge survives a reload and is never taken twice. What it does **not** do is withhold yield:
neither `Produce()` nor `TickInterval(int)` consults it, directly or through any property [V].

***So VEF ships a scribed "this one has paid" ledger and no pay-before-you-yield gate. The withhold
is one `if` of ours on top of that ledger.*** **Do not read this as "`costPaid` is dead" — removing
it stops charging the player.**

**Cannot** [V]: `TradeRequestComp` carries exactly one `ThingDef` and count, so a multi-item cost
needs several comps or one of ours in the same shape; `ActiveRequest` is `expiration > TicksGame`,
so a never-lapsing debt means an absurd expiration or an override.

**Tech-tier scaling: yes, and it is XML** [V]. `FactionDef.techLevel` is a public `TechLevel` field
and a settlement's owner is `Settlement.Faction`; a cost table keyed by `TechLevel` is a
`DefModExtension` in the shape `OutpostExtension.CostToMake` already uses. **Caveat:**
`RimWorld.Planet.Settlement` carries **no tier field of its own** [V] — the tier is its faction's —
for an NPC settlement. A holding under R1 belongs to the player, so its tier must be stored at
conquest from the former faction; see § *Paying to advance a holding to a later era*, TR-1, and
**T-145**. Whether a settlement can carry anything of its own is
[#165](https://github.com/cjd721/Rimworld-Archinity/issues/165)'s.

#### P5 — accrued credit spent on a menu

**The list is free** [V]. `Settlement_TraderTracker` gives every settlement a faction-derived,
restocking stock: `TraderKind` is
`settlement.Faction.def.baseTraderKinds[abs(settlement.HashOffset()) % count]`,
`RegenerateStockEveryDays` is 30, and `RandomPriceFactorSeed` is
`Gen.HashCombineInt(settlement.ID, 1933327354)` — deterministic per settlement. Multiplayer
replaces the trade session with a synced `MpTradeSession` keyed on
`CaravanVisitUtility.SettlementVisitedNow(caravan)` [V].

**The currency is the constraint, and it is a fork rather than a shade** [V].
`RimWorld.TradeCurrency` has exactly two values — `Silver` and `Favor` — chosen by
`TraderKindDef.tradeCurrency`; `TradeDeal.CurrencyTradeable` tests `IsFavor` or
`ThingDef == ThingDefOf.Silver`, `TradeDeal` adds a `Tradeable_RoyalFavor` row in favour mode, and
`TradeUtility.GetPricePlayerSell` takes a `TradeCurrency`. **A menu priced in silver or royal favour
is Easy and rides the whole shipped UI; a menu priced in a bespoke per-holding credit is Hard** —
a `Tradeable` subclass plus patches across `CurrencyTradeable`, `UpdateCurrencyCount`,
`LimitCurrencyCountToFunds` and the price path.

#### Where payment arrives — and it follows home for free

**Both shipped delivery paths pick their destination by `Map.IsPlayerHome`** [V] —
`TitheWorker.DeliverInt` gates on it; `Outpost.Deliver` and `Outpost.SpawnSetup` select the nearest
map satisfying it. And [V] `Verse.Map.IsPlayerHome` is true when `wasSpawnedViaGravShipLanding`,
**or** the parent is a player-faction `MapParent` with `def.canBePlayerHome`, **or**
`GravshipUtility.PlayerHasGravEngine(this)`.

**So when the gravship becomes home, delivery follows it with no code at all** — the direct answer
to the requirement's *"delivery has to follow that move rather than assume a fixed tile"* and to
[#127](https://github.com/cjd721/Rimworld-Archinity/issues/127).

Surfaces available, all [V]: a drop pod at `DropCellFinder.TradeDropSpot` (orbital trade beacon →
comms console → any colonist building → random cell); a player-placed delivery-spot building; a
map-edge placement; a pack animal that walks in; a direct add to a caravan; and a stockpile on the
world object. **No planet-layer gate exists on any of them** — the only one read anywhere in the
payment paths is `RoyalTitlePermitDef.layerBlacklist`, which proves such a gate is expressible if
orbit should ever be excluded.

#### Can the pawn payload generate people? Yes — three read implementations

1. **`VFEEmpire.TitheWorker_Slaves.CreateDeliveryThings`** [V]:
   `PawnGenerator.GeneratePawn(PawnKindDefOf.Slave, Find.FactionManager.RandomNonHostileFaction(…))`
   then `pawn.guest.SetGuestStatus(Faction.OfPlayer, GuestStatus.Slave)`. **It never touches the
   settlement's inhabitants** — the settlement is a fiction, the pawn is fresh.
2. **`VOE.Outpost_Town.Produce`** [V]: generates pawns of the occupants' own `kindDef` and faction
   on a per-occupant social-skill roll.
3. **Vanilla `RoyalAid.pawnKindDef` + `pawnCount`** [V], XML-authored, delivered by the permit workers.

**So a people-paying holding needs no population model**, and
[#10](https://github.com/cjd721/Rimworld-Archinity/issues/10)'s altar-fuel route is a `workerClass`
and a def.

#### Recommendation (not a selection)

**P1 for the ledger, P2 for the arrival, P4 for the gate.** P1 is the only read carrier that already
holds payload, cadence, accrual and legibility in one scribed record and is synced end to end; P2
is the only read carrier for *how the goods physically show up*, and its `PackOrPods` branch gets
era-appropriate delivery without a rule of ours; P4 is vanilla and synced. **P3 is what
[#168](https://github.com/cjd721/Rimworld-Archinity/issues/168) should read** before designing an
ask. **P5 is Easy only if the credit is silver or royal favour** — see *Open questions*.

### Constraints

- **No shipped carrier lets the campaign choose who pays or what they pay.** P1's two selectors are
  both hardcoded; that is the single line every route has to cross.
- **`costPaid` gates the build charge, not the yield** [V]. It is read and written only inside
  `Outpost.AddPawn`; the production path never consults it. The withhold is ours — the charge is not.
- **`Settlement` stores no tier or specialty field** [V]. Vanilla does assign a per-settlement
  `TraderKind` from `baseTraderKinds` by ID hash (idle in the corpus), and #165's SS-1–SS-3 give a
  settlement a specialty of its own — see § *A settlement's specialty, and learning it before you
  commit*. Under R1 a holding's tier is stored, not read from its owner (P4's caveat, #167).
- **Vanilla trade knows two currencies** [V]. A third is a patch set, not a field.
- **The tithe walk's order is client-dependent.** [V on the mechanism; [I] that it desyncs in play.]
  `WorldComponent_Vassals.DoDay` iterates a `Dictionary<Settlement, TitheInfo>` whose insertion
  order is set by `GetTitheInfo` calls — and the Royalty tab's `AllPossibleVassals` is one such
  call, made client-locally. `TitheWorker.AmountProduced` draws `GenMath.RoundRandom` off the
  shared stream (always fractional at `TitheSpeed.Half` or `NormalAndHalf`), and
  `TitheWorker_Slaves` additionally calls `RandomNonHostileFaction` and `PawnGenerator.GeneratePawn`.
  MP Compat seeds `GetTitheInfo` but **does nothing about the walk order.** This sharpens §3's
  RUN item: the trigger is *one client opened the Royalty tab and the other did not.*
- **`OutpostsMod.Settings.DeliveryMethod` is a third T-18 read on the payout path**, and the branch
  it chooses is the one that generates a pawn.
- **Multiplayer registers `OrderForceTarget` only for `ITargetingSource` implementors
  `where t.Assembly == typeof(Game).Assembly`** [V] (`Multiplayer.Client.SyncMethods`). **A permit
  worker — or any targeting source — declared in our assembly is silently outside that
  registration.** Proposed as a trap.
- **`Dialog_TakeItems` and `Dialog_GiveItems` are `Window`s and are unsynced** (**T-80**). The
  commits to register are `Outpost.TakeItem` / `TakeItems` and the give side.
- **Already synced, and free:** `TradeRequestComp.Fulfill`,
  `RoyalTitlePermitWorker_DropResources.CallResourcesToCaravan` and every vanilla
  `OrderForceTarget`, `MpTradeSession`, and the whole VFE Empire tithe surface [V].

### Available mechanisms

| Mechanism | What it provides | Route | Evidence |
|---|---|---|---|
| `VFEEmpire.TitheInfo` / `WorldComponent_Vassals.DoDay` / `TitheWorker` | Scribed record, daily clock, accrual, undelivered-debt carry-over | P1 | [V] `294100/2938820380/1.6/Assemblies/VFEEmpire.dll` |
| `VFEEmpire.TitheTypeDef` (7 defs) | Payload catalogue in XML, with `workerClass` and `deliveryDays` | P1 | [V] `.../1.6/Defs/Misc/TitheTypeDefs.xml` |
| `VassalUtility.DeliveryDays` / `Mult` / `Commonality` | Cadence set (7 / 15 / 60 / never) and a 0.5×–2.5× weighted speed | P1 | [V] |
| `TitheWorker.DeliverInt` | Delivery to a caravan, or `DropPodUtility.DropThingsNear` on a player home map; **returns false and preserves the accrual** when neither is available | P1 | [V] |
| `TitheWorker_Honor.DeliverInt` | A payload that is not a `Thing` at all | P1 | [V] |
| `TitheWorker_Slaves.CreateDeliveryThings` | Generated slave pawns, independent of the settlement's population | P1 | [V] |
| `RoyaltyTabWorker_Vassals.DoVassal` | The legibility surface: per-delivery range, accrued "in stockpile", due-date bar | P1 | [V] |
| `Multiplayer.Compat.VanillaFactionsEmpire` | Syncs vassalise, cadence, release; seeds the payload draw | P1 | [V] `294100/1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll` |
| `Outposts.Outpost.Deliver` (+ `Deliver_Pods`, `Deliver_PackAnimal`, `LordJob_Deliver`) | Five arrival surfaces, a player-set `deliveryMap`, a delivery letter | P2 | [V] `294100/2023507013/1.6/Assemblies/Outposts.dll` |
| `Outposts.Dialog_TakeItems` / `Dialog_GiveItems` / `TransportPodsArrivalAction_AddToOutpost` | Caravan and pod transfer both ways against a player-held world object | P2, P4 | [V] |
| `RoyalTitlePermitDef` / `RoyalAid` / `RoyalTitlePermitWorker_DropResources` | XML-authored requested drop of goods **or pawns**, on a cooldown, priced in favour, with a planet-layer blacklist | P3 | [V] `Assembly-CSharp.dll` |
| `RimWorld.Planet.TradeRequestComp` | A scribed standing demand on a world object, legible in its inspect string, paid by a visiting caravan, **synced by Multiplayer** | P4 | [V] `Assembly-CSharp.dll` |
| `Outposts.Utils.CanSpawnOnWithExt` / `Outpost.AddPawn` / `costPaid` | Cost check against caravan inventory, one-time consumption of it, and a scribed paid-flag that **gates the charge inside `AddPawn` and nothing on the production path** | P4 | [V] |
| `FactionDef.techLevel` | The only tech-tier signal a settlement has | P4 | [V] |
| `Settlement_TraderTracker` / `TradeCurrency` / `Tradeable_RoyalFavor` | A faction-derived restocking list, priced, in two currencies only | P5 | [V] |
| `Verse.Map.IsPlayerHome` | Gravship clauses — delivery follows home without code | P2, P4, #127 | [V] |

**What does not exist, and where it shaped the routes:** nothing in the corpus lets a *chosen*
settlement pay a *chosen* payload. The wide pass narrowed to five mods — VFE Empire, Rim War, FT&V,
RimPacts, Worksites Expanded — all already depth-read on
[#120](https://github.com/cjd721/Rimworld-Archinity/issues/120), and `VFEEmpire.TitheTypeDef` is
the **only payment def family in the corpus**. What is far better supplied than the payment systems
are the **delivery, request, accrual and debt primitives**, and they come from vanilla and VEF
rather than from a vassalage mod. That is why every route above composes a shipped primitive with
one hardcoded selector replaced.

### Status

**Evidence class: READ**, established on
[#166](https://github.com/cjd721/Rimworld-Archinity/issues/166). Every mechanism in the table is
[V]; every route is [I] by construction.

**Sweeps, with the form that produced each result.** Both corpus roots plus
`common/RimWorld/Data`, `-g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'` throughout, attributed
with `python tools/corpus.py --which -`.

| Sweep | Form | Result |
|---|---|---|
| ASCII validator | `rg -a -l -e "TitheTypeDef"` | VFE Empire only — the form finds a `#Strings` name known present |
| ASCII, case-sensitive | `-e "Tithe"` / `"Vassal"` / `"Tribute"` | Tithe: VFE Empire, Worksites Expanded. Vassal: Rim War, VFE Empire, FT&V, RimPacts. Tribute: Rim War, FT&V, RimPacts, Worksites Expanded |
| ASCII validator, `-i` | `rg -a -l -i -e "TitheWorker"` | VFE Empire — a `#Strings` type name known present, found by the case-insensitive form |
| ASCII, `-i` | `rg -a -l -i -e "Stipend"` / `-e "Upkeep"` | **zero** |
| UTF-16 validator, same heap, `-i` | `rg -a -l -i "T\x00i\x00t\x00h\x00e\x00A\x00r\x00r\x00i\x00v\x00e\x00d\x00"` and `"I\x00n\x00S\x00t\x00o\x00c\x00k\x00p\x00i\x00l\x00e\x00"`, escapes typed literally into the pattern, never through `$(…)` | VFE Empire (and MP Compat for the second) — both are `Translate` key literals, i.e. `#US` strings, so each validator is drawn from the heap being searched |
| UTF-16 `#US`, `-i` | same form for `Tithe`, `Tribute`, `Vassal` | **the same five mods** |
| UTF-16 `#US`, `-i` | same form for `Stipend`, `Upkeep` | **zero** |
| XML, `-i` | `rg -l -i -e "Stipend" -e "Upkeep" -g '*.xml'` | 4 mods, **all prose**: two building descriptions, one backstory, and RimPacts' keyed strings for the **player** paying silver to keep a world decision active — the mirror of this document, not a carrier |
| XML def families | `rg -o -i -e "<[A-Za-z0-9_]+\.[A-Za-z0-9_]*(Tithe\|Tribute\|Vassal\|Payout\|Levy\|Tax)[A-Za-z0-9_]*>" -g '*.xml'`, read as a frequency table | **`VFEEmpire.TitheTypeDef` only** (18 occurrences = 7 defs × copies across roots and versions) |

**The load-bearing negative is the def-family row**, which was built case-insensitively over both
roots and `Data` from the start. The `Stipend` / `Upkeep` rows were first run ASCII-only and
case-sensitive; they have been re-run in both encodings with `-i` and with a validator drawn from
each heap, and the result is unchanged.

**Premises corrected:**

1. **`Outpost.costPaid` gates the build charge and nothing on the production path** [V]. Any
   reading of *The build* §2 or of
   [#170](https://github.com/cjd721/Rimworld-Archinity/issues/170) that treats VEF as shipping a
   pay-before-you-yield gate is wrong — and any reading that treats `costPaid` as inert is also
   wrong, because the `if (!costPaid)` inside `Outpost.AddPawn` is what charges the player.
2. **§2b's B4 is incomplete.** `OutpostsMod.Settings.DeliveryMethod` is a third settings read on the
   payout path, and the branch it selects generates a pawn off the shared stream [V]. Recorded
   here; the edit belongs to #81's section.
3. **§3 R0's *"delivers only into the lord's caravan or by drop pod beside the lord"*** is exact
   [V], and the omitted half matters: **when it can do neither it preserves the accrual** rather
   than dropping the payment.

**Verified available mechanisms — not selected:** the whole table above.

### Open questions

**Requirement gaps.** [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) was authored by
[#35](https://github.com/cjd721/Rimworld-Archinity/issues/35), now closed, so these are **unowned**:

1. **Is a per-holding accrued credit a "third currency"?** § *Constraints* forbids one — *"Goodwill
   and Reverence are the levers"* — while § *Required behavior* offers *"a credit the holding
   accrues that the player spends against that holding's own list"* as a live route. Vanilla makes
   this a sharp fork: silver or royal favour is Easy and free, anything else is Hard. **Someone must
   say whether a per-holding ledger counts as a currency.**
2. **Can the rebuild debt lapse?** The requirement says *"the debt stands either way"* but never
   says whether it expires, and `TradeRequestComp.expiration` is mandatory in the shipped shape.
3. **What happens to accrual the player cannot collect** — home unreachable, or in transit to orbit.
   The shipped behaviour is *keep accruing and pay out whole later*; the requirement states no
   intent, and "pays out whole later" carries a balance tail.

**Handed to a sibling, not taken here:**

- **The characteristic payload** replaces `WorldComponent_Vassals.GetTitheInfo`'s random draw.
  [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165).
- **Changing what a holding pays after the fact** is a field write, not a rebuild — `TitheInfo.Type`
  and `.Speed` are plain scribed fields [V].
  [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167) should know this.
- **P3 is the shipped *"the player asks"* shape** and is
  [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168)'s to reuse rather than re-derive.

**RUN, narrow, unowned — only if P1 is selected.** Two clients. Client A alone opens the Royalty
vassal tab (populating the dictionary through `AllPossibleVassals`); client B does not. Vassalise
two settlements with fractional per-day amounts on the same cadence. On the first shared delivery
day, expect identical stacks on both clients, or a desync trace naming `GenMath.RoundRandom` under
`WorldComponent_Vassals.DoDay`.

**Build questions deferred to the next map** (unowned until a route is selected): whether P1's
record is repointed or reimplemented; where the rebuild `if` sits; whether one delivery path serves
holdings and §2's outposts; which delivery method a holding uses and whether the player chooses it;
the numbers, which are
[the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

---

## Taking a settlement must be hard — a defended map and real defenders

### Purpose and scope

**Answers** [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *A holding is a settlement taken by force*: *"Taking one must be hard… real defenses and real defenders, with nobody helping… a settlement the colony can walk into does not satisfy this requirement"*, and § *Campaign progression* (difficulty follows the eras). Established on [#164](https://github.com/cjd721/Rimworld-Archinity/issues/164).

**Owns:**
- what builds a settlement's map;
- how strong its garrison is, and whether that follows tech tier;
- whether hand-authored and generated maps coexist;
- what survives the map being discarded.

**Does not own:**
- what happens once the settlement falls: § 3 *Vassals* (R1/R2) and [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172);
- tier changes to a holding: [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167);
- the orbital strongholds: [`ORBIT.md`](ORBIT.md) § *The build → 6*, which this section reuses as SM-6's donor;
- whether allies may join the fight: [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168) and *Open questions*.

### Verdict

- **Possible?** **Yes. Vanilla alone does not get there.** Every vanilla settlement carries a 1150–1600-point garrison regardless of faction or tier. Anything below Industrial gets sandbags and no turrets or mortars. KCSG layouts (XML) and one small C# hook on garrison size make the fight hard and tier-scaled. Set pieces and generated maps coexist. **Nothing done to a settlement map survives the players leaving**: it is rebuilt from the tile at full strength.
- **Multiplayer?** **With work.** Maps generate in lockstep and vanilla seeds them from the world seed and the tile (#88, #104). Three conditions apply:
  - KCSG's *generated* branch needs MP Compat's **T-33** transpiler.
  - The stale KCSG static that sets garrison size (**T-143**) must be owned, and SM-4 owns it.
  - Anything we write that runs at map generation draws only on `Verse.Rand` (**T-120**).

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **SM-1** Vanilla settlement, pawn kinds re-authored | Tier-flavoured defenders; turrets and mortars from Industrial. **Not hard enough alone** | vanilla `Base_Faction` | XML | Easy | Yes |
| **SM-2** KCSG generated layouts per faction | A varied walled base per faction; `defenseOptions` and `pawnGroupMultiplier`; tier by which layouts a faction def lists | VEF KCSG `chooseFromSettlements`; VBGE, VFEM2, VFEI2 content | XML | Easy | With work (T-33) |
| **SM-3** KCSG hand-authored set pieces per faction | Exporter-built castles and forts with turrets, siege engines and **authored defenders** in the grid | VEF KCSG `chooseFromlayouts`; Medieval Overhaul, VFE Classical content | XML | Easy | Yes |
| **SM-4** Garrison strength in C# | Garrison points on a curve we pick: tech tier, a per-settlement value, losses recorded on an earlier visit | ours; donor VFE Insectoids 2 prefix on KCSG `AddHostilePawnGroup`; vanilla `ResolveParams.settlementPawnGroupPoints` | C# | Medium | Yes |
| **SM-5** Named set pieces for particular settlements | One named settlement always a citadel; its siblings stay generated | ours: distinct Settlement `WorldObjectDef`, or our `MapGeneratorDef` postfix + `WorldObjectComp` | C# + XML | Medium | With work |
| **SM-6** Vanilla layout engine on the surface | Procedural fortress from a `StructureLayoutDef`, KCSG-free | ours: surface genstep shaped like `GenStep_OrbitalPlatform`; vanilla `LayoutWorker_Structure`, `GenStep_SettlementPawnsLoot` | C# + XML | Medium | Yes |
| **SM-7** Defenders who fight back during the assault | In-map reinforcements, stoppable by killing the caller; a defeat test we own | ours; donor Better Traders Guild | C# | Medium | With work |

| Requirement clause → | Real defenses | Real defenders | Follows tier | Set pieces + generated | Survives discard |
|---|---|---|---|---|---|
| SM-1 | Industrial+ only | 1150–1600 pts | pawn kinds only | — | no |
| SM-2 | yes | × layout multiplier | by layout list | generated half | layout yes, damage no |
| SM-3 | yes | authored + 1150–1600 | by layout list | set-piece half | layout yes, damage no |
| SM-4 | — | **yes** | **yes** | — | **only route that can carry losses** |
| SM-5 | per piece | per piece | per piece | **yes, per settlement** | as SM-2/SM-3 |
| SM-6 | yes | via SettlementPawnsLoot | by layout def | generated half | layout yes, damage no |
| SM-7 | — | **during the fight** | by threat points | — | — |

#### SM-1 — vanilla, pawn kinds re-authored

**Gets us [V]:**
- `GenStep_Settlement` → `SymbolResolver_Settlement`, under `LordJob_DefendBase`.
- **Garrison points** = `DefaultPawnsPoints` (1150–1600), unless `ResolveParams.settlementPawnGroupPoints` is set. `GenStep_Settlement` never sets it.
- **XML reaches** the faction's `Settlement` `pawnGroupMakers`: which pawns the points buy.
- **Industrial+ factions** get edge-defense turrets and mortars, and firefoam poppers.

**Cannot [V]:**
- raise the points;
- give a pre-Industrial base turrets, mortars or a perimeter wall. `SymbolResolver_EdgeDefense` zeroes turrets and mortars below Industrial, and edge defense rolls 50% below Industrial.

**Consequences:** the baseline #35 called "virtually pointless". It is free and sits under every other route for factions that no other route covers.

#### SM-2 — KCSG generated layouts per faction

**Gets us [V]:**
- `KCSG.Postfix_Settlement_MapGeneratorDef` returns `KCSG_Base_Faction` for any non-player settlement whose faction def carries `KCSG.CustomGenOption`.
- `SymbolResolver_Settlement` then builds the layout and pushes a `Settlement`-kind garrison of `DefaultPawnsPoints × defenseOptions.pawnGroupMultiplier`.
- `defenseOptions`: `addEdgeDefense`, `addSandbags`, `addTurrets`, `addMortars`, and turret/mortar def lists.
- **Shipped content:**
  - VBGE: Empire, Tribal, Outlander, Pirate. Defence layouts ×1.45–1.8, turrets and mortars on the Outlander and Empire Defence sets.
  - VFEM2: kingdom, clan, merchant guild.
  - VFEI2: insect hives.

**Levers:**
- **Tier is the layout list a faction def carries.** A faction whose def climbs at an era boundary generates its new tier's base on its next generation ([`engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md) § *What survives a swap*) [V].

**Cannot:**
- turrets or mortars below Industrial (**T-30**; siege engines go in a layout grid instead);
- any garrison curve beyond one multiplier per layout [V].

**Consequences:**
- **T-33** — `SettlementGenUtils.Sampling.Sample` uses an unseeded `System.Random`, fixed only by MP Compat's `PatchKCSG` [V].
- **Mixing SM-2 with SM-3 in one load order arms T-143.**

#### SM-3 — KCSG hand-authored set pieces per faction

**Gets us [V]:**
- The same faction hook with `chooseFromlayouts`: `SymbolResolver_RoomGenFromStructure` → `StructureLayoutDef.Generate`, plus a `Settlement`-kind garrison at `DefaultPawnsPoints`.
- A layout places anything with a ThingDef, including turrets, trebuchets and **pawns** (`SymbolDef.pawnKindDef`, `defendSpawnPoint`), per [`engine/mods/kcsg.md`](../engine/mods/kcsg.md) § *Siege placement*.
- **Shipped:** Medieval Overhaul's noble houses (three hand-built castles each); VFE Classical (`VFEC_ClassicalSettlement1`).
- **The exporter** makes a layout from a base built in dev mode.

**Levers:**
- walls and gates of any era, which is the answer to SM-1's missing pre-Industrial perimeter;
- defenders as authored as the walls;
- tier by layout list, as SM-2.

**Cannot:**
- scale the *generated* garrison. No multiplier applies on this branch, except by **T-143**'s accident.
- vary much: a set piece is the same fort every time, only rotated or picked from a short list.

**Consequences:**
- **This branch never calls `SettlementGenUtils.Generate`, so T-33 does not apply to it** [V]. It is MP-safe with or without MP Compat.
- Authoring cost is one exported layout per fort.

#### SM-4 — garrison strength in C#

**Mechanisms [V]:**
- KCSG `SymbolResolver_Settlement.AddHostilePawnGroup`, a private method with a shipped prefix precedent. VFE Insectoids 2 replaces it for `Faction.OfInsects` and multiplies points by a `SimpleCurve` of `WealthUtility.PlayerWealth` (25k→×0.25, 100k→×1, 1M→×10).
- Vanilla `ResolveParams.settlementPawnGroupPoints`. `GenStep_Outpost` sets it from `sitePart.parms.threatPoints` and exposes `defaultPawnGroupPointsRange` to XML.

**Levers [I]:**
- points from `faction.def.techLevel`, from a value stored per settlement, from player wealth, or reduced by losses recorded on an earlier visit;
- one seam covers SM-2, SM-3 and any KCSG faction; a second covers vanilla.

**Cannot:** change *what* stands on the map. It is a garrison dial only.

**Consequences:**
- **Owning the multiplier removes T-143**, since the stale static is no longer read.
- Inputs must be simulation state, never `ModSettings` (**T-18**).

#### SM-5 — named set pieces for particular settlements

**Mechanisms [V]:**
- `Settlement.MapGeneratorDef` returns `def.mapGenerator` first, then `Base_Player` for the player, then `Base_Faction`.
- KCSG's postfix then:
  - (a) overrides that with `KCSG_Base_Faction` if the **faction** has a `CustomGenOption`;
  - (b) otherwise returns `KCSG_WorldObject` if any world object on the tile has one.
- `KCSG.GenStep_WorldObject` reads the extension from `map.Parent.def`, so (b) works **only when the Settlement's own def carries it**. A marker or overlay object (e.g. #92's) null-refs at generation.
- **Every settlement, player or NPC, is built from `layer.Def.SettlementWorldObjectDef`** (`FactionGenerator`, `SettleUtility`, `ScenPart_PlayerFaction`). **Never put `<mapGenerator>` on that def**, because new player colonies would generate from it too.
- **Precedents for a Settlement on a distinct def:**
  - vanilla `ArchotechSettlement` (`Settlement_SecondArchonexusCycle`);
  - Faction Territories' `ExecuteCedeToFactionAtTile`, which re-adds a Settlement by `defName` (§ 3 R2) (uncalled in FT&V; a precedent for the write, not a live path — #172).
- An XML-patched `WorldObjectComp` on the Settlement def backfills existing saves ([`engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md) § *A `WorldObjectComp` added by XML patch backfills into an existing save*).

**Levers:** a campaign beat can name *the* fortress, and the rest of its faction still generates under SM-2 or SM-3.

**Cannot:** be placed by XML. Worldgen places one Settlement def for everyone, so the named piece is placed or re-defined by our code [V]:
- at worldgen;
- at a reveal;
- by recreating the settlement (new ID, per #165 and #167 on the board);
- by writing `def` in place (comps rebuilt only on reload, per #167).

**Consequences:**
- Our postfix and KCSG's run on the same getter, so priority must be set.
- The placement must be a synced command or run at worldgen.

#### SM-6 — vanilla layout engine on the surface

**Mechanisms [V]:**
- #66 established that `GenStep_OrbitalPlatform` + a `StructureLayoutDef` + `GenStep_SettlementPawnsLoot` (which needs the `SpawnRect` map var) yields a garrisoned procedural structure with no new C# **on orbit** ([`ORBIT.md`](ORBIT.md) § *The build → 6*).
- **Surface pieces vanilla ships:**
  - `GenStep_AncientRuins`, which takes a `layoutDef` (faction `AncientsHostile`);
  - `LayoutWorker_Mechhive`;
  - `PrefabDef`, which holds things and terrain but no pawns;
  - `GenStep_ScatterGroupPrefabs`.
- **No shipped surface genstep** places one layout as a faction base and sets `SpawnRect`.

**Levers [I]:**
- one layout def gives a different fortress every time;
- no KCSG, so no T-33;
- the garrison can be refilled by `GenStep_SettlementPawnsLoot`, whose XML sets the faction and loot.

**Cannot:**
- choose the settlement it applies to (SM-5's seam);
- look like a tribal village or a medieval town without authored `LayoutRoomDef`s. Shipped rooms are Ancient-, Orbital- or Mechhive-flavoured [I].

**Consequences:** one genstep of ours on a verified vanilla engine; **T-55** applies to any `LayoutWorker` we author.

#### SM-7 — defenders who fight back during the assault

**Donors [V]:**
- **Better Traders Guild's defender job** (`JobDriver_BTGCallResupply` → `ResupplyRaidUtility.TryTriggerReinforcementRaid`) fires a forced `RaidEnemy` on the settlement map at `StorytellerUtility.DefaultThreatPointsNow`, 15% as a centre drop on a colonist.
- **BTG replaces the defeat test**: patches on `SettlementDefeatUtility.IsDefeated`/`CheckDefeated` and a `SecurityCensus` `MapComponent`.
- **Vanilla already adds** `TimedDetectionRaids.StartDetectionCountdown(240000)` on any non-home settlement map it generates.

**Levers:**
- a timer the player races;
- a caller to kill first;
- a fall condition that is not "every humanlike threat is down".

**Cannot [V]:** BTG's version is gated on a `ModSettings` bool (**T-18**), so it cannot be used as shipped.

**Consequences:** a custom defeat test moves the instant `CheckDefeated` swaps the Settlement for a `DestroyedSettlement`. That is the seam § 3 R1/R2, #152 and #172 all key on. Three writers touch it, and they should be one build question with one owner (see *Open questions*):

  - §1 Build B's `CheckDefeated` block (#92);
  - SM-7's replaced `IsDefeated`;
  - § 3's last-base `defeated` intercept (R1/R4).


#### What survives the map being discarded — every route

**What vanilla does [V]:**
- `Settlement.ShouldRemoveMapNow` is true once no colony pawn, rescue-quest relative, grav anchor or grav engine remains, and **the map is deinitialised**.
- `EnterCooldownComp` (on the `Settlement` def, `durationDays` 1, `autoStartOnMapRemoved`) then blocks re-entry for one day.
- `MapGenerator.GenerateMap` seeds `Rand` from `HashCombineInt(world seed, Tile)`, so the next visit **rebuilds the same base** for the same inputs [I, follows from the seed]. The inputs are the faction def, map size and the def set.
- **Losses do not carry over.** `Settlement.previouslyGeneratedInhabitants` is never populated: `PawnGenerator` adds to it only under `request.Inhabitant && !request.Tile.Valid`. The garrison returns at full strength, with loot regenerated.
- **Under SM-2 without MP Compat** the rebuilt base also differs from visit to visit (T-33).

**Consequences for the story:**
- **An assault is won in one sitting**, or started again.
- **A raid-and-retreat cannot whittle a garrison down.**
- **A settlement recreated on the same tile rebuilds the same layout**, since the tile is the only identity that survives replacement (#165).

**Routes to make attrition survive:**
- **SM-4 reading a loss record** kept on the Settlement (an XML-patched comp), Medium.
- **Keeping the map alive** by overriding `ShouldRemoveMapNow`, Hard, which leaves a live map ticking on both clients. **Not recommended**: it is a second colony map in all but name, and costs performance under lockstep.

#### Recommendation (not a selection)

- **SM-3 for the factions whose bases should read as authored places** (medieval, classical), and **SM-2 for the rest**. Both are XML, and between them they cover walls and defenses at every tier.
- **Add SM-4 under both.** It is the only route that makes the garrison follow tier, the only one that can carry losses across visits, and it removes **T-143**.
- **SM-5 only for the handful of settlements the plot names.**
- **SM-7 is flavour, worth it where a fall condition is wanted.**
- **SM-6 if KCSG is ever dropped**, or for procedural variety without T-33.

### Constraints

- **Garrison points are not reachable from XML on a vanilla settlement.** `DefaultPawnsPoints` is `static readonly`, and `GenStep_Settlement` sets no `settlementPawnGroupPoints` [V].
- **Below Industrial, no generator places turrets or mortars** (**T-30** for KCSG; `SymbolResolver_EdgeDefense` for vanilla) [V]. Pre-Industrial defenses must be in a layout grid.
- **Player colonies and NPC settlements share one `WorldObjectDef`** [V]. A `mapGenerator` on it rebuilds new player colonies too (**T-144**). Per-settlement choice needs a getter postfix or a distinct def.
- **A settlement's map does not persist** once the players leave, and its garrison resets [V].
- **T-33** — KCSG `chooseFromSettlements` is unseeded without MP Compat. **`chooseFromlayouts` is not affected** [V].
- **T-143** — KCSG's static `GenOption.settlementLayout` is never reset. On the `chooseFromlayouts` branch it multiplies garrison points by the last generated `SettlementLayoutDef`'s `pawnGroupMultiplier`: process history, divergent between clients after a rejoin [V mechanism, I consequence].
- **T-120** — anything we run at map generation iterates ordered collections and draws only `Verse.Rand`.
- **T-18** — no garrison or reinforcement rule may read `ModSettings`.
- **T-55** — any `LayoutWorker` of ours goes in an `Archinity.*` namespace; write `<StructureLayoutDef>` for vanilla's and `<KCSG.StructureLayoutDef>` for KCSG's.
- **T-29, T-32** — KCSG layout authoring.

### Available mechanisms

| Mechanism | What it is | Used by | Evidence |
|---|---|---|---|
| `GenStep_Settlement`, `SymbolResolver_Settlement` | vanilla base + garrison; `DefaultPawnsPoints` 1150–1600; Industrial gates on firefoam | SM-1 | [V] `Assembly-CSharp.dll` |
| `SymbolResolver_EdgeDefense` | turrets and mortars zeroed below Industrial | SM-1 | [V] |
| `ResolveParams.settlementPawnGroupPoints`, `GenStep_Outpost` | garrison points override; outpost fills it from site threat points | SM-4 | [V] |
| `Settlement.MapGeneratorDef` | `def.mapGenerator` → `Base_Player` → `Base_Faction` | SM-5 | [V] |
| `layer.Def.SettlementWorldObjectDef` | one def for player and NPC settlements | SM-5 constraint | [V] `FactionGenerator`, `SettleUtility`, `ScenPart_PlayerFaction` |
| `Settlement.ShouldRemoveMapNow`, `EnterCooldownComp`, `MapGenerator.GenerateMap` seed | discard, 1-day cooldown, tile-seeded rebuild | persistence | [V] |
| `Settlement.previouslyGeneratedInhabitants` / `PawnGenerator` | dead: the writer's condition is inverted | persistence | [V] |
| `TimedDetectionRaids` | retaliation countdown on a generated settlement map | SM-7 | [V] |
| KCSG `CustomGenOption`, `Postfix_Settlement_MapGeneratorDef`, `GenStep_Settlement`, `GenStep_WorldObject`, `SymbolResolver_Settlement`, `DefenseOptions`, `SymbolResolver_EdgeDefenseCustomizable` | faction and per-def settlement generation, garrison, defense options | SM-2, SM-3, SM-5 | [V] `2023507013/1.6/Assemblies/KCSG.dll` |
| VBGE `Patches/Settlements.xml`, `SettlementDefs/*.xml` | Empire/Tribal/Outlander/Pirate layout sets, Defence ×1.45–1.8 | SM-2 | [V] `3209927822/1.6` |
| VFEM2, VFEI2 faction `CustomGenOption` | `chooseFromSettlements` | SM-2 | [V] `3444347874/1.6`, `3309003431/1.6` |
| Medieval Overhaul noble houses, VFE Classical | `chooseFromlayouts` set pieces; 33 pawn symbols in MO | SM-3 | [V] `3219596926/1.6`, `2787850474/1.6` |
| VFE Insectoids 2 `SymbolResolver_Settlement_AddHostilePawnGroup_Patch` | garrison × wealth curve, one faction | SM-4 donor | [V] `3309003431/1.6/Assemblies/VFEInsectoids.dll` |
| Odyssey `GenStep_OrbitalPlatform`, `GenStep_SettlementPawnsLoot`, `GenStep_AncientRuins`, `PrefabDef` | vanilla layout engine and garrison genstep | SM-6 | [V] (#66; this ticket) |
| Better Traders Guild `ResupplyRaidUtility`, `SecurityCensus`, defeat patches | in-map reinforcement; custom fall test | SM-7 donor | [V] `3684587591/1.6/Assemblies/BetterTradersGuild.dll` |
| MP Compat `VanillaExpandedFramework.PatchKCSG` | T-33 fix on `Sampling.Sample`; `KCSG_Skyfaller` push/pop | SM-2 | [V] `1629973374/1.6/Assemblies/Multiplayer_Compat.dll` |

**Read and set aside:**
- **Rim War's settlement reinforcement** (`AttackNow_SettlementReinforcement_Postfix`): Rim War is barred [I, name only].
- **VEF `IncidentWorker_Reinforcements`**: a storyteller raid, not a settlement defense [V].
- **VFE Settlers' `GenStep_SpawnWanted`** and **Factional War's camp gensteps**: sites, not settlements [V, type lists].
- **KCSG `SpawnAtWorldGen`**: spawns `Site`s only (it casts to `Site`), so it cannot seed a set-piece Settlement [V].

### Status

**Evidence class: READ**, [#164](https://github.com/cjd721/Rimworld-Archinity/issues/164).

- **Every mechanism in the table is [V]. Every route is [I] by construction.**
- **Wide pass**, run by ASCII sweeps of both roots (`!**/obj/**`, `!**/Referenced/**`, case-insensitive) for:
  - `settlementPawnGroupPoints`, `DefaultPawnsPoints`, `SymbolResolver_Settlement`, `GenStep_Settlement`, `pawnGroupMultiplier`, `AddHostilePawnGroup`, `einforcement`;
  - an XML sweep for `KCSG.CustomGenOption`, and the MP Compat check for `RotAllThing`.
- **The UTF-16 sweep was hand-typed null-interleaved**, validated against `Sampling`.

**Premises corrected:**
1. T-33's *"faction strongholds take the `SettlementLayoutDef` path regardless"*: `chooseFromlayouts` does not.
2. `engine/mods/kcsg.md`'s garrison formula holds only on `chooseFromSettlements`.
3. § 3 R2's regeneration note is vanilla map discard, not T-33.

### Open questions

- **Requirement — unowned, `requirements/TERRITORY.md`:**
  - Should a failed assault leave the garrison weakened? Today it resets; only SM-4 can change that.
  - Does *"nobody helping"* exclude allied aid? Per #168, a royal permit's aid runs at Neutral on any non-hostile map, and a settlement assault map is not excluded [I].
- **Balance, build map ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)):**
  - the garrison curve by tier;
  - which factions get SM-3 set pieces;
  - which settlements SM-5 names.
- **Residual [I]:** KCSG's `SettlementUtility.Attack` postfix draws `Rand` in `LongEventHandler.ExecuteWhenFinished` (`GenOption.RotAllThing`), and MP Compat does not patch it. It is believed identical on both clients. Owner: [#16](https://github.com/cjd721/Rimworld-Archinity/issues/16).
- **Build (unowned until selected):**
  - Harmony priority against KCSG's getter postfix;
  - where a named set piece gets its def;
  - the loss record's shape;
  - whether SM-7's fall test replaces or wraps `IsDefeated`.
- **Build, one question ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)): who owns the defeat seam.** Three writers touch the moment
  `CheckDefeated` swaps a settlement for a `DestroyedSettlement`: §1 Build B's `CheckDefeated` block,
  SM-7's replaced `IsDefeated`, and §3's last-base `defeated` intercept (R1/R4). They must be
  designed as one seam, not three.

---

## A settlement's specialty, and learning it before you commit

### Purpose and scope

This section answers [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) on three points:

- § *A holding is a settlement taken by force*: *"what a holding pays is characteristic of what was taken… two layers: the faction's and the particular settlement's, with the tile making a yield plausible"*;
- § *Player information and agency*: *"knowing is earned by going"* and *"a faction's own specialty is public"*.

Established on [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165).

**Owns:** whether a faction and a settlement can carry a specialty, what derives or stores it, and what reveals it.

**Does not own:**
- the payload's form and schedule: § *What a holding pays* ([#166](https://github.com/cjd721/Rimworld-Archinity/issues/166)). This section feeds its P1 selector.
- retiering: [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167).
- the discovery engine: [`CHARTING.md`](CHARTING.md) § *Natural discovery* ([#146](https://github.com/cjd721/Rimworld-Archinity/issues/146)), whose Routes A and D are this section's SV-3 and SV-4 seams.
- the caravan encounter: [`POLITICS.md`](POLITICS.md) § *Settlements meet passing caravans* ([#136](https://github.com/cjd721/Rimworld-Archinity/issues/136)).

### Verdict

- **Possible? Yes, for both layers.** A faction's specialty is XML, and vanilla already announces part of it at first trade. A particular settlement can carry a durable specialty of its own by three different routes:
  - vanilla's idle per-settlement trader selection (XML);
  - a pure derivation from tile + faction (RimPacts ships one);
  - a stored per-settlement record (VFE Empire and Better Traders Guild ship the shape).

  Every named reveal has a seam. The fallback of *no settlement layer* is not needed.
- **Multiplayer? Yes for derived and XML routes. With work for stored state and reveals.**
  - Derivations read only shared, scribed values and draw no `Rand`.
  - Stored rolls and knowledge writes must come from a synced context, or be seeded.
  - The scouting outpost carries #146's T-18 settings work.

### Routes

**Faction layer**

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **SF-1** Vanilla legibility | Trade caravans arrive named by trader kind; an Ideology faction sends slavers only if its creed approves | vanilla (+ Ideology) | XML | Easy | Yes |
| **SF-2** Declared specialty on the `FactionDef` | A named payload or category per faction for #166 to read; public from worldgen | vanilla `DefModExtension`; precedent FT&V `Dialog_Vassalage` | XML | Easy | Yes |
| **SF-3** First-contact gate | Specialty hidden until the first envoy, caravan, comms call or meeting | ours | C# | Medium | With work |

**Settlement layer**

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **SS-1** Several `baseTraderKinds` per faction | Each settlement draws one of several trade profiles: stock, buy list, prices | vanilla `Settlement_TraderTracker.TraderKind` | XML | Easy | Yes |
| **SS-2** Derived from tile + faction | A specialty computed on demand from biome, hilliness, mutators and landmark; no record | ours; donor RimPacts `RptSpecialtyUtility` | C# | Medium | Yes |
| **SS-3** Stored per settlement | Rolled once, scribed, hand-placeable, rewritable, immune to later table edits | ours; donors VFE Empire `TitheInfo` + MP Compat seed, BTG `TradersGuildWorldComponent` | C# + XML comp patch | Medium | Yes if seeded |
| **SS-4** Settlement def variants at worldgen | Specialty as a def extension on one of several settlement defs | ours; patch `FactionGenerator` | C# + XML | Medium | Yes. **Not recommended**: SS-3 with worse reach |
| **SS-5** No settlement layer | Faction specialty only; the requirement survives | SF-1/SF-2 | XML | Easy | Yes |

**Reveal**

| Route | Reveals on | Seam | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **SV-1** Visit | A caravan arriving to visit, trade, gift or attack | `CaravanArrivalAction_*.Arrived` | C# | Medium | Yes |
| **SV-2** Trade | Opening trade there | vanilla `everGeneratedStock` / `EverVisited`, or the stock itself | none, or C# display | Easy–Medium | Yes |
| **SV-3** Caravan nearby | Tile entry within N tiles, or a pinned meeting | [`CHARTING.md`](CHARTING.md) Natural discovery Route A; [`POLITICS.md`](POLITICS.md) #136 Route B | C# | Medium | Yes |
| **SV-4** Scouting outpost | Its tick reveals settlements within range | [`CHARTING.md`](CHARTING.md) Natural discovery Route D | C# + XML | Medium | With work (T-18) |
| **SV-5** First contact | Faction layer only | SF-3 | C# | Medium | With work |
| **SV-6** Public at once | Nothing earned | vanilla `Dialog_SellableItems`, inspect strings | none | Easy | Yes. **Fails the requirement**; SS-1 does this by default |

Every route is **[I]** as a composition; its mechanisms are [V].

#### SF-1 — vanilla legibility

**Gets us** [V]:
- `IncidentWorker_TraderCaravanArrival.SendLetter` labels the letter with `traderKind.label`, so the first caravan says what the faction trades.
- `TraderKindCommonality` zeroes a `"Slaver"`-category kind unless every ideo of the faction approves of slavery. A slaver tribe is readable from its creed.

**Cannot:** hide anything.

#### SF-2 — declared faction specialty

**Gets us:** a `DefModExtension` on `FactionDef` [V seam]. FT&V already builds a holding catalogue from `faction.def.baseTraderKinds` filtered by `techLevel` [V, via #167].

**Consequence:** it follows `Faction.def`, so a tier climb at an era boundary changes it. Under #120 R1, **never read it from `holding.Faction`**, which is the player. Read it from the remembered former faction.

#### SF-3 — first contact

**Gets us** [V]:
- **No carrier exists.** `Faction` scribes no met state, and no mod in either root carries one. `firstcontact`, `knownfaction`, `unknownfaction`, `metfaction`, `contactedfaction`, `factionreveal`, `factionknown` and `everMet` all returned 0 in an ASCII `-i` sweep over `.dll`+`.xml`.
- VEF's *FactionDiscovery* adds factions missing from a save; it is not knowledge.
- The route is a `WorldComponent` set of factions, written from:
  - trade and visitor incidents;
  - `CaravanArrivalAction_Trade.Arrived`;
  - the #136 meeting;
  - `Faction.TryOpenComms`. Medieval Overhaul's messenger table reaches it before radio (#154).

**Cannot:** reach a Neolithic colony by comms, since there is no console.

**MP:** write from the incident or arrival, never from dialog construction (T-82, T-95) [I].

#### SS-1 — several `baseTraderKinds`

**Gets us** [V]:
- `TraderKind` returns `Faction.def.baseTraderKinds[|ID.HashOffset()| % count]`, live, with no `Rand`.
- **No faction in the corpus lists more than one.** Every `baseTraderKinds` node in both roots + `Data`, with comments stripped, has a single `<li>`, and no patch adds one.
- That kind drives the stock (`RegenerateStock` passes `traderDef`, `tile`, `makingFaction`), the buy list, the prices, and #166 P5's menu.

**Cannot** [V]:
- consult the tile.
- survive replacement: `WorldObjectMaker.MakeWorldObject` assigns a fresh ID. `SetFaction` keeps the ID (#152).
- stay hidden: **Show sellable items** (`Settlement.GetGizmos` → `Dialog_SellableItems`) lists every `WillTrade` def to anyone.

An R1 holding is a plain `WorldObject` with no trader tracker, so copy the kind at conquest.

#### SS-2 — derived from tile + faction

**Gets us** [V] (`3762723122/Assemblies/RimPacts.dll`, `RimPacts.RptSpecialtyUtility`):
- `SpecialtyOf` (`RptSpecialtyUtility.BuildPool`) pools candidate defs from the tile's mutators and landmark together, else hilliness, else (Spacer and above) a tech pool, else biome.
- It filters and extends the pool by `Faction.def.techLevel` (Industrial and Spacer factions add components) and picks `|HashCombineInt(ID, 977)| % count`, with no stored state.
- RimPacts spends it in its stock (a `RegenerateStock` postfix), its tribute and its prices, and displays it to all in `WITab_RptTrade`.

**It is a donor, not the rule** [V]:
- the tables are C#;
- **the tile computes the yield**, which is the requirement's "formula";
- the ID hash re-rolls on replacement. Derive from `Tile`.

**Consequences:**
- **re-derivable means movable.** A later edit to tables or weights, or a faction's tier climb, silently changes every existing settlement's specialty in a running save.

#### SS-3 — stored per settlement

**Gets us** [V]:
- **Storage option 1:** a `WorldObjectComp` patched onto the `Settlement` def (`PostExposeData`, `CompInspectStringExtra`, `GetCaravanGizmos`, `PostMapGenerate`). It backfills into existing saves (`engine/factions-and-worldgen.md`).
- **Storage option 2:** a `WorldComponent` keyed on `PlanetTile`, which scribes ([`CHARTING.md`](CHARTING.md) Natural discovery).
- **Donor 1:** VFE Empire's per-settlement `TitheInfo`, seeded under MP by MP Compat's `Rand.PushState(HashCombineInt(ID, tile))` (§ *What a holding pays* P1).
- **Donor 2:** Better Traders Guild (`3684587591/1.6/Assemblies/BetterTradersGuild.dll`). It postfixes the `TraderKind` getter, draws under `Rand.PushState(HashCombineInt(ID, ticks))`, caches in a scribed `Dictionary<int,string>` on `TradersGuildWorldComponent`, and prints it in a `GetInspectString` postfix. It rotates on restock, so it is the shape rather than the rule.

**Levers:**
- the story can place a specialty by hand;
- #167 can rewrite it;
- balance edits do not move it;
- a tile-keyed record survives conquest untouched.

**Cost:** a shadow record. The comp form dies with the `Settlement`, so it must be copied at R1.

**MP:**
- seeded, or rolled in a synced context;
- a lazy `Rand` draw from UI is client-local.

#### SS-4 — settlement def variants (not recommended)

[V] Worldgen creates every settlement from `layer.Def.SettlementWorldObjectDef` (`FactionGenerator`, two sites). That is one def per layer, and no mod varies it.

Everything keyed on `WorldObjectDefOf.Settlement` would need the variants, including FT&V's cede path.

#### The tile nudges, not computes

**Vanilla's shape** [V]:
- `StockGenerator.GenerateThings(PlanetTile forTile, Faction)` receives the settlement's tile.
- `StockGenerator_Animals` filters by that tile's temperature behind the XML flag `checkTemperature`.
- A stock generator subclass can weight by biome the same way. This is plausibility, not computation.

**Inside SS-2 or SS-3** [I]: the faction authors the list, and biome and hilliness multiply the weights of a seeded pick. RimPacts is the counter-example to avoid.

#### Reveal routes

**The knowledge record.** Apart from vanilla's trade bit, it is ours. Hold one colony-wide record, which both players share, **keyed on the tile** so it survives conversion to a holding.

- **SV-1** [V]: `CaravanArrivalAction_{VisitSettlement,Trade,OfferGifts,AttackSettlement}.Arrived` run from the pather in the world tick. Trade's arrival opens `Dialog_Trade`, which MP turns into an `MpTradeSession` (#136).
- **SV-2** [V]: `Settlement_TraderTracker.everGeneratedStock` is scribed as `wasStockGeneratedYet`, set by `RegenerateStock`, and printed by `Dialog_SellableItems` as `TraderNotVisitedYet`.
  - **It means "stock generated":** any code reading `Goods` sets it.
  - If the specialty rides the stock (SS-1, or RimPacts' injection), the trade window reveals it with no code.
- **SV-3:** cite [`CHARTING.md`](CHARTING.md) Natural discovery Route A (`WorldObject.PositionChanged`, which covers foot and vehicle caravans) plus a tile-distance check (`ApproxDistanceInTiles` / `TraversalDistanceBetween`). Alternatively, #136 Route B's pinned meeting.
- **SV-4:**
  - **No scouting outpost ships** [V]. VOE 1.6 has 13 defs and VFE Classical has 4, none of them a scout. Only Artillery and Defensive set `Range`.
  - The route is Natural discovery Route D: an `Outpost` subclass walking settlements with VOE `Outpost_Artillery`'s `ApproxDistanceInTiles(target.Tile, Tile) <= Range`.
  - `OutpostsMod.Setup` overwrites `OutpostExtension.Range` per client (T-18). Once §2c's unconditional `Setup` prefix is built, `Range` is safe as XML; until then, the range belongs on our own `DefModExtension`.
  - The same tick can find (#146) and reveal (#165).
- **SV-6:** SS-1's **Show sellable items**, RimPacts' tab and BTG's inspect line all show their values to everyone. Any selected display needs a knowledge check.

#### Recommendation (not a selection)

- **Faction layer:** SF-1 + SF-2. SF-3 only where a beat needs a secret trade.
- **Settlement layer:**
  - **SS-3 keyed on the tile** is the only route unchanged by conquest, era climbs and balance edits;
  - **SS-1** is the cheapest and worth having as trade flavour regardless;
  - **SS-2** if no record is wanted and a movable specialty is acceptable.
- **Reveal:** SV-1 + SV-2 + SV-3, with SV-4 as the scouting outpost's job, all writing one tile-keyed record.

### Constraints

- **Identity.** `WorldObjectMaker.MakeWorldObject` assigns a new ID [V]. Anything derived from or keyed on `WorldObject.ID` re-rolls or orphans when a settlement is replaced: conquest (#120 R1), R2's recreation, or a cede by destroy-and-add. `SetFaction` keeps the ID (#152). **The tile is the only identity that survives replacement** (**T-140**).
- **Owner.** Under R1 a holding's `Faction` is the player. A specialty read live from it — a `FactionDef` extension or a tech filter — reads the colony's def. An R1 holding has no trader tracker, so `TraderKind` is not read; copy it at conquest. This extends #167's tier warning (**T-145**).
- **Era.** Every derived route reads `Faction.def`, which the era boundary may swap (`engine/factions-and-worldgen.md` § *Climbing a faction by swapping `Faction.def`*). Stored routes do not.
- **A factionless settlement NREs in `TraderKind`** [V, #172]. SS-1 cannot serve a settlement with no faction.
- **T-18** on any outpost range; **T-82 / T-95 / T-96** on any dialog-borne reveal.

### Available mechanisms

| Mechanism | Provides | Route | Evidence |
|---|---|---|---|
| `Settlement_TraderTracker.TraderKind` | Per-settlement pick from `baseTraderKinds` by ID hash; idle in the corpus | SS-1 | [V] `Assembly-CSharp.dll` |
| `Settlement_TraderTracker.everGeneratedStock` / `EverVisited` | Scribed per-settlement "stock generated" bit | SV-2 | [V] |
| `Dialog_SellableItems` (Show sellable items gizmo) | Public per-settlement trade profile; `TraderNotVisitedYet` line | SV-2, SV-6 | [V] |
| `StockGenerator.GenerateThings(PlanetTile, Faction)`; `StockGenerator_Animals.checkTemperature` | Tile-aware stock, a plausibility filter in XML | Tile nudge | [V] |
| `IncidentWorker_TraderCaravanArrival.SendLetter` / `TraderKindCommonality` | Trader kind named at arrival; slaver kinds gated on creed | SF-1 | [V] |
| `CaravanArrivalAction_{VisitSettlement,Trade,OfferGifts,AttackSettlement}` | Arrival hooks in the world tick | SV-1, SF-3 | [V] |
| `WorldObjectComp` (`PostExposeData`, `CompInspectStringExtra`, `PostMapGenerate`) | Per-settlement storage and display | SS-3 | [V] |
| `WorldObjectMaker.MakeWorldObject`; `FactionGenerator` | New ID on creation; one settlement def per layer | Constraints, SS-4 | [V] |
| RimPacts `RptSpecialtyUtility`, `Patch_SettlementStock_Specialty`, `WITab_RptTrade` | Derived per-settlement specialty, spent in stock, tribute and prices; public tab | SS-2 donor | [V] `3762723122/Assemblies/RimPacts.dll` |
| BTG `SettlementTraderTrackerGetTraderKind`, `TradersGuildWorldComponent`, `SettlementGetInspectString` | Seeded, cached, scribed per-settlement trader kind, shown in inspect | SS-3 donor | [V] `3684587591/1.6/Assemblies/BetterTradersGuild.dll` |
| VFE Empire `TitheInfo` + MP Compat seed | Stored per-settlement record, deterministic under MP | SS-3 donor | [V] § *What a holding pays* P1 |
| FT&V `Dialog_Vassalage.BuildSettlementSimCatalog` | Holding catalogue from `faction.def.baseTraderKinds` | SF-2 precedent | [V] via #167 |
| VEF `Outposts.Outpost` / VOE `Outpost_Artillery` range predicate | Range-bounded outpost action | SV-4 | [V] via #146 |

**What does not exist:**
- a met-faction record;
- a scouting outpost;
- any faction with more than one settlement trader kind;
- a per-settlement specialty carrier other than RimPacts. The sweeps are listed under *Status*.

### Status

**Evidence class: READ**, established on [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165). Mechanisms [V]; routes [I].

**Sweeps.** Both corpus roots + `Data`, with `obj/` and `Referenced/` excluded:

| Sweep | Encoding and pattern | Result | Validation |
|---|---|---|---|
| Specialty, `.dll` | ASCII `-i` `specialty\|speciality\|specializ\|specialis` | RimPacts is the only real carrier; the rest is `Specialist`/`Specialized` | — |
| Specialty, `.dll` | UTF-16, typed literally | RimPacts only | validated on `Rpt_TT_Specialty` |
| Settlement specialty by another name, `.dll`+`.xml` | `settlement(trait\|type\|kind\|focus\|resource\|product\|export\|industry\|role)` | 0 | form validated on `settlement(defeat\|trader)` |
| First contact | the eight met-faction terms, ASCII `-i`, `.dll`+`.xml` | 0 | — |
| `baseTraderKinds` | two independent counts | none with more than one `<li>` | — |
| `Settlement_TraderTracker` | `.dll` | 5 mods; Lemmy Progression, RimPacts and BTG read | — |

**Premise corrected.** § *What a holding pays* → *Constraints* said *"`Settlement` has no tier or specialty of its own [V]"*. It has no **stored** one. Vanilla assigns a per-settlement `TraderKind` (idle), and RimPacts and BTG ship per-settlement specialty and trader-kind machinery. The P4 tier caveat is amended by #167 (holding tier under R1 is stored, not read from the owner).

### Open questions

- **Requirement, unowned (#35 closed).** Must a specialty stay fixed when its faction climbs a tier at an era boundary? Derived routes move with it; stored ones do not. It bears on [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167).
- **Requirement, unowned.** Is vanilla's public **Show sellable items** an acceptable pre-visit leak?
- **Requirement, unowned.** Does knowledge lapse?
- **Balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).** Nearby distance, scouting range, reveal chance.
- **Build, next map.**
  - the storage shape (comp or tile-keyed);
  - whether the specialty rides the stock;
  - where the copy-at-conquest happens;
  - the plug into #166 P1's `GetTitheInfo` replacement.

---

## Showing what the player has learned about a settlement

### Purpose and scope

This section answers [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *Player information and agency*: *"the player must be able to learn what a settlement will give before committing to take it"*, *"nothing shows a settlement's specialty to a player who has not learned it"* (vanilla's *Show sellable items* included), *"once learned, known for good… always current"*, and *"planning a campaign against what has been learned is a feature"*. Established on [#178](https://github.com/cjd721/Rimworld-Archinity/issues/178).

**Owns:** where a learned, per-settlement fact — specialty, tier, how hard it is to take — can be drawn; what each surface needs from the store; and whether a fact one player learns is shown to both.

**Does not own:**
- whether the fact exists, and what reveals it: § *A settlement's specialty* ([#165](https://github.com/cjd721/Rimworld-Archinity/issues/165)). Its **one colony-wide record, keyed on the tile**, is the store every route here reads.
- what the garrison is: § *Taking a settlement must be hard* ([#164](https://github.com/cjd721/Rimworld-Archinity/issues/164)).
- a holding's tier after conquest: § *Paying to advance a holding* ([#167](https://github.com/cjd721/Rimworld-Archinity/issues/167)).
- which campaign window hosts what: [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61) resolved that every surface has a route and a main tab is always available; choosing one is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

### Verdict

- **Possible? Yes, for every per-settlement surface the ticket names, and four more. The Factions tab is the partial exception: it can carry only the faction's own specialty.**
  - Vanilla draws no settlement specialty anywhere [V].
  - Its one hover surface for a settlement is the **Alt-held inspector**. It lists label, faction and goodwill beside the cursor, and a postfix can add a line (SD-11).
  - Every surface is ours to fill, and each has a verified seam, most of them one small C# hook. Five have shipped donors in the corpus (SD-1, SD-2, SD-5, SD-6, SD-8).
  - The inspect pane, a world inspect tab, the Alt-hover line and the caravan's float menu cover *before you commit*. A world-map badge, a map mode, the world search and a campaign tab of our own cover *planning*.
- **Multiplayer? Yes, with no work beyond #165's.** Every route here is **render code that reads state at draw time**. A fact in synced, scribed game state (#165's tile-keyed record) is drawn identically on both clients, so one player's learning is shown to both by construction. Both players are one faction, and the requirement says *the colony* finds out. Two conditions:
  - #165's reveal write must come from a synced context.
  - **No surface may keep a client-local store or draw `Rand`.** Vanilla's own "learned" store, `PlayerKnowledgeDatabase`, is a file on each machine [V]. It is exactly the wrong model (**T-160**).

### Routes

Every route reads one store: #165's colony-wide record, keyed on the tile. **SD-0 is required whichever others are taken.**

| Route | What the player sees | Seam | Carrier / donor | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|---|
| **SD-0** Suppression | Nothing about an unlearned settlement's trade: *Show sellable items* gone or disabled until learned | `Settlement.GetGizmos` postfix | ours | C# | Medium | Yes |
| **SD-1** Inspect-pane line | *"Known for: arms · Medieval · fortified"* under the goodwill line whenever the settlement is selected | `WorldObjectComp.CompInspectStringExtra` on an XML-patched comp; or a `Settlement.GetInspectString` postfix | ours; donor BTG `SettlementGetInspectString` | C# + XML patch | Medium | Yes |
| **SD-2** Settlement inspect tab | A *Known* tab beside Terrain/Planet: full specialty, goods, tier, garrison band, when and how learned. **Absent for an unlearned settlement** | a `WITab` subclass, via the def's `inspectorTabs` or a `WorldObject.GetInspectTabs` postfix; `InspectTabBase.IsVisible` | ours; donor RimPacts `WITab_RptTrade` | C# (+ XML) | Medium | Yes |
| **SD-3** At the commit | The caravan's right-click menu reads *"Attack Ironhold (known for arms, fortified)"*, or a confirmation dialog restates what is known | `Settlement.GetFloatMenuOptions(Caravan)` postfix; a confirmation only through `CaravanArrivalActionUtility.GetFloatMenuOptions`' `confirmation` parameter | ours | C# | Medium | Yes for labels; a confirm dialog only through vanilla's `confirmation` parameter [I] |
| **SD-4** Info card | The learned fact in the settlement's ⓘ card | `WorldObjectComp.GetDescriptionPart` (same comp as SD-1) | ours | C# | Easy, once SD-1's comp exists | Yes |
| **SD-5** World-map badge and hover | A glyph on every learned settlement's icon; the fact in a tooltip on hover | `ExpandableWorldObjectsUtility.ExpandableWorldObjectsOnGUI` postfix + `TooltipHandler.TipRegion` | ours; donors FT&V `Patches_ExpandableWorldObjectsOnGUI`, RimPacts `Patch_WorldWarOverlayGUI` | C# | Medium | Yes |
| **SD-6** A *What we know* map mode | A toggleable world overlay: tiles tinted by learned specialty, labels and tooltips per tile | Map Mode Framework `MapModeDef` + a `MapMode` subclass (`GetMaterial`, `GetTileLabel`, `GetTooltip`) | Map Mode Framework; donor FT&V `MapMode_FactionTerritories` | C# + XML | Medium | Yes [I] |
| **SD-7** World search | Typing *"steel"* into the world search lists and highlights every settlement known for it | `Dialog_WorldSearch.ElementMatch` (private) postfix | ours | C# | Medium | Yes |
| **SD-8** A campaign tab of our own | A ledger of every learned settlement, sortable by specialty, tier or distance, click to jump | `MainButtonDef` (XML) + a `MainTabWindow` | ours; donor RimPacts `MainTabWindow_RimPacts` | C# + XML | Medium | Yes |
| **SD-9** Factions tab | The **faction's** public specialty only, in its row tooltip | `FactionDef.description`, which `FactionUIUtility.DrawFactionRow` shows; or a row postfix | vanilla | XML (or C#) | Easy | Yes. **Faction layer only** |
| **SD-10** A letter at the reveal | *"Our caravan learned Ironhold is known for arms"*, with a jump button, kept in the History archive | `LetterStack.ReceiveLetter` with `LookTargets`, sent from #165's reveal | vanilla | C# (inside the reveal) | Easy, once #165's reveal exists | Yes, if sent from the synced reveal |
| **SD-11** Alt-hover line | Holding Alt over a settlement already shows its name, faction and goodwill beside the cursor. A *"Known for: arms"* row joins them | `Verse.CellInspectorDrawer.DrawWorldInspector` (private) postfix | vanilla surface, ours to extend | C# | Medium | Yes |

Every route is **[I]** as a composition. Its seams are [V].

#### SD-0 — suppression

**Gets us** [V]:
- `Settlement.GetGizmos` yields *Show sellable items* whenever `TraderKind != null` and the faction is not `permanentEnemy`. It opens `Dialog_SellableItems`, which lists the settlement's whole trade profile from anywhere on the map.
- A postfix can drop it or disable it with a reason (*"We have not traded here"*) while the settlement is unlearned. The gizmo only opens a window, so removing it per synced state changes nothing either client can *do*.

**Must also cover** (§ *A settlement's specialty*, SV-6): RimPacts' `WITab_RptTrade` and BTG's inspect line, **if either ships**. Both show their values to everyone.

**A small leak stays** [V]: `Settlement.GetInspectString` prints *"Requires trade permission: <title>"* from `TraderKind.TitleRequiredToTrade`. That tells the player an Empire settlement's trader is a royal one before any visit.

#### SD-1 — inspect-pane line

**Gets us** [V]:
- `InspectPaneFiller.DoPaneContentsFor` draws `GetInspectString()` whenever a world object is selected.
- `WorldObject.GetInspectString` appends every comp's `CompInspectStringExtra`. A comp patched onto the `Settlement` def backfills into existing saves (`engine/factions-and-worldgen.md` § *A `WorldObjectComp` added by XML patch backfills into an existing save*).
- `Settlement.GetInspectString` already prints the relation and goodwill. Ours sits beneath.

**Levers:** the one place a player always looks when they click a settlement. It shows three facts in a line each, or *"Nothing known"*.

**Cannot:** hold more than a few lines, nor anything laid out.

#### SD-2 — settlement inspect tab

**Gets us** [V]:
- `WorldInspectPane.CurTabs` returns `SingleSelectedObject.GetInspectTabs()`, which is `def.inspectorTabsResolved`.
- `Settlement` inherits `WITab_Terrain`, `WITab_Planet` and `WITab_Orbit` from `StaticWorldObjectBase` (`Data/Core/Defs/WorldObjectDefs/WorldObjects.xml`).
- **`InspectTabBase.IsVisible` is virtual.** The tab can hide itself until the settlement is learned, so *"nothing shows before it is learned"* holds on the tab strip too.
- **Donor:** RimPacts appends `WITab_RptTrade` to every non-player `Settlement` through a `WorldObject.GetInspectTabs` postfix, and gates `IsVisible` on the faction (`3762723122/Assemblies/RimPacts.dll`).

**Levers:** room for the full picture — the goods it is known for, tier, garrison band, when and how it was learned. It can also carry #166's *what it would pay*.

**Cannot:** be seen without selecting the settlement and opening the tab.

**Consequence:** adding through the def's `<inspectorTabs>` relies on XML list inheritance appending to the parent's three [I]. The `GetInspectTabs` postfix is RimPacts' form and needs no def edit.

#### SD-3 — at the commit

**Gets us** [V]:
- `Settlement.GetFloatMenuOptions(Caravan)` builds the right-click options for a caravan: *Visit*, *Trade*, *Offer gifts*, *Attack*. Attack's label is `"AttackSettlement".Translate(settlement.Label)`.
- For an allied or neutral faction, vanilla already wraps Attack in `Dialog_MessageBox.CreateConfirmation("ConfirmAttackFriendlyFaction")`. It passes that dialog as the `confirmation` argument of `CaravanArrivalActionUtility.GetFloatMenuOptions`. That is the shape of a commit dialog that restates what is known.
- **Multiplayer wraps options a default-priority postfix appends** (`engine/determinism.md` § *Multiplayer's float-menu sync wraps options a postfix appends*).
- **Only vanilla's confirmation closure is special-cased** [V, `2606448745/1.6/AssembliesCustom/Multiplayer.dll`]:
  - `SyncActions.WorldObjectCaravanMenuWrapper` recognises only `CaravanArrivalActionUtility`'s `<>c__DisplayClass0_1<T>`. It swaps that closure's inner `action` for the sync, so the dialog opens locally and the confirmed act is synced.
  - Any other dialog wrapped around an option falls to the default wrap. That syncs the dialog's *opening* and leaves its confirm button unsynced.
  - **So a commit dialog is MP-safe only when built through the `confirmation` parameter** [I on our use; V on the wrapper] (**T-80**).

**Levers:** the fact is in front of the player at the exact moment they commit, which is the requirement's own wording.

**Cannot:**
- appear except to a player who has selected a caravan and right-clicked;
- reach the transport-pod and shuttle menus. `GetTransportersFloatMenuOptions` and `GetShuttleFloatMenuOptions` are separate seams. While pods are aimed, `WorldTargeter.BeginTargeting`'s `extraLabelGetter` puts a label beside the cursor for the hovered target [V]. The other vanilla cursor text is SD-11's Alt-held inspector.

**Consequence:** option labels must come only from synced state, so both clients build the same list (**T-82**'s index rule, applied to float menus) [I].

#### SD-4 — info card

**Gets us** [V]: `Dialog_InfoCard(WorldObject)` → `StatsReportUtility.StatsToDraw(WorldObject)` shows `GetDescription()`, which appends each comp's `GetDescriptionPart`. It is free once SD-1's comp exists. `SpecialDisplayStats` is a second, stat-row seam, but only by override or postfix, since comps have no hook for it.

**Cannot:** be found by a player who does not click the ⓘ.

#### SD-5 — world-map badge and hover tooltip

**Gets us** [V]:
- `WorldInterface.WorldInterfaceOnGUI` calls `ExpandableWorldObjectsUtility.ExpandableWorldObjectsOnGUI` each frame. That draws each expanded icon at `ExpandedIconScreenRect(o)`, on `Repaint` only.
- **Vanilla draws no text or tooltip on the icon itself.** Its cursor text is the Alt-held inspector (SD-11) and the targeter's label while pods are aimed (SD-3). The only highlight is `Dialog_WorldSearch`'s yellow.
- `TooltipHandler.TipRegion` acts only on `Repaint`, which is the same gate, so a tooltip over the icon rect composes.
- **Donors:**
  - FT&V draws a badge over every settlement under invasion from exactly this postfix (`FactionTerritories.Invasions.Patches_ExpandableWorldObjectsOnGUI`, `3626725895/Assemblies/FactionTerritories.dll`).
  - RimPacts draws war dots per settlement from the same seam (`Patch_WorldWarOverlayGUI`).

**Levers:** the only route that shows *where* the colony has learned things across the whole map at a glance, without clicking or holding a key. SD-11 shows one settlement at a time, under the cursor, while Alt is held. That makes SD-5 the planning surface on the map itself.

**Cannot:** badge a settlement drawn as a mesh when zoomed in. `ExpandableWorldObjectsOnGUI` skips objects whose `TransitionPct` is 0 [V]; a close-zoom tooltip would need `GenWorldUI.WorldObjectsUnderMouse` instead [I].

**Consequence:** Map Mode Framework prefixes the same method and returns `false` when its mode hides world objects [V], so our badge disappears in those modes.

#### SD-6 — a *What we know* map mode

**Gets us** [V] (`3296654393/1.6/Assemblies/MapModeFramework.dll`):
- `MapModeDef` (XML) names a `mapModeClass`. `MapMode` exposes `GetMaterial(int tile)`, `GetTileLabel(int tile)` and `GetTooltip(int tile)`, with `doTooltip` and `displayLabels` switches on the def.
- The mode is picked from MMF's own button strip on the world map.
- **Shipped precedent:** FT&V's territory overlay is an MMF `MapMode_Region` subclass with its own label layer (`MapMode_FactionTerritories`, `WorldLayer_MapMode_OnGUI_FactionTerritoriesLabels`).

**Levers:** a whole-world view of what the colony knows, tinted by specialty, which the player can toggle off.

**Cannot:** stand without MMF, which becomes a dependency. It is only worth taking if FT&V's territory mode or another overlay brings MMF in anyway.

**MP** [I]: MMF keeps the chosen mode in `MapModeComponent`, a `GameComponent`. Each player's choice is a per-client UI selection, and nothing in the tick reads it. MP Compat carries no MMF patch: ASCII and UTF-16 sweeps of `1629973374/1.6` for `mapmode` both return 0, validated on `PatchKCSG`. Confirm on a two-client run only if SD-6 is selected.

#### SD-7 — world search

**Gets us** [V]:
- `Dialog_WorldSearch.ElementMatch` matches a typed query against `worldObject.Label`, landmark names and tile mutators.
- A matched object is listed, and `ExpandableWorldObjectsUtility.IsHighlighted` paints it yellow on the map.
- A postfix that also matches the settlement's **learned** specialty makes *"where can we get steel?"* a search.

**Levers:** planning with no new window. The query cannot find an unlearned settlement by its specialty, because the postfix reads the knowledge record.

**Cannot:** do more than list and highlight.

**Consequence:** no mod in the corpus patches the dialog (sweep under *Status*), so nothing contests it.

#### SD-8 — a campaign tab of our own

**Gets us** [V]:
- A `MainButtonDef` is pure XML. Set `minimized: true`, or every button shrinks ([`CURRENCIES.md`](CURRENCIES.md), the `MainButtonDef` note).
- The window is a `MainTabWindow` of ours.
- **Donor:** RimPacts' `MainTabWindow_RimPacts` lists factions with a per-row detail and jumps the camera to a settlement with `CameraJumper.TryJump`.

**Levers:**
- the campaign ledger — every learned settlement, sorted by specialty, tier, difficulty or distance;
- the requirement's *"deciding which to take, in what order"* made a list;
- #61's own-tab option would host it.

**Cannot:** show anything in place on the map. It is a list the player opens.

**Consequence:** it is the heaviest route here, and it overlaps with SD-5 and SD-7. Take it if #61's own tab is built, and not otherwise.

#### SD-9 — factions tab (faction layer only)

**Gets us** [V]: `FactionUIUtility.DrawFactionRow` tooltips `faction.def.LabelCap` plus `faction.def.Description`. The faction's specialty written into its def's description is public from worldgen, with zero code.

**Cannot:**
- show a settlement's own specialty. The tab is per faction.
- wait for first contact. The tab lists every visible faction from the start, so *"learnable at first contact"* needs SF-3's gate and a row postfix.

**Consequence:** the row is contested by VFE Classical, RimPacts and Faction Territories (#61 A1).

#### SD-10 — a letter at the reveal

**Gets us:**
- a named moment when the colony learns something, sent from #165's reveal with a `LookTargets` jump [V seam];
- the History tab's archive keeps it.

**Cannot be the store.** A letter is a snapshot, and the requirement forbids a stale one (*"always current; no stale snapshot is kept"*). The archive also culls unpinned letters by stack membership (**T-21**).

**MP:** send it only from the synced reveal. A letter sent from UI code reaches one client.

#### SD-11 — the Alt-hover line

**Gets us** [V] (`Assembly-CSharp.dll`, `Verse.CellInspectorDrawer`):
- While the `ShowCellInspector` key is held (`KeyBindingDefOf`, default Left/Right Alt, `Data/Core/Defs/Misc/KeyBindings/KeyBindings.xml`), `OnGUI` draws an immediate window beside the cursor.
- On the world map, `FillWindow` calls `DrawWorldInspector`. That iterates `GenWorldUI.WorldObjectsUnderMouse`, gives each object a header of its `LabelCap`, and for a `Settlement` adds the faction and the relation with goodwill. It then adds the tile's biome, features, hilliness, road, river, movement difficulty and pollution.
- The window's height comes from `numLines`, which every private `DrawRow`/`DrawHeader` increments. A postfix that adds rows through them sizes the window correctly [I on the postfix; V on the counter].

**Levers:** a native hover line for a settlement — *"Known for: arms · Medieval"* — with no new window, no badge art and no click. It works at any zoom, because it uses `WorldObjectsUnderMouse`, which is not gated on the expanded icon.

**Cannot:**
- appear without the player holding Alt. It is a vanilla feature many players never discover.
- sit in the right place without a transpiler, or reflection onto private `DrawRow`. `DrawWorldInspector` is private and writes all its rows in one loop, so a postfix appends after the tile rows rather than under the settlement's own header.

**Consequence:** Vehicle Framework references `CellInspectorDrawer` (ASCII and UTF-16 hits, `3014915404/1.6/Assemblies/Vehicles.dll`) [I, name only], so check the patch order if both ship.

#### Specialty, tier, difficulty — what each surface can truthfully say

- **Specialty:** #165's record. It is **fixed and known for good** ([#174](https://github.com/cjd721/Rimworld-Archinity/issues/174)).
- **Tier:** before conquest, an NPC settlement's tier is its faction's `Faction.def.techLevel`, read live [V, #167]. After conquest it is the stored tier (TR-1).
- **Difficulty:** vanilla has nothing to show, because every vanilla settlement's garrison is 1150–1600 points whatever its faction or tier (#164, SM-1) [V].
  - A difficulty band is only as real as the route that makes difficulty vary: SM-2/SM-3's layout list per faction, or SM-4's curve.
  - It is **a prediction drawn from that route's inputs**. The garrison itself does not exist until the map is generated on arrival [V, #164].
  - **The band must be a pure function of synced state**, never a map generation and never a `Rand` draw at render.

#### Recommendation (not a selection)

- **SD-0 regardless.** Without it, every other route is undercut by vanilla's public sellable-items window.
- **Before committing:** SD-1 for the one-line fact, SD-2 for the full picture, and SD-3 at the moment of commitment. SD-4 comes free with SD-1's comp. SD-11 is a cheap extra that puts the fact where vanilla already puts goodwill on hover.
- **For planning:** SD-5 (badge + hover) and SD-7 (search) are the cheapest surfaces on the map itself. SD-8 only if #61's own tab is built. SD-6 only if MMF ships for another reason.
- **SD-10 as the reveal's voice**, never as its memory. **SD-9** as the zero-code carrier of the faction's public specialty.

### Constraints

- **One store, synced, keyed on the tile.** Every surface reads #165's record. A surface keeping its own copy — a static cache populated at draw, a `ModSettings` value (**T-18**) or `PlayerKnowledgeDatabase` — diverges between clients, and after a rejoin [V for `PlayerKnowledgeDatabase`: `GenFilePaths.ConceptKnowledgeFilePath`].
- **Render code draws no `Rand`.** An inspect string, tab, tooltip or badge runs on one machine at a tick the other is not rendering (**T-39**; [`CHARTING.md`](CHARTING.md) § *The Waystone's out-of-reach signal*). So a lazily-rolled specialty (SS-3 without a seed) cannot be rolled from a display route. It is rolled at worldgen or in a synced context.
- **Filter at draw time** (**T-21**). A surface that hides unlearned settlements hides them when it draws, never by editing a list the tick reads.
- **A display that acts is a command.** SD-8's jump-to is camera-only and safe. Any button on SD-2 or SD-8 that *does* something is a synced command (**T-80**; float menu per `engine/determinism.md`).
- **Identity** (**T-140**): a record keyed on `WorldObject.ID` orphans when a settlement is replaced; the tile does not.

### Available mechanisms

| Mechanism | Provides | Route | Evidence |
|---|---|---|---|
| `Settlement.GetGizmos` → `Dialog_SellableItems` | the public trade-profile leak | SD-0 | [V] `Assembly-CSharp.dll` |
| `Settlement.GetInspectString`, `WorldObject.GetInspectString`, `WorldObjectComp.CompInspectStringExtra`, `InspectPaneFiller.DoPaneContentsFor` | inspect-pane text, per comp | SD-1 | [V] |
| `WorldInspectPane.CurTabs`, `WorldObject.GetInspectTabs`, `WorldObjectDef.inspectorTabs`/`inspectorTabsResolved`, `WITab`, `InspectTabBase.IsVisible` | a per-object tab that can hide itself | SD-2 | [V] |
| `Settlement.GetFloatMenuOptions(Caravan)`, `CaravanArrivalAction_AttackSettlement.GetFloatMenuOptions`, `ConfirmAttackFriendlyFaction` | the commit menu and vanilla's confirm shape | SD-3 | [V] |
| `Dialog_InfoCard(WorldObject)`, `StatsReportUtility.StatsToDraw(WorldObject)`, `WorldObject.GetDescription`, `WorldObjectComp.GetDescriptionPart`, `WorldObject.SpecialDisplayStats` | the ⓘ card | SD-4 | [V] |
| `WorldInterface.WorldInterfaceOnGUI`, `ExpandableWorldObjectsUtility.ExpandableWorldObjectsOnGUI`/`ExpandedIconScreenRect`/`IsHighlighted`, `TooltipHandler.TipRegion` | icon-space GUI on the world map; no vanilla hover | SD-5, SD-7 | [V] |
| `Dialog_WorldSearch.ElementMatch`/`IsListed` | world search and map highlight | SD-7 | [V] |
| `Verse.CellInspectorDrawer.DrawWorldInspector`/`DrawRow`/`numLines`, `KeyBindingDefOf.ShowCellInspector` | Alt-held hover inspector: label, faction, goodwill, tile | SD-11 | [V] |
| MP `SyncActions.WorldObjectCaravanMenuWrapper` | special-cases only `CaravanArrivalActionUtility`'s confirmation closure | SD-3 | [V] `2606448745/1.6/AssembliesCustom/Multiplayer.dll` |
| `FactionUIUtility.DrawFactionRow` | faction row, def description in tooltip | SD-9 | [V] |
| `PlayerKnowledgeDatabase` | vanilla's "learned" store — a per-machine file | Constraints | [V] |
| BTG `SettlementGetInspectString` | per-settlement line in the inspect pane | SD-1 donor | [V] § *A settlement's specialty* |
| RimPacts `WITab_RptTrade` + `Patch_WorldObject_GetInspectTabs_RptTrade`; `Patch_WorldWarOverlayGUI`; `MainTabWindow_RimPacts` | settlement tab gated by `IsVisible`; per-settlement map glyphs; own campaign tab | SD-2, SD-5, SD-8 donors | [V] `3762723122/Assemblies/RimPacts.dll` |
| FT&V `Patches_ExpandableWorldObjectsOnGUI`; `MapMode_FactionTerritories` | per-settlement badge; an MMF map mode with labels | SD-5, SD-6 donors | [V] `3626725895/Assemblies/FactionTerritories.dll` |
| Map Mode Framework `MapModeDef`, `MapMode`, `MapModeComponent`, `ExpandableWorldObjectsOnGUI` prefix | switchable world overlays with per-tile colour, label, tooltip | SD-6 | [V] `3296654393/1.6/Assemblies/MapModeFramework.dll` |

**What does not exist:**
- a vanilla tooltip or text label on a world-object icon. The Alt-held inspector (SD-11) is vanilla's only settlement hover, and it shows owner and goodwill, not specialty;
- any mod that shows a *learned*, per-settlement fact;
- any patch on `Dialog_WorldSearch`.

**Off the corpus:** RimPacts reflects into *Evolving Enemy Strongholds* (`EvolvingEnemyStrongholds.StrongholdData`: `intelLevel`, `militaryPower`, `tier`, `roleDefName`; a `ScoutUtility`) through `RptEesBridge`. That is a per-settlement intel record of exactly this shape, but the mod is **not on disk** in either root [I, name only]. It is a sourcing lead for [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14), not a carrier.

### Status

**Evidence class: READ**, established on [#178](https://github.com/cjd721/Rimworld-Archinity/issues/178). Seams [V] by decompiling `Assembly-CSharp.dll` 1.6 and the named mod assemblies; routes [I].

**Sweeps.** Both roots, `.dll`, `-g '!**/obj/**' -g '!**/Referenced/**'`:

| Sweep | Result | Validation |
|---|---|---|
| ASCII `WITab_` | RimPacts, WTL, VFEI2, VEF, Vehicles, VCR, MP; only RimPacts adds one to a settlement | — |
| ASCII `ExpandableWorldObjectsOnGUI` | MMF, FT&V, RimPacts, MP | — |
| ASCII `WorldInspectPane` | RimPacts, MP | — |
| ASCII `-i` `Settlement_?GetInspectString`, `Settlement_?GetFloatMenuOptions` | BTG only | — |
| ASCII `-i` `Settlement_?GetInspectTabs\|WorldObject_?GetInspectTabs` | RimPacts only | — |
| ASCII `-i` `SettlementInfo\|SettlementDetail\|SettlementIntel\|SettlementKnowledge\|KnownSettlement\|ScoutedSettlement\|scouted\|scouting` | RimPacts (the EES bridge), Rim War (`ScoutingParty`, barred) | — |
| ASCII `Dialog_WorldSearch`, `ElementMatch`; UTF-16 (typed literally) `ElementMatch`, `WorldSearch` | **0** | ASCII form on `ExpandableWorldObjectsOnGUI`; UTF-16 form on `Rpt_TT_Specialty` |
| `-i` `mapmode` in MP Compat `1629973374/1.6`, ASCII and UTF-16 | **0** | `PatchKCSG` |
| `CellInspectorDrawer\|DrawWorldInspector`, ASCII; UTF-16 typed literally | Vehicle Framework (both); FloatSubMenu (ASCII only) | — |
| `EvolvingEnemyStrongholds`, ASCII and UTF-16; `stronghold` in every `About.xml` | RimPacts' bridge only | — |

### Open questions

- **Requirement, for Conrad via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2)** (`requirements/TERRITORY.md`). Only *"what it is known for"* is required to be earned. Are a settlement's **tier** and **how hard it is to take** public, as its owner is, or also earned by going? Nothing reads either way today.
- **Requirement, for Conrad via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2).** Is the *"Requires trade permission"* inspect line an acceptable leak (SD-0)?
- **Selection, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)** with [#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)'s own-tab call: which of SD-1 to SD-11 ship.
- **Build, depends on [#164](https://github.com/cjd721/Rimworld-Archinity/issues/164)'s selection:** the difficulty band's inputs. Vanilla gives nothing to show.
- **Unverified [I]:**
  - SD-6 under two clients;
  - the `<inspectorTabs>` inheritance merge (SD-2);
  - close-zoom hover (SD-5);
  - an SD-3 commit dialog routed through `confirmation`;
  - SD-11's row placement.

---

## Paying to advance a holding to a later era

### Purpose and scope

This section answers [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167) against [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *A holding is a settlement taken by force*, which carries two clauses: *"Paying to advance a holding is a route worth having"* and *"The era advance does not touch a holding"*. It also answers the second clause's twin in [`requirements/ERA.md`](../requirements/ERA.md): *"The advance never modifies anything the player built or owns."*

It owns **where a holding's era lives, whether it can be rewritten, how what it pays follows it, what gates and prices the rewrite, and whether the era advance can reach it.** It does not own:

- what a holding *is*: § 3 R1/R2, [#120](https://github.com/cjd721/Rimworld-Archinity/issues/120);
- the payment forms: § *What a holding pays* P1–P5, [#166](https://github.com/cjd721/Rimworld-Archinity/issues/166);
- the characteristic payload: [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165);
- the era clock: [`ERA.md`](ERA.md), [#109](https://github.com/cjd721/Rimworld-Archinity/issues/109) / [#113](https://github.com/cjd721/Rimworld-Archinity/issues/113);
- which factions climb at a boundary: [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34).

### Verdict

- **Possible? Yes. No shipped carrier does it, and every route is a few writes on state R1 or R2 already creates.** The tier can be rewritten, the payment can follow it, the price can be era-scaled from #166's table, and the gate can be the colony's era, research, nothing, or (fiddly) the parent faction's climb. **The era advance cannot touch a holding only under R1 with a stored tier.** Under R2, or with a derived tier, it can, silently.
- **Multiplayer? Yes, with the usual work.** The advance is one synced player act writing plain fields, with no `Rand`. It must be a float-menu option on the world object (§0 P5), never a gizmo or dialog (**T-80**). TR-4's `SetFaction` is not synced by MP and has to sit inside our command.

### Routes

The T routes say where the era lives. They sit beneath R1/R2 and combine with any of P1–P5.

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **TR-1** Stored tier on the holding | A scribed `TechLevel` set at conquest from the **former** faction. The advance is one field write, and nothing else moves it | ours; R1 object field or R2 `WorldObjectComp` (backfills, `engine/factions-and-worldgen.md`) | C# + XML cost table | **Medium** (Easy on top of R1/R2) | **Yes** |
| **TR-2** Derived from the former faction | Always the parent's current tier, the shape FT&V ships. **Cannot advance one holding, and climbs for free with its parent.** **Not recommended**: it breaks *"does not improve on its own"* | donor FT&V | C# | Easy | Yes; the era advance reaches it |
| **TR-3** Derived from the holding's def | An XML tier table, one def per era. The cheap form is one `TitheTypeDef` per specialty × tier, and the advance rewrites `TitheInfo.Type` | vanilla `WorldObject.def` / VFE Empire `TitheTypeDef` | XML + C# | **Medium** | Yes (`TitheTypeDef` form); With work (world-object replacement form: a replacement object is created in the synced command) |
| **TR-4** Advance by transfer (R2 only) | `SetFaction` to an existing later-era faction. **The map, defenders and trader become the new era's** | vanilla `WorldObject.SetFaction` | C# | **Medium**; **Hard** with per-era holder factions authored into the roster | With work |

**What an advance rewrites, per payment route.** All [V] unless marked.

| | Tier lives in | The advance rewrites |
|---|---|---|
| P1 tithe engine | `TitheInfo.Type` / `.Speed`. It has no tier field | `TitheInfo.Type` (+ `.Speed`), plain scribed fields |
| P2 Outposts delivery | nowhere. `PackOrPods` keys on the colony's research | nothing |
| P3 royal permit | which `RoyalTitlePermitDef` is offered | which permit the holding offers [I] |
| P4 standing debt | #166's `TechLevel`-keyed cost `DefModExtension` | nothing. **P4 *is* the advancement price**: a second debt at the target tier's row |
| P5 menu | R2: `Settlement_TraderTracker.TraderKind` = `Faction.def.baseTraderKinds[abs(HashOffset) % n]`, live, with each trader kind's own `maxTechLevelGenerate`. R1: no trader | R2: a `TraderKind` getter postfix for marked holdings, or TR-4. R1: FT&V's catalogue builder takes the tier as a parameter (`TraderSellablesUtility.GetSellableBuildingThingDefs(traderKind, TechLevel)`), so feed it TR-1 |

**Every route is [I] as a route.** The mechanisms are [V].

#### TR-1 — stored tier

- **Gets us:** a holding frozen at the era it was taken, until the player pays. One number that every payment route reads. Under R1 nothing else in the game can reach it.
- **Cannot:** under R2, change the place itself. Map, defenders and trader derive from `Faction.def` [V, `engine/factions-and-worldgen.md` § *What survives a swap*], so an advanced R2 holding pays in the new era and still generates its old-era map.
- **Consequences:** the capture-time read must be the **former** faction's tier, never `holding.Faction`'s (see *Constraints*).

#### TR-2 — derived from the former faction (not recommended)

- **Gets us** [V]: `FactionTerritories_VassalOutpost` stores only the former faction's loadID, the settlement name and the `WorldObjectDef` defName. `VassalagePointsComponent` scales daily points by `GetTechLevelMultiplierPercent(faction.def.techLevel)`, resolved live, with the multiplier held in `ModSettings` (T-18). `Dialog_Vassalage.BuildSettlementSimCatalog` filters by `fac.def.techLevel`. This is **the corpus's only shipped "tier scales yield"**.
- **Cannot:** advance one holding. A `Faction.def` climb of the parent retiers every holding it lost, for free.
- **Consequence:** useful only as gate TG-2's *read*.

#### TR-3 — tier in the def

- **Gets us:** the most authorable form, a def per era.
- **Cannot** [V]: an in-place `WorldObject.def` write is not clean. It is public and scribed, but `InitializeComps` runs only in `PostMake` and at `LoadingVars`, so the old comps persist until reload and the reload then drops state the new def lacks. Replacement gives a **new ID** and orphans everything keyed on the old object, including `TitheInfo`'s `Settlement` key.
- **Consequence:** for P1, prefer the tier living in `TitheTypeDef` and rewrite `TitheInfo.Type`. No world object changes.

#### TR-4 — advance by transfer (R2 only)

- **Gets us:** the only route where the visited place is visibly of the new era. Its map is generated afresh on the next visit, as every NPC settlement's is (#164), from the new faction's def; **T-33** applies only if that faction uses KCSG's generated branch without MP Compat. The stock is rebuilt through `TryDestroyStock`.
- **Cannot:** stay part of its former faction. No faction can be created mid-game (**T-07**), so a target must already exist, and a clean version means per-era holder factions in the worldgen roster.
- **Consequences:** `SetFaction` is a bare field write with no notification and no MP sync. The leaks are listed in the engine doc (**T-12** and others).

#### Price and gates

**The price is era-scaled with no new mechanism.** It reads #166 P4's `TechLevel`-keyed table at the target tier, and is paid by a caravan on the tile (`TradeRequestComp.Fulfill`, synced) or by a float-menu option taking goods through `CaravanInventoryUtility.TakeThings` [V, #166].

| Gate | Reads | Weight | Limit |
|---|---|---|---|
| **TG-1** colony era | `GameComponent_Era.CurrentEra` (unbuilt) or `WorldTechLevel.Current` [V] | Easy | none. This is the requirement's own wording |
| **TG-2** parent climbed | former faction → `def.techLevel` [V shape] | Easy to read | **opens only if the grid climbs by `Faction.def` swap.** Never if it climbs by transfer to a successor, or if the parent was defeated [I]. #8 allowed dropping it |
| **TG-3** research | `ResearchProjectDef.IsFinished` | Easy | none |
| **TG-4** price only, plus #8's cooldown | — | Easy | none |

#### Recommendation (not a selection)

**Under R1: TR-1 + P4 as the price + TG-1**, with P1's payload rewritten through `TitheInfo.Type`. It is the only combination where the era advance provably cannot reach the holding, and it reuses #166's cost table unchanged. **Under R2: TR-1 for the payment, plus TR-4 only if the story wants the visited place to change era.** Drop TG-2.

### Constraints

- **The era advance can reach a holding in three ways, and each is silent.**
  1. **`AdvanceEra()` write 3 sets `Faction.OfPlayer.def.techLevel`** ([`ERA.md`](ERA.md) § 3). An R1 holding is owned by the player (#120), so any tier read from `holding.Faction.def.techLevel` retiers every R1 holding to the colony's era at every boundary (**T-145**).
  2. **The faction-grid pass (#34) reaches every R2 holding.** An R2 holding is an NPC `Settlement`, inside any pass over `Find.WorldObjects.Settlements`. Excluding holdings is a rule the pass must implement. **An overlay outcome can also replace an R2 holding in absentia**: Build B copying FT&V's `ApplyWinnerToSettlement` destroys and recreates when no map is open (`FactionTerritories.Invasions.Utility.ApplyWinnerToSettlement` [V]), which gives a new ID and orphans a TR-1 comp (**T-140**).
  3. **A parent's `Faction.def` climb retiers a TR-2 holding** through derivation [V, FT&V].

  **R1 + TR-1 is immune to all three**: FT&V's object is a bare `WorldObject`, not a `Settlement` [V].
- **Shipped proof** [V]: Lemmy Progression's `FactionUpgrader.UpgradeToTechLevel` swaps `faction.def` on era advance, choosing through unseeded `System.Random`, then `UpdateSettlements` restocks every `Settlement` of that faction. BLOCK per [`ERA.md`](ERA.md) § 6c.
- **Never retier by writing `FactionDef.techLevel`.** It reverts on load and mutates every faction sharing the def (**T-11**).
- **World Tech Level touches no world object when the level changes** [V]. `Patch_StockGenerator` only *lowers* a trader's ceiling to `WorldTechLevel.Current` (`TechLevelUtility.CurrentFilterLevel`, except factions in a settings list, T-18). In-era stock does not climb, because vanilla trader kinds cap themselves. **An above-era R2 holding's uncapped generators do rise toward their own tier at each advance** [I on the consequence].
- **VFE Empire's `WorldComponent_Vassals.DoDay`** checks neither the settlement's faction nor its existence [V]. `titheInfo` is a `Dictionary<Settlement, TitheInfo>` keyed by reference. Transfer by `SetFaction`: a P1 holding keeps paying, to the same lord. Destroyed or recreated: the old entry keeps paying until the next load, then is dropped with a logged null-key error [I, `Scribe_References`]; the new object is not a vassal.
- **The commit is a float-menu option on the world object** (§0 P5; postfix-added options are synced too, per #154). Never a gizmo or dialog (**T-80**).

### Available mechanisms

| Mechanism | Provides | Route | Evidence |
|---|---|---|---|
| FT&V `FactionTerritories_VassalOutpost` | player-held holding storing the former faction by loadID; no tier field | TR-1 donor, TR-2 | [V] `294100/3626725895/Assemblies/FactionTerritories.dll` |
| FT&V `VassalagePointsComponent`, `Dialog_Vassalage.BuildSettlementSimCatalog`, `TraderSellablesUtility.GetSellableBuildingThingDefs(TraderKindDef, TechLevel)` | yield and catalogue scaled by tier, derived live; the catalogue builder is already tier-parameterised | TR-2; P5 donor | [V] same |
| VFE Empire `TitheInfo`, `WorldComponent_Vassals.DoDay` | payload as plain scribed `Type` / `Speed`; no faction or existence check | P1 × TR-1/TR-3 | [V] `294100/2938820380/1.6/Assemblies/VFEEmpire.dll` |
| `WorldObject.def`, `InitializeComps`, `ExposeData` | public scribed def; comps rebuilt only at `PostMake` / `LoadingVars` | TR-3 | [V] `Assembly-CSharp.dll` |
| `Settlement_TraderTracker.TraderKind`, vanilla `TraderKindDefs` | trader derived live from `Faction.def`; per-generator `maxTechLevelGenerate` | P5, TR-4 | [V] `Assembly-CSharp.dll`, `Data/Core/Defs/TraderKindDefs` |
| `WorldObject.SetFaction`, `Faction.def` swap | transfer and climb, with their leaks | TR-4, Constraints | [V] `engine/factions-and-worldgen.md` |
| WTL `Patch_StockGenerator`, `TechLevelUtility.CurrentFilterLevel` | stock ceiling clamp to world era; no world-object writes | Constraints | [V] `294100/3414187030/1.6/Lunar/Components/WorldTechLevel.dll` |
| Lemmy `FactionUpgrader.UpgradeToTechLevel` / `UpdateSettlements` | shipped era-advance def swap + settlement restock | Constraints | [V] `294100/3548896697/1.6/Assemblies/LemProgress.dll` |
| #166 P4 `TechLevel`-keyed cost extension; `TradeRequestComp` | era-scaled price, standing debt | price | [V] § *What a holding pays* |

**What does not exist:** a paid upgrade of any world object, holding, outpost or vassal anywhere in the corpus. The wide pass is recorded under *Status*.

### Status

**Evidence class: READ**, established on [#167](https://github.com/cjd721/Rimworld-Archinity/issues/167). Mechanisms are [V] and routes are [I].

**Sweeps.** All of them covered both roots and `Data`, with `-g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'`:

- **ASCII, `-i`**, over 12 upgrade and tier names. The only real hit is Lemmy Progression. `Retier` returned only false positives.
- **UTF-16, `-i`**, escapes typed literally, over four names. **Zero.** The validator was a same-heap Scribe-key literal.
- **`upgrade`** over the VEF `Outposts.dll`, VOE, FT&V and VFE Empire carriers. **Zero.**

**Premises corrected:**

1. #166 P4's *"the tier is its faction's"* is right for an NPC settlement and **wrong for an R1 holding**, whose faction is the player's.
2. *"The era advance does not touch a holding"* is a requirement, not a property. It holds by construction only under R1 + TR-1.

### Open questions

- **Requirement gaps**, unowned; [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35) is closed:
  - May an advance exceed the former faction's tier, or is it capped at the colony's era?
  - One rung per payment, or straight to the current era?
- **Obligation on [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34), if R2 is selected:** the boundary pass must exclude holdings. The requirement needs a sentence in [`requirements/ERA.md`](../requirements/ERA.md).
- **Build, for the next map:** where TR-1's field sits; whether P1's per-tier catalogue is defs or a tier-reading worker; which gates. Owned by [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) once a route is selected.

---

## How a holding ends — released, retaken, destroyed

### Purpose and scope

**What this section answers:** whether a holding can end, how, and whether each ending can reach the
player as a moment they act on. It covers the four endings in
[`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *A holding is a settlement taken by
force*: release, retaken by the parent, destroyed, and throwing the colony off. It answers each under
both of §3's holding representations:
- **R1:** a player-held world object;
- **R2:** a marked NPC settlement.

It also answers what happens to what the holding owed. It resolves
[#172](https://github.com/cjd721/Rimworld-Archinity/issues/172).

**The hard constraint** is [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8)'s: no
vassal-gets-raided simulation. **Loss must be something the player acts on**, never a background roll
they read about afterwards.

**Whether a holding *should* be losable is Conrad's call and is not made here.**

**What this section does not own:**
- **Ending a sworn faction:** [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168).
  RimPacts' tributary revolt, below, is that ticket's donor.
- **The outpost-attacked event:** [#171](https://github.com/cjd721/Rimworld-Archinity/issues/171).
  It is H-T1's twin.
- **Caravans in flight when the owner changes:**
  [#152](https://github.com/cjd721/Rimworld-Archinity/issues/152).
- **What a holding pays:** *What a holding pays* above (#166).
- **The ally-aid battle:** §1 (#92).

**Shape names** are shared with #154, #164 and #171:
- **E-letter:** a letter.
- **E-quest:** the #91 declinable demand, [`POLITICS.md`](POLITICS.md) § *The faction demand*.
- **E-overlay:** §1's world object on the tile; attend, or it resolves in absentia.
- **E-site:** a vanilla `Site` the player travels to, delivered by a quest with a deadline.
- **E-march:** a hostile world object moving toward the target (#154; not used here).
- **E-quest→E-overlay, E-quest→E-site:** the #91 shell, whose accept or refusal spawns the arena.
- **/roll, /forfeit:** the in-absentia branch. /roll is the §0 P4 seeded roll; /forfeit is a
  deterministic loss with no roll.
- **M-proxy, M-site, M-own:** where the fight's map comes from.

### Verdict

- **Possible? Yes.** Each of the four endings can reach the player as a moment they act on, under
  both R1 and R2. Nothing on disk does it as shipped.
  - VFE Empire ships a per-lord *Release all* button.
  - RimPacts ships one live revolt roll, its tributary revolt, which reports afterwards. Its settlement hold reversion is unreachable code.
  - Every compliant route is our code on verified seams. The donors are FT&V's vassal invasion,
    Worksites Expanded's counter-attack sequence, and the POLITICS faction demand.
- **Multiplayer? With work.** Every ending is authored on the world tick or committed by a synced
  player act:
  - synced: a caravan `FloatMenuOption` (§0 P5), `Quest.Accept` and a `QuestPart_Choice` pick [V];
  - never the commit: a gizmo, a dialog or a modded `ChoiceLetter` (T-80, T-96);
  - in-absentia rolls use §0 P4, and nothing reads ModSettings.

### Routes

"Moment" means what the player acts on. **Silent** means they read about it afterwards.

| Route | Ending | What it gets the story | Under R1 | Under R2 | Moment | Carrier | Kind | Weight | MP |
|---|---|---|---|---|---|---|---|---|---|
| **H-L1** Return to the parent | Release | Hand the place back, and goodwill moves with it | Replace the object with the remembered faction's `Settlement` | Delete the record | The player's own act | ours; donor FT&V cede path | C# | Medium | With work |
| **H-L2** Cede to another faction | Release | Give it to an ally, a rival or a sworn faction. **The only form "independent" can take** | Replace, with a chosen recipient | `SetFaction`, then delete the record | The player's own act | ours; same donor | C# | Medium | With work |
| **H-L3** Abandon | Release | Gone, or a ruin | `Destroy()` | as H-L1 | The player's own act | ours | C# | Medium | With work |
| **H-L4** The parent buys it back | Release | A release offered for a price | E-quest → H-L1 | E-quest → H-L1 | Accept or decline | vanilla quest + a QuestPart of ours | XML + C# | Medium | Yes |
| **H-T1** Retake overlay | Retaken | A timer, then attend and fight, or lose it | E-overlay, M-proxy map | — (see H-T6) | Attend; E-overlay/roll or E-overlay/forfeit | ours; donors FT&V `TryCreateForVassalOutpost`, §1 Build B | C# | Medium on top of §1, Hard alone | With work |
| **H-T2** Retake demand | Retaken | *"Return it or we come"* | E-quest; refusing fires H-T1 or a raid on home | E-quest → H-T6 | Accept or decline | POLITICS § *The faction demand* | XML + C# | Medium | Yes |
| **H-T3** Counter-attack waves | Retaken | A warning, then 1–4 assaults over weeks | Each wave on M-proxy | — | Each wave | ours; donor Worksites Expanded | C# | Hard | With work |
| **H-T4** Strike the staging camp | Retaken or destroyed | Break a nearby camp before its deadline | E-quest→E-site, M-site | E-quest→E-site, M-site | Go, or let it expire | vanilla site quest + our tile node | XML + C# | Medium | Yes [I] |
| **H-T5** Silent reversion | Retaken | RimPacts' reversion shape: a `SetFaction` back to the original owner by name | — | — | **Silent** | RimPacts (shape donor only) | — | **not recommended**: the shipped code path is unreachable | — |
| **H-T6** Repudiation | Retaken | The parent stops honouring the obligation | — | Delete the record on an event | E-quest grace period, or E-letter | ours | C# | Medium | With work |
| **H-D1** Raze overlay | Destroyed | A named faction burns it | H-T1 with a destroy outcome | §1 overlay with a destroy outcome | as H-T1 | as H-T1 | C# | as H-T1 | Yes (R2) / With work (R1) |
| **H-D2** The colony razes it | Destroyed | The player ends their own holding | A player act | Vanilla attack → `CheckDefeated` | The player's own act | vanilla (R2) / ours (R1) | — / C# | Easy (R2) / Medium (R1) | Yes / With work |
| **H-O1** Unrest crosses a line | Throws off | Answerable grievance events; past a threshold, H-T1 or H-T2 | Fiction carried by an existing faction | Real population | Every step answered, no roll | ours; donor RimPacts | C# | Medium–Hard | With work |
| **H-O2** RimPacts as shipped | Throws off | The quarterly tributary revolt roll only | — | — | **Silent** | RimPacts | as shipped | Hard, **not recommended** | No |
| **H-V** VFE Empire release | Release, R0/R3 only | Release all of one lord's vassals | — | — | The player's own act | VFE Empire + MP Compat | as shipped | Easy | Yes |

**Every route is [I] as a route.** The mechanisms each composes are [V].

#### Release (H-L1 to H-L4)

**Gets us [V]:**
- **FT&V ships the replace write twice.**
  - `VassaliseUtility.ExecuteCedeToFactionAtTile(tile, recipientLoadId, name, defName)` removes the
    object on the tile and adds a `Settlement` of the recipient. It refuses the player. It is
    **uncalled** in FT&V.
  - `Invasions.Utility.ApplyWinnerToVassalOffMap` does the same for a lost holding.
- **Under R2, a transfer is `WorldObject.SetFaction`,** a bare field write that `Settlement` and
  `MapParent` do not override. It keeps the ID.
- **Goodwill moves through `TryAffectGoodwillWith`.** State amounts as *requested* (#160).
- **H-L4's accept is synced** (`SyncMethod.Register(typeof(Quest), "Accept")`), and
  `IncidentWorker_GiveQuest` fires it from the storyteller in XML (#154).

**Cannot [V]:**
- **Leave a settlement factionless.** `Settlement_TraderTracker.TraderKind` dereferences
  `settlement.Faction.def` unguarded, and T-07 forbids a new faction.
- **Pay goodwill to a defeated parent, or return it to the storyteller's pool, without clearing
  `Faction.defeated`.** `CheckDefeated` sets it on the last base, `CanChangeGoodwillFor` fails for
  it, and `IncidentWorker_PawnsArrive.FactionCanBeGroupSource` rejects it. **An authored raid that pins it
  still fires:** `IncidentWorker_RaidEnemy.TryResolveRaidFaction` checks only hostility and
  `deactivated` [V].

**A holding returned to its parent (H-L1) comes back at full garrison** [V]. It comes back with the
same layout only [I], from the tile seed, and not under T-33 or after a def climb (#164).

**Consequences:**
- **R1 replacement mints a new ID.** Anything keyed on the old one is orphaned (#165, #167).
- **Caravans bound for the tile abort** (#152). Under R2, `SetFaction` keeps the ID; each order then re-checks against the new owner (#152's table).
- **The commit must be synced.** A caravan float option is synced (§0 P5), including one appended by
  our postfix (#154). A gizmo needs `[SyncMethod]` (T-80).

#### Retaken by the parent (H-T1 to H-T6)

- **H-T1 [V].** FT&V's `TryCreateForVassalOutpost(outpost, attacker, now)` spawns `FT_BaseInvasion` on
  a map-less player holding. It sends a letter: *"…will resolve in <period> unless you intervene"*.
  - `GetOrCreateVassalBattleSettlement` borrows a map with a temporary proxy-faction `Settlement`
    (M-proxy).
  - `ApplyWinnerToVassalOffMap` removes the holding and re-adds the winner's `Settlement`.
  - **Its sides are cast for a third party:**
    - defender and map-defender are set to the holding's original faction;
    - there is no attacker≠original guard;
    - `FindEligibleAttackers` admits any hostile claimant, the parent included.
  - **With the parent as attacker, `winner == attacker` always holds, and the holding is always
    lost.** A donor to re-cast, not a drop-in.
  - **Under R1 there is no defender for /roll.** /forfeit needs none.
  - **The attend option must override `CaravanArrivalAction.StillValid`** (default true, **T-139**). So
    must any H-L release option built as an arrival action.
  - **M-proxy works only while the holding is not a `MapParent`,** because `MapParentAt(tile)`
    returns the first one (**T-150**). If R1 is built as M-own, the holding generates the map itself and
    needs a `ShouldRemoveMapNow`.
- **H-T2.** The POLITICS demand is XML plus a `QuestPart_DemandRefused`. Its refusal fires H-T1
  (E-quest→E-overlay) or a raid on home. **The holding goes only by a choice the player made.**
- **H-T3 [V].** Worksites Expanded's `WorkSiteRevengeTracker`: a 60% start, a warning letter at 1–2
  days, and 1–4 `ThreatBig` raids in windows of days 3–7, 12–20, 25–35 and 38–44 over 45 days. It
  cancels once no player `Settlement` remains on the tile.
  - It **clears `faction.defeated` for the faction of an active revenge sequence**, which returns the
    parent to the storyteller's pool and to goodwill.
  - Its `Rand` is shared-stream on a synced tick, and it reads no ModSettings.
  - It needs a player map. An R1 holding has none.
- **H-T4 (E-quest→E-site).** A deadline site near the holding, delivered by a quest. Its refusal part
  is the #91 one. `QuestNode_GetSiteTile` cannot aim near an arbitrary
  tile (#154 [V]), so this needs our tile node. There is no map borrowing.
- **H-T5 — not recommended: the shipped code path is unreachable [V].** RimPacts'
  `WorldComponent_RimPacts.holdBySettlement` has two writers: `NoteConquered` sets it to 30, and
  `ProcessHoldQuarter` adds 8 a quarter and removes the entry at 70. Nothing decrements it, so its
  `< 25` branch — `Rand.Chance(0.2f)`, then `TryRevertConquered`, a `SetFaction` back to the original
  owner **by name** — never runs, and `TryRevertConquered` has no other caller. The branch is also
  gated on the original owner not being defeated and the current owner holding more than one
  settlement, and the whole model on `Settings.enableTerritory && enableDynamics` and
  `Settings.quarterDays` (T-18). `NoteConquered` has three callers (`CapturePlayerDefeatedSettlement`,
  `CaptureSettlement` for NPC captures, `AbsorbTransferOne`). **What survives is the reversion's shape**
  (`SetFaction` back by name), a donor for shape only. The meter is a five-quarter timer, not a loss
  trigger.
- **H-T6.** Under R2 the record **survives any `SetFaction` silently**. That includes FT&V's
  `ApplyWinnerToSettlement` **when a map is open**. Resolved in absentia, it destroys and recreates
  the settlement (`Remove` + `MakeWorldObject` + `SetFaction` + `Add`), so the record dies with the
  old object and the parent gets a new ID. Build B inherits whichever shape it copies. The owner
  must be checked by our code. A hostile turn arrives only as
  vanilla's relation letter, which is not a moment. An E-quest grace period makes it one [I].

#### Destroyed (H-D1, H-D2)

- **Under R1, nothing in vanilla can end a holding by accident** [V]. `WorldObject` is not an
  `IIncidentTarget`, so every R1 loss is authored. H-D1 is H-T1 with a destroy outcome and a named
  attacker. FT&V's own attacker pick belongs to its scheduler, the background simulation #8
  excluded.
- **H-D2 under R2 is vanilla.** `CheckDefeated` swaps in a `DestroyedSettlement` and destroys the
  original, and the comp record dies with it.

#### Throws the colony off (H-O1, H-O2)

**RimPacts carries one live model [V].**
- **The tributary revolt, at faction level, is #168's.**
  - `TreatyWorker_Tribute.OnQuarter` starts after a 1,800,000-tick grace period.
  - It rolls only when `RptFactionUtility.TributeRatio(faction) < 1.2` (`< 1.5` for the Empire); at
    or above that ratio tribute is paid and nothing is drawn.
  - It draws `Rand.Chance(RevoltChanceFor)` off the shared stream (no `PushState`): 0 at stability
    ≥70, 0.15 at 40–69, 0.35 below that; ×1.5 for the Empire; ×0.7 at `subjugationBasis >= 70`;
    × `GovernorRevoltFactor`; halved by a hostage and by an active `tributeArmamentCheckTick`;
    floored at 0.05 or 0.10 (0.075 or 0.15 for the Empire).
  - A hit kills the governor, breaks the treaty and applies −30 goodwill.
  - It sends an **informational** `Rpt_TributeTrouble` letter, and schedules a revenge raid with a
    50% chance, 120,000 ticks later.
- **The settlement hold reversion** is dead code in 1.6 (H-T5).

**Is it reachable without its dependency and its settings? Not as shipped.**
- Its only declared dependency is Harmony.
- Its captures for the player go through RimPacts' runtime puppet faction (T-07).
- The quarterly clock reads `Settings.quarterDays` (T-18).
- No roll is seeded, and MP Compat does not cover RimPacts.

**H-O1 copies the part that is compliant.** In RimPacts the player's levers come before the roll:
the tribute ratio gate (keep tribute high enough and nothing is drawn), and
`ChoiceLetter_RptTributeEvent`s that move stability by 5–15.
- Swap the modded letter for a quest or a `QuestPart_Choice`, both synced.
- Replace the roll with a threshold that fires H-T1 or H-T2.
- The grievance value is state aimed at the colony, not a currency [I].

#### Debt and credit at the end

| What is owed | At the ending, as shipped | Evidence |
|---|---|---|
| **Rebuild debt** (payment route P4, a comp) | **Extinguished.** It dies with the object on `Remove` (`PostPostRemove`) and on `Destroy` (`PostDestroy` + the `Destroyed` quest signal). **Under R2 it follows a `SetFaction` to the new owner** | [V] `WorldObjectsHolder.Remove`, `WorldObject.Destroy`, `SetFaction` |
| **Accrued tithe** (P1) | **Forfeited on release.** `ReleaseAllVassalsOf` zeroes `DaysSinceDelivery` without delivering. Transfer by `SetFaction`: it keeps paying, to the same lord. Destroyed or recreated: the old entry keeps paying until the next load, then is dropped with a logged null-key error [I]; the new object is not a vassal | [V] `VFEEmpire.WorldComponent_Vassals.DoDay`, `titheInfo` (keyed by reference) |
| **Stored goods** (P2 `Store`) | **Lost** with `Destroy` (#171) | [V] |
| **Bespoke credit** (FT&V points) | **Stranded.** It is kept per original faction but hidden until another holding of that faction exists | [V] `VassalagePointsComponent`, `VassalageUI` |
| **Silver or favour credit** (payment route P5) | Already the player's; nothing is owed | [V] |

**Routes for what was owed [I]:**
1. **Extinguish.** Free, the default.
2. **Pay out, then end.**
3. **A colony-level ledger** keyed by tile or former faction, reattached if the place is retaken.
   Donor: FT&V's points.
4. **Convert it into the ending's price.** Unpaid debt becomes goodwill owed, or H-L4's price.

#### Recommendation (not a selection)

- **Release:** H-L1 or H-L2 through a caravan float option, plus H-L4 if a release should be
  *offered*.
- **Loss:** **H-T2 → H-T1.** The holding goes only through the player's own choice, reusing the #91
  and #92 builds. Take E-overlay/forfeit if #8 is read strictly.
- **Destruction:** H-T4 is the cheapest real fight.
- **Throwing off:** H-O1 is the only compliant form.
- **Under R2, H-T6's owner check is needed whatever is chosen.**

### Constraints

- **No vanilla path ends an R1 holding** (`WorldObject` is not an `IIncidentTarget`). Every loss is
  ours to author, so none can happen silently by accident [V].
- **`SetFaction` has no hook** [V] (**T-140**). An R2 record, a comp-held debt and a VFE tithe all survive a
  transfer unless our code ends them.
- **A defeated parent cannot take goodwill and is never picked by the storyteller** [V]. An
  authored raid that pins it still fires (`IncidentWorker_RaidEnemy.TryResolveRaidFaction`) [V].
  Anything else means clearing `Faction.defeated`, as Worksites Expanded does.
- **No factionless settlement** [V], and **no new faction** (T-07).
- **Player commits:** caravan float options, `Quest.Accept` and `QuestPart_Choice` are synced. Gizmos,
  dialogs and modded `ChoiceLetter`s are not (T-80, T-96).
- **Rolls:** seeded per §0 P4. Nothing reads ModSettings (T-18). This rules out RimPacts as shipped.
- **R1 fights borrow a map** (M-proxy, M-own) or happen elsewhere (M-site).
- **Every attend or release arrival action of ours must override `CaravanArrivalAction.StillValid`**,
  which defaults to true (#152, **T-139**).

### Available mechanisms

| Mechanism | What it provides | Routes | Evidence |
|---|---|---|---|
| FT&V `VassaliseUtility.ExecuteCedeToFactionAtTile` | Replace any object on a tile with a named faction's `Settlement`. Uncalled; refuses the player | H-L1, H-L2 | [V] `294100/3626725895/Assemblies/FactionTerritories.dll` |
| FT&V `Invasions.Utility.TryCreateForVassalOutpost` / `GetOrCreateVassalBattleSettlement` / `ResolveWithWinner` / `ApplyWinnerToVassalOffMap` | Overlay on a map-less holding, a borrowed map, and a transfer. Sides cast for a third party | H-T1, H-D1 | [V] same |
| FT&V `VassalagePointsComponent`, `VassalageUI` | A per-original-faction credit that outlives the holding; shop hidden without a holding | debt/credit | [V] same |
| Worksites Expanded `WorkSiteRevengeTracker` | Warning, then scheduled counter-attack raids; clears `defeated`; no settings | H-T3 | [V] `294100/3687071198/Assemblies/MiningOutpost.dll` |
| RimPacts `WorldComponent_RimPacts.ProcessHoldQuarter` / `TryRevertConquered` / `NoteConquered` | Settlement hold meter; its reversion branch is unreachable (the meter only rises) | H-T5 (shape only) | [V] `294100/3762723122/Assemblies/RimPacts.dll` |
| RimPacts `TreatyWorker_Tribute.OnQuarter`, `RevoltChanceFor`, `TryTributeEvent`, `ResolveTributeEventA/B` | Tributary revolt roll; stability events answered by choice | H-O2; donor H-O1, #168 | [V] same |
| VFE Empire `WorldComponent_Vassals.ReleaseAllVassalsOf` | Per-lord release; forfeits accrual; synced by MP Compat | H-V | [V] `294100/2938820380/1.6/Assemblies/VFEEmpire.dll` |
| `SettlementDefeatUtility.CheckDefeated`, `IncidentWorker_PawnsArrive.FactionCanBeGroupSource` | `defeated` on the last base; the storyteller never picks a defeated faction, though a pinned `IncidentWorker_RaidEnemy` does not check it | all retakes, H-D2 | [V] `Assembly-CSharp.dll` |
| `WorldObject.SetFaction` / `Destroy`, `WorldObjectsHolder.Remove` | Bare owner write; comp teardown and quest signal | all | [V] same |
| `Settlement_TraderTracker.TraderKind` | Unguarded `Faction.def`, so no factionless settlement | H-L2 | [V] same |
| Multiplayer `SyncMethod.Register(Quest, "Accept")`, `SettlementAbandonUtility.Abandon`, choice-letter registrations | Synced commits; modded letters absent | all | [V] `294100/2606448745/1.6/AssembliesCustom/Multiplayer.dll` |

**What does not exist:** no mod ships a holding ending that gives the player the moment. The wide
pass found only RimPacts and Worksites Expanded outside #120's six vassal mods. The remaining hits are
pawn-level slave rebellion (Slave Rebellions Improved, VME, VEF, MP) and name-only false positives.

### Status

**Evidence class: READ**, on [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172). Every
mechanism in the table is [V]; every route is [I].
- **Roots and filters:** both roots, `-g '*.dll' -g '!**/obj/**' -g '!**/Referenced/**'`, attributed
  with `corpus.py --which`.
- **ASCII `-i`:** `Independence`, `Secede`, `Secession`, `Reclaim`, `Retake`, `Rebellion`, `Uprising`,
  `Insurrect`, `Liberat`, `Revolt`.
- **UTF-16 `-i`** with literal `\x00` escapes: the same stems, plus `releaseVassal`.
- **Validators from the `#US` heap:** `RevoltBack` hit RimPacts (the ASCII form missed it), and
  `ReleaseAllVassals` hit VFE Empire.

**Premises corrected:**
1. **§3 R1's *"its invasions against vassals are what #8 excluded".*** What #8 excluded is FT&V's
   *scheduler*. Its vassal-invasion *object* is the donor for an authored retake, though its sides
   need re-casting.
2. **The ticket's *"under R1 ordinary destruction paths may not apply".*** Under R1 none apply at all.
   Under R2 they do, and `SetFaction` carries the record silently.
3. **The ticket's *"RimPacts carries a vassal-revolt model".*** It carries one live one, the
   tributary revolt: an unseeded roll on a settings clock with an after-the-fact letter. Its
   settlement hold reversion is unreachable, because the hold meter only rises [V].
4. **The ticket's *"VFE Empire ships Release all and nothing finer".*** Confirmed. It is also per lord
   and forfeits the accrual.
5. **A retake by the parent runs into `defeated`.** Taking its last base defeats it. The parent then
   leaves the storyteller's pool and can no longer take goodwill, though a pinned raid still fires.

### Open questions

**Requirement gaps**, unowned since #35 is closed:
1. **What happens at the end to an unpaid rebuild debt or accrued credit?** Extinguish, pay out, carry
   or convert.
2. **Is a declined retake /forfeit or /roll?** The answer decides whether §1's
   in-absentia shape satisfies #8 for holdings.
3. **Can a holding be returned to a defeated parent, and can a defeated parent retake it?** A pinned
   raid needs nothing. Goodwill, or a return to the storyteller's pool, needs `defeated` cleared.

**Handed to siblings:**
- **The R2 owner check on transfer:** #152 and #167.
- **Ending a sworn faction:** #168.
- **The outpost-attacked twin of H-T1:** #171.

**Build questions, deferred to the next map:**
- the R1 defender weight for /roll;
- M-proxy against M-own;
- which synced surface commits a release;
- where the colony-level ledger lives.

---

## A caravan en route when its destination changes hands

### Purpose and scope

This section answers [#152](https://github.com/cjd721/Rimworld-Archinity/issues/152): **what
happens to a player's in-flight commitment (a caravan, a vehicle, a pod) when the world object
it is heading to changes faction, and by which routes the commitment can be kept.**

It serves [`requirements/ERA.md`](../requirements/ERA.md) § *The era advance* (*"Nothing else
may change on a delay… while the player is caravanning toward it"*). It applies equally to the
Schism's transfers ([#130](https://github.com/cjd721/Rimworld-Archinity/issues/130)), revolts
([#131](https://github.com/cjd721/Rimworld-Archinity/issues/131)), and conquest (§ 3 R1/R2).

**This section is a clause of the settlement-transfer command, not a system of its own.**

It does not own:
- **Which** settlements transfer — [#34](https://github.com/cjd721/Rimworld-Archinity/issues/34).
- **How** the transfer is written — `engine/factions-and-worldgen.md`, on rules settled by [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) (closed); open build choices are [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.
- **Selecting a route** — [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).

### Verdict

- **Possible?** **Yes.** Vanilla already re-checks a caravan's order on every movement interval,
  and cancels trade, visit and gift orders when the new owner rules them out. The gaps are:
  - an **attack order carries on against a settlement that has passed to an ally or neutral**;
  - the abort message gives no reason;
  - VF aircraft and pods do not re-check while they are in the air.

  Every route closes these gaps inside the transfer command.
- **Multiplayer?** **Yes**, provided the transfer is one synced command. The re-check runs on the synced world tick and reads synced state. Routes CF-A–CF-E and CF-G draw no `Rand`. Route CF-F is Yes as an E-quest, and With work only as our own dialog or a modded letter (T-82/T-95/T-96).

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **CF-A** Vanilla as shipped | Friendly→friendly transfers are seamless. Trade, visit and gift orders stop mid-route with *"couldn't reach its destination"*. **Attack orders land on allies.** Not recommended alone | vanilla + VF | — | Easy | Yes |
| **CF-B** Re-check and abort with a letter | The transfer sweeps every inbound caravan, VF vehicle and pod. Invalidated orders stop, with a letter naming the new owner. Closes the attack hazard for transfers we author | our transfer command | C# | Medium | Yes |
| **CF-C** Re-target | Rebind the order to a recreated settlement, swap it to what the new relation allows, or send the caravan on to the former owner's nearest settlement | our transfer command | C# | Medium | Yes, with a deterministic "nearest" (T-135) |
| **CF-D** Protect the endpoint | The selection skips settlements with anything inbound. **Not recommended for the era advance** | our transfer selection (#34) | C# | Medium | Yes |
| **CF-E** Accept the loss and warn | Vanilla's behaviour stands. The transfer letter names the affected caravans | our transfer letter | C# | Medium | Yes |
| **CF-F** The arrival becomes an encounter | A scene with the new owner at the gate | our arrival action + dialog | C# | Medium–Hard | Yes as an E-quest or a synced E-letter; With work as our own dialog (T-82/T-95) or a modded letter (T-96) |
| **CF-G** Guard the order itself | Attack orders (caravan, pod, aircraft) refuse once the target's faction is no longer the one ordered against, **whoever made the transfer** | Harmony on vanilla + VF arrival actions | C# | Medium | Yes [I] |

**CF-A — vanilla as shipped.**
- **Gets:** nothing to build. A caravan heading to a settlement that passes to another friendly faction arrives and trades with the new owner.
- **Cannot:**
  - explain why an order stopped;
  - avoid stranding the caravan mid-route;
  - stop an attack order turning an ally hostile with no confirmation. VF aircraft and pods share this hole.
- **Consequences:** the hazard fires on the campaign's own authored transfers — the Schism taking Church ground, or an ally absorbing a hostile settlement.

**CF-B — re-check and abort with a letter.**
- **Gets:** a sweep inside the synced transfer over:
  - `Find.WorldObjects.Caravans`, reading `pather` or VF's `vehiclePather` `Destination` / `ArrivalAction`;
  - VF `AerialVehicleInFlight.flightPath` (`Last`, `ArrivalAction`);
  - travelling pods.

  All of these are public [V]. Each invalidated order gets `StopDead()` and one letter that says what happened. An attack order whose target is now non-hostile is stopped the same way.
- **Cannot:** see transfers made by anything other than our command.
- **Consequences:** no state and no `Rand`. It is the smallest honest answer.

**CF-C — re-target.**
- **Gets** three levers [I as composed]:
  - rebind to the recreated object at the same tile, which is needed because destroy-and-recreate aborts every order;
  - swap Trade and OfferGifts when the relation flips;
  - send the caravan on to the former owner's next settlement.
- **Cannot:** know what the player intended. A re-aimed trade run may not be wanted.
- **Consequences:** `StartPath` inside the synced command is the same call a synced order click makes. Pick "nearest" deterministically, not through `GetClosestTile_NewTemp` (**T-135**).

**CF-D — protect the endpoint.**
- **Gets:** the commitment is never broken. It fits #34's rule that factions the player knows are treated differently.
- **Cannot:** keep the advance whole. An exempted settlement stays with its old faction **for good**, because a later transfer is the delay #128 forbids. That is close to the half-re-authored world `requirements/ERA.md` names as the failure. It also lets either player freeze a settlement by sending a caravan.
- **Consequences:** usable for a blow-by-blow Schism, which can pick another target. Not for the advance.

**CF-E — accept the loss and warn.**
- **Gets:** one line in the advance's historian letter or the Schism/revolt letter.
- **Cannot:** warn in advance of the era turn. [#113](https://github.com/cjd721/Rimworld-Archinity/issues/113) fixed that capstone completion calls `AdvanceEra()` directly, with no rite and no confirmation. Quest-driven transfers can warn ahead.
- **Consequences:** leaves the attack hazard open unless it is paired with CF-B's attack clause or CF-G.

**CF-F — the arrival becomes an encounter** (an E-letter or E-quest fired at arrival; no E-overlay needed).
- **Gets:** the handover as a beat: parley, toll, or being turned away.
- **Cannot:** reuse `IncidentWorker_CaravanMeeting`. It ignores `parms.faction`, and MP registers only vanilla's `TryExecuteWorker` (`engine/storyteller-and-incidents.md`).
- **Consequences:** our own dialog carries T-82/T-95, and a modded letter carries T-96. It needs CF-B's sweep to know which caravans are affected.

**CF-G — guard the order itself.**
- **Gets:** these patches, which fail when the target's faction differs from the one the order was aimed at:
  - a postfix on `CaravanArrivalAction_AttackSettlement.StillValid`, which covers vanilla **and** VF ground caravans;
  - a postfix on `TransportersArrivalAction_AttackSettlement.StillValid`;
  - a prefix on VF's `ArrivalAction_LoadMap.Arrived`, filtered to `ArrivalAction_AttackSettlement` (which declares no `Arrived` of its own), or on `FlightPath.ConsumeNode`, since aircraft have no `StillValid`.
- **Cannot:** remember the ordered faction without adding scribed state to vanilla action objects. That is a build question.
- **Consequences:** the only route that also covers Rim War, RimPacts, Faction Territories and quest `SetFaction` transfers.

**Recommendation (not a selection):** **CF-B, with CF-C's rebind** for destroy-and-recreate transfers, and **CF-E's line** in the advance letter. Add **CF-G** if any transfer we do not author ships. **CF-F** is where the story wants to go, and it costs dialog-sync work.

### Constraints

- **The transfer's shape decides what an in-flight order does** [V]:
  - **`SetFaction`** keeps the object, and each order re-checks against the new owner.
  - **Destroy-and-recreate** sets `Spawned == false`, and every order aborts.
  - **#92's overlay outcome takes both shapes** if Build B copies FT&V: FT&V's `ApplyWinnerToSettlement` recreates in absentia and `SetFaction`s when a map is open [V] (**T-140**). That is exactly the per-beat shape question handed to #119.
- **`CaravanArrivalAction.StillValid` defaults to `true`** [V]. Any arrival action we write for §1, #154 or #171 never aborts unless it overrides `StillValid`. **T-139.**
- **`CaravanArrivalAction_AttackSettlement` has no faction check** [V]. The "attack a friendly faction?" confirmation runs only when the order is given. **T-138.**
- **VF aircraft never re-check**, and resolve their target by tile [V].
- **Patch the arrival action, not the pather.** VF ground caravans reuse vanilla's actions under their own pather (**T-117**) [V].
- **No warning can precede the era advance.** #113 gives it no confirmation.

### Available mechanisms

- **Vanilla `Caravan_PathFollower`** [V]:
  - `StartPath` checks `StillValid` when the order is given.
  - `PatherTickInterval` re-checks every interval. On failure it posts a `NegativeEvent` message (`MessageCaravanArrivalActionNoLongerValid`: *"{0} couldn't reach its destination."*, plus `FailMessage` if set) and calls `StopDead`.
  - `PatherArrived` re-checks and otherwise posts *"arrived at its destination"*.
  - `Destination` and `ArrivalAction` are public.
- **Settlement arrival actions** [V]:
  - `Trade.CanTradeWith`: `Spawned`, no map open, not player, not `permanentEnemy`, not hostile, `CanTradeNow`, negotiator.
  - `VisitSettlement.CanVisit`: `Settlement.Visitable`, which is not player, not hostile, not space.
  - `OfferGifts.CanOfferGiftsTo`: **hostile** only.
  - `AttackSettlement.CanAttack`: `Spawned`, `Attackable` (not player), enter cooldown.
  - `Enter.CanEnter`: `HasMap`, cooldown.
  - All of them hold a `Settlement` reference and check `Tile == destinationTile`.
- **`SettlementUtility.AttackNow` → `AffectRelationsOnAttacked`** [V]: drives a non-hostile owner to hostile.
- **Vehicle Framework (`3014915404/1.6/Assemblies/Vehicles.dll`)** [V]:
  - `Patch_WorldPathing.StartVehicleCaravanPath` forwards the vanilla action to `VehicleCaravan_PathFollower.StartPath`.
  - `PatherTick` (from `VehicleCaravan.Tick`) runs the identical re-check, and `PatherArrived` re-checks.
  - For aircraft, `IArrivalAction` has only `Arrived`, and `FlightPath.ConsumeNode` calls it unchecked.
  - `ArrivalAction_LoadMap.Arrived` resolves `MapParentAt(tile)`.
  - `ArrivalAction_AttackSettlement.MapLoaded` calls `AffectRelationsOnAttacked`.
  - `ArrivalAction_Trade.Arrived` re-checks for a negotiator.
- **Vanilla pods and shuttles** [V]:
  - `TravellingTransporters.Arrived` checks only on arrival, then falls back to landing on the map or forming a caravan.
  - `TransportersArrivalAction_AttackSettlement.CanAttack` has no faction check.
- **Shipped transfer code** [V]:
  - Rim War `SettlementUtility.ConvertSettlement` is `Destroy()` + `AddNewHome`.
  - RimPacts `CedeOne` is `SetFaction`.
  - Faction Territories' generic cede (`ExecuteCedeToFactionAtTile`) has no caller. Its live transfer, `Invasions.Utility.ApplyWinnerToSettlement`, **recreates** the settlement when it resolves with no map open and **`SetFaction`s** it when a map is open [V, `FactionTerritories.Invasions.Utility.ApplyWinnerToSettlement`; the cede has no call site in the assembly]. `ApplyWinnerToVassalOffMap` recreates.
  - **None of the three handles in-flight caravans** [V]. The wide pass swept `StopDead`,
    `get_ArrivalAction` and `CaravanArrivalAction` (ASCII `#Strings` heap, both roots,
    `!**/obj/**`, `!**/Referenced/**`). It returned 13, 2 and 11 mods. `get_ArrivalAction` hit
    only Rim War and VF, and both were read. The other hits were not depth-read. By name, they
    are mods' own arrival actions or pawn pathing, and none of them is a settlement-transfer
    system [I].

### Status

**READ.** Every mechanism is [V] and cited by `Type.Method` above. Routes CF-B–CF-G are [I] as compositions. Established by [#152](https://github.com/cjd721/Rimworld-Archinity/issues/152).

### Open questions

- **Transfer shape per beat** (`SetFaction` or recreate). It decides whether an order carries on or aborts. *[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).*
- **Odyssey gravship travel toward a tile that changes hands.** Answered by [#177](https://github.com/cjd721/Rimworld-Archinity/issues/177) in `GRAVSHIP.md` — never re-checked; routes GF-A…GF-G mirror CF-A…CF-G (T-171, T-172).
- **A caravan inside the settlement's map at the moment of transfer.** Map pawns keep the old faction. *Unowned (first raised on #8 § 4, now closed).*
- **Build questions for the next map:** CF-B's letter text, CF-C's re-target precedence, and how CF-G stores the ordered faction.

---

## A sworn faction owes services — every form that can take

### Purpose and scope

**What this section answers:** what a sworn faction can owe the colony, every shape in which it can
reach the player, whether the player can **ask** or only **receive**, and what Reverence and Goodwill
can gate. It resolves [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168) against
[`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *A sworn faction owes services, not
goods*, and answers the two questions that document hands here by name: a holding whose parent later
swears itself, and whether a sworn faction can stop being one.

**Cited, not re-derived:** §3 *Vassals* R4 (the faction-level record in a `WorldComponent`) and R5
(vanilla ally machinery); *What a holding pays* P1–P6; [`RELIGION.md`](RELIGION.md) § *Revolt*
O1–O7, § *The Schism* H1–H3 (holding an alliance), § *The build — Reverence* (the store, bands and
decay); [`POLITICS.md`](POLITICS.md) § *Standing as a content gate* and § *Settlements meet passing
caravans*; [`CURRENCIES.md`](CURRENCIES.md) (VEF's quest-giver shelf).

**What this section does not own:**

- **How a faction comes to swear itself** — submission and revolt are
  [`RELIGION.md`](RELIGION.md)'s doors.
- **Reverence scaling Goodwill** — [#160](https://github.com/cjd721/Rimworld-Archinity/issues/160).
  This section only notes where that scaling touches a service priced in Goodwill.
- **How a holding ends** — [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172). This
  section reuses its end paths for the "return the holding" answer below.
- **A settlement's own specialty** — [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165).
  What a *faction* is known for is answered here; what one *settlement* is known for is not.

### Verdict

- **Possible? Yes.** Every kind of service the requirement names has at least one carrier in 1.6,
  and every delivery shape exists. **The player can ask** through four shipped surfaces: the royal
  aid menu, the comms console, VEF's quest-giver shelf and a caravan's float menu on a settlement.
  **Reverence can gate which services are available, and how often, without being spent**, on
  seams that are already verified. Most carriers are vanilla. The one piece nothing ships is **naming
  the sworn faction as the source**, and every route names it in a small C# piece or in XML.
- **Multiplayer? Yes** for the vanilla carriers used as they ship: permits, comms asks, quests and
  friendly raids. **With work** for anything that hosts its own action: a comms option of ours
  (T-82, T-97, whitelisted host), a targeting permit worker in our assembly (**T-137**), VEF's
  shelf (one sync registration), or boons that patch at runtime. **No** for RimPacts as shipped.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **OS-1** Vanilla comms asks | Request a trade caravan, an orbital trader or military aid from the sworn faction. The price in Goodwill is shown, and so is the cooldown | vanilla `FactionDialogMaker` | XML (`FactionDef.canRequest*`) | **Easy** | **Yes** |
| **OS-2** The sworn faction's permits | A per-faction menu of services on cooldowns: troops, lent labourers and specialists, goods drops of what the faction is known for, a shuttle, strikes, title-gated trade. The set follows the Reverence band | vanilla Royalty permits; VFE Empire workers as donors | XML permits + C# grant hook | **Medium** | **Yes** with vanilla workers; **With work** for our own targeting worker (T-137) |
| **OS-3** Gated comms options of ours | Any service as a visibly locked or unlocked option, with the Reverence threshold, a price in Goodwill and a cooldown. The option can start a quest, send troops or send people | vanilla `FactionDialogMaker` + POLITICS's D2 postfix, standing gate | C# | **Medium** | **With work** |
| **OS-4** A service shelf | A menu window of the sworn faction's services, each one a quest, priced in Goodwill with a minimum-Goodwill gate | VEF `QuestGiverDef` + `GoodwillCurrency` (donor: VFED services) | XML + C# gate + 1 sync registration | **Medium** | **With work** |
| **OS-5** Standing boons | Passive services that follow the band: troops when raided, better prices at its traders, a periodic donation, the right to recruit its visitors | ours; donor VFE Classical `PerkDef` / `PerkWorker` | C# + XML catalogue | **Medium** | **With work** |
| **OS-6** On the faction's own schedule | Offers, visits, gifts and help arriving unasked, at a frequency the band sets | vanilla storyteller + `IncidentWorker_GiveQuest`; ours to name the faction | XML + a `StorytellerComp` | **Medium** (Easy as R5 alone) | **Yes** |
| **OS-7** On a fixed schedule | A fixed basket or labour on a clock, keyed to the faction | §3 R4 record + P1 tithe engine; donor RimPacts' tributary | C# + XML | **Medium** | **With work** |
| **OS-8** People who are offered or lent, never dumped | A specialist lent for N days who returns, or a quest whose reward is a pawn the player picks | vanilla `Permit_CallLaborers` / VFE Empire `Permit_CallTechfriar` shape; `Reward_Pawn` + `QuestPart_Choice` | XML (+ the trigger from OS-2/OS-3/OS-6) | **Easy–Medium** | **Yes** |
| **OS-9** Asked in person | A caravan standing at a sworn settlement asks for guides, recruits, resupply or shelter | `Settlement.GetFloatMenuOptions` postfix (§0 P5, synced) | C# | **Medium** | **Yes** |
| **OS-10** A signal the colony builds | A beacon or signal fire that calls the sworn faction's warband, usable before any comms console exists | ours; donor VFE Classical `Buildings.Beacon` | XML building + C# | **Easy–Medium** | **With work** |
| RimPacts as shipped | Treaties, tributaries, goods orders, defence pacts. **Not recommended**: no sync, T-18 rolls, creates factions (T-07); §3 R6 | RimPacts | as shipped | Hard | **No** |

**Every route is [I] as a route.** The mechanisms each composes are [V], and the composition is
inferred until built. **The routes compose.** OS-2 or OS-3 carries asking, OS-6 carries the faction's own
initiative, OS-8 decides what "people" means, and OS-5 is the always-on layer.

#### Who asks, and who only receives

| Shape | Carriers | The player… |
|---|---|---|
| Semi-random sends on the faction's schedule | OS-6, R5, OS-5 (troops when raided) | **receives** |
| Specific things on a fixed schedule | OS-7 | **receives**, and may set the cadence (P1's cadence setting) |
| Categories it is known for | OS-2 (permits per `FactionDef`), OS-1 (its `caravanTraderKinds`), OS-7 (RimPacts' specialty goods as donor) | **asks** under OS-1/OS-2, **receives** under OS-7 |
| A favour requested on a cooldown | OS-1, OS-2, OS-3, OS-10 | **asks** |
| A menu like a holding's, but greater | OS-2 (the royal aid menu), OS-4 (the shelf), OS-3 (the comms list) | **asks** |
| Offered, then chosen | OS-6 offers carrying OS-8 choices | **receives the offer, chooses the content** |
| Asked in person | OS-9 | **asks**, at the cost of travel |

**The failure the requirement names is answered by OS-8, not by the schedule.** A borrowed specialist
who leaves by shuttle cannot be sold, and a pawn reward the player picks is not a random body.

#### OS-1 — vanilla comms asks

**Gets us** [V] (`RimWorld.FactionDialogMaker`):

- **Three shipped asks.** A trade caravan costs −15 Goodwill with a 4-day cooldown; an orbital trader
  −30 and 15 days; military aid −25 and 1 day. The adjusted price is rendered in the option label.
- **Per-faction switches in XML.** `FactionDef.canRequestTraders`, `canRequestOrbitalTrader` and
  `canRequestMilitaryAid`.
- **A choice of caravan.** The player picks from the faction's `requestable` `caravanTraderKinds` —
  *what it is known for*, as trade.

**Cannot** [V]:

- **Answer anyone below Ally.** Each ask is `Disable("MustBeAlly")` otherwise.
- **Send troops from a faction below Industrial.** `techLevel < Industrial` links to
  `CantMakeItInTime`, so a Neolithic or Medieval sworn faction never answers this ask.
- **Be reached without a comms console.** The one earlier surface is Medieval Overhaul's messenger
  table (per #154).
- **Read Reverence**, or vary its cooldowns.

**Consequences.** A sworn faction has to be **held at Ally** for OS-1, R5, OS-10 and the storyteller's
friendly raid. [`RELIGION.md`](RELIGION.md) H1–H3 are the levers that hold it, and they supersede
§3 R4's *"cannot hold the relation still"*.

#### OS-2 — the sworn faction's permits

**Gets us** [V] (`Assembly-CSharp.dll`):

- **Permits are keyed to a faction instance, not to the Empire.** `Pawn_RoyaltyTracker` stores
  `FactionPermit(faction, title, permit)`. The permits card ships a faction switcher, and the royal
  aid gizmo lists every held permit of every faction.
- **A permit needs no title.** `AddPermit` stores whatever title is current, which can be null. The
  "Call aid" gizmo appears whenever any permit is held, and vanilla never removes a titleless permit
  automatically; the only faction-keyed removal is the player's *Return all permits*
  (`Pawn_RoyaltyTracker.RefundPermits`, titled factions only) (**T-146**).
  So a Reverence band can **grant** a founder this faction's permits and **revoke** them, with no
  title ladder (**OS-2b**).
- **Or a title ladder** (**OS-2a**). Give the sworn faction's `FactionDef` `royalTitleTags` and titles;
  the engine is faction-generic (`GainFavor`, `CanUpdateTitleOfAnyFaction`, bestowing quests, the
  permit comm options in `FactionDialogFor`). Every vanilla title obligation is optional XML:
  `decreeMtbDays` −1, room and apparel requirements null, `maxPsylinkLevel`, `canBeInherited`. **No
  faction but the Empire carries titles anywhere in the corpus**, so OS-2a has no precedent.
- **The catalogue, all XML, via `RoyalAid`:** troops by `pawnKindDef` + `pawnCount` or by `points`;
  lent labourers (`Permit_CallLaborers` → quest lodgers who leave); goods drops (`itemsToDrop`); a
  transport shuttle; strikes; `aidDurationDays`; `cooldownDays`; `layerBlacklist`. VFE Empire adds a
  regiment, a techfriar and an absolver as worker donors.
- **What it is known for is free.** Each `RoyalTitlePermitDef` names a `FactionDef`, so each sworn
  faction's permit set is its own authored catalogue.
- **"How often" by band.** A higher band grants the next permit in a `prerequisite` chain, and
  `AddPermit` replaces the prerequisite, so a shorter cooldown or a larger force can replace the
  smaller one.
- **It runs at Neutral.** `AidDisabled_NewTemp` refuses only a hostile faction, an underground map,
  a blacklisted layer or bad temperature. A pinned `RaidFriendly` skips the Ally filter.
- **Legible for free.** Each option reads *free* or *cooldown N days*.

**Cannot:**

- **Be priced in anything but royal favour on cooldown** [V]. `FillAidOption` offers use while on
  cooldown only for `favorCost` favour. With no favour ever granted, the permit is **cooldown-only**
  (`ConfigErrors` requires `favorCost > 0`).
- **Revoke itself** [V]. Revocation is a write of ours on the live `AllFactionPermits` list.
- **Act without a holder.** The permit sits on a pawn, who must be on the map, or in a caravan for
  `usableOnWorldMap` [V].
- **Offer title-gated trade (OS-2a only)** [V]. `permitRequiredForTrading` needs a title that grants
  the permit, so OS-2b loses it.

**Consequences:**

- **OS-2a breaks if the sworn faction's def is ever swapped (T-36).**
- **Multiplayer.** `AddPermit`, `SetTitle`, `RefundPermits` and `ResetPermitsAndPoints` are
  Multiplayer SyncMethods, and vanilla workers' targeting is registered. A targeting worker of ours
  is not (**T-137**).

#### OS-3 — gated comms options of ours

**Gets us.** Any service can sit behind a `DiaOption` appended by POLITICS's D2 postfix, locked with
*"requires N Reverence — currently M"* ([`POLITICS.md`](POLITICS.md) § *Standing as a content gate*
§3) [V seam]. Its action can do any of three things:

- **generate a quest** — vanilla's `RequestAICoreQuest` does exactly this [V];
- **pin the faction on `RaidFriendly`**, which honours a set `parms.faction` [V];
- **price itself in Goodwill** the way vanilla's asks do [V].

**Cannot:** reuse vanilla's cooldowns. `lastMilitaryAidRequestTick` exists per faction [V], but any
band-scaled cooldown is a field of ours [I].

**Consequences:** the enabled action must live on a whitelisted type (T-82, T-97,
[`docs/engine/determinism.md`](../engine/determinism.md)).

#### OS-4 — a service shelf

**Gets us** [V] (`VEF.Storyteller`):

- **`QuestGiverDef` scopes the shelf to one faction.** `fixedQuestGiverFaction` is a `FactionDef`,
  and `onlySpecifiedQuests` lists the services.
- **The price and the gate ship.** `GoodwillCurrency` debits Goodwill, and `minimunGoodwillRequirement`
  refuses below a threshold.
- **Every entry is an authored quest**, so any OS-8 shape is a shelf entry.

**Cannot:**

- **Read Reverence.** It needs our gate node, the way `CURRENCIES.md` builds its currency subclass.
- **Offer an entry with no asker** [V] (**T-147**). `GoodwillCurrency.Allows` returns false when the slate has
  no `asker`.

**Consequences:** `CURRENCIES.md`'s three defects and its one sync registration apply unchanged.
VFE Deserters' `DeserterServiceDef` menu is the same shape, synced by MP Compat's
`SyncedPurchaseService` [V], but it is bound to Intel and the Deserters.

#### OS-5 — standing boons

**Donor** [V] (`2787850474/1.6/Assemblies/VFEC.dll`): VFE Classical's senate. A Republic's
`FactionDef` extension lists one `PerkDef` per senator and a final perk. Three of the shipped perks
are sworn-faction services in all but name:

- **`Auxilia`** — a 25% chance of reinforcements on every raid;
- **`Tributum`** — an annual donation, and halved prices at one faction's vendors;
- **`VeniVidiVici`** — a gizmo that recruits that faction's pawns at will.

**Gets us:** the always-on layer, band by band. Its price lever is the virtual
`Settlement_TraderTracker.TradePriceImprovementOffsetForPlayer` (a flat 0.02 in vanilla) or a
postfix on `Tradeable`'s price setup. RimPacts and VFE Classical both patch prices per faction [V].
**Vanilla has no relation-based price at all** [V].

**Cannot:** be asked for. These services are received.

**Consequences:** `PerkWorker` applies and removes Harmony patches at runtime. Doing that in synced
context on both clients is [I].

#### OS-6, OS-7 — the faction's own schedule, and a fixed one

- **OS-6.** [`#154`](https://github.com/cjd721/Rimworld-Archinity/issues/154) verified that
  `IncidentWorker_GiveQuest` makes any quest storyteller-fired from XML. Naming the sworn faction
  needs a quest node or comp of ours, since `QuestNode_GetFaction` has no record filter (§3 R4). A
  `StorytellerComp` scaled by band is [#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)'s
  shape. R5 is the free background.
- **OS-7.** §3 R4's record with P1's clock, or RimPacts' quarterly tributary as design: silver, goods
  in the faction's specialty, or **one labourer each quarter for five days** (`TributeLaborer`) [V].
  This is the route nearest to "goods". The requirement's *services, not goods* is the check against
  it.

#### OS-8 — people, offered or lent

- **Lent** [V]: vanilla `Permit_CallLaborers` and VFE Empire's `Permit_CallTechfriar`. The script
  generates its pawn with `<faction>$permitFaction</faction>`. The pawn:
  - joins as a controllable lodger with its work restricted;
  - leaves by shuttle after `aidDurationDays`;
  - costs Goodwill if it dies or goes missing.
- **Offered** [V]: `Reward_Pawn` exists, and a quest's `QuestPart_Choice` pick is synced (per #171).
  `QuestNode_GeneratePawn` exposes `kindDef`, faction, traits and gender in XML, but **not an ideo**.
  A *convert* is `PawnGenerationRequest.FixedIdeo` from C# [V field].

#### OS-9, OS-10 — asked in person, and a signal the colony builds

- **OS-9.** An option our postfix appends to `Settlement.GetFloatMenuOptions` rides Multiplayer's
  float-menu sync (per #154) [V]. It must never be a caravan gizmo (T-80).
- **OS-10** [V]. VFE Classical's `Beacon` is a building whose gizmo fires `RaidFriendly` with a chosen
  Ally faction and a map cooldown. MP Compat syncs its `LightCommand` lambda. Ours would pin the
  sworn faction, and it answers the Neolithic era, where OS-1 does not exist.

#### Every service, by carrier

| Service | Carriers |
|---|---|
| **Troops** | OS-1 (Industrial+ only), OS-2 `CallAid`, OS-3 pinned `RaidFriendly`, OS-5 Auxilia-shaped, OS-6 / R5 help when raided, OS-10 |
| **Pawns** — recruits, converts, specialists | OS-8 lent specialists and picked rewards, OS-2 labourers, OS-5 recruit-at-will, OS-7 labour tribute |
| **Goods in kind, as it is known for** | OS-2 goods permits per `FactionDef`, OS-1 its trader kinds, OS-4 shelf entries, OS-7 basket (the requirement's boundary) |
| **Trade access and prices** | OS-1 requested caravans and orbital traders; OS-2a title-gated trader kinds (`permitRequiredForTrading`); OS-5 price offset — no vanilla carrier, two mod donors |
| **Safe passage** | Non-hostility already gives it ([`POLITICS.md`](POLITICS.md) § *Settlements meet passing caravans*, A/B). Extras: OS-2 transport shuttle; RimPacts' ambush exemption and caravan speed near treaty settlements as donors |
| **Political weight** | [`POLITICS.md`](POLITICS.md)'s ripple with a seeded sworn edge; an intercession quest (`QuestNode_ChangeFactionGoodwill` on a third faction, XML); #92's ally-aid battle; a `GoodwillSituationWorker` natural offset for its friends (**T-115** caution) |
| **Following into orbit** | Per-`FactionDef` XML: `arrivalLayerWhitelist` must list Orbit. OS-2 permits must not blacklist Orbit. Comms and permits work from the gravship because it `IsPlayerHome` (P2 § *Where payment arrives*) |

#### Reverence and Goodwill — the gate, and whether Reverence can be spent

**Reverence can gate which services and how often, without being spent** — three seams, all [V]:

1. **Permits per band (OS-2).** A `ReverenceBandDef` effect ([`RELIGION.md`](RELIGION.md) §5 bands)
   grants or revokes permits. *Which* is the permit set; *how often* is each permit's
   `cooldownDays`, upgraded along a `prerequisite` chain.
2. **The standing gate (OS-3, OS-4, OS-6 offers).** `StandingAxisDef` Reverence on a `DiaOption` or a
   quest's accept, shown before it is reached. A band-scaled cooldown is ours [I].
3. **Frequency of what is received (OS-5, OS-6).** Boons and storyteller weights keyed on the band.

**Goodwill pays; Reverence opens.** That is the pairing the requirement's own grammar already uses
for institutions (*"Reverence unlocks the diplomatic option; normal Goodwill remains the spend
lever"*). The vanilla asks (OS-1), the shelf (OS-4) and the lent-pawn penalties all spend Goodwill
already. **#160 couples the two.** If high Reverence accelerates Goodwill gain, a sworn faction's
services refill faster with no mechanism of their own. Vanilla renders the ask price from
`CalculateAdjustedGoodwillChange`. #160's routes scale **positive** gains only, and an ask is a
negative change, so an ask's price label stays true. It would drift only if #97 extends scaling to
negatives (#160 open question).

**Reverence can be made spendable, and what it would cost** [I]:

- **Mechanically** it is a debit on the §1 record — a `QuestCurrency` subclass or a permit-favour
  analogue. Medium.
- **It contradicts a stated requirement.** The grammar table in
  [`requirements/RELIGION.md`](../requirements/RELIGION.md) says Reverence *"gates … rather than
  being spent"*, while [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) keeps spending
  open.
- **It drains the eligibility it was earned for.** Submission, revolt, institutions and #160's
  Goodwill curve all read the same number.
- **It hands the player a dial on betrayal.** Global Reverence sets the Church's betrayal threshold.
- **It stacks with decay** (§4).
- **Royal favour as a separate per-faction pool** avoids touching Reverence, but it raises the
  third-currency question.

#### A holding whose parent faction later swears itself

This answer reads a holding as **R1**. That reading rests on §3 *Open questions* (*"answered: it
becomes the colony's"*); siblings still keep R2 live, and whether R2 stays open is Conrad's to confirm.
FT&V's model remembers the parent by load ID (per #167). All three outcomes are expressible:

| Outcome | How | Weight |
|---|---|---|
| **Stays a holding** | Nothing happens. It keeps paying as a holding | none |
| **Folds into the oath** | Our code retires the holding's own payout and adds its yield as a service, or a permit, of the sworn relationship. Delivery shared with OS-7 | Medium |
| **Returns** | #172's release: a `Settlement` recreated for the parent (the shape of FT&V's `ExecuteCedeToFactionAtTile`, which ships uncalled) | Medium |

A return gets a new ID (per #165) and a full garrison [V]; the same layout is [I] — it follows from
the tile seed, and does not hold under T-33 or a def climb (#164). Under **R2** the holding is still the parent's settlement, so folding is the default and
"stays" would need two relationships on one faction. **Choosing among the three is a requirement.**

#### Can a sworn faction stop being one?

Yes, by every cause the question names:

- **Reverence collapses.** Decay (§4) crosses a band down. The band-change letter (§5) is the
  E-letter. Permits are revoked (OS-2) or options relock (OS-3). This can be **erosion**, services
  shrinking band by band, or **an end** at the submission threshold.
- **Betrayal.** The colony attacks it. Vanilla's `AffectRelationsOnAttacked` and the member-death
  hooks make it hostile, and **every relation-riding carrier stops on its own**:
  - permits refuse a hostile faction;
  - comms asks and friendly raids need Ally.

  A deliberate attack prompts `ConfirmAttackFriendlyFaction` as usual. #152's hole is different: an
  attack order issued **before** the faction swore or became allied, which then lands without a
  prompt.
- **It throws the colony off.** RimPacts' tributary revolt is the shipped model (per #172). It is a
  silent roll **off the shared stream** (`Rand.Chance`, no `PushState`) with choice letters beforehand, so under #8's rule it must arrive as an
  E-quest or E-letter the player answers.
- **Defeat in war.** No background war exists (#13), so this can only happen in an authored #92
  ally-aid battle. `Faction.defeated` is set **true** only by `CheckDefeated` in vanilla; Worksites Expanded clears it
(per #172).

Each ending writes the §3 R4 record, revokes OS-2 permits and, for H3's latch, needs its
"attacks can break it" hook. **The requirement states no intent either way.**

### Constraints

- **Vanilla addresses a faction only when the caller names it.** The storyteller's ally comps pass
  none (§3 R5). Direct `RaidFriendly` / `RaidEnemy.TryExecute` with `parms.faction` set is honoured
  (per #168 and #172) [V]; one engine entry covers both workers.
- **Ally is a latch, not a number** — ≥75 up, ≤0 down ([`POLITICS.md`](POLITICS.md) §0). Every
  vanilla ask needs it. Permits do not.
- **Vanilla comms military aid refuses factions below Industrial** [V].
- **No relation-based price exists in vanilla** [V]. Trade prices are a patch.
- **Orbit refuses every surface faction** unless its `FactionDef.arrivalLayerWhitelist` lists Orbit
  (Empire, TradersGuild, Salvagers and Mechanoid only, in vanilla), and orbit takes only whitelisted
  incidents [V]. **T-48** records the orbit gates.
- **A titleless permit is permanent until we remove it** [V] (**T-146**). See *Open questions*.
- **Every player act is a synced command** — T-80, T-82, T-95, T-96, T-97, T-137. Nothing is a
  setting (T-18). Never swap the sworn faction's def (T-36, T-98).

### Available mechanisms

| Mechanism | What it provides | Route | Evidence |
|---|---|---|---|
| `FactionDialogMaker.RequestTraderOption` / `RequestOrbitalTraderOption` / `RequestMilitaryAidOption` / `CallForAid` | Ally-only asks: −15 / 4 d, −30 / 15 d, −25 / 1 d; aid refused below Industrial | OS-1 | [V] `Assembly-CSharp.dll` |
| `FactionDialogMaker.RequestAICoreQuest` | A comms option that generates a quest | OS-3 | [V] |
| `Pawn_RoyaltyTracker` (`AddPermit`, `GetPermit`, `RoyalAidGizmo`, `AllFactionPermits`, `SetTitle`, `GainFavor`) | Per-faction permits and titles; titleless permits held and usable | OS-2 | [V] |
| `RoyalTitlePermitDef` / `RoyalAid` / `RoyalTitlePermitWorker(_CallAid, _CallLaborers, _DropResources, _CallShuttle)` | XML services with cooldown, favour, layer blacklist; aid at Neutral | OS-2 | [V] |
| `RoyalTitleDef` | Every obligation optional in XML | OS-2a | [V] |
| `PermitsCardUtility` | Faction switcher; shows permits only for titled factions | OS-2a | [V] |
| `IncidentWorker_RaidFriendly.TryResolveRaidFaction` | Honours a pinned faction, skipping the Ally filter | OS-2, OS-3, OS-10 | [V] |
| Multiplayer `SyncMethods` | `AddPermit`, `SetTitle`, `RefundPermits`, `ResetPermitsAndPoints`, `CallResourcesToCaravan` | OS-2 | [V] `2606448745/1.6/AssembliesCustom/Multiplayer.dll` |
| `Permit_CallLaborers`; VFE Empire `Permit_CallTechfriar` | Lent pawns keyed to `$permitFaction`, returned by shuttle | OS-8 | [V] XML |
| `Reward_Pawn`, `QuestNode_GeneratePawn`, `PawnGenerationRequest.FixedIdeo` | Offered pawns; converts from C# | OS-8 | [V] |
| VEF `QuestGiverDef` / `GoodwillCurrency` | A faction-scoped quest shelf priced in Goodwill with a minimum | OS-4 | [V] `2023507013/1.6/Assemblies/VEF.dll` |
| VFED `DeserterServiceDef` + MP Compat `SyncedPurchaseService` | A synced menu of services, Deserters-bound | OS-4 donor | [V] `3025493377`, `1629973374/1.6/Referenced/` |
| VFE Classical `PerkDef` / `PerkWorker` (`Auxilia`, `Tributum`, `VeniVidiVici`) | Per-faction boons won from a government | OS-5 donor | [V] `2787850474/1.6/Assemblies/VFEC.dll` |
| VFE Classical `Buildings.Beacon` + MP Compat `LightCommand` | A built signal calling an Ally's warband, map cooldown, synced | OS-10 donor | [V] |
| `Settlement_TraderTracker.TradePriceImprovementOffsetForPlayer` (virtual, 0.02); RimPacts `Patch_Tradeable_GetPriceFor` | The price seam; a per-faction price donor | OS-5 | [V] |
| RimPacts `TreatyDef`s, `TreatyWorker_Tribute`, `TributeLaborer`, `GoodsOrder` / `Dialog_RptGoodsRequest`, `FriendlyAid` | Treaties, labour tribute, player goods orders, disaster aid — all design donors | OS-7, OS-5 donors | [V] `3762723122/Assemblies/RimPacts.dll` |
| `FactionDef.arrivalLayerWhitelist`; `PlanetLayerDef.onlyAllowWhitelisted*` | Orbit arrival gate | orbit | [V] |

**What does not exist, where it shaped the routes:**

- **No faction but the Empire carries titles.** An XML sweep of `royalTitleTags` over both roots and
  `Data` finds Royalty only.
- **No shipped system gives a *chosen* faction's services to the player under Multiplayer.** The
  two-encoding wide pass narrowed to vanilla, RimPacts, VFE Classical, VFE Deserters and VFE Empire,
  and all were depth-read where they carried a service. Every route therefore composes a vanilla
  primitive with the sworn faction named by us.

### Status

**Evidence class: READ**, established on [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168).
Every mechanism in the table is [V]; every route is [I] by construction.

**Sweeps.** Both roots, `-g '!**/obj/**' -g '!**/Referenced/**'`, `.dll`. ASCII, and UTF-16LE built
byte-wise by a Python reader rather than through a shell. Case-insensitive throughout. Validators
came from the heap being searched: `TitheTypeDef` (ASCII) and `InStockpile` (UTF-16) both hit VFE
Empire.

| Term | Result |
|---|---|
| `MilitaryAid` | vanilla, RimPacts, Rim War; VFE Empire and Vehicles (ASCII only) |
| `CallAid` | vanilla, Multiplayer; Mechanoids: Total Warfare (an icon path) |
| `Reinforce` | 12 mods and vanilla. Carriers read: VFE Classical (`Beacon`, `Auxilia`), RimPacts. Others are raid or trader internals by name [I] |
| `Tributary` | RimPacts only |
| `Fealty`, `Liege`, `Overlord`, `Protectorate`, `Levy`, `Conscript`, `Hireling`, `Emissary`, `RequestAid` | **zero** in both encodings |

The XML def-family frequency table (`<Ns.Type>` tags matching service-like names) finds
`VFEC.Perks.PerkDef`, `VFEEmpire.TitheTypeDef`, `VFED.DeserterServiceDef`, `RimPacts.TreatyDef`
and nothing else of the kind.

**Premises corrected:**

1. **P3's *"cannot exist without a royal title"* is wrong** [V]. A permit is held and used with no
   title. Only the permits card, title-gated trade and the permit comm options need one.
2. **§3 R5's *"cannot address a named faction"* holds only for the storyteller path** [V].
3. **[`POLITICS.md`](POLITICS.md) §0's *"all three spend goodwill … −30"* is imprecise** [V]. The
   prices are −15, −30 and −25, and military aid also refuses factions below Industrial.
4. **[`RELIGION.md`](RELIGION.md) §5's inherited `RoyalAid` field list is now [V]**, with `points`,
   `aidDurationDays` and `favorCost` added.
5. **§3 R4's *"cannot hold the relation still"*** is superseded by
   [`RELIGION.md`](RELIGION.md) H1–H3.

### Open questions

**Requirement gaps — to Conrad via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2)**
(#35, the requirement's author, is closed):

1. **Is a goods drop the player asks for on a cooldown a *service* or *goods*?** OS-2 goods permits and
   OS-7 baskets sit on the requirement's hard boundary.
2. **Reverence spend.** The religion grammar says *"gated, not spent"*; territory keeps spending
   open. One of them must give.
3. **May a sworn faction grant a founder a title of its own (OS-2a)?** Titles are otherwise the
   Church's grammar. And **is royal favour with a sworn faction a third currency?** OS-2b avoids both
   questions.
4. **Must a sworn faction be held at Ally?** OS-1, R5 and OS-10 need it; OS-2 does not.
5. **A holding whose parent swears** — stays, folds or returns.
6. **Can a sworn faction stop being one**, and by which of the four causes?
7. **Which sworn factions follow into orbit.**
8. **Who holds the services.** A founder, any colonist, or one holder per player.

**Build questions, next map (unowned until a route is selected):**

- the band-effect grant/revoke hook;
- the revoke write on `AllFactionPermits`;
- our cooldown store (OS-3);
- T-137 registration if a targeting worker is ours;
- the OS-4 gate node;
- the OS-5 runtime-patch discipline under Multiplayer;
- OS-10's faction pin.

**Owned elsewhere:** Reverence → Goodwill scaling and where its price is displayed:
[#160](https://github.com/cjd721/Rimworld-Archinity/issues/160). The ending shapes' E-letter and
E-quest: [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172)'s naming.

---

## What an outpost costs — materials, silver and committed pawns

### Purpose and scope

This answers [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *An outpost is built, staffed and worth it*: its cost in materials and silver, which pawns may be committed, whether staffing bounds how many outposts exist, and whether a yield can justify the pawns it takes. Resolved by [#170](https://github.com/cjd721/Rimworld-Archinity/issues/170).

It builds on §2 (the engine is VEF's `Outposts.dll`; #81's multiplayer harness B1–B5) and cites that section rather than repeating it. Upkeep, and what happens when an outpost is attacked or loses staff, belong to [#171](https://github.com/cjd721/Rimworld-Archinity/issues/171). A scouting outpost's reveal belongs to [#165](https://github.com/cjd721/Rimworld-Archinity/issues/165) and to Charting. The numbers belong to [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).

### Verdict

- **Possible? Yes.** Committed pawns, material and silver costs, and restatted yields are all shipped or XML. **As shipped, the carrier cannot tell pawn kinds apart, and staffing does not limit the count.** Each gap is closed by a contained piece of C# on a seam that has been read.
- **Multiplayer? With work.** Every VEF route needs §2's harness. The routes here add deterministic reads of synced state, not new sync surface. §2c's settings gate is now unconditional (#170; see Constraints).

> **Premise changed by #175:** committed pawns are consumed. OC-N1 and OC-N2 are retired, and the kind rule moves into the founding commit. See § *An outpost that consumes its pawns and runs on its own* (#179).

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **OC-S1** VEF outpost as shipped | Pawns leave the colony and live at the tile until removed or packed | VEF `Outposts.dll` + VOE / VFE Classical defs | as shipped | Easy | With work (§2 harness) |
| **OC-S2** Timed lend quest | "Lend N colonists for D days". A contract that returns them, not a standing place. | vanilla `QuestPart_LendColonistsToFaction`, Royalty `Script_PawnLend` | XML quest | Easy→Medium | Yes [I] |
| **OC-S3** Own engine | Any roster rule | our code (§2 Build B) | C# | Hard — **not recommended**, since the harness is a third of the work | With work |
| **OC-K1** Founding gate on our subclass | A founding-only kind rule, e.g. at least one non-slave colonist; no Harmony | VEF's reflection hook `CanSpawnOnWith` | C# | Medium | With work |
| **OC-K2** Per-pawn admission + roster invariant | Who may join, who may leave, and each kind's yield, for the outpost's whole life | Harmony on `Utils.CanAddPawn`, `Outpost.RemovePawn`, `Outpost.IsCapable` | C# | Medium | With work |
| **OC-K3** Vanilla shuttle filter | Colonist / prisoner / slave / health / age flags, in XML | `CompShuttle.IsAllowed` (with OC-S2) | XML | Easy | Yes [I] |
| **OC-C1** `CostToMake` restat | A one-time cost in materials and silver per outpost type, carried by the founding caravan | `OutpostExtension.CostToMake` | XML patch | Easy | With work |
| **OC-C2** Computed cost | A cost scaled by era, or rising with each outpost held | our postfix on the three `CostToMake` readers | C# | Medium | With work |
| **OC-C3** Build debt | Found now, pay from home, no yield until paid | VEF `costPaid` + `Dialog_GiveItems` / pod arrival (P4 shape) | C# + XML | Medium | With work |
| **OC-N1** Continuous staffing floor | An outpost cannot be run below its minimum or kind rule | our patch on the Remove gizmo / `RemovePawn` | C# | Medium | With work |
| **OC-N2** Population accounting | Committed pawns still count toward the storyteller's population, so the colony isn't refilled | our postfix on `StorytellerUtilityPopulation.AdjustedPopulation` | C# | Medium (one patch) | Yes |
| **OC-N3** Hard cap | A fixed or era-keyed maximum | our check in the founding gate | C# | Medium | With work |
| **OC-N4** Escalating cost | A soft bound through cost | = OC-C2 | C# | Medium | With work |
| **OC-Y1** XML yield restat | Per-pawn, per-skill and per-cycle amounts, 7 of 13 VOE defs | `ResultOption` (§2a) | XML patch | Easy | With work |
| **OC-Y2** C# yield for the rest | Scavenging, Town and the generated halves | our overrides (§2a) | C# | Medium | With work |
| **OC-Y3** Yield by pawn kind | A slave, prisoner or colonist weighted differently | our override of `IsCapable` / `ProducedThings` | C# | Medium | With work |

**OC-S1 — as shipped.**
- *Gets:* `Outpost.AddPawn` removes the pawn from its caravan, its `holdingOwner` and `Find.WorldPawns`, and scribes it `Deep` in `occupants` [V]. It comes back through Remove (a one-pawn caravan) or Pack [V]. The outpost ticks only rest, `ProvidedFood`, chemical needs, health and tending; mood and suppression are never ticked, so there is no rebellion, escape or break [V].
- *Cannot:* limit its own count (see OC-N0 under Constraints).
- *Consequence:* committed pawns drop out of the storyteller's population (OC-N2).

**OC-S2 — timed lend quest.**
- *Gets:* a shuttle collects N pawns. `returnLentColonistsInTicks` later they come back by shuttle or pod, with the reward scaled by count × days. They stay counted through `QuestUtility.TotalBorrowedColonistCount` [V].
- *Cannot:* be a place. It has no tile yield and it ends. The script is Royalty's; the quest part is core [V].

**OC-K1 — founding gate on our subclass.**
- *Gets:* `Dialog_CreateCamp` evaluates `ext.CanSpawnOnWithExt(...) ?? <worldObjectClass>.CanSpawnOnWith(PlanetTile, List<Pawn>)` by reflection, so a static method on our class runs whenever VEF's gate passes [V].
- *Cannot:* see prisoners (the list is `HumanColonists`), police the roster after founding, or reach VOE's and VFEC's classes without subclassing each one.

**OC-K2 — admission + invariant.**
- *Gets:* one postfix on `Utils.CanAddPawn` covers the founding loop, the caravan Add gizmo and pod arrival, because all of them call `AddPawn` [V]. Vanilla supplies every distinction (`IsFreeNonSlaveColonist`, `IsSlaveOfColony`, `IsPrisonerOfColony`, `IsAnimal`) [V]. A rule such as *at least one colonist, slaves may add to it* is expressible here and nowhere cheaper.
- *Consequence:* the build charge fires only when the caravan's **last humanlike** joins [V]. A rule that rejects a humanlike leaves the caravan alive and **the cost uncharged**, so OC-K2 and OC-C1 have to be built together (**T-149**).
- *Also reaches:* VOE `Outpost_Defensive`'s Deploy removes occupants through `RemovePawn`, bypassing the Remove gizmo, and VOE `Outpost_Town.Produce` adds generated pawns through `AddPawn` — with the producing pawn's `kindDef` and **faction**, so a prisoner recruits foreigners. A kind rule on `CanAddPawn` would silently discard them, and Town growth enlarges T-148's invisible population over time [V].

**OC-K3 — shuttle filter.**
- *Gets:* `acceptColonists`, `acceptColonyPrisoners`, `allowSlaves`, `onlyAcceptColonists`, `onlyAcceptHealthy`, `minAge` and `requiredColonistCount` [V].
- *Cannot:* express "at least one non-slave", because `allowSlaves` is all-or-nothing.

**OC-C1 — `CostToMake`.**
- *Gets:* any `ThingDef`, silver included, checked against the first player caravan on the tile (`PlayerControlledCaravanAt`, not necessarily the founding one) and charged to the founding caravan, shown in the founding tooltip, and charged once behind the scribed `costPaid` [V].
- *Today:* **0 of 13** VOE and **0 of 4** VFE Classical 1.6 defs carry a cost [V].
- *Cannot:* scale by era (it is static per def), be paid from home, or impose build time. `TicksToSetUp` is declared and read nowhere [V].

**OC-C2 — computed cost.**
- *Gets:* any cost function. It needs a postfix on `CanSpawnOnWithExt`, `RequirementsStringBase` and the charge in `AddPawn`.
- *Consequence:* never write the value into `outpost.Ext`, which is shared by the def (§2b B3).

**OC-C3 — build debt.**
- *Gets:* VEF's ledger and its two reverse-delivery paths, plus one `if` of ours withholding production (P4 correction). Pushing back `ticksTillProduction` models build time (#171). Paying by pod is synced as shipped. Paying by caravan (`Dialog_GiveItems`) is §2b B5 (#171).

**OC-N1 — staffing floor.**
- *Gets:* the outpost is only as real as its staff. It pairs with #171's **OU-D4** (*staff in trouble*) and its *Loss* section.
- *Consequence:* the rule must live inside the synced Remove commit (§2b B5), not only in the button's disabled state.

**OC-N2 — population accounting.**
- *Gets:* committed pawns count toward population intent, which is vanilla's own `TotalBorrowedColonistCount` precedent [V]. It is a deterministic read, so it is multiplayer-safe.

**OC-N3 / OC-N4 — caps.**
- *OC-N3:* a hard cap, if one is ever wanted.
- *OC-N4:* the OC-C2 cost function, bounding the count through price.

**OC-Y1–OC-Y3 — yield.**
- *OC-Y1 and OC-Y2:* as in §2a.
- *Levers:* `BaseAmount`, `AmountPerPawn`, `AmountsPerSkills`, `TicksPerProduction`, the `ResultOptions` list (silver included) and the delivery method (P2).
- *OC-Y3:* weights by kind, and is OC-K2's yield half.

**Recommendation (not a selection).** OC-S1 + OC-C1 + OC-Y1 is everything XML alone can do. Making staffing *the* limiter, as the requirement asks, needs **OC-N2 and OC-N1 together**. Any kind rule needs **OC-K2**, since OC-K1 covers founding only. The three share the founding gate and the roster seam. OC-S2 is a different beat (a contract, not a place) and is worth keeping for other uses.

### Constraints

- **OC-N0 — nothing bounds the count as shipped** [V]. `Outposts.dll` has no cap. `CanSpawnOnWithExt` rejects only a tile with a settlement base on or next to it, or a neighbouring `Outpost`. `MinPawns` and `RequiredSkills` are checked **only at founding**. After that the Remove gizmo is disabled only at one occupant, and `Tick()` abandons the outpost only at zero, so **every outpost can be run on one occupant of any kind, an animal included**.
- **VEF cannot tell pawn kinds apart** [V].
  - Founding counts `Pawn.IsFreeColonist`, which in 1.6 includes slaves (`hostFactionInt` null, `SlaveIsSecure` off-map) and excludes prisoners.
  - The founding commit calls `AddPawn` on **every pawn in the caravan**.
  - `Utils.CanAddPawn` checks only the ideology `Event`.
  - `IsCapable` (humanlike + skills) makes a prisoner or slave produce like a colonist.
- **Committed pawns leave the storyteller's population** [V] (**T-148**). `AdjustedPopulation` reads maps, caravans, travelling transporters and borrowed colonists only.
- **The build charge and the roster share a seam** [V] (**T-149**). `CostToMake` is taken inside `AddPawn` only when the caravan's last humanlike joins.
- **The staffing rule is a player setting** [V]. `MinPawns`, `Range`, `TicksPerProduction` and `TicksToPack` are `[PostToSetings]`. §2c item 1 now blocks `Setup` unconditionally (#170), so these and the two `Settings` multipliers keep their XML values in both modes. An MP-only gate would have left them editable in single-player, where the campaign is playtested, which the requirement forbids (T-18).
- A removed prisoner leaves as a caravan of **their own faction** (`Outpost.GetGizmos` Remove lambda) [V code; the in-play effect is I].
- All founding and roster writes are unsynced until §2's harness exists (T-80).

### Available mechanisms

| Mechanism | What it provides | Evidence |
|---|---|---|
| `Outposts.Outpost.AddPawn` / `RemovePawn` / `occupants` | Commitment, removal from the colony, deep-scribed roster | [V] `2023507013/1.6/Assemblies/Outposts.dll` |
| `Outposts.Dialog_CreateCamp` (ctor + `DoOutpostDisplay`) | Founding validation over `HumanColonists`; commit of every caravan pawn; the `CanSpawnOnWith` reflection hook | [V] |
| `Outposts.Utils.CanAddPawn` / `CanSpawnOnWithExt` / `RequirementsStringBase` | Per-pawn ideology gate; founding gates; the cost tooltip | [V] |
| `Outposts.Outpost.IsCapable` / `CapablePawns` | Which occupants produce | [V] |
| `OutpostExtension.CostToMake`, `MinPawns`, `TicksToSetUp` | Cost list; founding minimum; a dead field | [V] |
| `RimWorld.StorytellerUtilityPopulation.AdjustedPopulation`, `QuestUtility.TotalBorrowedColonistCount` | Population the storyteller sees; the borrowed-pawn precedent | [V] Assembly-CSharp 1.6 |
| `RimWorld.QuestPart_LendColonistsToFaction`, `CompShuttle.IsAllowed`, Royalty `Script_PawnLend` | Timed lend with population kept; XML pawn-kind filter | [V] |
| VFE Classical `Outposts.xml` + `VFEC.Outposts.*` | A second content carrier on the same engine; 4 defs, same defNames as VOE's | [V] `2787850474/1.6` |

**Wide pass.** I swept both roots with `-i` for `outpost` in `.dll`, ASCII and null-interleaved UTF-16 (validated on `Outposts.dll`), excluding `obj/` and `Referenced/`. I also enumerated every `<worldObjectClass>` in the corpus XML. Nothing turned up **no player-founded, pawn-staffed carrier other than `Outposts.dll`**. The alternatives cleared:

- **FT&V `FactionTerritories_VassalOutpost`:** a vassal, consumes no pawns (§3).
- **Worksites Expanded:** NPC sites.
- **Rim War `Settler`:** NPC expansion driven by abstract points; barred as background war simulation.
- **RimPacts:** an interop shim (#81).
- **Medieval Overhaul:** a Harmony patch on VOE's hunting yield.
- **Better Architect Menu:** an architect-menu reference to VEF's `Outposts.*` / `OutpostDeliverySpot` (a `#US` literal) [I].
- **VFE Security:** the hit is in the 1.4 assembly only.
- **Vanilla `Settle`:** a player-operated map, which fails *operates nothing*.
- **Vanilla `Camp`:** a temporary map.

### Status

READ. The mechanisms are [V] against the 1.6 assemblies and defs cited. Every route is [I] by construction: the mechanisms are read, their composition is unbuilt. [#170](https://github.com/cjd721/Rimworld-Archinity/issues/170), building on [#81](https://github.com/cjd721/Rimworld-Archinity/issues/81).

### Open questions

- **Which pawn kinds may be committed.** A requirement: Conrad, via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2) (the requirement's author, #35, is closed); balance with #119. All three candidate rules are expressible under OC-K2.
- **Cost, `MinPawns` and yield numbers, and the era key for OC-C1/OC-C2.** Owned by #119. `docs/progression/` is empty.
- **What an outpost below its floor does.** Owned by #171 (OU-D4 and *Loss*); pairs with OC-N1.
- **VOE vs VFE Classical defName collision.** Sourcing, #14 / `MOD-VERDICTS.md`.
- **Optional RUN:** one single-player save; compare the storyteller's "Adjusted population" debug readout before and after founding an outpost with 3 colonists.

---

## An outpost's upkeep arrives as events, not as a management surface

### Purpose and scope

This section answers [`docs/requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *An outpost is built, staffed and worth it*. The clause it answers is *"an outpost's upkeep reaches the player as an event, never as a management surface"*: something happens, the player decides once, and it is over.

It covers four questions:
- whether an outpost can raise events;
- whether an outpost can be attacked and defended;
- whether an outpost can degrade or stop paying without a per-tick simulation or a screen;
- whether any of that can be authored per outpost type.

Resolved by [#171](https://github.com/cjd721/Rimworld-Archinity/issues/171).

**Not owned here:**
- the engine and its multiplayer harness (§2, [#81](https://github.com/cjd721/Rimworld-Archinity/issues/81));
- cost and staffing ([#170](https://github.com/cjd721/Rimworld-Archinity/issues/170));
- the demand shell ([`POLITICS.md`](POLITICS.md) § *The faction demand*, [#91](https://github.com/cjd721/Rimworld-Archinity/issues/91));
- the overlay battle (§1, [#92](https://github.com/cjd721/Rimworld-Archinity/issues/92));
- how often and how harshly any of this happens (balance, [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)).

Route IDs carry the **OU-** prefix.

**Shape names**, shared with [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172) and [#154](https://github.com/cjd721/Rimworld-Archinity/issues/154).

Events the player answers:
- **E-letter:** a letter.
- **E-quest:** #91's declinable quest.
- **E-overlay:** #92's overlay world object on the target's tile.
- **E-site:** a vanilla `Site` the player travels to.
- **E-march:** a hostile world object that moves toward the target (#154). **Not recommended.** No outpost route uses it: there is no MP-safe donor, and OU-A1 and OU-A2 give the same beat without movement.
- **E-quest→E-overlay** and **E-quest→E-site:** #91's quest is the shell, and accepting it spawns the arena.

What happens if the player does not come:
- **/roll:** §0 P4's seeded roll.
- **/forfeit:** a deterministic loss or degrade (#172's variant (b)).

Where the fight's map comes from:
- **M-own:** the target is its own map parent.
- **M-site:** the site's own map.
- **M-proxy:** FT&V's temporary settlement on the tile.

### Verdict

- **Possible? Yes.** No shipped carrier exists: VEF's outpost engine raises no events of its own, and nothing in the corpus attacks a VEF outpost.
- **Multiplayer? With work.** This is on top of #81's harness. The player's one decision must be a synced commit: a quest accept or choice, a world-object float-menu option, or a pod launch. It must never be a custom `ChoiceLetter` option (T-96) or VEF's give-items dialog (§2b B5).

> **Premise changed by #175:** staff are consumed, and a lost outpost is destroyed into a ruin. There is no capture, rescue or evacuation. OU-D3 has nobody to send home, and OU-D4 applies only to #179's OR-1. The attack routes here stand. See § *An outpost that consumes its pawns and runs on its own* (#179).

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| OU-N1 E-letter on a clock | a notice at the outpost with an immediate effect | our World-tagged `IncidentDef` + worker | XML + C# | Medium | Yes. Options need `[SyncMethod]` (T-96) |
| OU-N2 E-quest | a declinable ask with a deadline, a countdown and a refusal consequence | vanilla quests + #91's refusal part + our outpost picker | XML + C# | Medium | Yes |
| OU-A1 E-overlay on the outpost (/roll or /forfeit) | a timed attack on the outpost, which the player attends or which resolves in absentia | §1 Build B generalised; FT&V as read donor | C# | Hard | With work (§0 P4, §0 P5; plus the map under M-own) |
| OU-A2 E-quest→E-site | a hostile site near the outpost; ignoring it hurts the outpost | vanilla `Site` + #91 + our tile node and consequence part | XML + C# | Medium | Yes [I] |
| OU-A3 E-quest→E-overlay | OU-A2's shell, with the fight at the outpost | #91 + §1 | C# | Hard | as OU-A1 |
| OU-A4 staff ambush | the outpost's own pawns fight on a vanilla ambush map | `IncidentWorker_Ambush` + an XML flag + a map-removal override | XML + C# | Medium–Hard | Yes. **Not recommended** for upkeep: the player cannot decline it |
| OU-D1 late payout | the next delivery slips | a write to `Outpost.ticksTillProduction` | C#, no Harmony | Easy on OU-N1/N2 | Yes |
| OU-D2 stalled until answered | no yield until the player acts | a scribed flag on a `WorldObjectComp` added to `OutpostBase` by XML + a production-time prefix | XML + C# | Medium | Yes |
| OU-D3 packing ultimatum | production stops, VEF's countdown shows, and the staff come home at zero | VEF `Packing` + `ConvertToCaravan` | C#, no Harmony | Easy–Medium | With work (the stop-pack gizmo, B5) |
| OU-D4 staff in trouble | a real disease or injury that VEF's health tick runs; sending medicine is the answer (each tend spends a whole stack) | VEF occupant health tick + our hediff | C# worker, XML table | Medium | Yes |
| OU-T1 per-type table | failures, weights and consequences per kind | our `DefModExtension` on each outpost `WorldObjectDef` | XML | Easy (once OU-N1/N2 exist) | Yes |
| OU-T2 per-class behaviour | failures that touch type-specific state | VOE `worldObjectClass` | C# | Medium | Yes |
| OU-T3 a quest per type | quests per kind | separate `QuestScriptDef`s | XML | Easy each | Yes |

The routes compose:
- **OU-N** carries the decision.
- **OU-D** is the stake.
- **OU-T** varies both by kind.

#### OU-N1 — E-letter on a clock

- **Gets us:** a letter pointing at the outpost. It applies OU-D1–D4 in the same synced tick.
- **Trigger:**
  - `Storyteller.AllIncidentTargets` includes `Find.World`, and vanilla storytellers already run World-tagged comps [V]. No clock of our own is needed.
  - Alternatively, a `WorldComponent` gated on `IsHashIntervalTick` (§0 P3).
- **Cannot:** offer a choice for free. A custom `ChoiceLetter`'s options act on one client only (T-96).
- **Consequence:** with no decision elsewhere, this is the background roll the requirement rules out.

#### OU-N2 — E-quest

- **Gets us:** the whole loop, from shipped parts:
  - `expireDaysRange` gives the offer window.
  - `QuestPart_Choice` gives *pay this or that*.
  - The Quests tab gives the countdown.
  - #91's `QuestPart_DemandRefused` handles refusal.
  - `IncidentWorker_GiveQuest` is the XML trigger.
  - `QuestNode_DemandBudget` is the cap.
- **Multiplayer:** `Quest.Accept` and `QuestPart_Choice` are synced [V].
- **Cannot:** find an outpost, or act on one, in XML. The picker node and the consequence part are C#.
- **Ways the demand can be paid:**
  - By transport pod into the outpost. This is synced [V].
  - By caravan through VEF's `Dialog_GiveItems`. This is unsynced until B5 is closed.
  - At home, by a part of ours.
  - At a settlement, in vanilla's `TradeRequest` shape.
- **Traps:** T-71, T-77, T-101.

#### OU-A1 — E-overlay on the outpost

- **Gets us:** a named attacker, a timer, an attend-or-not decision, and a stated result.
- **Read donor:** FT&V's `Invasions.Utility.TryCreateForVassalOutpost` already runs the overlay against a player-held, map-less world object [V]. It is typed to FT&V's own class.
- **The map.** **M-proxy works only while the target is not a `MapParent`**, and an outpost is one (see *Constraints*). That leaves two options:
  - **M-own:** the outpost is the map parent. This needs a `ShouldRemoveMapNow` override, plus spawning occupants onto the map and returning them afterwards.
  - **M-site:** the fight happens on a site one tile away.
- **Attend option:** our own `CaravanArrivalAction`. It must override `StillValid`, because the base returns `true` (#152's trap, **T-139**).
- **In absentia:** either:
  - **/roll:** §0 P4's seeded roll.
  - **/forfeit:** a deterministic loss or degrade (#172 (b)).

  Either way, the result is the OU-D family or a loss.
- **Consequence:** this is §1's Build B built for two target kinds. #172 (H-T1) and #154 want the same thing.

#### OU-A2 — E-quest→E-site

- **Gets us:** a real fight on a vanilla site map, with the vanilla timeout and quest UI. `SitePartWorker_RaidSource` is the read shape for a site that threatens until it is destroyed (§0 P3).
- **Cannot:**
  - Place the site relative to an outpost in XML. `QuestNode_GetSiteTile` measures only from a player home map (#154), so the tile node is C#.
  - Put the fight *at* the outpost. It happens near it, and the staff are absent.
- **Consequence:** the best story-to-weight ratio among the attack routes.

#### OU-A4 — staff ambush

- **Gets us:** the committed pawns defending themselves on a vanilla map (`CaravanIncidentUtility.SetupCaravanAttackMap`) [V].
- **Cannot, as shipped:**
  - Map-generating caravan incidents are blocked on outpost tiles. `allowCaravanIncidentsWhichGenerateMap` defaults `false`, and `OutpostBase` does not set it [V].
  - Once unblocked, the map's parent is the outpost and nothing removes the map.
  - A caravan of *all* the occupants destroys the outpost.
- **Consequence:** the player cannot decline it, so it is a set piece. **Not recommended** as routine upkeep.

#### OU-D1–D4 — degrade without a per-tick simulation

All four ride clocks VEF already runs. **None adds per-tick work.**

- **OU-D1:** `ticksTillProduction` is a private scribed int, decremented by delta. Writing it delays the payout [V].
- **OU-D2:** the production seam is not uniform [V]:
  - `Outpost_Town` overrides `Produce()` (it yields pawns).
  - `Outpost_Scavenging` and `Outpost_Drilling` override `ProducedThings()`.

  A stall is still one contained patch; where it hooks is a build question. `OutpostBase` declares no `comps` today [V].
- **OU-D3:** a packing outpost produces nothing (`if (Packing) … else if (production)`) and shows *"Packing: N days"*. At zero, `ConvertToCaravan` returns its occupants and goods as a caravan on the tile [V].
  - **Limit:** VEF's stop-pack gizmo sets `ticksTillPacked = -1` [V]. The player can cancel the ultimatum for free unless the gizmo is suppressed or replaced. It is unsynced either way (B5).
- **OU-D4:** occupant hediffs progress on VEF's clocks, an existing cost [V]. Disease progression, injuries, bleeding and tending run on the interval path (`TickInterval` → `SatisfyNeedsInterval` → `OutpostHealthTickInterval`); the per-tick `Hediff.Tick` is mostly empty in 1.6.
  - **Tending spends whole stacks** [V]. `OutpostHealthTickInterval` takes every "best so far" medicine stack out of `containedItems` with `TakeItem`, and `TendUtility.DoTend` decrements the last one, which is never returned. A delivery of N medicine buys about one tend per stack, not N tends. A VEF defect we may want to patch (#119).
  - **A pawn can die, but VEF cleans up deaths only on the per-tick path** [V code; in play I]. `SatisfyNeeds` removes a dead pawn and stores its corpse only if the death happened inside its own `OutpostHealthTick`. A death from disease or bleeding happens on the interval path, so the dead pawn stays in `occupants`, still counts toward `PawnCount` and, through `IsCapable`, still produces. The outpost is never abandoned by it (**T-152**). Handling death is ours: a check in the synced tick.
  - At zero occupants, VEF sends *"Abandoned"* and destroys the outpost.
  - **Food cannot run short:** `ProvidedFood` is conjured with no stock [V]. A food shortfall is our code.

#### Loss

`OutpostsMod.Notify_Removed` is empty, and the occupants are no longer world pawns (#170) [V]. A bare `Destroy()` on a staffed outpost therefore drops living pawns silently.

A loss route has to choose what happens to them. Each choice is a different story:
- **Evacuate** (`ConvertToCaravan`): *they fled home*.
- **Kill:** *they fell*.
- **Capture:** *they were taken*. This is the only choice that opens a rescue.

#### OU-T1–T3 — per type

- **OU-T1:** a `DefModExtension` of our own type on each outpost def. Mind T-06, T-02 and T-05.
- **Two content carriers ship the same defNames:** VOE, and VFE Classical's four (#170). Which one wins is [I].
- **OU-T2:** reaches the ten VOE classes only. `Outpost_Logging` and `Outpost_Trading` run `Outposts.Outpost`; `Outpost_Production` runs VEF's `Outposts.Outpost_ChooseResult` (§2).

#### Recommendation (not a selection)

**OU-N2, with OU-D3 and OU-D4 as the stakes, and OU-A2 for attacks.**
- OU-N2 delivers the decision, the countdown and the refusal from synced, shipped parts.
- OU-D3 and OU-D4 make *"unanswered"* visible through mechanics VEF already runs.
- OU-A2 is the cheapest real fight.

OU-A1 and OU-A3 are worth building only if §1's Build B is built for #172 or #154 anyway.

### Constraints

- **No shipped event attacks a VEF outpost** [V].
  - `Outpost.raidFaction` and `raidPoints` are scribed and read nowhere.
  - VOE's `Outpost_Defensive.InterceptRaid` is inert.
- **An outpost has no map, and it adopts any map made on its tile** [V] (**T-150**). **M-proxy works only while the target is not a `MapParent`.**
  - `OutpostBase` declares no `mapGenerator`, so `MapParent.MapGeneratorDef` falls back to `Encounter`.
  - `WorldObjectsHolder.MapParentAt` returns the first `MapParent` on the tile.
  - `ShouldRemoveMapNow` is not overridden, and the base returns `false`.
  - `Tick` skips occupant needs while a map exists.
- **The player's one decision must be a synced commit.**
  - Synced: `Quest.Accept`, `QuestPart_Choice`, `CompLaunchable.TryLaunch`, and float-menu options on a world object (§0 P5, extended to postfix-added options per #154) [V].
  - Not synced:
    - custom `ChoiceLetter` options (T-96);
    - every VEF gizmo and dialog (B5), including the stop-pack gizmo OU-D3 needs to govern;
    - node-tree dialogs, where T-82 and T-95 apply.
- **Any attend option of ours overrides `CaravanArrivalAction.StillValid`.** The base returns `true` (#152).
- **Occupants must never be dropped by a bare `Destroy()`** (see *Loss*; **T-151**).
- **No ModSettings** (T-18). VEF's `TimeMultiplier` scales `TicksToPack` when the player packs, so OU-D3's duration must be ours.

### Available mechanisms

- **VEF `Outposts.dll`** [V]:
  - two clocks: `Tick` (needs, health, abandonment) and `TickInterval` (packing or production);
  - `Packing` and `ConvertToCaravan`;
  - medicine drawn from `containedItems` when tending;
  - the *"Abandoned"* letter;
  - `TransportPodsArrivalAction_AddToOutpost`, which scribes its outpost.

  It has no incident workers, no raid use and no map.
- **VOE `VOE.dll`** [V]: ten subclasses.
  - Several override `Tick`, and all of those call the base.
  - `Town` overrides `Produce`; `Scavenging` and `Drilling` override `ProducedThings`.
  - `Defensive`'s raid intercept is inert.
- **VFE Classical and Medieval Overhaul** [V]: yield variants only.
- **FT&V** [V]: attacks its own map-less vassal object through the §1 overlay. It borrows a map through a proxy `Settlement`. Declined as a dependency (#8); it is the donor for OU-A1.
- **Vanilla** [V]:
  - World-tagged storyteller comps and `Storyteller.AllIncidentTargets`;
  - `IncidentWorker_GiveQuest`;
  - `IncidentWorker_Ambush` and `CaravanIncidentUtility`;
  - `WorldObjectDef.allowCaravanIncidentsWhichGenerateMap` (default `false`);
  - `GetOrGenerateMapUtility` and `MapParent.CheckRemoveMapNow`;
  - `SitePartWorker_RaidSource` (§0 P3).
- **Wide pass.**
  - **How it ran:** `rg -a -l "Outposts"` over both roots and `*.dll`, excluding `obj/` and `Referenced/`, piped to `corpus.py --which`. Validated: VEF and VOE hit.
  - **What it found:** seven mods.
    - VEF, VOE, VFE Classical and Medieval Overhaul: read.
    - FT&V and RimPacts: territory and interop reads only, cleared on #81 and #92.
    - MP Compat: its two-line VOE patch (§2b).
  - **Result:** no mod raises an event from a VEF outpost [V over the read assemblies].
  - **UTF-16 half:** see #170's wide pass (§ *What an outpost costs*); it adds only mods already cleared there.

### Status

Evidence class **READ**, via [#171](https://github.com/cjd721/Rimworld-Archinity/issues/171), building on #81, #92, #91 and #170. The mechanisms are [V]. That the routes compose them into working behaviour is [I] until built.

### Open questions

- **RUN (#119):** under M-own, what happens to occupants while the outpost has a map? `Tick` skips `SatisfyNeeds`, so observe whether they freeze or starve. One client is enough.
- **RUN (#119):** give an occupant a lethal disease and observe `occupants` and the yield after the death (**T-152**).
- **Build (#119):**
  - where OU-D2's stall hooks, given the non-uniform production seam;
  - which storyteller comp draws OU-N1's World incident;
  - whether OU-D3 suppresses VEF's stop-pack gizmo or replaces it with a synced relief command;
  - how occupants are spawned onto, and returned from, a battle map (OU-A1/A3).
- **Story call (Conrad):** /roll or /forfeit for OU-A1/A3's in-absentia branch.
- **Balance (#119):** cadence, severity, OU-D2/D3 durations, and a budget shared with #91's.
- **Requirement gap — Conrad, via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2)** (the requirement's author, #35, is closed):
  - whether an outpost may be *lost* outright or only degraded;
  - whether staff can be *captured*, which a rescue beat needs.

  #8's *"loss must arrive as something the player acts on"* is written for holdings only.

---

## An outpost that consumes its pawns and runs on its own

### Purpose and scope

This answers the two clauses of [`requirements/TERRITORY.md`](../requirements/TERRITORY.md) § *An outpost is built, paid for in people, and worth it* that [#175](https://github.com/cjd721/Rimworld-Archinity/issues/175) changed:
- committed pawns are **consumed** (not recallable, not tracked, sold to the outpost), and the outpost then runs on its own with no staffing floor;
- a destroyed outpost is a **ruin** a caravan can loot, and paying the build cost again rebuilds it.

Resolved by [#179](https://github.com/cjd721/Rimworld-Archinity/issues/179). It re-answers only what the new premise changes; cost, yield levers and the harness stay in § *What an outpost costs* (#170) and §2 (#81), and the attack that destroys an outpost stays in § *An outpost's upkeep arrives as events* (#171).

Route IDs: **OR-** for how the outpost runs without staff, **RU-** for the ruin and rebuild.

### Verdict

- **Possible? Yes.** Nothing ships it. **VEF's production reads the staff**: every yield formula takes the occupant list, all 5 shipped VOE `ResultOption` entries are per-pawn or per-skill, and `Outpost.Tick` destroys an outpost on the first tick it has no occupants. Five routes decouple it, from a gizmo filter to our own world object. **Nothing in the corpus leaves an outpost ruin**; four vanilla shapes and one of ours carry it.
- **Multiplayer? With work.** The VEF routes still need §2's harness, and B1 (the founding commit) is where the pawn sale and the kind rule land. Consumption *shrinks* B5, because the Remove, Pack and item-transfer gizmos are deleted rather than synced. Our own world object (OR-5, RU-2) needs none of §2's harness. MP Compat covers none of this: its whole VOE patch is `Outpost_Artillery.Fire` and one `Outpost_Defensive` gizmo lambda, and it has no VEF Outposts class [V].

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **OR-1** Ghost staff | Pawns stay in `occupants`; every recall and transfer control is removed. Yield reads them exactly as shipped. | VEF + our gizmo filter; tabs removed by XML | patch + XML | Medium | With work (§2 harness) |
| **OR-2** Frozen staff | OR-1, and the staff are also frozen: no aging, disease or death. The yield stays fixed at what was sent. | OR-1 + two prefixes on VEF's needs ticks | patch | Medium | With work (§2 harness) |
| **OR-3** Consume, flat yield | Pawns are really sold and gone; the outpost runs at zero occupants on `BaseAmount` | our commit + a prefix on `Outpost.Tick`; XML restat | C# + XML | Medium | With work (§2 harness) |
| **OR-4** Consume, stored snapshot | OR-3, but the yield scales with the count, skills and kinds sold, read from a record stored at the sale | OR-3 + our comp + production prefixes per class | C# | Medium–Hard | With work (§2 harness) |
| **OR-5** Our own world object | A map-less outpost that never holds pawns: sale at founding, clock, delivery | ours; donors FT&V `FactionTerritories_VassalOutpost`, VEF `Deliver` | C# | Hard | Yes, our own `[SyncMethod]`s |
| **RU-1** The outpost is its own ruin | Production stops, goods stay, label changes; rebuild clears the flag | VEF `Outpost` + our scribed comp | C# + XML | Medium | With work (loot is B5) |
| **RU-2** Our ruin object | A persistent, readable ruin holding the goods; *Loot* and *Rebuild* from the caravan's menu | ours; donors vanilla `TradeRequestComp` (P4), VEF `CanSpawnOnWithExt` cost check | C# | Medium | Yes (world-object float menus are synced) |
| **RU-3** Loot site | The goods lie on a real map the caravan walks, optionally guarded; with `leaveAbandonedSettlement`, a dated marker is left for the rebuild | vanilla `Site` + `ItemStash` part (Odyssey `AbandonedSettlement` part for a ruined layout) | XML + one C# call | Medium | Yes [I] |
| **RU-4** Vanilla marker | A dated "abandoned settlement" marker; no loot | vanilla `AbandonedSettlement` | C#, no Harmony | Easy | Yes |
| **RU-5** Re-found in place | *Rebuild* is VEF's own founding on the same tile, full price, any type | VEF as shipped | none | Easy | With work (B1) |

The two halves compose. Pick one OR route for how the outpost runs, and one RU route (RU-4 or RU-5 only as a complement) for how it ends.

#### What production reads today [V]

- `Outpost.ProducedThings()` = `ResultOptions.SelectMany(ro => ro.Make(CapablePawns.ToList()))`. `ResultOption.Amount(pawns)` = `(BaseAmount + AmountPerPawn × pawns.Count + Σ AmountsPerSkills) × ProductionMultiplier`, and `AmountBySkill.Amount` sums each pawn's skill level.
- **At zero occupants the base path yields `BaseAmount`, and no shipped def sets it.** VOE's 1.6 `Outposts.xml` has **0** `BaseAmount` and **5** `ResultOption` entries across 4 defs: Logging's is `AmountPerPawn`, and Drilling's, Production's two and Trading's are `AmountsPerSkills`.
- **The C# yields read staff too.** In VOE and in VFE Classical's three classes:
  - `Town` recruits per capable pawn.
  - `Science` researches per capable pawn.
  - `Hunting`, `Farming` and `Mining` synthesize per-skill or per-pawn options, and ore options carry `MinSkills`.
  - `Drilling` accrues `workDone` from `TotalSkill(Construction)`. Its `ProductionString` divides by that total with **integer division**, and only while the well is not `Ready`. Founding requires Construction 20, so as shipped this throws only if staff are emptied or lose the skill before the well is ready, which is exactly what OR-3 does.
  - `Defensive` intercepts only with `PawnCount > 0`.
  - Only `Scavenging`'s product ignores staff; staff only shorten its interval.
- **Zero occupants destroys the outpost.** `Outpost.Tick` sends *"Abandoned"* and calls `Destroy()` on the first tick that `PawnCount == 0`.
- `TicksToPack` divides by `occupants.Count`. It is read only by the Pack gizmo.
- **Delivery never reads staff.** `Deliver` and its five methods depend on the delivery map only.

#### OR-1 — ghost staff

- **Gets us:** the shipped yield formulas, untouched, and *"Bob runs the outpost now"* taken literally, since Bob is still in `occupants`.
  - A postfix on `Outpost.GetGizmos` drops Remove, Pack and Stop-pack.
  - A postfix on `Outpost.GetCaravanGizmos` drops Add pawn, Take items and Give items.
  - `GetTransportersFloatMenuOptions` drops VEF's add-to-outpost pod option.
  - The four `WITab_Outpost_*` tabs are removed from `OutpostBase` by XML patch.

  Nothing remains for the player to recall, tend or equip.
- **Cannot:** stop the staff living.
  - They age (`SatisfyNeedsInterval` calls `AgeTickInterval`), sicken, heal and use medicine.
  - A death on the per-tick path removes the pawn, and the last one triggers *"Abandoned"*.
  - A death on the interval path leaves a dead producer (**T-152**).
  - `Town` keeps adding recruits. "Not tracked" holds for the player, not for the save.
- **Consequences:** **T-148 becomes the intended behaviour.** Sold pawns *should* leave the storyteller's population, so #170's OC-N2 is retired. **T-151 still binds:** a destroyed outpost must kill or otherwise dispose of the staff first.

#### OR-2 — frozen staff

- **Gets us:** OR-1 with a **build-time snapshot for free**. Prefixes returning `false` on `Outpost.SatisfyNeeds()` and `Outpost.SatisfyNeedsInterval(int)` stop every per-pawn tick VEF runs: needs, health, tending and aging.
  - Skills never change, so the yield stays fixed at what was sent.
  - Nobody dies, so neither *"Abandoned"* nor T-152 can fire.
  - Medicine is never drawn.
- **Cannot:** grow or decline with its people. `Town`'s recruitment and `Science`'s research still run, because they are production, not needs.
- **Also:** VOE `Outpost_Encampment.Tick` refills food and rest, tends, and calls `HealthTick` directly. It needs the same freeze, one more prefix [V].

#### OR-3 — consume, flat yield

- **Gets us:** the requirement read strictly. The pawns are sold inside the synced founding commit that §2c item 3 already has to write, and they cease to exist for the colony.
  - Vanilla supplies the sale [V]. `Pawn.PreTraded(TradeAction.PlayerSells, …)` records the *SoldPrisoner* tale, clears the faction, and calls `relations.Notify_PawnSold`, so relatives get vanilla's sold-family thoughts. If the pawn's home or host faction is foreign, it applies `GoodwillToMakeHostile` under *MemberSold*, which **makes that faction hostile**, not merely annoyed. `Tradeable_Pawn.ResolveTrade` records `HistoryEventDefOf.SoldSlave` for ideology precepts.
  - The yield becomes `BaseAmount`, an existing `ResultOption` field restatted by XML, as in §2a.
  - One patch keeps a zero-occupant outpost alive. `Tick`'s abandonment branch sits between `WorldObject.Tick` and `SatisfyNeeds`, so this is a transpiler or a reimplementing prefix, not a bare `return false`.
- **Cannot:** reward sending more or better people, which the requirement's *"return justifies the pawns"* clause leans on.
  - `Town`, `Science`, `Hunting`, `Farming`, `Mining` ores, `Drilling` and `Defensive` yield nothing or break at zero staff. Each is dropped or gets an override (§2a's content call, widened).
  - VEF's four occupant tabs show empty lists until removed.
- **Consequences:** T-148, T-151 and T-152 all vanish, because there are no occupants.

#### OR-4 — consume, stored snapshot

- **Gets us:** OR-3, plus a yield that scales with the people sold.
  - A scribed comp on `OutpostBase` records, at the sale, the count, the skill totals and the kinds. A kind weight is #170's OC-Y3.
  - Production reads the comp instead of `CapablePawns`.
- **Cannot:** use VEF's yield maths unchanged. `ResultOption.Amount` takes a `List<Pawn>` and has no reference to its outpost, and `CapablePawns` and `TotalSkill` are non-virtual. The snapshot therefore enters through prefixes on `ProducedThings` and `ProductionString`, and again on each class that overrides them (§2a's non-uniform seam) [V seams; the composition is I].
- **Weight:** Medium–Hard because of that fan-out. OR-2 buys the same fixed yield with two prefixes.

#### OR-5 — our own world object

- **Gets us:** an outpost with nothing to decouple. It is a plain `WorldObject`, like FT&V's `FactionTerritories_VassalOutpost`, which stores only defNames and a name [V, §3].
  - It holds a def, a yield record like OR-4's, a clock (§0 P3) and delivery copied from VEF's `Deliver`. Delivery never reads staff, but it is an instance method on `Outpost`, so it is copied, not called.
  - The founding sale is our own synced float-menu option or `[SyncMethod]`.
  - **Not a `MapParent`, so T-150 does not apply.** M-proxy and FT&V's overlay donor work against it as they already do against FT&V's object, which is #171's OU-A1 at its cheapest.
  - §2's B1–B5 never arise. T-148, T-149, T-151 and T-152 do not apply.
- **Cannot:** reuse VOE's or VFE Classical's content classes, VEF's tabs or VEF's delivery without copying them. It is §2's *Build B*, minus occupants, needs, health, packing and tabs. That is why it drops from "not recommended" to a live route.

#### Choosing, requiring or forbidding a pawn kind

- **Vanilla tells them apart** [V, #170]. `IsFreeNonSlaveColonist`, `IsSlaveOfColony` and `IsPrisonerOfColony` are all public on `Pawn` in 1.6.
- **Consumption moves the rule into the commit.**
  - VEF's founding commit adds **every** caravan pawn: prisoners, and **pack animals**, which a sale would then consume as well [V, `Dialog_CreateCamp.DoOutpostDisplay`].
  - It validates only `IsFreeColonist`, which in 1.6 includes slaves [V, `Utils.HumanColonists`].
  - §2c item 3 must replace that commit with our synced `FoundOutpost` anyway. Choosing the pawns, and requiring or forbidding a kind, is a filter inside it at negligible extra weight.
  - OR-1 removes the caravan Add gizmo and the pod option, so the commit becomes the **only** entry, and #170's OC-K2 postfix on `Utils.CanAddPawn` is no longer needed.
  - T-149 dissolves too, because the commit charges `CostToMake` explicitly rather than inside `AddPawn`'s last-humanlike branch.
- **Display:** VEF's founding tooltip (`RequirementsStringBase`) lists requirements. A kind rule needs a line there, or in our own dialog, for the player to see why a founding is refused.

#### What destruction does today [V]

- **VEF has two exits.**
  - At zero occupants `Tick` sends *"Abandoned"* and calls `Destroy()`.
  - `ConvertToCaravan`, at the end of packing, hands everyone and everything back.
- `PostRemove` calls `OutpostsMod.Notify_Removed`, which is empty. **`containedItems` is a plain `List<Thing>`, not a `ThingOwner`**, so a destroyed outpost's goods vanish with it, and its occupants are dropped (T-151).
- **No corpus mod leaves an outpost ruin** (*Available mechanisms*).
- **Our code does the destroying.** #171's attack routes (OU-A1 or OU-A2 lost, /forfeit or /roll) end in a call of ours, which must:
  1. take the goods out of `containedItems`;
  2. dispose of any occupants (OR-1 and OR-2: *they fell*, and VEF's own path already turns corpses into goods);
  3. destroy the outpost, or flag it (RU-1);
  4. place the ruin.

#### RU-1 — the outpost is its own ruin

- **Gets us:** the cheapest ruin on VEF.
  - A scribed flag on a `WorldObjectComp` added to `OutpostBase` by XML is the OU-D2 shape. The stall prefix it needs is the same patch.
  - The goods stay in `containedItems`.
  - A `Label`/`Material` postfix marks it ruined.
  - A ruined `Outpost` still blocks founding on its own and neighbouring tiles (`CanSpawnOnWithExt`), so nobody founds over it [V].
- **Rebuild:** a caravan float-menu option of ours, which is synced as a world-object option (§0 P5). It checks the caravan against `CostToMake` the way `CanSpawnOnWithExt` does, takes it, clears the flag, and resets `ticksTillProduction`.
- **Cannot:** loot through VEF's *Take items* dialog in multiplayer, which is B5. Loot is ours: a float-menu option or a synced dialog commit.
- **With OR-1:** the staff died with the outpost, so a rebuilt one has nobody to read. Rebuild then has to take pawns again, which is a requirement call (see *Open questions*).
- **With OR-2, OR-3 and OR-4:** the staff are frozen and survive with it, or the stored snapshot does. The outpost resumes as built.
- **Consequence:** T-150 stays, since it is still a `MapParent`.

#### RU-2 — our ruin object

- **Gets us:** a ruin that stands until rebuilt and says what it was.
  - A plain `WorldObject` with a `ThingOwner` of the surviving goods, the remembered outpost def and name, and OR-4/OR-5's snapshot if one exists.
  - *Loot* and *Rebuild* are options on its caravan float menu. Multiplayer patches every `WorldObject.GetFloatMenuOptions(Caravan)` override through `SyncWorldObjCaravanMenus` [V, `Multiplayer.dll`], so both are synced.
  - *Loot* moves the goods into the caravan with no map.
  - *Rebuild* takes the cost in P4's `TradeRequestComp` shape (Multiplayer registers vanilla's `TradeRequestComp.Fulfill` as a sync method [V]; ours needs its own) and spawns a fresh outpost of the remembered def.
  - The inspect string is ours: type, date destroyed, what survives, and what rebuilding costs. This is the ruin's player-facing surface, shared with #178.
- **Cannot:** give the player a map to fight across. Pair it with RU-3 if the loot should be contested.
- **Consequence:** it is not a `MapParent`, so T-150 does not apply to the ruin.

#### RU-3 — loot site

- **Gets us:** a real map visit with vanilla parts.
  - `SiteMaker.MakeSite` with vanilla's `ItemStash` part.
  - The outpost's goods go into `SitePart.things`, scribed `Deep`. `GenStep_ItemStash` spawns exactly `parms.sitePart.things` as the stockpile [V].
  - `SitePartWorker_ItemStash` fills `things` only from QuestGen, so outside a quest the goods are ours to place [V].
  - A threat part can be added for scavengers.
  - Odyssey's `AbandonedSettlement` part (`GenStep_Settlement`, `generatePawns=false`) generates a walkable ruined settlement instead. It is Odyssey-only and **dead content today**: its only user, `Gravcore_AbandonedSettlement`, is commented out of `Script_GravShip.xml` [V].
- **The site leaves its own marker.** Vanilla `SitePartDef.leaveAbandonedSettlement` makes `SitePartWorker.PostDestroy` spawn a player-faction `AbandonedSettlement` on the tile when the site goes, on the surface layer only. Odyssey's `GravcoreLocationBase` sets it [V]. RU-3 + RU-4 is therefore **one XML flag** on our site part, and the marker is the rebuild anchor.
- **Cannot:** stay a loot site. `Site.ShouldRemoveMapNow` removes the site as soon as its map is left with no pawn, building or live threat blocking it, **whether or not the goods were taken** [V]. What stands afterwards is the lootless marker, anchoring RU-4's or RU-5's rebuild.
- **Order matters (T-150):** the outpost must be gone before the site is added, or `MapParentAt` finds the outpost first.

#### RU-4 — vanilla marker

- **Gets us:** vanilla `AbandonedSettlement`, a plain `WorldObject` (`canHaveMap` false). Its inspect string shows *"Abandoned: date (time ago)"* for the player's faction [V]. It costs one spawn call, or no code at all when RU-3's `leaveAbandonedSettlement` spawns it.
- **Cannot:** hold loot or offer anything. Nothing in vanilla removes it [I]. It works only as RU-3's or RU-5's anchor.

#### RU-5 — re-found in place

- **Gets us:** VEF's founding flow already works on the ruin's tile. `CanSpawnOnWithExt` rejects only a tile at or beside a settlement, or beside an `Outpost` [V]. *Paying the build cost again* is founding again: `CostToMake` plus pawns.
- **Cannot:** remember the type, name or snapshot, or waive the pawns.

#### How *rebuild* reaches the player

Every channel below is a synced commit:
- **At the ruin, by caravan:** a world-object float-menu option (RU-1, RU-2) or VEF's founding gizmo (RU-5, B1).
- **From home, by pods:** a `TransportersArrivalAction` of ours in the shape of VEF's `TransportPodsArrivalAction_AddToOutpost`. Pod launch is synced [V, #171].
- **As an offer:** #171's OU-N2 quest, *"rebuild for N"*, through `QuestPart_Choice`.

#### Recommendation (not a selection)

- **OR-2 + RU-1 is the cheapest faithful build on VEF.**
  - The shipped yield formulas are untouched and reward who was sent.
  - The staff are gone to the player and can never die, desert or come home.
  - The ruin is the same object.
  - It adds about four patches to §2's harness, and it deletes most of B5's sync surface.
- **OR-5 + RU-2 is the clean alternative.** It drops §2's harness entirely and makes #171's overlay attack (OU-A1) work with FT&V's donor. It costs VOE's content classes and a copied delivery layer.
- **OR-3 fits only if yields are flat by design.**
- **RU-3 is worth adding to either** if looting a ruin should be a fight. With `leaveAbandonedSettlement` it is also a complete ruin → marker → re-found loop, from vanilla parts.

### Constraints

- **Production reads the staff, and zero staff destroys the outpost** [V] (*What production reads today*). Any route that empties `occupants` must patch `Tick`'s abandonment and restat or override the yield.
- **`containedItems` is not a `ThingOwner`** [V]. A bare `Destroy()` loses the goods as well as the pawns (T-151). The ruin's loot exists only if our destroy moves it first.
- **T-148 inverts under this premise.** Leaving the storyteller's population is what a sale means, so #170's OC-N2 must **not** be built. The trap's mechanism stays true.
- **T-150 binds every VEF route and RU-1**, because `Outpost` is a `MapParent`. OR-5 and RU-2 are free of it.
- **T-152 binds OR-1 only.** OR-2 freezes health, and OR-3, OR-4 and OR-5 have no occupants.
- **The player's decisions must be synced commits** (#171 Constraints): the founding sale, *Loot* and *Rebuild*. VEF's gizmos and dialogs are not synced (B5). Deleting them is the cheapest sync.
- **No capture, no rescue** (#175). #171's *Loss* options *evacuate* and *capture* are out; only *they fell* remains, and only for OR-1 and OR-2.

### Available mechanisms

| Mechanism | What it provides | Evidence |
|---|---|---|
| `Outposts.Outpost.Tick` / `TickInterval` / `ProducedThings` / `Produce` / `CapablePawns` / `TotalSkill` / `IsCapable` | Abandonment at zero; production clock; yield from occupants | [V] `2023507013/1.6/Assemblies/Outposts.dll` (identical SHA-1 under `common/RimWorld/Mods`, T-22) |
| `Outposts.ResultOption.Amount` / `AmountBySkill.Amount` | `BaseAmount` + per-pawn + per-skill | [V] same |
| `Outposts.Outpost.SatisfyNeeds()` / `SatisfyNeedsInterval(int)` | Every per-occupant tick: needs, health, tending, aging | [V] same |
| `Outposts.Outpost.GetGizmos` / `GetCaravanGizmos` / `GetTransportersFloatMenuOptions` | Remove, Pack, Stop-pack, Add, Take, Give, pod add | [V] same |
| `Outposts.Dialog_CreateCamp.DoOutpostDisplay`, `Utils.HumanColonists` / `CanSpawnOnWithExt` | Founding commits every caravan pawn; tile rules | [V] same |
| VOE `Outpost_*` (10), VFE Classical `VFEC.Outposts.*` (3) | Staff-reading yields; Drilling's integer division; Encampment's own need tick | [V] `2688941031/1.6/Assemblies/VOE.dll`, `2787850474/1.6/Assemblies/VFEC.dll`. VOE's `1.6/Factory` folder is commented out of `loadFolders.xml` and never loads |
| `Verse.Pawn.PreTraded`, `RimWorld.Tradeable_Pawn.ResolveTrade` | The sale's tale, relations thoughts, goodwill and `SoldSlave` event | [V] 1.6 `Assembly-CSharp.dll` |
| `RimWorld.Planet.SitePart.things`, `GenStep_ItemStash`, `SitePartWorker_ItemStash`, `SiteMaker.MakeSite`, `Site.ShouldRemoveMapNow` | Loot site from our goods; removed once its map is left unblocked, looted or not | [V] same; `Data/Core/Defs/Sites/Parts/ItemStash.xml` |
| Odyssey `SitePartDef AbandonedSettlement`, `WorldObjectDef ClaimableSite` | Ruined-settlement layout site; dead content (its quest is commented out of `Script_GravShip.xml`) | [V] `Data/Odyssey/Defs/Sites/GravcoreLocations.xml` |
| `SitePartDef.leaveAbandonedSettlement` → `SitePartWorker.PostDestroy` | A player-faction `AbandonedSettlement` is left when the site goes (surface only) | [V] 1.6 `Assembly-CSharp.dll`; `GravcoreLocationBase` |
| `RimWorld.Planet.AbandonedSettlement`, `DestroyedSettlement` | Dated marker; post-defeat map holder that removes itself with its map | [V] 1.6 `Assembly-CSharp.dll`, `Data/Core/Defs/WorldObjectDefs/WorldObjects.xml` |
| Multiplayer `SyncWorldObjCaravanMenus`, `SyncMethod.Register(typeof(TradeRequestComp), "Fulfill")` | Synced world-object caravan menus; synced trade-request fulfil | [V] `2606448745/1.6/AssembliesCustom/Multiplayer.dll` |
| MP Compat `VanillaOutpostsExpanded` | `Outpost_Artillery.Fire` + one `Outpost_Defensive` lambda; no VEF Outposts class | [V] `1629973374/1.6/Assemblies/Multiplayer_Compat.dll` |

**`DestroyedSettlement` is not a map-less ruin** [V]. It is a `MapParent` created by `SettlementDefeatUtility.CheckDefeated` to adopt a live map. Its `ShouldRemoveMapNow` removes the world object along with the map. VFE Medieval 2's merchant-guild camp and Better Traders Guild use it the same way.

**Wide pass.**
- **Outposts:** both roots, `*.dll`, `-i`, ASCII `outpost` and null-interleaved UTF-16 `o\x00u\x00t\x00p\x00o\x00s\x00t\x00` typed literally, excluding `obj/` and `Referenced/`, piped to `corpus.py --which`. Both halves return the same ten mods as #170 (Better Architect Menu in UTF-16 only; [SR]Factional War in ASCII only). Validated: VEF and VOE hit. No player-founded, pawn-consuming carrier other than `Outposts.dll`.
- **Yield without staff:** ASCII `tithe` and `vassal` return VFE Empire, Worksites Expanded, Rim War, FT&V and RimPacts. Their no-staff yields are §3's and P1's holdings machinery, not outposts. FT&V's object is OR-5's donor.
- **Ruins:** `-i "passiveincome|ruinedoutpost|destroyedoutpost|outpostruin|ruinsite"`, same form, returns **0**. The validator is the same sweep plus `destroyedsettlement`, which returns five mods (FT&V, RimPacts, VFE Medieval 2, VFE Security, Better Traders Guild). Every 1.6 hit that was read handles a *defeated settlement's* map. **No mod ships an outpost ruin or a rebuild.**

### Status

READ, via [#179](https://github.com/cjd721/Rimworld-Archinity/issues/179), building on #81, #170, #171 and #175. The mechanisms are [V] against the 1.6 assemblies and defs cited. Every route is [I] by construction: the seams are read, the compositions are unbuilt.

### Open questions

- **Requirement — Conrad, via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2):**
  - does *rebuild* cost pawns again, or only materials and silver? Under OR-1 the staff died with the outpost, so a pawn-free rebuild needs OR-2, OR-3, OR-4 or OR-5.
  - does *"not tracked"* allow the pawns to persist unseen in the save (OR-1, OR-2), or must they cease to exist (OR-3 to OR-5)?
  - may pack animals be consumed with a caravan, or does the commit exclude them?
- **Story call (Conrad):** whether the sale carries vanilla's consequences: sold-family thoughts, *MemberSold* turning a foreign prisoner's faction hostile, and the `SoldSlave` precept event.
- **Build (next map):**
  - where OR-3's abandonment patch sits (a transpiler, or a prefix reimplementing `Tick`);
  - what OR-4's snapshot records;
  - whether RU-1's loot is a float-menu option or a synced dialog.
- **Balance (#119):** `BaseAmount` values under OR-3; whether a ruin's goods are all, part or a roll of `containedItems`; the rebuild price.
- **Content (#119 / #14):** under OR-3, the VOE and VFE Classical classes that yield nothing at zero staff (`Town`, `Science`, `Hunting`, `Farming`, `Mining` ores, `Drilling`, `Defensive`) are dropped or overridden.
- **Shared surface with [#178](https://github.com/cjd721/Rimworld-Archinity/issues/178):** a ruin is read through its world-object inspect string and float menu. RU-2 owns both; RU-1 patches VEF's; RU-3 gets vanilla's site description.

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
in-absentia outcome in this document that rolls uses it**; /forfeit resolves with no roll (§ *How a
holding ends*).

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
| Class | a bare `WorldObject` overlaying an existing `Settlement` | a `MapParent` with no `mapGenerator` and no map |
| Why | the settlement underneath already generates the map, so no site map generation is involved | it holds its colonists off-map in `occupants`. If a map is ever forced on its tile it adopts it (`Encounter` fallback) and never removes it (**T-150**) |
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
| `Outposts.Outpost : MapParent, IRenameable` | `occupants` (`List<Pawn>`), `containedItems`, `ticksTillProduction`, `ticksTillPacked`, `costPaid`, `deliveryMap`, `raidFaction`/`raidPoints` (`raidFaction`/`raidPoints` are scribed and read nowhere — vestigial, #171). |
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

1. **One prefix on `OutpostsMod.Setup(Outpost)` returning `false` unconditionally.**
   Closes **B2 and B3 together** and is the highest-value line in the build: with `Setup` never
   running, every `[PostToSetings]` field — `MinPawns`, `Range`, `TicksPerProduction`, `TicksToPack`
   and the per-subclass multipliers — keeps its XML value in single-player and multiplayer alike,
   and the shared `DefModExtension` is never written. Gating on `MP.IsInMultiplayer` would leave the
   staffing limiter (#170) and the yield clock editable by the player in the mode the campaign is
   playtested in.
2. **Two prefixes forcing `Settings.ProductionMultiplier` and `Settings.TimeMultiplier` to `1f`**,
   unconditionally. Closes the part of **B4** that `Setup` does not reach.
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

### 3. Vassals — every shape, by route

#### Purpose and scope

**What this section answers:** whether the colony can hold vassals, and by which routes. It covers
every shape named on
[Vassals — can we, and by which routes](https://github.com/cjd721/Rimworld-Archinity/issues/120).
None of the shapes is selected.

1. **A settlement vassal by conquest** — now called a **holding**
   ([`requirements/TERRITORY.md`](../requirements/TERRITORY.md)). Break a `Settlement`, pay to
   rebuild it, and it then yields. A cooldown applies; **the cap of three does not** — #35
   replaced it with a rebuild cost that scales with the settlement's tech tier. This is
   [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8) session 2's shape, amended.
2. **A friendly faction that submits at high Reverence**
   ([`requirements/RELIGION.md`](../requirements/RELIGION.md) § *Reverence*).
3. **A whole faction as a vassal,** after the player conquers or liberates all of it, or after a
   [revolt](../requirements/RELIGION.md#revolt).
4. **Payouts from a friendly faction that is not a vassal:** the Schism's successor, a permanent
   ally ([`requirements/RELIGION.md`](../requirements/RELIGION.md) § *The Schism Path*).

**What this section does not own:**
- **What a vassal must be and owe:**
  [Vassalage and the tithe catalogue](https://github.com/cjd721/Rimworld-Archinity/issues/35).
- **What a successful revolt makes of a faction:**
  [#131](https://github.com/cjd721/Rimworld-Archinity/issues/131).
- **Faith changes:** [#133](https://github.com/cjd721/Rimworld-Archinity/issues/133).
- **Keeping founders out of transfers:** [#134](https://github.com/cjd721/Rimworld-Archinity/issues/134).
- **Pinning the successor's alliance:** [#130](https://github.com/cjd721/Rimworld-Archinity/issues/130).

**Boundary with §2.** An outpost uses up colonists: its yield formula is its occupants. A vassal uses
none. Both can share §0's pattern.

#### Verdict

- **Possible?** **Yes, for all four shapes, but nothing on disk delivers any of them as it ships.**
  Shape 1 is a build with a complete donor to copy. Shapes 2 to 4 are one build: a per-faction record
  plus a payout clock. **XML alone gets none of the four.**
- **Multiplayer?** **With work.** Every action the player takes goes through a synced command
  (**T-80**, **T-82**, **T-95**, **T-96**), and every clock runs on the world tick (§0 P1/P3). The one
  shipped system that is already synced, VFE Empire's vassals through MP Compat, serves none of the
  shapes and has one unverified ordering hazard (RUN, under *Open questions*).

#### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **R0** VFE Empire's tithe catalogue, restatted | Church settlements within 100 tiles pay tithe to a colonist holding an Empire title. None of the four shapes | VFE Empire + MP Compat | XML | Easy | Yes, one [I] hazard |
| **R1** Settlement vassal as a player-held world object | Shape 1: a conquered `Settlement` becomes ours. It yields once the rebuild is paid, and remembers its parent faction | ours; donor Faction Territories, catalogue shape from VFE Empire | C# + XML defs | Medium (Hard with a vassal shop) | With work |
| **R2** Settlement vassal as a marked NPC settlement | Shape 1, with the vassal still part of its faction. The only route where part of a faction can be a vassal | ours; donors VFE Empire `TitheInfo`, Faction Territories cede path | C# + XML patch | Medium | With work |
| **R3** VFE Empire's vassals widened by patch | Any settlement in reach becomes a vassal of a Church-titled colonist, using VFE Empire's UI and sync. **Not recommended** | VFE Empire + MP Compat + our patches | patch C# | Medium | Yes, one [I] hazard |
| **R4** Faction-level vassal record | Shapes 2, 3 and 4 through one record and one payout clock | ours; donors RimPacts' tribute treaty, VFE Empire `TitheWorker` | C# + XML defs | Medium | With work |
| **R5** Vanilla ally machinery | Shape 4 in part: gifts from visitors, traders, and allies sending help when raided | vanilla | XML | Easy | Yes |
| **R6** RimPacts as shipped | Shapes 2 and 3 as military tributaries. **Not recommended**: no sync, settings inside `Rand` paths, creates factions at runtime | RimPacts | as shipped | Hard | No |
| **R7** Faction Territories as shipped | Shape 1 as that mod designed it. **Not recommended**: declined on #8, and its prompt, pause and purchase door all fail under Multiplayer | Faction Territories | as shipped | Hard | No |

| Carries shape → | 1 conquest | 2 submission | 3 whole faction | 4 ally payouts |
|---|---|---|---|---|
| R0 | — | — | — | — |
| R1 | **yes** | — | only settlement by settlement | — |
| R2 | **yes** | as a set of its settlements | as all its settlements | — |
| R3 | no conquest gate | — | — | — |
| R4 | — | **yes** | **yes** | **yes** |
| R5 | — | — | — | partial |
| R6 | — | military gate | yes | — |
| R7 | yes (declined) | — | — | — |

##### R0: VFE Empire's tithe catalogue, restatted

**Gets us [V]:**
- Seven `TitheTypeDef`s: steel 25, wood 40, gold 5, silver 50, meals 2, honor (5, every 5 days), and
  `VFEE_Slavery`, which gives 1 slave every 10 days and needs Ideology.
- XML reaches each def's `item`, `count`, `deliveryDays`, `workerClass` and labels, and
  `vassalagePointsAwarded` on the Empire title rungs (seven award 1, one awards 0).
- `TitheWorker_Slaves` generates a new `PawnKindDefOf.Slave` pawn as the player's slave. It never
  takes a colonist.

**Cannot [V]:**
- **Choose who can be a vassal.** `WorldComponent_Vassals.AllPossibleVassals` filters on
  `Faction == Faction.OfEmpire`.
- **Choose what a settlement pays.** `GetTitheInfo` draws a random `TitheTypeDef` and speed (0.5× to
  2.5×).
- **Open vassalage without a title.** `RoyaltyTabWorker_Vassals.DoMainSection` requires
  `VassalagePointsAvailable(Faction.OfEmpire) >= 1` and 100-tile reach from a player home or a held
  vassal.
- **End a vassalage.** Outside debug, only the tab's *Release all* button calls
  `ReleaseAllVassalsOf`.
- **Deliver anywhere but the lord.** `TitheWorker.DeliverInt` delivers only into the lord's caravan
  or by drop pod beside the lord on a player home map.

**Consequences:**
- **It is a Church perk.** If VFE Empire ships, it is live content on the Church path regardless of
  this section [I].
- **MP Compat's `Multiplayer.Compat.VanillaFactionsEmpire` syncs it** [V]: vassalising, the
  `DoVassal` settings, release, and a `GetTitheInfo` seed of `Gen.HashCombineInt(settlement.ID, tile)`.
- **Ordering hazard** [I]. `DoDay` walks a dictionary filled in the order each client first draws the
  tab, and each delivery draws `Rand`.

##### R1: Settlement vassal as a player-held world object

**Mechanisms [V]:**
- `SettlementDefeatUtility.CheckDefeated(Settlement)` swaps the settlement for a
  `DestroyedSettlement` of the same faction, destroys it, and sets `Faction.defeated = true` if it
  was the faction's last base.
- Faction Territories prefixes that method (`InterceptBaseDestroyedLetterPatch`).
- `VassaliseUtility.ExecuteVassalisationAtTile` replaces the ruin with a
  `FactionTerritories_VassalOutpost : WorldObject` owned by the player, keeping the original faction,
  name and def.
- `VassalagePointsComponent` accrues a per-original-faction ledger once a day.
- A build-cost check against the caravan exists in VEF's `Outposts.Utils.CanSpawnOnWithExt`
  (`CostToMake`), per §2.

**Levers:**
- `Settlement`-only by construction [V].
- Pay then yield; cap and cooldown are counts plus a tick stamp, with no roll [I].
- A catalogue we assign, including people on a clock in the manner of `TitheWorker_Slaves` [I].
- A goodwill hit on the parent, subject to `Faction.CanChangeGoodwillFor` [V].
- Consequences can point at the remembered parent [V].

**Cannot:**
- **Keep the place in its faction.** It leaves; the object is a plain `WorldObject` with no people,
  trader or map [V].
- **Make part of a faction a vassal.**
- **Raise raid weight through XML.** Raid-faction selection weighs only `RaidCommonalityFromPoints`
  and a last-raider penalty ([`engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md)
  § *Raid faction selection*) [V], so this needs a patch.

**Consequences:**
- **A faction's last base still marks the faction defeated** unless we intercept before the write
  [V for where it is written].
- **Copy the vassalise half of Faction Territories; copy the invasion object only behind an
  authored trigger, never its scheduler, and re-cast its sides** (see § *How a holding ends*).
  What #8 session 2 excluded is the scheduler (#172).
- **Create the object inside a synced command** (T-80), and never offer the choice as a modded
  `ChoiceLetter` (T-96).

##### R2: Settlement vassal as a marked NPC settlement

**Mechanisms [V]:**
- The vassal stays a `Settlement` of its faction, with a `WorldObjectComp` patched onto
  `WorldObjectDef Settlement`. The comp backfills into existing saves
  ([`engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md) § *A `WorldObjectComp`
  added by XML patch backfills into an existing save*).
- VFE Empire's `TitheInfo` is the precedent for marking a settlement rather than replacing it.
- Conquest destroys the settlement. Faction Territories' `ExecuteCedeToFactionAtTile` (uncalled in
  FT&V; a precedent for the write, not a live path) shows the recreation: a new `WorldObjectDefOf.Settlement`, `SetFaction` (a bare field write), and the old
  name.

**Levers:**
- The vassal keeps its people, trader, map and faction faith [I].
- Part of a faction can be a vassal with no new faction, which is load-bearing for #131.
- Payouts work as in R1.

**Cannot:**
- **Escape its parent's relation.** `FactionUtility.CanTradeWith` rejects hostility
  ([`RELIGION.md`](RELIGION.md) § *Exaltation — the donor is vanilla Royalty's own Empire*) [V].
- **Resolve a hostile parent owning a vassal** without a rule from requirements [I].

**Consequences:**
- **The recreated settlement generates its map afresh on its next visit, as every NPC settlement
  does** — vanilla discards a settlement's map once the players leave and blocks re-entry for a day
  (#164). The garrison returns at full strength [V]. The tile seed rebuilds the same layout [I] —
  not under **T-33** (a KCSG `chooseFromSettlements` faction without MP Compat), and not if the
  faction's def has climbed since.
- **`defeated` must be cleared** if the recreated settlement was the faction's last base. It is a
  plain public field [V].

##### R3: VFE Empire's vassals widened by patch

**What it would take [V]:**
- A postfix on `AllPossibleVassals`.
- Replacing the Empire checks in `RoyaltyTabWorker_Vassals.DoMainSection` and
  `HonorWorker_Vassal.SettlementValid`.
- MP Compat's sync keys on `Settlement` / `TitheInfo`, so it should follow [I].

**Cannot [V]:** no conquest, cost or cooldown at entry; nothing ends a vassalage when its settlement
falls; vassals held only by a titled lord; delivery only where that lord is.

**Consequences:** vassalage becomes a Church-title privilege, which sits badly with the Schism and
Independent paths [I]. **Not recommended.**

##### R4: Faction-level vassal record

**Mechanisms [V]:**
- `FactionRelationKind` is `Hostile`, `Neutral`, `Ally` only.
- `Faction` has no comps, so per-faction state is a `WorldComponent` list keyed by `Faction`
  ([`RELIGION.md`](RELIGION.md) § *The build — Reverence* §1).
- **Entry surfaces:**
  - a gated diplomacy option ([`POLITICS.md`](POLITICS.md) § *Standing as a content gate* §3);
  - a quest from the vassal, which needs a node of ours, because
    `QuestNode_GetFaction.IsGoodFaction` filters on relation, hidden, permanent-enemy and exclude,
    never on def or on a record.
- **Lifecycle donor: RimPacts' `TreatyWorker_Tribute`.**
  - `WouldAccept` weighs a power ratio and `Submission`.
  - `OnSigned` enforces non-aggression.
  - `OnQuarter` pays, or rolls a revolt that breaks the treaty.
  - `OnBroken` handles release: +10 goodwill and a 1,800,000-tick cooldown.
- **Delivery donors:** `WorldComponent_RimPacts.DeliverTributeQuarter` (silver or settlement
  specialties at `Find.AnyPlayerHomeMap`'s trade drop spot) and VFE Empire's
  `TitheWorker.DeliverInt`.
- **Perks vanilla gives an Ally:**
  - `IncidentWorker_RaidFriendly.FactionCanBeGroupSource` requires `PlayerRelationKind == Ally`;
  - `StorytellerComp_FactionInteraction` scales by `AllyIncidentFraction`;
  - `VisitorGiftForPlayerUtility.ChanceToLeaveGift` scales on goodwill.

**Levers:**
- Submission, whole-faction vassalage and the successor's payouts are one record with different
  entry acts and a kind [I].
- A vassal kept at Ally gets vanilla aid, visitors and gifts [I].
- A vassal can throw off its overlord, on RimPacts' model [V].

**Cannot:**
- **Make part of a faction a vassal.** That needs R2.
- **Create a faction** (**T-07**).
- **Hold the relation still, by itself.** [`RELIGION.md`](RELIGION.md) § *The Schism* H1–H3
  carry it (#130, #168).

**Consequences:**
- **Whole-faction conquest collides with `defeated`.** `CheckDefeated` writes it on the last base,
  and a defeated faction fails `CanChangeGoodwillFor` [V]. Intercept before the write, or define
  conquest as every settlement except those held [I].
- **Multiplayer:** T-82 / T-95 / T-96 on the entry dialogs, and §0 P4 for any revolt-out roll.

##### R5: Vanilla ally machinery

**Gets us [V]:**
- `StorytellerCompProperties_FactionInteraction` (`incident`, `baseIncidentsPerYear`,
  `minSpacingDays`, `fullAlliesOnly`, `minWealth`) schedules trader and visitor incidents weighted
  toward allies.
- Visitors leave gifts at a base 25%, scaled by goodwill and wealth curves.
- Allies send help when the colony is raided.

**Cannot [V]:** address a named faction, because `MakeIntervalIncidents` passes none — on the
storyteller path. A direct `RaidFriendly.TryExecute` with `parms.faction` set sends that faction
(#168), and `RaidEnemy` does the same, even for a defeated faction (#172). Nor can it pay on a
schedule.

**Consequences:** free background under any choice. It touches the storyteller that
[#60](https://github.com/cjd721/Rimworld-Archinity/issues/60) owns.

##### R6 and R7: shipped carriers, not recommended

**R6, RimPacts.**
- **Gets us:** `Rpt_Treaty_Tribute`, the only shipped faction-level vassalage in the corpus [V].
- **Its gate is military** (`WouldAccept`) [V].
- **No Multiplayer sync.** `RimPacts.dll` has no Multiplayer reference in either encoding and no MP
  Compat coverage [V].
- **Rolls behind settings.** `OnQuarter` rolls `Rand.Chance` in a component gating `Rand` behind 57
  settings (**T-18**).
- **Creates factions mid-game.** `CreatePuppet` calls `FactionGenerator.CreateFactionAndAddToManager`
  (**T-07** / **T-15**) [V].
- **Verdict:** a donor for R4.

**R7, Faction Territories.** Declined as a dependency on #8 session 2
([`data/MOD-VERDICTS.md`](../data/MOD-VERDICTS.md) § *Declined*). Beyond the decline, all [V]:
- a `MapDeiniter.Deinit` postfix opens a modded `ChoiceLetter_VassaliseDestroyedSettlement` (T-96)
  and calls `Find.TickManager.Pause()`;
- points come from `ModSettings` (T-18);
- `TryPurchaseVassalisation` keeps the goodwill-purchase door #8 removed;
- MP Compat covers none of it.

##### Coexistence

**Yes** [I]:
- **R1 or R2 with R4.** They key on a world object and on a faction respectively, so they never
  collide, and one delivery path can serve both.
- **The only overlap is one rule:** a settlement vassal whose parent later becomes a vassal
  faction. § *A sworn faction owes services* → *A holding whose parent faction later swears itself*
  answers it at route depth; the choice among its outcomes is Conrad's.
- **R1 and R2 answer the same question two ways** (does a conquered settlement leave its faction?),
  so they coexist only as two different actions.
- **R0 coexists by accident** if VFE Empire ships.

##### What each route implies for the sibling tickets

- **Revolt ([#131](https://github.com/cjd721/Rimworld-Archinity/issues/131)).**
  - R4: success writes one record and moves no world objects; it cannot hand over part of a faction.
  - R2: success marks some of the faction's settlements, or `SetFaction`s them to an existing faction
    first.
  - R1: success turns settlements into player-held objects. Code replacement does not run
    `CheckDefeated`, so `defeated` is not written [I].
  - R0 and R3 cannot install a vassal after a revolt [V].
- **Faith ([#133](https://github.com/cjd721/Rimworld-Archinity/issues/133)).** Faith lives on
  `Faction.ideos` ([`engine/factions-and-worldgen.md`](../engine/factions-and-worldgen.md)).
  - Under R2 and R4, the vassal's people hold the faction's faith, so a vassal's faith change is
    #133's faction-level change [I].
  - Under R1, the vassal object has no population to hold one [I].
- **Founders ([#134](https://github.com/cjd721/Rimworld-Archinity/issues/134)).** No payout route
  takes colonists; `TitheWorker_Slaves` generates pawns [V]. Only a rebuild cost paid in pawns, or a
  revolt contribution, could reach a founder.

##### Recommendation (not a selection)

- **If only shape 1 exists:** R1. It is closest to #8 session 2's settled rules and has a donor read
  end to end.
- **R2 instead** if a conquered vassal should stay part of its faction, and it is the only route that
  lets a revolt hand over part of a faction.
- **For shapes 2 to 4:** R4, since one record and one clock cover all three.
- **R5 underneath any choice.**
- **R0 and R3 are the Church's perk, not our vassals.**

#### Constraints

- **No vassal relation exists in the engine.** `FactionRelationKind` has three values [V]. Every
  route stores vassalage itself.
- **A faction cannot be created after worldgen (T-07).** No shape may need one, and R6's puppets break
  this.
- **Conquering a faction's last settlement sets `Faction.defeated`** in
  `SettlementDefeatUtility.CheckDefeated`, and a defeated faction fails `CanChangeGoodwillFor` [V].
  Shape 3 by conquest must plan for it.
- **Every player act is a synced command.**
  - A caravan gizmo or a dialog is not synced (**T-80**).
  - Diplomacy options sync by index (**T-82**).
  - Subclassed node-tree dialogs lose sync (**T-95**).
  - Modded choice letters are unsynced (**T-96**).
  - World objects created from UI get client-local IDs (§ *Persistence and multiplayer*).
- **Clocks go on `WorldObject.Tick` / `WorldComponentTick`,** gated by `IsHashIntervalTick` (§0 P1,
  P3). Never override `UpdateRateTicks` (**T-81**).
- **No per-faction raid weight is reachable from XML** [V, § *Raid faction selection*].
- **Settings may not steer yields or rolls (T-18).** This rules out R6 and R7 as shipped.

#### Available mechanisms

| Mechanism | What it is | Used by | Evidence |
|---|---|---|---|
| `SettlementDefeatUtility.CheckDefeated` | Settlement → `DestroyedSettlement`; `defeated` on the last base | R1, R2, R4 | [V] `Assembly-CSharp.dll` |
| `Faction.CanChangeGoodwillFor` | fails for `defeated` factions | R4 | [V] `Assembly-CSharp.dll` |
| `FactionRelationKind` | `Hostile`, `Neutral`, `Ally` | all | [V] |
| `IncidentWorker_RaidFriendly.FactionCanBeGroupSource` | Ally only | R4, R5 | [V] |
| `StorytellerComp_FactionInteraction` + props | scheduled faction incidents; the worker picks the faction | R5 | [V] |
| `VisitorGiftForPlayerUtility` | 25% base gift chance × goodwill and wealth curves | R5 | [V] |
| `QuestNode_GetFaction.IsGoodFaction` | no def or record filter | R4 | [V] |
| VFE Empire `WorldComponent_Vassals`, `TitheInfo`, `TitheTypeDef`, `TitheWorker`, `TitheWorker_Slaves`, `VassalUtility`, `RoyaltyTabWorker_Vassals` | per-settlement tithe to a titled lord; Empire-only; random catalogue; release only by button | R0, R3; donor R1, R2, R4 | [V] `294100/2938820380/1.6/Assemblies/VFEEmpire.dll`, `1.6/Defs/Misc/TitheTypeDefs.xml` |
| MP Compat `Multiplayer.Compat.VanillaFactionsEmpire` | syncs vassalise, settings, release; seeds `GetTitheInfo` | R0, R3 | [V] `294100/1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll` |
| Faction Territories `VassaliseUtility`, `FactionTerritories_VassalOutpost`, `VassalagePointsComponent`, `InterceptBaseDestroyedLetterPatch`, `ShowVassalisePromptOnMapRemovedPatch` | conquest → player-held vassal object; points ledger; cede path | R7; donor R1, R2 | [V] `294100/3626725895/Assemblies/FactionTerritories.dll` |
| RimPacts `TreatyWorker_Tribute`, `WorldComponent_RimPacts.DeliverTributeQuarter` / `Submission` / `CreatePuppet` | faction-level tributary lifecycle; runtime faction creation | R6; donor R4 | [V] `294100/3762723122/Assemblies/RimPacts.dll` |
| VEF `Outposts.Outpost.Tick`, `Outposts.Utils.CanSpawnOnWithExt` | empty outpost destroyed; settlement-adjacent tiles rejected | ruled out as carrier; §2 | [V] `294100/2023507013/1.6/Assemblies/Outposts.dll` |

**Read and cleared, all [V]:**
- **Rim War.** `WorldUtility.IsVassalFaction` is a `"PColony"` defName check, and Rim War is barred.
- **Worksites Expanded.** `ApplyTributeReward` / `ApplyRoyalTitheReward` are one-off parley rewards.
- **VFE Classical.** `Tributum` is a senate perk.
- **Royalty's tribute collector** points the other way, from the colony to the Empire
  ([`CURRENCIES.md`](CURRENCIES.md)).

#### Status

**Evidence class: READ**, established on [#120](https://github.com/cjd721/Rimworld-Archinity/issues/120).
- **Every mechanism in the table is [V].**
- **Every route is [I] by construction.**
- **The corpus negative** ("no shipped carrier for shapes 1–4 that runs under Multiplayer") rests on
  sweeps across both roots in ASCII and hand-typed null-interleaved UTF-16, each validated against a
  known hit in the same heap. They narrowed to VFE Empire, Faction Territories, RimPacts, Rim War,
  Worksites Expanded and VFE Classical, and all six were depth-read.

**Premises corrected:**
1. **VFE Empire's vassals are not "unsynced."** MP Compat syncs them.
2. **Their only removal is a UI button,** not a lord losing standing.
3. **The catalogue has seven defs, including slaves,** and is assigned at random.
4. **XML alone yields no vassal.**
5. **RimPacts is a faction-level donor.**
6. **This section's earlier boundary described Faction Territories' design,** invasions included, as
   what a vassal is.

#### Open questions

- **Requirements — answered by [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35),
  now closed, in [`requirements/TERRITORY.md`](../requirements/TERRITORY.md).** It states the two
  kinds (a **holding** taken, a **sworn faction** given) and hands the rest onward:
  - does a conquered vassal leave its faction or stay in it (R1 against R2) — **answered: it
    becomes the colony's, and "ours means owed, not operated" is the requirement**;
  - what happens to a settlement vassal whose parent faction becomes a sworn faction — answered
    at route depth in § *A sworn faction owes services* → *A holding whose parent faction later
    swears itself* ([#168](https://github.com/cjd721/Rimworld-Archinity/issues/168)); choosing among
    stays, folds or returns is Conrad's, via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2);
  - how vassalage ends → [#172](https://github.com/cjd721/Rimworld-Archinity/issues/172);
  - where tribute arrives → [#166](https://github.com/cjd721/Rimworld-Archinity/issues/166);
  - which perks a vassal faction gives beyond tribute →
    [#168](https://github.com/cjd721/Rimworld-Archinity/issues/168);
  - adjacent: **the colony paying tribute is explicitly not #35's.**
    [`requirements/POLITICS.md`](../requirements/POLITICS.md) § *Campaign progression* now
    records that it has no owner.
- **RUN (only if R0 or R3 is selected).** Two clients. Client A alone opens the Royalty vassal page.
  Vassalise two Empire settlements in reverse list order, on the same weekly schedule, with fractional
  amounts. On the first shared delivery day, expect identical stacks, or a desync naming
  `GenMath.RoundRandom` under `WorldComponent_Vassals.DoDay`. **Unowned.**
- **Build map (unowned until a route is selected):**
  - the storage shape, and whether R1/R2/R4 share one delivery path;
  - our own catalogue def, or `VFEEmpire.TitheTypeDef`;
  - where to intercept the defeat of a last base — part of the one defeat-seam question in
    § *Taking a settlement must be hard* → *Open questions*;
  - the raid-weight patch target;
  - how the rebuild cost is charged;
  - the display surface (#8's gizmo, or the faction row);
  - whether VFE Empire's Church vassals stay enabled.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| **§1 — Build B (plan of record).** World object + `WorldComponent` clock + nine `Utility` methods + `CaravanArrivalAction` + `Settlement.GetFloatMenuOptions` postfix + a `SettlementDefeatUtility.CheckDefeated` block | new C# | **350–500 lean, 450–700 faithful** | `Archinity.Core` |
| **§1** `Trigger_BecameNonHostileToPlayer` transition surgery on the attacker's lord | new C# | ~10 lines | `Archinity.Core` |
| **§1** authored trigger (`IncidentWorker` naming both factions) | new C# | ~50 lines | `Archinity.Core` |
| **§1** `IncidentDef` and letter text | XML | ~25 lines | `Defs/IncidentDefs/Territory.xml` |
| **§1** multiplayer harness under Build B | **none** — no settings of ours; §0 P4 for the roll; §0 P5 covers the attendance option | 0 | — |
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
| **§3** vassals | **unpriced** — routes only, none selected ([#120](https://github.com/cjd721/Rimworld-Archinity/issues/120)) | — | — |

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
- **Every outcome roll uses §0 P4's seeded form.**
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
`294100/2938820380/1.6/Assemblies/VFEEmpire.dll`,
`294100/1629973374/1.6/Referenced/Multiplayer_Compat_Referenced.dll`,
`294100/2023507013/1.6/Assemblies/Outposts.dll`,
`294100/2688941031/1.6/Assemblies/VOE.dll`,
`294100/3687071198/Assemblies/MiningOutpost.dll`,
`294100/3423264477/Assemblies/ModRimworldFactionalWar.dll`,
`294100/3684587591/1.6/Assemblies/BetterTradersGuild.dll`,
`294100/3762723122/Assemblies/RimPacts.dll`,
`294100/2606448745/1.6/AssembliesCustom/Multiplayer.dll` and all 18
`Multiplayer_Compat*.dll` builds under `1629973374`.

§3 by [#120](https://github.com/cjd721/Rimworld-Archinity/issues/120). §1 established by [#92](https://github.com/cjd721/Rimworld-Archinity/issues/92), §2 by
[#81](https://github.com/cjd721/Rimworld-Archinity/issues/81), both revised after an adversarial
audit. No source tree was read as 1.6 fact: VOE ships 1.3-era source, [SR]Factional War's `Source/`
calls a `TileFinder.TryFindNewSiteTile` overload absent from 1.6, and VEF ships none.

The eight capability sections above *The build* carry their own *Status*, each naming its
establishing ticket (#164, #165, #167, #172, #152, #168, #170, #171).

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

**Not selected**: its roll is a bare `Rand.Chance` off the shared stream rather than §0 P4's seeded
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
   §0 P4-seeded, the winner can be **computed from the world object's own fields before the tick
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
