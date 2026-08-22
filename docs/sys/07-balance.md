# 07 — Balance

**Blocked by 02, 03, 04.** This is the last pass. Do not start it early — every number
here moves when the tree, the benches or the item set move.

**Read `QUESTLINE.md` alongside this brief** for the beat structure and the altar power
curve this pass is setting numbers for.

## What this system must do

Make every step forward feel earned and every upgrade actually be one.

Two distinct jobs that get conflated:

1. **Ladder integrity** — leather → boiled leather → hardened leather must each be a real
   improvement, at each rung, on the stats that matter.
2. **Pacing** — how long an era takes, and whether the player is ever stuck with nothing
   to do or drowning in options.

## Ladder integrity

The failure mode is a tier that costs more, requires more research, and is not better —
or is better only on a stat nothing cares about.

Known instances already recorded:

- **`VFEM2_LeatherBoilpot`** — `StuffPower_Armor_*` values mean hardleather is **not worth
  boiling**. Needs `PatchOperationReplace`. This is the canonical example of the whole
  problem class.
- **`PlateArmor`** bundles two distinct armour rungs into one research node. Split them.
- **Archoplate** buff already agreed: Sharp → 2.00, Blunt → ~1.20, Heat → ~1.50, shield
  energy 5.6 → ~20 with ~2× recharge. Keep `disarmedByEmpForTicks`.

**Method:** for each equipment family, table every rung against the stats that matter for
that family, and confirm monotonic improvement. Where a rung is flat or negative, either
buff it or cut it. A tier that exists only to be skipped should not exist.

## Food buffs

`Player Progression Ideology.txt` wants food to matter, on the Palworld model:

- Different foods give different **kinds** of benefit — satiety, work speed, defence, offence.
- The **scale** of the buff rises with ingredient quality.
- Early game tops out around **+10%**; late game around **+30%**.
- Recipe complexity stays **linear** — each tier adds one *generic* ingredient class, never
  a new processing chain.

The ladder, as sketched:

| Tier | Ingredients |
|---|---|
| 1 | one meat |
| 2 | meat + 1 other |
| 3 | any 2 vegetables + any meat |
| 4 | + eggs (now you keep animals) |
| 5 | + one processed input (flour, cheese) |

**The load-bearing detail: ingredients are specified by class, not by named crop.** "Any two
vegetables," never "corn and potatoes." The player should never be optimising which specific
plant to grow for which specific recipe — that is the exact failure the doc is written against.

## Pacing

- **A RimWorld year is 60 days.** Every duration estimate must use this.
- Neolithic intro target: **~20–30 days** to clear the initial tribal research and unlock the
  base jobs and gizmos.
- Medieval three-leap structure approved: Forge ~5,100 / Mail+Siege ~12,400 /
  Plate+Powder ~13,400 points.
- `requiredPointsMedieval` **0.75 (~88 bench days) vs 1.0 (~117)** — undecided, see `sys/02`.
- **Chronicle beat gaps are held as variables** pending this pass. `QUESTLINE.md` §9 is
  explicit: the prior ~45–50 day gaps were too long — a full year between beats means the
  player has forgotten the altar exists. Denser, mostly-small beats.

## The altar power curve

From `QUESTLINE.md` §9 — the balance reference, not a target:

| Era | Failure chance | Listed cost | Effective cost |
|---|---:|---:|---:|
| Neolithic | 25% | 1 | 1 |
| Medieval | ~19% → ~15% | 2–3 | ~1.5 |
| Industrial | ~11% | 4 | ~2 |
| Spacer | ~7% | 6–8 | ~3.5 |
| Ultra | ~2% | 12–20 | ~6–9 |
| Archotech | ~0% | 50 | ~23 |

**Risk falls monotonically while cost rises superlinearly.** Efficiency never means mercy;
it means scale.

## Work items

Nothing here should start before 02, 03 and 04 land.

- [ ] Equipment ladder audit — every armour and weapon family, every rung, monotonicity
      confirmed. Start with the leather chain, which has a known break.
- [ ] Fix `VFEM2_LeatherBoilpot` `StuffPower_Armor_*`.
- [ ] Split `PlateArmor`'s two rungs.
- [ ] Apply the archoplate buff.
- [ ] Author the food buff ladder — buff kinds, magnitudes per tier, generic ingredient
      classes.
- [ ] Set era durations, then **set Chronicle beat gaps** — this unblocks the last of
      `QUESTLINE.md`.
- [ ] Rule on `requiredPointsMedieval`.
- [ ] Verify `VQEA_Electromagnetized` holds the archoplate shield through EMP. The whole
      Ultra-era reward rests on it.
- [ ] Produce a turn-to-turn walkthrough of the Medieval route mapped onto the three leaps —
      the cheapest way to find pacing holes without playing 100 days.
