# Faction politics

## Purpose

In vanilla, factions are vending machines. Goodwill rises when the player runs
their quests and falls when the player shoots them, and all it buys is better
prices and fewer raids. Nothing any faction does depends on what any other faction
thinks, so there is no reason to prefer one over another beyond the reward on
offer.

This system exists to make the player care which faction is asking. It should
produce choices where serving one party costs something with another, where a
refusal is a real option with a real price, and where a relationship built over
several eras is visibly worth more than a better payout from a stranger.

Settled on [#13](https://github.com/cjd721/Rimworld-Archinity/issues/13). **How
much of it ships is not decided here.** The scope of faction involvement follows
capability and ease of implementation. The rules below are what the system must do
wherever it appears; how far it extends is set once
[#90](https://github.com/cjd721/Rimworld-Archinity/issues/90)–[#93](https://github.com/cjd721/Rimworld-Archinity/issues/93)
report what each piece costs. Cheap levers are used generously; expensive ones are
cut rather than scaled down.

## Meaning

**Goodwill** is the government's relationship with the colony — the ordinary spend
lever, and the axis this document is mostly about. **Reverence** is a separate
per-faction axis owned by [religion](RELIGION.md): how deeply the founders' ideology
has penetrated that faction's population. Neither substitutes for the other, and a
faction can be politically warm and religiously cold, or the reverse.

**A demand** is a faction asking the colony for something specific, on a clock, with
a stated consequence for failing. It is an event the player answers, not a tax that
is levied.

**A war** is an event, not a simulation. It is a notification, a goodwill change,
and a tile the player can travel to. Wars exist once the player has been told about
them; there is no background model of conflicts they never see.

**Standing** is what accumulated Goodwill has bought. It unlocks relationships —
access, people, knowledge — never discounts.

**Safe passage** is not being attacked by a faction's settlements when a caravan passes
them. Every faction that is not hostile gives it; nothing buys it separately.

## Required behavior

**Relationships form through encounters.** Factions have interests involving each
other, so helping one can antagonize another. A faction's identity is learned by
meeting it — by trading with it, fighting it, or being told — never by reading a
sheet.

**Demands ask for specific capabilities.** A specialist on loan, a protected route,
supplies for an army, military intervention, a prisoner released, an embargo on a
rival. The ask should be inconvenient and pointed at something the colony could
build but has not. Fungible payment is the weakest form and belongs to factions with
nothing more interesting to want. Every demand carries a deadline and states its
consequence before the player answers.

**Refusal remains viable, and is not free.** Refusing costs standing with the faction
refused and produces the consequence it telegraphed. It must never be the only losing
move on the board: a refusal that serves that faction's enemies earns with them.
Refusing everyone stays survivable without becoming costless.

**A single act moves more than one faction.** Two propagations, running along
different edges of the relationship graph:

- **Along rivalries** — serving a faction costs standing with those hostile to it.
- **Along alliances** — wronging a faction costs standing with those allied to it.
  Kidnapping a visiting pawn, harming a neutral, or fouling the ground beside a
  settlement reaches that faction's friends as well. Gossip spreads.

Magnitudes are balance work. The requirement is that the second-order consequence
exists, is legible, and is attributed to the act that caused it.

**Paired demands from rivals are the sharpest instrument found.** Two factions that
hate each other asking for incompatible things in the same window, where satisfying
one fails the other and the player is told so before choosing. The #13 prototype
found this carried more than simulated warfare did, for far less. Prefer it wherever
a choice between factions is wanted.

**Standing buys relationships, never discounts.** Tech transfer, a loaned specialist,
a granted site, candour about who a faction hates. Where the world map
expresses standing, it does so through which factions thrive.

**Settlements meet passing caravans.** A caravan that travels within a few tiles of a
settlement meets its faction. A hostile faction attacks it; a neutral or allied faction
offers to trade. This is faction-generic — the Church is no different. Range and how
often a settlement reacts are balance work.
[#136](https://github.com/cjd721/Rimworld-Archinity/issues/136)

**Aid is requested at a place.** An ally under attack names a tile and a short window.
Attending makes it a real fight; declining resolves it without the player and reports
the outcome. Two NPC factions fighting on the colony's own map is not a requirement —
being raided and calling in an ally is already ordinary play.

**Reverence is an input to this system**, not a part of it. A faction whose population
increasingly follows the founders' ideology reacts politically to that, whether or not
it is allied. The measure itself, its decay and its religious consequences belong to
[religion](RELIGION.md).

**The planetary resolution produces an immutable outcome.** At the moment the early-Spacer
political struggle resolves, authored rules evaluate the live campaign state and snapshot:
the route taken, every faction that ascends into orbit, and any faction defeated or absorbed
by that result. The snapshot may name zero, one or multiple ascending factions. It is not a
binary choice fixed at world creation, and later changes to Goodwill, Reverence or settlement
ownership do not rewrite it. [#100](https://github.com/cjd721/Rimworld-Archinity/issues/100)
owns the route predicates and tie rules.

## Campaign progression

Faction involvement should be common rather than occasional — hosting requests,
pilgrim escorts, loaned specialists, tribute, intervention. Frequency and weighting
belong to [the storyteller](https://github.com/cjd721/Rimworld-Archinity/issues/60).

Distinct enemy doctrines and non-raid hostility can change what the colony needs to
build. Defeat needs a route back through peace, tribute or subordination — **the colony
paying a stronger faction**, which is the mirror of [territory](TERRITORY.md) and has no
owner yet ([#35](https://github.com/cjd721/Rimworld-Archinity/issues/35) states what the
colony's own outposts, holdings and sworn factions must be, not what it owes others).
Only a handful of hand-authored factions carry the campaign, so
faction-generic selection is a fallback rather than the primary path.

## Player information and agency

The player must be able to see a second-order consequence and attribute it to the act
that caused it. A goodwill change that arrives unexplained is noise. This makes the
[political UI](https://github.com/cjd721/Rimworld-Archinity/issues/61) load-bearing
rather than decorative: none of the rules above matter if the effect is invisible.

Standing shows the carrot before the player reaches it — a locked row with its
threshold, not an absent one.

A manageable number of live diplomatic situations prevents notification fatigue.

## Constraints

- This document selects neither an engine hook nor a mathematical formula.
- **No background war simulation**, and none is wanted. Wars exist once the player
  has been told about them.
- Exact goodwill magnitudes, ripple coefficients, deadlines, concurrency caps and
  standing thresholds are balance work.
- The ripple must not compound into a runaway; whatever bounds it is an
  implementation constraint, not a balance knob.
- Multiplayer: one shared player faction means one goodwill number per NPC faction,
  seen by both players and actionable by either — accepted as design, not arbitrated
  ([Quests](QUESTS.md#player-information-and-agency)). Every write is a synced command and
  every tunable ships as a Def rather than a mod setting.

## Open questions

- [Multi-faction goodwill writes and the political ripple](https://github.com/cjd721/Rimworld-Archinity/issues/90)
  — what carries NPC↔NPC writes and the two propagations.
- [The faction demand](https://github.com/cjd721/Rimworld-Archinity/issues/91) — the
  ask, the deadline, the consequence, and moving a second faction on resolution.
- [The ally-aid battle at a world tile](https://github.com/cjd721/Rimworld-Archinity/issues/92)
  — the world object, resolution in absentia, and the attendance path.
- [Standing as a content gate](https://github.com/cjd721/Rimworld-Archinity/issues/93)
  — whether standing can gate content at all, and on which surfaces.
- [A caravan near a settlement meets it](https://github.com/cjd721/Rimworld-Archinity/issues/136)
  — proximity encounters, attack or trade by relation.
- Threat pressure — raid strength, composition and frequency — is
  [difficulty and pursuit](PRESSURE.md), not this document. Glitterites use
  [Trace](GLITTERTECH.md#trace--the-glitterites-learn-you-back).
- [The planetary political outcome](https://github.com/cjd721/Rimworld-Archinity/issues/100)
  — which live-state predicates select each route and ascending faction, and how multiple
  satisfied paths compose into one immutable snapshot.
