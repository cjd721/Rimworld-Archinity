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
remainder left after every non-hidden faction's freebie.** With a large roster, the freebies dominate the low-population layers.

---

## Hostility and Aggressive Actions (Issue #2 Routes)

Addressing how a hostile faction acts against the colony, harder the more it hates you, beyond vanilla's bottoming-out goodwill at −100 and basic incident filtering. Verified available routes against the 1.6.4566 codebase:

1. **Goodwill as the Input (Vanilla Weighting & Patches)**
   - **Mechanism:** Vanilla selects raid factions based on goodwill thresholds (hostile vs ally) via `IncidentWorker_Raid`. However, per #120, per-faction raid weight has **no XML lever** and requires a C# harmony patch or custom `IncidentWorker` extension. Goodwill ranges from −100 to +100.
   - **Multiplayer Sync:** Safe if deterministic or governed by host storyteller ticks; sync required if goodwill changes trigger desyncs (managed via RimWorld's standard multiplayer compatibility layers).
   - **Story Impact:** Frequency and target selection scale directly with negative standing.
   - **Difficulty:** Easy (C# patch on raid worker weight calculation).

2. **A Named Hostility Value (Persistent Campaign Metric)**
   - **Mechanism:** A dedicated integer/float dictionary or component tracking per-faction hostility independently of goodwill (e.g., ticking up on settlement loss or raids). Composes with bounded campaign terms via `StorytellerUtility.DefaultThreatPointsNow` postfix (~345 lines, #60).
   - **Multiplayer Sync:** Requires MP field synchronization for the per-faction campaign component.
   - **Story Impact:** Decouples diplomacy (goodwill) from blood-feud mechanics (hostility), allowing trading partners to still harbor deep operational animosity.
   - **Difficulty:** Medium (Component state + MP sync + storyteller integration).

3. **Declared-War State**
   - **Mechanism:** A distinct state flag on the `Faction` or campaign manager rather than continuous simulation. Triggers hardcoded modifiers (e.g., trade embargoes, automated siege parties, forced hostile targeting).
   - **Multiplayer Sync:** State change packet broadcasted across clients.
   - **Story Impact:** Creates clear narrative phases (Peace -> Tension -> Declared War) with dramatic escalation.
   - **Difficulty:** Easy/Medium (State machine + event triggers).

4. **Per-Faction Accumulating Values Spent in Player-Facing Events**
   - **Mechanism:** Factions accumulate "pressure" or "grievance" points over time or via player actions (taking settlements). Once a threshold is met, it triggers a specific scripted event at the colony's door (e.g., massive coordinated siege, ultimatum, blockade) drawing from #91 (faction demands) and #77 (raid objectives).
   - **Multiplayer Sync:** Accumulator values must be synced via multiplayer ticks/packets.
   - **Story Impact:** Replaces random chance with deterministic, build-up-based pressure, making player expansion carry visible, threatening consequences ("taking a faction's settlements makes them come for you").
   - **Difficulty:** Hard (Requires custom tracker component, event dispatchers, MP sync, and UI hooks).

5. **Actions Other Than Raids (Blockades, Bounties, Demands, Sieges, Pressure, Refusal of Trade)**
   - **Mechanism:** Utilizing existing incident workers or custom world objects (e.g., blockading world tiles, halting caravan paths, issuing formal demands via #91).
   - **Multiplayer Sync:** Standard RimWorld incident and world object synchronization.
   - **Story Impact:** Diversifies hostility beyond combat; economic and logistical strangulation.
   - **Difficulty:** Medium (Leveraging existing incident structures with customized payloads).