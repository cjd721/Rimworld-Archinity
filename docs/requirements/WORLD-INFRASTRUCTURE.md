# World infrastructure

## Purpose

Roads and vehicles exist to change **the size of the political world the player can
practically participate in**. That is the Industrial transformation stated in
[`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md): horse journeys become road trips, then
flights, then effectively no distance at all. The colony stops solving one settlement and
starts solving the planet.

Roads carry a second job: they are how the world's **technological era and political
relationships become visible on the world map**. A player who looks at the map and sees
paved highways between two factions has read something true about both of them without
opening a menu.

Roads are not produced by Charting and are not an altar reward.

## Meaning

**Infrastructure is the world's, not the player's.** Every settlement builds roads, all the
time, toward its neighbours. The player is a participant in a process that would happen
without them — which is what makes funding a route feel like politics rather than
construction.

**The road network is a ladder, and it climbs with the era.** In the Neolithic nobody builds
anything; everyone is a hunter-gatherer and nobody cares about anyone else. Cities make
routes matter, and each era paves what the last one trod. The vanilla world must therefore
**not** begin covered in modern paved roads.

**Finance and build are complementary verbs, not one verb.** Funding participates in another
civilization's project. Direct construction lets the colony make its own route. They should
not collapse into each other.

## Required behavior

### Era-driven network growth

- **Every settlement builds roads toward the settlements near it.** This is world-wide and
  continuous, not a radius around the player and not a player-faction effect.
- **Eligible neighbours are the nearest settlements of its own faction and of its allies**,
  with **no priority between the two** — a settlement looks at what is close and builds
  toward whichever of those are its own or allied.
- **A player colony is an eligible endpoint** for a civilization allied to the player. An
  ally paving a road to the player's door is the clearest expression of what this system is
  for.
- **Completing an era capstone advances the road quality available to civilizations**, and
  the network begins building or upgrading to the new tier.
- **Construction unfolds visibly over time** rather than replacing the map instantly. If the
  gradual build proves expensive, replacing the whole network at the instant of the advance
  is an acceptable fallback — it is less immersive, not wrong.
- **When the politics change mid-build, an alliance and a conquest resolve differently.** A
  broken alliance **pauses** the project: the politics are recoverable, and repairing them
  should recover something real. A settlement captured at a route's end **completes** it —
  that road is already half-built on the ground, and letting its new owner inherit it is
  better story than erasing the work.

### Player agency over routes

- The player can **contribute resources toward a specific, named route** — making it
  complete sooner, reach farther, or reach a higher tier than the autonomous network would
  have chosen.
- **What *farther* may reach is another settlement, or the player's own colony — never an
  arbitrary tile.** Every route wants two endpoints that mean something; a road to empty
  ground is not infrastructure.
- Contribution is **directed at that route**, and must be distinguishable in play from a
  plain goodwill gift to the same faction. The player should see a particular line on the
  map change.
- **The channel is era-appropriate.** Whatever the act is, it must make sense for a colony
  that has no radio. The moment radio makes it possible to fund a project on the far side of
  the continent is itself a progression beat.
- The player can also **build roads directly**, as the colony's own construction.

### No route is threatened

- **Routes are never threatened, and the player holds no stake in one.** A threatened-route
  event was cut by [#174](https://github.com/cjd721/Rimworld-Archinity/issues/174): one more
  thing to manage, for no gain the campaign needs.
- **The road itself is never physically damaged.** Routes do not degrade, decay or need
  repair.

### The mobility ladder

Vehicles must deliver, as requirements:

- **World travel speed** — the colony crosses the map faster than it could on foot.
- **Carrying capacity** — logistics, moving goods and people at a scale caravans cannot.
- **On-map combat platforms** — armored vehicles that fight in colony defence and raids.

And as a strong want, not a requirement:

- **Road dependence.** Ground vehicles should be fast on roads and close to useless off
  them, the way a car is. Vanilla already gives roads a movement bonus, so the requirement
  is not that roads matter at all — it is that they matter *much more* to a vehicle than to
  a walking caravan. This is what gives the road network teeth.

Vehicles are era-gated like everything else: a faction fields what its era affords.

## Campaign progression

Neolithic travel uses paths and dirt tracks. Medieval powers begin maintaining routes.
Industrial civilization paves and expands them, and this is where the system comes fully
alive: early vehicles change local and regional travel, armored vehicles turn roads into
military logistics, and aircraft partially escape the network to make continental
intervention practical. The gravship, late Industrial, eventually removes distance
altogether.

[`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md) § *Roads and Mobility* is the narrative
statement of this arc.

