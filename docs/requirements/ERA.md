# Era

## Purpose

The campaign runs through every technological era in order, and the era is the single axis
everything else hangs from. This document owns **what the era does** — what it gates, what
it lets through, and what happens to the world when it changes.

It exists so that a Medieval colony is never shot at with an assault rifle. That is not a
balance preference; it is the campaign's core sensation. A player who can be raided by a
faction two eras ahead is playing a different game from the one this suite is building, and
no amount of tuning recovers it.

The experience the era gate must create: **the world you live in is the world you have
earned.** Everything that arrives at the colony belongs to the age the colony is in. What
lies beyond that age exists, is visible, is tantalising, and is somewhere you must go —
never something that comes to you.

**This document does not own the era clock.** Where the era is stored, when it advances, and
what `AdvanceEra()` writes are [`docs/specs/ERA.md`](../specs/ERA.md)'s. It does not own
what becomes available at each era ([`docs/progression/`](../progression/README.md)), the
crafting *menu surface* ([colony](COLONY.md)), or which faction replaces
which at a boundary ([the faction grid](https://github.com/cjd721/Rimworld-Archinity/issues/34)).

## Meaning

**The era is the world's floor and the player's ceiling.** Those are two different gates on
one number, and both must hold.

- **The ceiling** is on **acquisition** — what the colony may research, craft, buy and
  field. It is hard. The player cannot research into the next era before finishing this
  one.
- **The floor** is on **arrival** — what the world sends at the colony. It is a **band**,
  not a ceiling: the player's era or one below, never above.

**Arrival and encounter are not the same act, and only arrival is gated.** Something that
comes to the colony — a raid, a quest, a visitor, a trade caravan, a storyteller incident —
is arrival. Something the player deliberately travels to is an encounter, and encounters
are not banded at all. The player may walk into a Spacer settlement in the Medieval era and
be destroyed by it. That is working as intended.

**Above-era content is not walled off; it is made not worth the trip.** The design principle
is the deterrent, not the barrier. A wall the player can see past and never cross is
resented; a place that kills anyone who enters is respected, and the handful who survive it
have earned what they carry out. Above-era settlements are rare and lethal.

## Required behavior

### The acquisition gate

- Research is presented **one tab per era**. Each era's tab holds that era's projects,
  culminating in its **capstone**.
- **The whole tree is viewable at all times**, every era's tab, from the first day of the
  game. Seeing what is coming — and planting the crop a future recipe will need — is part
  of playing, and nothing may hide it.
- **Nothing in an era's tab may be researched until the previous era's capstone is
  complete.** Completing a capstone is what opens the next tab and what advances the era.
- **No route may advance a research project whose prerequisites are unmet.** The gate is
  the rule, not the research bench. **The test is applied to the project, never to the kind
  of source** — a book, a quest reward, a ritual, a building, a gene, a faction's favour:
  whatever the carrier, if it can progress a locked project it breaks the era arc exactly as
  researching it early would, and is closed on the same grounds. Naming a kind of carrier
  here asserts nothing about whether one exists; the survey in
  [`docs/specs/RESEARCH.md`](../specs/RESEARCH.md) says which actually do.
- **Nothing survives as an authored exception.** A reward that hands the player a project
  they have not earned is not shipped, however well it is dressed.
### The arrival band

**Everything that arrives at the player is the player's era or one below. Never above.**
This covers, without exception:

- hostile raids and friendly raids,
- quests and the threats inside them,
- visitors, travelers and trade caravans,
- storyteller incidents.

**No faction is above the band by virtue of being special, and a mechanism that exempts one
by default is a defect.** The band is not a difficulty setting with a list of exceptions; it
is the rule that makes each era feel like itself.

#### The one breach, and it is authored

**The campaign's own beats may deliberately breach the band. Nothing else may.**

The named case is the Glitterite pursuit. The Glitterites do not know the colony exists
until the player reaches orbit or does something that puts them on the map; from that moment
they begin sending things, and what they send is Ultra while the player may still be Spacer.
That is intended — being hunted by something out of your league is the point of the pursuit
([`GLITTERTECH.md`](GLITTERTECH.md), [`PRESSURE.md`](PRESSURE.md)) — and it is the reason
this is stated as an authored exception rather than left as a contradiction for whoever
builds the pursuit to discover.

The distinction that makes both rules true at once: **the band governs the ordinary world,
which arrives on its own. A breach is a beat the campaign wrote on purpose, triggered by
something the player did.** A breach that can fire without an authored trigger is not a
breach, it is a defect.

### The era advance

Completing the era's capstone advances the era. The advance is **one instant that re-authors
the world** — deliberately a wave of the wand, not a simulation. RimWorld already asks the
player to suspend disbelief about time; the advance spends that licence openly.

At the instant of the advance, in one go:

- a settlement's **owning faction may be swapped**;
- a faction may be **removed**, or **shrunk** to a remnant;
- a faction created at worldgen but absent from the map may **appear and settle**;
- the arrival band moves with the player;
- the world tech level and the player faction's tech level move together.

**Which factions change, and how, is authored** — decided against the state of the world at
the moment of transition, never by lottery. The transition must therefore be able to
**identify the factions the player has a relationship with** and treat them differently from
factions the player has never met.

**Only roads unfold over time.** Infrastructure is the one thing that visibly builds after
the advance ([`WORLD-INFRASTRUCTURE.md`](WORLD-INFRASTRUCTURE.md)). An instant road update
is an acceptable fallback if the gradual build proves expensive.

**Nothing else may change on a delay.** A settlement that changes hands twenty days after
the advance, while the player is caravanning toward it, is a defect. The world changes at
the moment the wand waves, and not afterward.

**The advance never modifies anything the player built or owns.** No colony building,
item, pawn or research is retiered, upgraded or invalidated at a boundary. **A holding
stores its own era**, set at conquest and moved only by the colony paying to advance it, so
the advance never touches one ([Territory](TERRITORY.md)).

**The advance happens as a single, indivisible act.** A world half re-authored — some
settlements transferred, others not, because something interrupted the pass — is the failure
this clause exists to prevent, and it is the failure mode Multiplayer makes likely.

> **Is any of this possible? Yes, and it is already answered — do not re-open it.** Settlement
> ownership transfer, the consequences it leaves behind, and revealing a faction that was
> created at worldgen but held off the map are all verified:
> [#8](https://github.com/cjd721/Rimworld-Archinity/issues/8),
> [#70](https://github.com/cjd721/Rimworld-Archinity/issues/70),
> [#130](https://github.com/cjd721/Rimworld-Archinity/issues/130), and
> `docs/engine/factions-and-worldgen.md`. A faction emptied of its settlements is **not**
> registered as defeated, which is exactly the shrink-to-a-remnant case this document wants.
> **Which** factions climb, shrink or survive — including protecting the ones the player has a
> relationship with — is [the faction grid's](https://github.com/cjd721/Rimworld-Archinity/issues/34).
> `docs/specs/ERA.md` carries the determinism rule the implementation must follow, and names
> the shipped mod that gets it wrong.

## Campaign progression

The eras run Neolithic → Medieval → Industrial → Spacer → Ultra, each closed by its capstone.
[`docs/PLOT.md`](../PLOT.md) carries the arc and [`docs/plot/`](../plot/) the era chapters;
[`docs/plot/INDUSTRIAL.md`](../plot/INDUSTRIAL.md) states the mobility half of the Industrial
transformation.

**The full faction roster for every era is authored up front and created at worldgen**,
with factions that have not yet arrived held absent from the map until their era. The
campaign never invents a faction at runtime that was not planned for.

The advance is a beat the player should feel as a turning of the age — some factions they
knew advancing alongside them, some falling away, others they have never met rising large.

## Player information and agency

- **The advance is announced by a letter**, written as the campaign's historian looking back:
  time has passed, the world is larger and smaller at once, deadlier and more beautiful, and
  here is what this new age brings. Authored flavour is sufficient.
- **A short changelog is wanted where it is cheap** — not every settlement, but what became
  of the handful of factions that actually mattered in the era just ended.
- **The player always knows what is coming.** The research tree is fully visible across all
  eras from the start.
- The player triggers the advance themselves, by finishing the capstone. Nothing else
  advances the era.

## Constraints

- **No arriving content above the player's era, except where a campaign beat deliberately
  sends it.** A mechanism that merely makes it unlikely does not satisfy this, and a breach
  that can fire without an authored trigger is a defect.
- **No exempt faction.** In particular, the Church is the Empire in place
  ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53)), and any band mechanism
  that exempts the Empire by default must be corrected rather than inherited.
- **The band must track the era clock**, not a number that only some other mod writes. The
  world tech level and the player faction's tech level must move together at every advance —
  already specified as `AdvanceEra()`'s writes 1–3 in
  [`docs/specs/ERA.md`](../specs/ERA.md) § *Change*, which exists precisely so the band has
  something to read once TechBlock is off.
- **The gate must hold identically on both Multiplayer clients.** A band computed from
  client-local settings is a divergence source, not a gate.
- **Nothing above the era is seeded on the player's own map, as structure or as event.** A
  sealed vanilla ancient danger full of charge rifles, sitting in the colony's back yard from
  day one and expected to be opened, is not the seek-it-out case — the seek-it-out case is a
  journey the player chooses to make. The same objection covers the Biotech mechanitor's
  crashed ship part and the ancient vehicle wrecks scattered on a roadless map.

  Three acceptable outcomes, in order of preference: **remove it**; **author when it appears**,
  so the mechanitor's crash lands in the Industrial era and not before; or **replace it with
  something that fits**, such as an Archon site with a few defenders that becomes part of the
  campaign's own quest line.

  **This is a deliberate reversal of [#7](https://github.com/cjd721/Rimworld-Archinity/issues/7)
  § 5's *"Exposure is free. Supply is gated"* rule**, which turned WTL's *Ancient debris* and
  *Ancient facilities* filters off on purpose. The exposure rule survives for things the player
  travels to; it does not survive for things placed in the colony's back yard at map
  generation.
- **Looted above-era gear is not artificially blocked from use.** Scarcity comes from the
  lethality of the places that hold it and from biocoding, not from a rule forbidding the
  player to carry out their prize.
- **The prerequisite rule is checked at the project, never at the source.** Vanilla's own
  completion path finishes every unfinished prerequisite recursively, so one unguarded
  grant does not skip an era — it shatters several. A survey that clears each *source*
  individually is not a defence.
- The advance is not reversible and the world era never outruns the player.

## Open questions

- **The arrival band's enforcement** — [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22)
  owns it. Four known gaps against the requirement above: Ignorance Is Bliss ships
  `numTechsAhead 1`, so the band is *one above* as well as one below; `empireIsAlwaysEligible`
  defaults true, and the Church is the Empire in place; quests have no general gate, only one
  hardcoded defName, with the storyteller filter likewise a hardcoded list; and its band
  computation is gated on client-local settings ahead of a `Rand` draw, with a static player
  tech-level cache never reset on save load.
- **A caravan already en route when its destination changes hands** — capability, the one
  unexamined case. Not era-specific: it fires on the Schism's transfers, on a revolt and on
  ordinary conquest too.
- **A rite between the capstone and the advance.** [#113](https://github.com/cjd721/Rimworld-Archinity/issues/113)
  resolved that capstone completion calls `AdvanceEra()` directly, with no rite and no
  confirmation, and **that decision stands**. Whether a ritual could sit between them — the
  capstone unlocking an effigy the colony celebrates, the advance firing on the celebration —
  is *explored, not chosen*, and **no capability work is outstanding on it**:
  - a `RitualOutcomeEffectWorker` calling arbitrary code on a good outcome is built twice in
    [`RELIGION.md`](RELIGION.md)'s spec, ~40 lines plus the XML trio;
  - the multiplayer chain for `AdvanceEra()` *specifically* from a ritual outcome is already
    verified in [`docs/specs/ERA.md`](../specs/ERA.md) § *Cost*, as a superseded bullet kept
    for this purpose — a cancelled or failed rite calls nothing;
  - an era parked indefinitely is a **designed-for** case, not a hazard:
    [`PRESSURE.md`](PRESSURE.md)'s threat curve flattens at each era's ceiling and its
    verification carries *"Park an era"* as a named acceptance test.

  What remains is the effigy building itself and one design call — whether the boundary is a
  thing the player **chooses** or a thing that **happens to them**, which is #113's own
  unfinished half.
- **Above-era structures and events seeded on the player's own map** — capability.
- **The rate of non-bench research sources.** A building, gene or item that produces
  research points into a project the player *could already research* does not break the arc
  by the rule above, but it can collapse an era's pacing.
  [`docs/specs/RESEARCH.md`](../specs/RESEARCH.md) § *Class C* carries the measured rates
  against a 213/day single-researcher baseline, and notes that the two pacing tickets this
  question was written against are both closed with nothing replacing them. Whether such a
  source is capped, restated or removed is balance and belongs to
  [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).
- **Era lengths, the number of factions per era, and the lethality of above-era settlements**
  are balance, and belong to [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).
- **Which faction replaces which at each boundary** is [the faction grid's](https://github.com/cjd721/Rimworld-Archinity/issues/34).

Authored by [#128](https://github.com/cjd721/Rimworld-Archinity/issues/128).
