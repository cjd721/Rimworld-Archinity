# Technical specifications

**What a technical specification owns:** whether RimWorld 1.6 can satisfy a system's
requirements, the **routes** by which it could, and what each route gets us and costs —
verified deeply enough that a narrative session can rely on it, and no deeper.

This directory holds those answers, organized by coherent system. It is not a place for
fiction (`docs/plot/`), for gameplay rules (`docs/requirements/`), or for what becomes
available and when (`docs/progression/`). **It is also not yet the buildable spec.** That
is the destination of the next map, which starts from a *selected* route and a written
beat; a spec here answers what is possible before anyone has chosen what to build.

## Index

| Area | Specs |
|---|---|
| Faith | [The altar](ALTAR.md) · [Religion](RELIGION.md) · [The psychic track](PSYCHIC.md) · [Transcendence](TRANSCENDENCE.md) |
| Politics | [Faction politics](POLITICS.md) · [Territory](TERRITORY.md) · [Pressure](PRESSURE.md) · [Encounters](ENCOUNTERS.md) |
| Glittertech | [Trace and the Glitterite pursuit](TRACE.md) · [Spendable currencies](CURRENCIES.md) · [Hacking](HACKING.md) · [Androids](ANDROIDS.md) · [Research](RESEARCH.md) |
| World and space | [Era](ERA.md) · [Charting](CHARTING.md) · [World infrastructure](WORLD-INFRASTRUCTURE.md) · [Orbit](ORBIT.md) · [Gravship](GRAVSHIP.md) |
| Colony | [Colony management](COLONY.md) · [Shipped defaults and presets](DEFAULTS.md) · [Items and gear](ITEMS.md) · [Specialisation](SPECIALISATION.md) |

[The integration register](INTEGRATION.md) lists the capability gaps still open across all of
these specs.

## Organize by system, not by mod or by ticket

Several capability tickets contribute to one spec. `RELIGION.md` can absorb the findings
of the Reverence, propagation, institution and Exaltation investigations. A sufficiently
substantial subsystem earns its own document when the content warrants it — do not
manufacture a document for every hook someone investigates.

## Where a research result goes

- **The issue** retains the investigation, the evidence and the resolution.
- **The system's spec** retains the verdict, the routes, their constraints and the open
  questions.
- **`docs/engine/`** retains broadly reusable engine and mod facts worth knowing
  outside the system, filed by subject, with a link rather than a copied
  investigation. If the finding is a behaviour that fails **silently**, it goes to
  the register at **`docs/TRAPS.md`** instead and is cited by ID.

## Answer the requirement that was asked

**A spec answers the requirement as written, not the build an agent imagines behind it.**
The specs written before 2026-09-16 regularly followed leads no requirement gave: they
picked a route, then designed it to the method signature and the line count. That is
build work, it is the next map's, and it cost this map two weeks.

The test for a paragraph: **would a narrative session writing a beat need it to know what is
possible?** If yes, it belongs. If it only matters once someone has decided to build this
route, it does not — stop there; it is the next map's.

Depth is still owed. **An unread assumption is wrong far more often than a read one**; the
evidence rules in `docs/agents/capability-research.md` stand in full. Verify that a route
exists and what it can do. Do not design it.

## Lead with the answer

**The first thing a reader meets is the verdict and the routes.** The survey — what exists,
what does not, which donor was ruled out and why — supports them and sits below.

A spec that opens on a catalogue of absences reads as a dead end, and the section a reader
gives up before reaching is the section nobody checks: `RELIGION.md`'s first draft buried its
answer four screens down, and the buried answer was also partly wrong.

### Verdict

Two lines, always:

- **Possible?** Yes · Partly (say which part) · No
- **Multiplayer?** Yes · With work (say what) · No · Unknown (say what would settle it)

### Routes

One row per genuinely different way to satisfy the requirement. Usually one to three.

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| A | The capabilities the player and the story actually receive | vanilla / named mod / our code | XML · patch · C# | Easy · Medium · Hard | Yes · With work · No |

**Weight** is development weight, not a price:

- **Easy** — defs and XML patches, or an existing mod used as it ships. No Harmony.
- **Medium** — a contained piece of C# on a seam that is verified to exist: a component, a
  worker subclass, a handful of patches.
- **Hard** — a new system: its own state, UI, many patches, or synchronization work beyond
  what Multiplayer and MP Compat already carry.

No line estimates. Mark a route **not recommended** where it is technically possible and
there is no good reason to take it, and say why in a clause.

Under the table, for each route that survives: **what it gets us** as a list of levers the
story can pull, **what it cannot do**, and **consequences** — what it forecloses, what it
drags in, what it conflicts with. That list is what a narrative session reads; write it for
that reader.

**Verified is not selected.** Say which route you would recommend and why, but a spec never
selects one. Selection is a story decision, taken on the next map.

## Template

```markdown
# <System>

## Purpose and scope
Which requirements this answers, linked to their source.
What this document owns and where adjacent systems take over.

## Verdict
Possible? Multiplayer? Two lines.

## Routes
The routes table, then per route: what it gets us, what it cannot do, consequences.
The recommendation, if any, and why — not a selection.

## Constraints
Engine facts that bound every route: what no route can do, and the traps (by T-ID)
a narrative session would otherwise write straight into.

## Available mechanisms
Relevant vanilla, DLC and mod support — the survey behind the routes.
What each provides, its limitations, and the evidence.
What does not exist, where that shaped the routes.

## Status
What is verified and what is inferred. The evidence class, and links to the capability
issues that established it.

## Open questions
Capability questions only: a requirement clause no route answers yet, or a route claim
not yet verified — each pointing at the ticket that answers it. Decisions (which route,
which value, which shape) are not listed; choosing is the next map's.
```

## Specs written before the routes rule

Most specs in this directory predate it and lead with a single designed build: *The build*,
state ownership, persistence, a cost table in lines. **They are not re-run.** Their evidence
stands and their build sections are kept for the next map, which will need them. Where one
already lists priced options (`CURRENCIES.md`, `WORLD-INFRASTRUCTURE.md`), those are routes
under another name. The cross-spec integration pass reconciles them, and the capabilities
summary reads routes out of them.