## Player information and agency

- The player can see the road network and read the world's era and alliances from it.
- The player can see which routes are under construction, and direct resources at one.

## Constraints

- **The world does not start paved.** Modern asphalt on a Neolithic map is the defect this
  system exists to correct.
- **Roads are world infrastructure state** — tier, ownership, alliances and constructed
  edges. Charting may later read completed mobility as one input to reach, but it does not
  own road creation, timing or cost.
- **Routes never degrade.** A route is taken by taking the settlements at its ends, never by
  wearing it down — there is no damage state, no repair and no decay anywhere in this system.
- **All writes must remain deterministic in Multiplayer.**
- Above-era anachronisms left on generated maps — ancient asphalt, scattered vehicle wrecks
  on a Neolithic map — contradict [`ERA.md`](ERA.md) and are its concern as much as this
  document's.

## Open questions

- **Contributing to a route** is answered by
  [#154](https://github.com/cjd721/Rimworld-Archinity/issues/154), which shares it with
  [the revolt](https://github.com/cjd721/Rimworld-Archinity/issues/131). Its threat half is
  cut ([#174](https://github.com/cjd721/Rimworld-Archinity/issues/174)).
- **Road-dependent vehicle movement is answered, and what is left of it is balance.**
  [`docs/specs/WORLD-INFRASTRUCTURE.md`](../specs/WORLD-INFRASTRUCTURE.md) § 4 verifies that
  both halves are already expressible as data: the era road ladder can be put in front of
  every vehicle, and a per-vehicle off-road penalty can be made severe enough to strand one.
  They compose in the right order, so "fast on roads, near-useless off them" is a pair of
  numbers rather than a mechanism to find. Owned by
  [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).
- **The numbers** — road tier multipliers, build duration, neighbour count and radius,
  funding prices, per-vehicle speeds and off-road multipliers — are balance and belong to
  [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119). The road ladder
  and the vehicle ladder must be set in one sitting, because they multiply — and a
  per-vehicle road cost can override the road ladder outright.
- **Ancient vehicle wrecks on a roadless map** moved to [`ERA.md`](ERA.md), with ancient
  dangers and the mechanitor's crashed ship part — one behaviour, three carriers — and are
  answered in [`docs/specs/ERA.md`](../specs/ERA.md) § *Above-era content seeded on the player's
  own map* ([#153](https://github.com/cjd721/Rimworld-Archinity/issues/153)).
- **Whether vehicles ship at all** is [the sourcing ledger's](https://github.com/cjd721/Rimworld-Archinity/issues/14).
- **Whether completed mobility feeds Charting's reach** is
  [the build map's](https://github.com/cjd721/Rimworld-Archinity/issues/119) route selection;
  the rung routes are in [`docs/specs/CHARTING.md`](../specs/CHARTING.md) § 4 and
  [`docs/specs/WORLD-INFRASTRUCTURE.md`](../specs/WORLD-INFRASTRUCTURE.md) § *Charting reach
  rungs — offered, not selected*.

---

**Six clauses [`docs/specs/WORLD-INFRASTRUCTURE.md`](../specs/WORLD-INFRASTRUCTURE.md)
§ *Outstanding decisions* handed back, all resolved by
[#128](https://github.com/cjd721/Rimworld-Archinity/issues/128).** Five are now stated as
rules above — own-settlement routes alongside allied ones, a player colony as an eligible
partner, what *extend farther* may reach, the era-appropriate funding channel, and how a
broken alliance differs from a captured endpoint. This note records only where they went, so
the spec's list can be struck.

The sixth needs no rule: **whether a save predating the feature starts construction or waits
for the next advance is moot**, because this is one fresh campaign on a frozen pre-worldgen
mod set ([#18](https://github.com/cjd721/Rimworld-Archinity/issues/18)). Out of scope, not
answered.
