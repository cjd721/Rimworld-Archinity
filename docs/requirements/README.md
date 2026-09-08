# Requirements

**What a requirements document owns:** the intended experience, meaning, behavior and
constraints of a campaign system. It establishes what must be delivered. It does **not**
establish that the implementation exists — that is `docs/specs/`.

A requirement states the conditions a **capability** must satisfy. A capability is
something the game must be able to do, defined by observable behavior, independently of
its implementation:

- Maintain a persistent measure of religious adoption for each faction.
- Discover the next eligible campaign site through pawn labor.
- Let a hacker at home interact with a system through a deployed pawn.

A mod is a possible *provider* of capabilities. One idea may demand several.

**Where requirements come from.** They are derived from the campaign arc in `docs/PLOT.md`
and the era chapters in `docs/plot/`. Where they are incomplete, the owning design ticket
fills them in. Requirements work may precede capability research; it is never gated on
individually authored beats.

**Gameplay rules live here, not in the plot.** *Reverence decays. Intel is spent. Charting
prioritizes ordered discoveries.* Those are requirements, not fiction.

**Boundaries.**

- `docs/plot/` — the particular events through which the player encounters the system.
- `docs/specs/` — how the system will satisfy these requirements.
- `docs/progression/` — what becomes available and when.
- `docs/technical-findings.md` — cross-cutting engine and mod facts.

## Template

```markdown
# <System>

## Purpose
Why this system exists in the campaign.
The experience and choices it should create.

## Meaning
What its concepts represent in the fiction and in play.
Distinctions that must remain clear.

## Required behavior
What the player and world can do.
Triggers, prerequisites, outcomes and interactions.
Rules that hold across individual narrative events.

## Campaign progression
How access and behavior change across the campaign.
Link to the chapters that introduce or transform the system.

## Player information and agency
What the player can see, understand, choose, refuse or recover from.

## Constraints
Boundaries the solution must respect.
Include explicit exclusions only where they prevent a plausible misreading.

## Open questions
What has not been decided, linked to the owning issues.
```

## Migrating the four existing documents

They predate the template and sit at uneven levels of detail. Migrate one when the owning
requirements ticket next touches it; do not reformat a document for its own sake.

Each currently closes with a `## Saved state and remaining work` section, which the
template has no slot for because it holds three different things. Split it on migration:

- **State enumerations** — what must be saved, and per what — go to the system's technical
  spec, under *Persistence and multiplayer*.
- **Undecided rules** stay here, under *Open questions*, linked to the owning issue.
- **"Remains to be verified"** goes to the spec, under *Status* or *Verification*.

**Known technical material to move out**, identified but deliberately not yet moved — each
belongs to `docs/specs/` and to the capability ticket named:

- `CHARTING.md` — the *Implementation pattern* paragraph (the Long-Range Mineral Scanner
  grammar) and the Deserters-style world-state cursor. [#57](https://github.com/cjd721/Rimworld-Archinity/issues/57), [#40](https://github.com/cjd721/Rimworld-Archinity/issues/40).
- `RELIGION.md` — "an Empire-like scale" / "the Church's Honor-equivalent" ([#53](https://github.com/cjd721/Rimworld-Archinity/issues/53));
  "Influence is the Schism's equivalent of Deserters Intel" ([#54](https://github.com/cjd721/Rimworld-Archinity/issues/54)); the commitment
  to a bespoke political UI ([#61](https://github.com/cjd721/Rimworld-Archinity/issues/61)); the storyteller incident-selection hook
  ([#60](https://github.com/cjd721/Rimworld-Archinity/issues/60)).
- `GLITTERTECH.md` — "the Ultra counterpart to Deserters Intel" ([#55](https://github.com/cjd721/Rimworld-Archinity/issues/55)); deferring
  the Trace/Visibility name to whatever implementation reads better ([#56](https://github.com/cjd721/Rimworld-Archinity/issues/56)).

In each case the **requirement** is the observable behavior; the named carrier is the
mechanism and does not belong here.
