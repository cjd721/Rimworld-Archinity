# Progression grids

**What a progression grid owns:** what becomes available to the player, and when.

One grid per domain. **Rows** are the domain's vocabulary — pools, categories, factions,
equipment lines. **Columns** are the eras and their meaningful capability leaps. **Each
cell** states what is available at that point, its prerequisites and its acquisition
route. Empty cells are expected and meaningful: a domain that does not change in an era
says so, and a row that never changes is a row that probably should not exist.

Each domain has **one** grid, filled by every era ticket in turn. Do not write a separate
prose ladder per era — that is the failure mode this directory exists to prevent.

## What a grid is not

- Not fiction, and not gameplay rules — `docs/plot/` and `docs/requirements/`.
- Not a sourcing verdict. A grid names a capability row; the sourcing ledger says which
  mod supplies it, what we restat, what we author and what we actively block.
- Not balance. Costs, durations, threat magnitudes and progression rates come last.

## Where a grid comes from

A **cell** is read off the requirements in `docs/requirements/` and, where the content is
authored, off the beats in `docs/plot/`. A beat says *the founders reach a place and take
from it a method that makes the altar spend less blood, and a gift of strength*; the cell
then says which exact items, which research node, and in what order.

**Scaffolding first, fill after.** Enumerating the domains, the row vocabulary, the era
columns and each domain's checks does **not** wait on the acts; those are the shape of the
grid, and they have to exist before anything can be written into one. Filling an era's
column *does* wait on the acts that supply that era's content, which is why every era fill
ticket is blocked by its act and the scaffolding ticket is blocked by neither.

The faction grid is the exception worth knowing: its worldgen column is read off
`docs/requirements/RELIGION.md` and the settled world rules rather than off any beat, and
it has a real deadline — the `FactionDef` set freezes silently the instant the world
generates.

Each domain defines its own checks — meaningful intermediate choices, staggered upgrades,
manageable unlock groups, deliberate ceilings. A flat row is not automatically a defect.
Research transitions are derived **after** the desired states, not before.

**When an era began — and when each prior era began — is
[`docs/specs/ERA.md`](../specs/ERA.md)'s `GameComponent_Era`.** A grid cell that wants
*"N days after the Medieval gate"* reads `StartTickOf(TechLevel.Medieval)`; the boundary log is
retained after the colony leaves that era, so a cell may key off a boundary the campaign has
already passed. Established by
[#109](https://github.com/cjd721/Rimworld-Archinity/issues/109), which found that nothing owned
the clock and that `AdvanceEra()` — assumed shipped by
[#7](https://github.com/cjd721/Rimworld-Archinity/issues/7) — had never been built.
