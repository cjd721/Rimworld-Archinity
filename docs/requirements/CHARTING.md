# Charting and the Archon discoveries

## Purpose

Discovery becomes labor. In vanilla RimWorld the world hands the player places to go;
here the colony goes looking, and the looking is work a pawn does at a building. That one
change carries two loads at once: it delivers the ordered campaign chain that the
[Chronicle](../../CONTEXT.md) is made of, and it supplies the ordinary texture of a
RimWorld colony — the logging camps, the ruins, the hunting grounds.

Both loads must be carried well. A Charting system that delivers the campaign but starves
the colony of ordinary sites has broken the game around the story it was built to tell.

Resolved on [how a beat arrives](https://github.com/cjd721/Rimworld-Archinity/issues/39).

## Meaning

**The Waystone.** At the opening the Archon leaves the founders a tiny piece of
Archotech that reacts to other Archotech. It is a head start, not a chosen-one password:
not cosmologically founder-bound, in principle stealable or usable by others, and it does
not make ascension exclusive to the marked. It points; it never explains.

**Charting is one activity with two jobs.** The apparatus surveys the surrounding region
by ordinary means — maps, stars, landmarks, correspondence, sensing — and it interprets
the Waystone's returns. Each apparatus tier is a more sophisticated attempt at both.

**The two pools.** Those two jobs feed two pools, and the distinction is the system's
spine:

| Pool | What it holds | Character |
| --- | --- | --- |
| **The survey pool** | Ordinary optional content: ruins, resource and hunting sites, faction places, discoverable world events, and a small Archon-flavoured subset. **Authored side content lives here too** — the pool is defined by its repeatable, optional role, not by who wrote it. | Effectively infinite, era-banded, frequent |
| **The return pool** | The ordered Archon spine, and the finite authored set of significant side discoveries: special Archon sites, augments, later capsules, named rewards. | Finite, ordered at its core, rare |

The split is by **role**, not by authorship. A side quest we wrote that the player may do
once, twice or never is survey-pool content. A named campaign reward is return-pool content
whoever authored it.

**The Archon Spine** is the return pool's ordered core: beat *n+1* cannot become
discoverable until beat *n* succeeds. The player may delay it indefinitely, but it cannot
fire out of order or be skipped by storyteller RNG. Each beat is a physical location or
encounter the player travels to and takes something from, learns something from, or
changes. Core rewards are deterministic founder progression — named Archogenes, psychic
breakthroughs, methods, devices, unique protocols.

**Search band.** A minimum and maximum tile distance bounding where a discovery may be
placed. Distinct from *the band* in [era gating](../../CONTEXT.md), which governs which
factions may contact the colony.

## Required behavior

### Eligibility is state, never a roll

A discovery is eligible when its declared preconditions are satisfied by saved world
state. Preconditions are open-ended and chosen per beat: spine cursor position, the era
ceiling, a research node, a built thing, a political state, elapsed time, colony wealth —
whatever the beat needs.

- **Nothing about eligibility is rolled.** A beat is reached by playing, per
  [Quests](QUESTS.md).
- **An ineligible return-pool beat does not stall Charting.** The return pool simply has
  nothing to offer and the work produces survey-pool finds instead.
- **No calendar deadline forces campaign advancement.** Elapsed time may make a beat
  eligible; it never expires one.

### Two accumulators, so the plot and the economy do not compete

The survey pool and the return pool accrue work separately. Survey finds arrive at
roughly the rate vanilla RimWorld reveals comparable content, independent of what the
campaign is doing; return finds land on top of that.

- **Each pool carries its own guarantee.** Uncertain effort with a guaranteed-find
  threshold, per pool.
- **Work does not bank.** When the return pool has nothing eligible, its share of the
  work produces survey finds. It does not accumulate against a beat that cannot currently
  be found — the colony was not failing to find that beat, it was doing other work.
- **Within the return pool, the spine takes priority.** If the next spine beat is
  eligible, it is discovered; otherwise a significant side discovery is, if one is
  eligible.

The single-accumulator alternative — one search, priority-ordered across all three tiers —
is the accepted fallback if two accumulators prove infeasible. It is worse, because it
makes every spine beat a logging camp the colony did not get, and it bites hardest exactly
when a new era has just made a beat eligible and the colony most needs ordinary sites.

### Reach: the era offers, the apparatus accepts

Two knobs with no interaction term.

- **Tech level sets which search bands the world offers.** The band expands as the
  campaign climbs, and the flow is meant to read as obvious: you reach Industrial, you get
  vehicles, the reachable world explodes outward. The system never announces a transport
  prerequisite.
- **The apparatus sets which search bands it can accept**, and its work speed. An
  apparatus accepts every band up to its ceiling. A Star Table at Industrial is not slow;
  it is blind to the far band, and the return pool goes quiet until the Observatory
  is built.
- **Everything discoverable lives inside a band.** Nothing is ever found that the
  colony's current reach cannot travel to and return from. Weighting the draw within a
  band is desirable, not required.

If a hard band filter proves inexpressible, the accepted fallback is to let every
apparatus accept every band and scale work speed instead, so that using a Star Table to
resolve an orbital return is technically possible and practically unusable.

### Floors and ceilings differ per pool

- **The survey pool's floor is zero, always.** A late-campaign colony still finds the
  quarry next door; it is carrying the ordinary economy and must never stop.
- **The survey pool has a ceiling too.** It is bounded above, and its ceiling does not
  chase the return pool outward. Travelling the world for Archotech is the campaign;
  travelling the world for logs is not.
- **The return pool walks outward, and that is authored, not filtered.** Each beat
  declares its own search band, and the sequence is authored so the bands move outward —
  which makes *"you already found all the Archon sites near you"* true by construction.

**No beat can be stranded.** Because the outward walk is an authoring pattern rather than
a runtime minimum, a player who techs up with a near beat still undone finds it exactly as
before: the higher apparatus accepts every lower band, and the beat is simply close to
home. A rising runtime floor would soft-lock that player, and is forbidden for that reason.

### Effort is uncertain; starvation is not

The player should not know whether the next find takes two effective workdays or six.
Better researchers compress the clock. A guaranteed-find threshold prevents starvation by
RNG. Exact formulas are balance.

**Skill buys more, never better.** A stronger Charting researcher yields *more*
discoveries, not higher-quality ones. Quality scaling would quietly make the low end of an
era band unreachable and waste the authored breadth; the observatory does not find better
places, it finds more of them.

### Arrival, persistence and recovery

- **Discoveries auto-accept.** A find lands as a world object and, for the return pool, a
  beat nested under its parent quest. There is no accept-or-decline dialog, because
  nothing has been asked yet — a place now exists. Declining is not going, and it is free.
- **A beat is consumed by resolution, not by attendance.** A caravan may retreat from a
  site and return later at no cost.
- **Persistence and expiry are both supported; each beat chooses.** This document requires
  that the system support a site that persists until resolved *and* a site that expires,
  not that any particular beat do either.
- **A lost site never costs a beat its place in the chain.** If a site expires or is
  destroyed unresolved, its beat returns to eligible and is discovered again through
  ordinary Charting work — which the spine's priority handles with no additional rule.
  The same holds one tier down: a significant side discovery leaves the finite set when it
  is **resolved**, never when it is merely found. Exhaustion then means what it says.
- **An already-active objective is not re-granted.** Deduplication is by beat, not by
  site: while a beat's site stands unresolved the return pool will not offer that beat
  again, and Charting continues producing other finds.

### The apparatus

One Charting apparatus at a time. The Star Table requires the Waystone to build and there
is exactly one Waystone, so one table is the maximum. Should duplicates ever exist — a
multiplayer edge case — they contribute to the same search rather than running separate
ones.

| Civilization | Apparatus | Fictional meaning |
| --- | --- | --- |
| Neolithic | Star Table | Crude maps, stars, landmarks and repeated Waystone reactions are compared until direction and distance can be inferred. |
| Medieval / Industrial | Observatory | Formal mapping and celestial observation make regional Waystone returns triangulable while conventional surveying finds ordinary world sites. |
| Late Industrial onward | Sensory Array | Electronic, orbital and deep-range sensing treats the Waystone as an anomalous detector and can resolve Archotech returns across planetary and orbital scale. |

The apparatus count may grow beyond three if that is what it takes to match search bands
to eras cleanly.

### Natural discovery

A caravan out in the world is moving and foraging, and an outpost set up to scout is
looking. Both can turn up survey-pool content on their own, alongside the apparatus.

- **Only caravans and eligible outposts find things.** A caravan on foot or in vehicles
  counts. The gravship, shuttles and transport pods fly over everything and never do.
- **Finds are rolled as you go.** A find is a survey-pool find, placed right next to
  whatever found it, and it is never guaranteed. Nothing about it can reach the return pool.
- **A tile can roll again once a timer on it has run out.** If a per-tile timer is not
  possible, the fallback is that a tile rolls only the first time the colony enters it.
- **A caravan that stays on one tile does not roll again**, even after that tile's timer has
  run out; finds come from entering tiles. (Conrad, #118, 2026-09-23)
- **The outpost decides.** Each outpost type declares whether it searches at all, its
  chance and its distance — a scout post always looks; a mining camp does not. An outpost
  with an unresolved find finds nothing more.
- **Finds are not seeded in advance.** A hidden layout of pre-placed finds is a shadow
  world held beside the real one, and it is ruled out.

[Natural discovery](https://github.com/cjd721/Rimworld-Archinity/issues/146), from
[#126](https://github.com/cjd721/Rimworld-Archinity/issues/126).

### The Waystone cannot be lost by accident

The Waystone is colony-level state, not a hauled item. No raider steals it, no caravan
wipe drops it, no fire destroys it. Only an authored beat may take it, and any beat that
does must ship its own recovery in the same chain. No beat currently does.

## Campaign progression

The apparatus ladder above is the progression: Star Table in the
[Neolithic](../plot/NEOLITHIC.md), Observatory through the Medieval and Industrial
chapters, Sensory Array from late [Industrial](../plot/INDUSTRIAL.md) onward, resolving
returns inside Glitterite space in [Spacer](../plot/SPACER.md) and, at the threshold,
pointing out of the universe entirely ([ending](../plot/ENDING.md)).

Charting's share of the world shrinks as reach grows, per the announcement test in
[Quests](QUESTS.md): a signal nobody can hear in the Neolithic is an ordinary letter once
the Sensory Array exists. It never reaches zero, because Archotech returns are not
announcements and nobody is in a position to tell the colony about them.

## Player information and agency

- **The player cannot steer between the pools.** Both jobs always run; there is no toggle.
  A steering control would be a trap — the right setting is always whichever pool is
  currently quiet — and it would put the plot and the economy straight back into the
  competition the two accumulators exist to end.
- **Both jobs are visible.** The apparatus shows accumulated effective work and the point
  at which a find is guaranteed. It never shows a probability or an estimate.
- **Survey finds use vanilla's notification treatment**, verbatim. The mechanic and its
  pacing are being moved behind a task the player performs, not redesigned. Return finds
  arrive as beats under a parent quest, which is what distinguishes them.
- **The research tree carries the forward nudge.** Each apparatus's research entry
  describes what it can find, so a player looking at the next one up can see it does more.
- **The Waystone carries the present-tense signal.** Its inspect text reports when returns
  exist that the current instrument cannot resolve. This is the only thing that separates
  *the apparatus is insufficient* from *you have done every eligible beat* — without it, a
  player at Industrial on a Star Table watches the return pool go silent and cannot tell
  design from bug.
- **Nothing names the beat or its location** before it is found. The Waystone reports that
  something is out of reach, never what.

## Constraints

- **Charting is the only systemic source of unannounced sites.** A trader selling a map or
  a visitor describing a place is a giver-channel quest under [Quests](QUESTS.md) and needs
  no Charting work — somebody told the colony. What is barred is the storyteller silently
  spawning a site nobody mentioned.
- **The ordered spine must not skip or soft-lock**, under any combination of declining,
  failing, expiring, or teching past an undone beat.
- **Party composition and haul are beat-level authoring**, not requirements here. Whether
  a beat needs a founder present, or yields something that must be carried home rather
  than granted on completion, is decided in `docs/plot/` when the beat is written. The one
  constraint this document imposes: the quest must be able to **declare that burden before
  the player commits**, per the difficulty-before-commitment rule in [Quests](QUESTS.md).
- **The mix of small and large discoveries in the spine is an authoring instruction**, not
  machinery. A run of five gruelling beats is a mistake made in `docs/plot/`, and no
  selection rule can correct a fixed order. Survey-pool variety is balance.
- **This document selects no mechanism.** The machinery lives in
  [`docs/specs/CHARTING.md`](../specs/CHARTING.md), where
  [the Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57)
  verified it against 1.6. The Long-Range Mineral Scanner grammar is confirmed and its
  payload selector is an abstract method; the Deserters-style cursor was **replaced** by
  vanilla's own derived subquest cursor, which stores nothing.

## Open questions

- **Neither of this document's named fallbacks is needed.** Two independent accumulators
  *are* expressible, and a hard search-band filter *is* expressible — `siteDistRange` is an
  `IntRange` honoured as both a minimum and a maximum. Capability does not force either
  degradation, so neither is expected to be used; **both remain accepted fallbacks and stay
  live**, because retiring an accepted degradation is this document's decision and nothing has
  asked it to. [The Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57).
- **Vanilla's scanner readout shows an estimate this document forbids.**
  `CompScanner.CompInspectStringExtra` emits an average-interval line alongside the progress
  bar, so *"never shows a probability or an estimate"* is satisfied by overriding the
  readout rather than by adopting it. Recorded so the requirement is not quietly lost to
  reuse.
- **Which def carries a beat**, and how the return pool's finds nest under a parent quest.
  The routes are answered by [the Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57)
  (`docs/specs/CHARTING.md`); choosing one is [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.
- **The mundane table.** A Waystone-less apparatus, buildable by ordinary research, that
  only ever feeds the survey pool. It would separate *the colony surveys* from *the
  founders detect* — a distinction the fiction already makes — and it is what a second
  colony or a settlement without the Waystone would need. Nothing requires it yet;
  capability and narrative decide together whether it ships.
- **Whether natural discovery's rules are expressible** — placement next to the finder, a
  per-tile re-roll timer, per-outpost-type chance and distance.
  [The Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57)
  verified the travel and tenure hooks, and that the per-tile presence record is ours to
  write; [natural discovery](https://github.com/cjd721/Rimworld-Archinity/issues/146) answers
  the new clauses.
- **Road construction is not a Charting decision.** Era-driven roads, allied route
  selection, construction time, player funding and direct road building belong to
  [world infrastructure](WORLD-INFRASTRUCTURE.md). Charting never creates, upgrades or pays
  for a road. Whether completed mobility infrastructure later contributes a reach rung is
  [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s route selection,
  not part of the road-building requirement.
- **Map generation must be cross-client identical, and that is an engineering trap, not a
  requirement.** Both clients generate every map and Multiplayer's checksum cannot see it, so
  a divergent map is a delayed desync. Registered as T-120 by
  [must both clients generate the same map](https://github.com/cjd721/Rimworld-Archinity/issues/104);
  T-33 covers KCSG. It is load-bearing for every site Charting produces.
- **The significant-site catalogue**, search band distances, effort formulas and
  presentation values. Balance and authoring, after the structure is built.
