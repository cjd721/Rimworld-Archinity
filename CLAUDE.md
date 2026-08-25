# Archinity

A suite of RimWorld 1.6 mods for one long two-player co-op playthrough on the
**Multiplayer** mod. Neolithic start, every tech era in order, endgame in orbit.

Most of the project is pure XML defs. One C# assembly ships: `Archinity.Altar`.

## How we work

Two modes. Know which one you are in.

**Design** — theory crafting, narrative, progression and quest shape, figuring out
what fun looks like. Read `docs/WAYSTONE.md` first: the premise, the arc, and what
this campaign is protecting. Then `docs/rimworld-design-philosophy.md` for how
RimWorld works as a game and the tests any addition has to pass. Do not bring
technical jargon into the realm of imagination.

**Implementation** — defs, code, diffs, integrations, tooling. Read
`CODING_STANDARDS.md` before touching a def or a `.cs` file. It carries the hard
constraints, the silent-failure list, the verification commands and the test
discipline, and several of its rules fail with **no error message at all** — you
will not discover them by running the game. You do not need the design docs to
write a patch. Carefully engineer the simplest solution to what was actually
asked.

## Agent skills

### Issue tracker

Issues live as GitHub issues on `cjd721/Rimworld-Archinity`, driven by the `gh`
CLI. `scratch/` is recon prose, not the tracker. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles, used verbatim as label strings. See
`docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and one `docs/adr/` at the repo root, both created
lazily. See `docs/agents/domain.md`.

## What earns a slot in this file

This file is the map, not the manual. It says what Archinity is, which mode you
are in, and where the real instructions live. Everything else is filed elsewhere:

- How code and defs get written → `CODING_STANDARDS.md`
- Verified facts, so they are never re-litigated → `docs/technical-findings.md`
- Design intent and the campaign's North Star → `docs/WAYSTONE.md`

If something here grows longer than a pointer, it is probably misfiled.
