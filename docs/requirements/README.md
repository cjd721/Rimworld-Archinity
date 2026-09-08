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

The four documents here predate the template and sit at uneven levels of detail. Migrate a
document to the template when the owning requirements ticket next touches it; do not
reformat one for its own sake.
