# Difficulty and pursuit

## Purpose

Overhaul wealth scaling to deliver a hard campaign for two demigod founders and
an increasingly powerful civilization. Opposition must reflect several kinds of
advantage and hostility, including development within an era. This is a set of
desired behaviors, not a selected formula or a claim of technical feasibility.

Resolved on [What replaces wealth scaling](https://github.com/cjd721/Rimworld-Archinity/issues/9).

## Meaning

Difficulty combines colony development, military capability and the world's
response to the player. Strength, composition and frequency are distinct outputs;
they need not all respond to every input in the same way.

[Reverence](RELIGION.md) represents religious adoption and the material power it
provides. [Trace](GLITTERTECH.md) represents the Glitterites' ability to correlate
and hunt the colony. Search progress represents how close they are to locating
its current position; it is distinct from Trace.

## Required behavior

### Difficulty contributors

- Wealth remains a limited contributor: comfort, infrastructure, mood advantages
  and equipment all make a colony stronger. Removing wealth entirely is not the
  objective. A suggested 10–20% share illustrates its subordinate role, not a
  settled weight.
- Time contributes according to time spent in the current era, reaching a ceiling
  rather than growing indefinitely. The ceiling and time to reach it are balance
  work; one or two years is illustrative, not fixed.
- Military capability contributes through practical broad indicators, potentially
  including research and wealth. Research must establish useful measurements;
  no detailed inventory or equipped-weapon census is required by this design.
- Reverence is a major contributor because religious power provides material
  advantages. A colony with little or no Reverence must still face appropriate
  difficulty through the other contributors.
- Diplomatic circumstances matter. More enemy factions should create more hostile
  pressure, with increased raid frequency a desired expression. Alliances belong
  among the inputs to investigate; their precise effect remains to be designed.
- Contributions must be bounded and combined without accidental runaway
  multiplication. Exact weights, curves and overlapping indicators need balance
  and technical investigation.

Opposition must remain dangerous to highly enhanced colonists. Numbers alone do
not satisfy this: large groups of weak enemies that cannot threaten the player's
defenses are inadequate. Enemy quality, equipment, composition and numbers should
produce an appropriate challenge within faction identity and campaign eligibility.
Era supplies context; continued development within an era can increase difficulty
without new research or story progress.

Pressure remains dynamic, with good luck, bad luck and uneven stretches of danger.
There is no required fixed recovery period after an attack. Human political
reactions retain the benefits and consequences described in [religion](RELIGION.md);
Reverence is not a universal multiplier on unrelated enemies. Glitterites use Trace.

### Raid objectives

Numbers and quality are not the only axis on which opposition varies. **A raid may
arrive wanting something other than the colony's destruction, and when it has what
it came for, it leaves.**

- **The objective is declared, not discovered.** The arrival letter names it, and it
  arrives before the group does, so the player chooses a response rather than
  reconstructing an intent afterwards.
- **Three objectives are required**: taking **people**, taking **livestock**, and
  taking from the colony's **stores**. Ordinary assault remains the common case;
  objective raids are the variation, not the norm.
- **Objectives are era-gated like everything else that arrives** ([era](ERA.md)'s
  arrival band). A Neolithic neighbour comes for animals and for food; coming for
  *people* is a later-era escalation. Which objective belongs to which era, and at
  what weight, is balance.
- **The opportunistic kidnapping and looting vanilla already performs on ordinary
  raids stays on.** A declared objective is an addition to that behavior, not a
  replacement for it.

**Burning the fields is a want, not a requirement.** It is desirable, and it is not
free. It is recorded here so that it is neither assumed available nor forgotten.

### Glitterite pursuit

**This document names no provider.** Which mechanism carries the pursuit belongs to
[`docs/specs/TRACE.md`](../specs/TRACE.md), which has read the field and returned
its verdict.

An earlier draft of this paragraph preferred Odyssey's gravship pursuit mechanic.
That preference was investigated and **declined**: what Odyssey ships cannot
express rules 1, 3, 4, 5 or 7 below, and
[`docs/specs/TRACE.md`](../specs/TRACE.md) § *Available mechanisms* carries the
per-rule evidence ([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)).
The correction is recorded rather than silently dropped, because the preference had
already been read as a commitment — but the carrier's name and its internals stay
in the spec, which is where a carrier belongs.

1. A qualifying relocation starts a fresh search for the colony's location without
   reducing Trace. Escape requires sufficient distance. A short move does not
   grant a fresh safe window and permits rapid reacquisition. **A jump between the
   planet and orbit, in either direction, always qualifies**
   ([space](SPACE.md), [#150](https://github.com/cjd721/Rimworld-Archinity/issues/150)).
2. Search initially proceeds invisibly. Landing does not reveal a countdown.
   The pursuit quest later announces the approaching threat and reveals the
   estimated time remaining at current Trace.
3. Trace controls search speed continuously: higher Trace accelerates progress,
   lower Trace slows it. Changes take effect without waiting for a periodic
   reassessment window. The visible estimate updates accordingly.
4. Accumulated search progress persists through Trace changes. Reducing Trace
   cannot undo progress already made. Qualifying relocation starts the new search.
5. At detection, the Glitterites send a huge raid scaled by both overall
   difficulty and Trace. They continue sending raids at a configurable interval
   while the colony remains located. Defeating one does not end pursuit.
6. The player may stay and fight. Detection neither forces departure nor causes
   automatic defeat. Reducing Trace after detection does not conceal the location;
   sufficient relocation is required to shake pursuit.
7. Glitterite quests provide opportunities to reduce Trace. These slow an ongoing
   search and improve future search windows, while never erasing accrued progress.

## Campaign progression

The campaign should be hard despite its powerful founders, genes and equipment.
Parking an era remains valid: time's contribution eventually stops growing, while
further development and political actions can still change pressure. There is no
whole-campaign calendar deadline.

Pursuit supports the [Ultra](../plot/ULTRA.md) experience of running, hiding,
stealing and learning, followed by the ability to stand against repeated attacks.
Individual quests and encounters are authored within these rules.

## Player information and agency

Players should broadly understand what is increasing pressure: wealth and
development, era time, military power, religious standing and enemies. A precise
formula need not be exposed.

Before the pursuit quest, remaining search time is hidden. After it, the countdown
is explicitly an estimate at current Trace, and changes explain that rising or
falling Trace is changing search speed. Relocation distance requirements must be
legible so a short hop is an informed risk. Quest opportunities allow Trace
management; movement and fighting remain meaningful alternatives.

## Constraints

- This document selects neither an engine hook nor a mathematical formula.
- Exact contribution weights, time ceilings, distances, search rates, quest reveal
  timing, raid sizes and repeat intervals are balance work.
- No automatic reset of Trace on movement, erasure of search progress by reducing
  Trace, or predictable consequence-free interval between reassessments.
- Multiplayer adaptation must preserve intended behavior across colonies, world
  events and relocation. It must not accidentally multiply pressure or advance
  local deadlines through extra maps or another colony's clock.

## Open questions

- [The storyteller](https://github.com/cjd721/Rimworld-Archinity/issues/60)
  investigates available measurements and control over strength, composition and
  frequency, including world/caravan scope and Multiplayer timing. Capability
  results must distinguish available mechanisms from selected design.
- **Trace and the pursuit are answered**, not open:
  [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) settled variable
  search speed, hidden-then-revealed pursuit, sufficient-distance escape and
  repeated attacks in [`docs/specs/TRACE.md`](../specs/TRACE.md). What remains is
  balance — search rates, distances, reveal timing, raid sizes and repeat intervals,
  already listed under *Constraints*.
- **Raid objectives are answered.**
  [#77](https://github.com/cjd721/Rimworld-Archinity/issues/77) verified all three
  against `docs/specs/PRESSURE.md` § 8. Which objectives the campaign authors, at
  which era and with what weights, is balance and belongs to
  [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119).
- [The faction pressure prototype](https://github.com/cjd721/Rimworld-Archinity/issues/13)
  develops political behavior within these requirements, including the effect of
  alliances. Exact input measurements and any necessary era-transition handling
  remain design choices informed by capability research.
