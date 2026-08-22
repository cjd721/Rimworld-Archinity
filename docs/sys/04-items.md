# 04 — Items & resources

**Blocked by 01.** The kill list is mostly Medieval Overhaul content. **D2 resolved yes —
MO is enabled specifically so it can be gutted, so this brief is now the point of it.**

## What this system must do

Decide what exists in the game at all. Every addition dilutes the vanilla pool, so
additions must earn their slot.

## The governing rule

From `Player Progression Ideology.txt`, and it is the sharpest test in the whole document:

> Any time you add anything to the game, you dilute the pool of vanilla resources in a way
> that is bad. Particularly if those ingredients really only matter during a specific era.

The test, stated operationally:

**Does this resource's use case evolve with the player across eras, or does it become
permanent noise in trade stock and quest rewards after one era?**

Salt fails. You stop caring in the Spacer era, but every trader slot and reward roll it
occupies is wasted for the remaining 500 days. **A resource that stops mattering is worse
than a resource that never existed**, because it keeps costing attention.

## Kill list

Cut outright. All Medieval Overhaul unless noted.

| Thing | Why |
|---|---|
| **Woodworking chain** (wood→planks→boards) | Process step producing a construction input. Fails the Spacer-era test outright. |
| **Paper, paper press, cartography, maps** | Whole system rejected. |
| **Textile spinning + linen** | Same class as woodworking. Tailoring absorbs it. Linen is a pure-noise resource. |
| **Mithril** | A medieval endgame material. We leave the medieval era; power armour supersedes it. |
| **Ingredient bloat** (salt, saffron, etc.) | The canonical failure of the dilution rule. |
| **Most added plants** | MO + VCE add ~30. Keep vanilla plus a curated few. |

## Keep list

Kept, most needing simplification. The pattern is **keep the surface, cut the management**.

| Thing | Treatment |
|---|---|
| **Carrier birds** | Keep, Neolithic, **without the paper chain**. Research it, build a bird post, own birds of any kind → the mechanic unlocks. All narrative, no complexity. |
| **Beekeeping, brewing, winemaking** | Keep as opt-in roleplay. Scale back but they are close to right out of the box. |
| **Mine shaft** | Keep. Place it, forget it, mine early and inefficiently. Model citizen for the QoL class. |
| **Medieval crane** | Keep. Scales through the whole game. |
| **Scarecrow, sprinkler** | Keep — and prefer these over MO's plowed soil, which was buggy in play. |
| **Flour mill, cheese press** | Keep. These change what an ingredient *is*, which is legitimate, unlike a second oven that only holds recipes. |
| **Silk** | Keep as a cloth upgrade, not a spun chain. Silk beds are fine — load-and-leave. |

## The QoL item class — where quest gating lives

A small set of items that **massively improve quality of life without gating progression**.
Scarecrow, mine shaft, crane, sprinkler, trough.

These are the correct target for hard requirements: a specific item wired in via Research
Mod's `reverseEngineeringMaterials` (the item is damaged, not consumed, so the player keeps
the trophy). Resource cost can be near zero — **the going and getting is the cost.**

**The requirement is a guaranteed route, not a quest.** A quest is one route. Trade and
raid loot are others, and lucking into the item early from a trader or a corpse is a
perfectly good outcome — it rewards paying attention. What must never happen is a required
item with no reliable way to obtain it. Every gated item needs at least one guaranteed
source in the acquisition ledger (`sys/05`); more than one is better.

Two rules, both from the Ideology and both easy to violate:

1. **Never gate spine progression this way.** Weapons, armour tiers and core benches take
   resource costs and light item costs only. The doc walks back its own bellows example for
   exactly this reason.
2. **TechBlock interacts here.** You must research most of an era to advance. So a QoL item
   can become *effectively* mandatory — "I need this research to tier up, so I must do this
   quest." That is a feature at low doses and a wall at high ones. Keep the count small.

## Repurposing

We are free to take any asset in any loaded mod and redefine what it is. If we want a
trough that cuts animal food consumption 20%, we find something with the right art and make
it that. `archon-asset-inventory.md` is the catalogue.

This is how the QoL class gets populated without new art.

## Work items

- [ ] Execute the kill list with `PatchOperationRemove` once D2 lands. **Neuter referencing
      defs first, remove research last** — deleting a `ResearchProjectDef` strips the
      prerequisite off its dependants and leaves them buildable with no research.
- [ ] Curate the plant set: vanilla + a named few, tiered across basic/intermediate/advanced
      agriculture. Target a number, then cut to it.
- [ ] Build the **QoL item ledger**: item, what it does, which research, which faction or
      quest supplies the requirement. Keep it short — this is a garnish, not a system.
- [ ] Rule on `woodChain` (never decided; same class as `metalChain`, which is off).
- [ ] Resolve the two-grape-plants collision if MO lands (`DankPyon_Plant_Grape` vs
      `VFEM2_Plant_Grape`) — no compat patch exists anywhere.
- [ ] Check `check_availability.py` still enforces the locked rule: 2–4 materials per
      requirement, ≥1 craftable/harvestable, flavour item raider-sourced, nothing ships
      under 2 acquisition routes.
- [ ] Note: MO's `component_replace` hits 395 ThingDefs and is half-broken — leave it off.
- [ ] Note: crossbow / heavy crossbow / handgonne need `DankPyon_IronIngot` and are dead
      under no-new-metals. VFEM2's Arbalest, HandCannon and Arquebus cover those slots.
- [ ] Note: MO moves `Bow_Recurve` / `Bow_Great` off `CraftingSpot`, removing the early bow.
      Needs a fix if MO lands.
