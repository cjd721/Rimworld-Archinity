# Charting

## Purpose and scope

How the discovery system in [`docs/requirements/CHARTING.md`](../requirements/CHARTING.md)
will be built: the apparatus, the two work accumulators, search-band placement, spine
ordering and the persistence they need.

This document owns the machinery. What a discovery *is*, when it becomes eligible and what
the player may see or refuse is requirements and stays there.
[Quests](../requirements/QUESTS.md) owns quest presentation and the parent/sub-quest
relationship; [the Chronicle's authoring mechanism](https://github.com/cjd721/Rimworld-Archinity/issues/40)
owns which def carries an individual beat.

## The build

**Not yet designed, and this section says so rather than implying otherwise.**
[The Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57) owns
it and has not run. What follows is the constraint set any build must satisfy, in the order
the constraints are most likely to bite — read it as the brief, not the answer.

1. **Two independent work accumulators** — the survey pool and the return pool — each with
   its own uncertainty and its own guaranteed-find threshold. If two accumulators are not
   expressible, the accepted fallback is one accumulator with the tier priority ordering
   across all pools.
2. **Return-pool work does not bank.** When nothing in the return pool is eligible, that
   work produces survey finds instead.
3. **Search bands as a hard placement filter** — a minimum and maximum tile distance, with
   the era ceiling selecting which bands the world offers and the apparatus declaring which
   it accepts. If a hard filter is not expressible, the accepted fallback is that every
   apparatus accepts every band and work speed degrades to unusable beyond its tier.
4. **Deduplication by beat, not by site.**
5. **Skill scales find count, never find quality.**
6. **The reach band** — how far the colony can look, scaling with transportation and sensing
   rather than calendar time. #57 owns this outright; roads
   ([#68](https://github.com/cjd721/Rimworld-Archinity/issues/68)) and vehicles
   ([#69](https://github.com/cjd721/Rimworld-Archinity/issues/69)) report their input format
   to it and do not design it.
7. **Travel and outpost discovery** — whether a caravan crossing unexplored world or an
   outpost standing in a region can surface a site, and which pool it feeds. Absorbed into
   #57 from #89, under #39's constraint that a find must correspond to the colony having
   actually been somewhere.

**Cost is unknown** because the carrier is unchosen. The scanner grammar under *Available
mechanisms* is the leading candidate and is unverified against 1.6.

## Persistence and multiplayer

The state Charting requires:

- **The spine cursor** — current beat and its completion state.
- **Per-pool work accumulated** toward the next find, and each pool's progress toward its
  guarantee.
- **Eligible pool contents**, and the finite return-pool set's remaining membership —
  noting that a significant side discovery leaves that set on **resolution**, not on
  discovery, so "found but unresolved" is a distinct third state.
- **The current apparatus** and the search bands it accepts.
- **Current travel reach**, derived from the era ceiling.
- **Active-site registry**, sufficient to prevent re-granting a beat whose site already
  stands unresolved.
- **Waystone presence** as colony-level state rather than a thing item, so no raid, fire or
  caravan loss can take it.

Both clients must agree on all of it. The uncertainty in find timing is the obvious
divergence hazard — a `System.Random` read outside a synced context would give the two
machines different discovery schedules — and the pity threshold makes that failure quiet
rather than immediate, which is the worst combination. See `CODING_STANDARDS.md`.

## Failure and recovery

The campaign softlocks this system must not permit are stated as requirements; each needs
a corresponding technical guarantee:

- A beat whose site expires or is destroyed unresolved must return to eligible.
- A beat must never fall outside every acceptable search band. The requirements forbid a
  rising runtime floor precisely to prevent this; an implementation that reintroduces one
  as an optimisation reintroduces the softlock.
- A player who techs past an undone near beat must still be able to find it.

## Status

**Nothing here is verified against 1.6, and nothing is selected.** This document exists to
hold the technical material carried out of the requirements document when
[how a beat arrives](https://github.com/cjd721/Rimworld-Archinity/issues/39) settled the
rules. It is a starting point for
[the Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57),
not a design it has produced.

The scanner grammar below is a *proposed* implementation. It is not evidence that the
Chronicle already exists in the build.

## Available mechanisms

**The Long-Range Mineral Scanner supplies the right grammar.** Vanilla already ships the
shape the requirements describe:

> operator labor → `ResearchSpeed`-scaled work → probabilistic success → guaranteed pity
> timer → root-special auto-accepted quest → world object

Archinity's change is to the payload selector: from *"a precious lump"* to *"what is
currently eligible to be discovered?"* The auto-accept, the pity guarantee and the
work-scaled uncertainty are all already there.

**A small persistent world-state cursor, Deserters-style**, is the candidate carrier for
the Archon Spine's ordering — beat *n+1* not becoming discoverable until beat *n* succeeds.

Both are *available mechanisms* on the strength of how the vanilla and Deserters systems
are described, not on a read of 1.6 source. #57 verifies or replaces them.

## Verification

Everything. Specifically, in the order #57 would want it:

- Whether the mineral scanner's machinery can be driven by an arbitrary payload selector,
  or whether it must be reimplemented.
- Whether two independent accumulators can be expressed in whatever carries the apparatus.
- Whether a world object's spawn distance can be bounded below as well as above.
- Whether the Deserters cursor pattern is available to us at all, given the mod's
  admission status.
- Whether anything vanilla, DLC or modded surfaces a world object as a consequence of
  caravan travel or outpost tenure.
- Whether any of it survives Multiplayer.

## Outstanding decisions

- **The mundane table** — a Waystone-less apparatus feeding only the survey pool. Open in
  the requirements document; capability and narrative decide it together.
- **Which def carries a beat** —
  [#40](https://github.com/cjd721/Rimworld-Archinity/issues/40).
