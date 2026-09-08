# Quests

## Purpose

Almost everything this campaign delivers reaches the player as an event or a quest: the
Chronicle, the Church and Schism tracks, Glitterite raids, and the ordinary texture of a
RimWorld colony. This document states how that content arrives, how it is presented, and
how the player finds it.

The player can always tell what is **necessary to move forward** from what is optional,
without leaving the game.

## Meaning

**RimWorld ships events.** Everything the world does is an event. Some events can be
accepted or declined; we call those **quests**.

**A plot line is presented as a parent quest, and its beats as sub-quests beneath it.**
The Chronicle is the main plot line's beat chain; a subplot has its own. _Main quest_
names the presentation, never the content.

**Three axes describe any quest, and they vary independently.**

| Axis        | Values                                                                                                          | What it governs                         |
| ----------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| **Channel** | How it arrived: storyteller pool · named incident · decree · plot-line engine · giver · world object · purchase | Pacing, and what the era gate can reach |
| **Payload** | What it is: a place · a person · an obligation · a threat · a process                                           | Whether it is a quest or an event       |
| **Theatre** | Where it happens: home · away · both · none                                                                     | Where the work lands                    |

## Required behavior

### Necessary content nests; optional content does not

- The main plot line and each subplot is presented as a **parent quest**: standing,
  auto-accepted.
- The beats that carry it appear **nested beneath it**.
- **The bar for what goes under a parent quest is necessity** — the essential content the player must do
  to move forward. Nice-to-haves, neat stuff, and everything else is an ordinary quest or event, however
  Archon-flavoured it is.
- A nested beat that is a quest may be declined or dismissed once it has arrived.
  Declining must not soft-lock a plot line; recovery is owned by
  [how a beat arrives](https://github.com/cjd721/Rimworld-Archinity/issues/39).

Nesting is the entire mechanism for telling necessary from optional. It replaces the
bespoke Archon marking required by
[who the altar serves](https://github.com/cjd721/Rimworld-Archinity/issues/10).

### The player can see where they are in a plot line

A parent quest shows progress through its chain without the player consulting anything
outside the game. Beats already taken remain visible and legible as taken.

### Difficulty is declared before commitment

Every quest declares a challenge rating the player sees before committing to it. That is
the campaign's difficulty signal, and it adds no second one.

### The announcement test decides whether Charting is required

A quest may arrive as an ordinary letter if somebody told the colony about it, or if it
announced itself. **Anything the player would not know about unless they went looking for
it must be discovered through Charting.**

**"Announced itself" is era-relative, and widens deliberately.** A signal nobody can hear
in the Neolithic is an ordinary letter once the Sensory Array exists, and an industrial
sweep across a region legitimately finds everything in it. Charting's share of the world
therefore shrinks as reach grows — the founders' instruments improve, and the world gets
louder to them. It never reaches zero, because Archotech returns are not announcements
and nobody is in a position to tell the colony about them.

The test applies per quest. The resulting disposition of each vanilla and mod quest is a
ledger entry rather than a requirement:
[the sourcing ledger](https://github.com/cjd721/Rimworld-Archinity/issues/14) owns the
list, and [the Charting discovery engine](https://github.com/cjd721/Rimworld-Archinity/issues/57)
owns what the discovered pool draws from.

### Necessary content never depends on a roll

A beat is reached by playing, not by winning a lottery. No plot line may be gated behind
a random arrival, a random reward or a channel the player cannot deliberately work. This
governs beats only; optional content is free to be as lucky as it likes.

### Channels

The campaign uses seven arrival channels, and each has a job. A channel is a design
choice per quest, not a property left to whatever a def happened to ship with.

| Channel              | Used for                                                                                                                           |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Plot-line engine** | Beats. A standing parent quest emits them as the plot line advances.                                                               |
| **Storyteller pool** | Ordinary optional content, paced by [difficulty and pursuit](PRESSURE.md).                                                         |
| **Named incident**   | Content fired for a specific reason by a specific condition.                                                                       |
| **World object**     | Content a thing the colony owns or reaches produces — including the Charting apparatus.                                            |
| **Giver**            | Content a trader, visitor, book or scan hands over.                                                                                |
| **Purchase**         | Content bought with a political currency — the Schism's Influence and Glitterite Intel both describe a catalogue the player shops. |
| **Decree**           | Obligations imposed by an institution the founders belong to, once they hold standing in it.                                       |

## Player information and agency

- Necessity is legible at a glance, from the shape of the quest list alone.
- Where content can be refused, refusing is visible and available to the player. Not all
  content can be refused.
- Progress through a plot line is visible in game.
- Difficulty is visible before commitment.
- A quest states plainly why it is happening. A quest with no sender and no discovery
  behind it does not ship.

## Constraints

- This document selects no engine mechanism. Whether beats nest through the vanilla
  parent/sub-quest relationship or something else is a capability verdict, recorded on
  [#12](https://github.com/cjd721/Rimworld-Archinity/issues/12) and settled in `docs/specs/`.
- Anomaly is out of the build; its quests are not part of any pool.
- Pacing — how much arrives and how often — belongs to
  [difficulty and pursuit](PRESSURE.md) and to
  [the storyteller](https://github.com/cjd721/Rimworld-Archinity/issues/60). This document
  imposes no cap on offers or on accepted quests.
- Reward pools, genes and psycast gates belong to
  [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31); conquest entry, cost and
  consequences to [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35).

## Open questions

- **Which mechanism carries nesting, and what it costs.** The vanilla parent/sub-quest
  relationship is a verified available mechanism; selecting it, and writing the generator
  it needs, belongs to
  [the Chronicle's authoring mechanism](https://github.com/cjd721/Rimworld-Archinity/issues/40).
- **Whether auto-accept is forced on beats by the presentation** rather than chosen. See
  the capability findings on
  [#12](https://github.com/cjd721/Rimworld-Archinity/issues/12).
- **Ownership of the quest board under Multiplayer.** Either founder can accept any quest
  and choose its rewards, and there is no faction-level ownership to restore. Whether that
  is accepted as design or arbitrated is a capability question with no ticket yet.
- **What a purchasable quest catalogue requires**, for the Schism's Influence and for
  Glitterite Intel. [#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) and
  [#55](https://github.com/cjd721/Rimworld-Archinity/issues/55) carry the currencies; the
  catalogue itself has no owner.
