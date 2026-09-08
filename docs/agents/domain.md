# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

**Layout: single-context.** One `CONTEXT.md` at the repo root, one `docs/adr/` at the
repo root. If the suite ever splits into contexts that need their own vocabulary,
add a root `CONTEXT-MAP.md` pointing at per-context `CONTEXT.md` files and update
this line.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root: the glossary of domain terms.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in.

If either doesn't exist, **proceed silently**. Don't flag its absence; don't suggest
creating it upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and
`/improve-codebase-architecture`) creates them lazily when terms or decisions actually
get resolved.

## Related docs already in this repo

These predate the skill setup and are not ADRs, but they carry real decisions —
read them when the topic overlaps:

- `docs/PLOT.md` — campaign overview, tone and links to era chapters.
- `docs/plot/` — Neolithic through the ending, one chapter per phase.
- `docs/requirements/` — what Charting, religion, altar progression and Glittertech/pursuit must do.
- `docs/specs/` — the technical designs that satisfy them, including ones still in progress.
- `docs/progression/` — the domain grids: what becomes available, and when.
- `docs/COSMOLOGY.md` — anima, the channel and selfhood, for writers.
- `docs/technical-findings.md` — verified engine and mod behavior; coding rules are in `CODING_STANDARDS.md`.

Superseded, and kept in `docs/archive/` as history rather than authority:
`VISION.md`, `MAP.md`, `PROGRESSION-MAP.md`, `HANDOFF.md`, `STORY-CANON.md`,
`cosmology-in-practice.md`. Do not read them for a current answer.

## File structure

```
/
├── CONTEXT.md
├── docs/
│   ├── adr/
│   │   ├── 0001-....md
│   │   └── 0002-....md
│   └── agents/          ← this directory
└── Archinity.*/         ← the mods
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a
hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to
synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're
inventing language the project doesn't use (reconsider) or there's a real gap (note
it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently
overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
