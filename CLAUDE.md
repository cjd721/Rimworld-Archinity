# Archinity

A suite of RimWorld 1.6 mods for one long two-player co-op playthrough on the
**Multiplayer** mod. Neolithic start, every tech era in order, endgame in orbit.
It is designed, built and playtested as single-player and migrated to Multiplayer
afterward by patch — the fiction is allowed to forget there are two players, the
code never is. See `docs/PLOT.md`.

## How we work

Two modes. Know which one you are in.

**Design** — start with `docs/PLOT.md` for the campaign overview and chapter
links. The relevant era chapter in `docs/plot/` carries its events;
`docs/requirements/` states what Charting, religion, the altar and Glittertech
must do, and `docs/specs/` states how. For fictional mechanisms, read
`docs/COSMOLOGY.md`. Writing tone and revelation are in the overview. The
current campaign reflects the final September 2026 map; older ticket comments
and archived drafts may describe superseded designs.

**Implementation** — defs, code, diffs, integrations, tooling. Read
`CODING_STANDARDS.md` before touching a def or a `.cs` file. It carries the hard
constraints, the silent-failure list, the verification commands and the test
discipline, and several of its rules fail with **no error message at all** — you
will not discover them by running the game. You do not need the design docs to
write a patch. Carefully engineer the simplest solution to what was actually
asked.

## Ground rules

**Work directly on `main`. Do not create branches.** No feature branches, no
`research/*` branches, no worktrees. One dev, one repo, no review gate — a
branch buys nothing here and costs a merge.

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
- The plot: what happens, in what order → `docs/PLOT.md`
- Era narratives → `docs/plot/`
- What campaign systems must do → `docs/requirements/`
- How they will do it → `docs/specs/`
- What is available, and when → `docs/progression/`
- How anima, the channel and the price work → `docs/COSMOLOGY.md`

Anything in `docs/archive/` is history, not authority — including `STORY-CANON.md`
and `cosmology-in-practice.md`, both superseded by the campaign references above. Do not
read them for a current answer.

If something here grows longer than a pointer, it is probably misfiled. The one
standing exception is **Ground rules** above: workflow rules have no other home,
and an agent that misses one has already done the wrong thing by the time anyone
could point it at a document.
