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

- `docs/VISION.md`, `docs/MAP.md`, `docs/PROGRESSION-MAP.md` — what the playthrough is
- `docs/rimworld-design-philosophy.md` — the design bar
- `docs/technical-findings.md` — noisy-failure engineering notes (the silent ones live in `CLAUDE.md`)
- `docs/HANDOFF.md` — current state between sessions

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
