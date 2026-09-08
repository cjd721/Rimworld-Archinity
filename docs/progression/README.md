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

**A cell waits on the beat that supplies it. The grid does not wait on the acts.** The
domains, the row vocabulary and the era columns are scaffolding and come first; where a
finer subdivision genuinely depends on an unauthored encounter, leave that column at era
resolution and let the era fill ticket refine it. The faction grid is the clearest case:
its worldgen column is read off `docs/requirements/RELIGION.md` and settled world rules,
not off any beat, and it has a real deadline.

Each domain defines its own checks — meaningful intermediate choices, staggered upgrades,
manageable unlock groups, deliberate ceilings. A flat row is not automatically a defect.
Research transitions are derived **after** the desired states, not before.
