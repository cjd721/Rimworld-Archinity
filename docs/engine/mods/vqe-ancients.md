# VQE Ancients — archite injection

The archogen injector: what gene pool it draws from, what outcomes it rolls, the
three things that must be true before it will fire, and why a blood cost cannot
be bolted on in XML.

Verified against decompiled RimWorld 1.6.4871 unless an entry says otherwise.
These are *verified available mechanisms*, not commitments to use them —
selection happens in `docs/specs/`.

---

## Gene pool

`GetFilteredGenes(pawn, g => g.biostatArc > 0)` — every archite gene in the
loaded def database, minus `InjectionBlacklistDef`, minus genes the pawn has,
minus genes whose prerequisite is unmet. ~50 genes with our load order,
including `VRE_Transcendent` (now blacklisted in `Archinity.Pacing`).

`blacklistedGenes` is `List<string>` — plain defName strings, not
cross-referenced. Naming an absent gene is silently ignored, so the patch is
safe to over-specify.

## Outcome table

| Outcome | `baseWeight` |
|---|---|
| Success | 50 |
| Rejection | 35 |
| Spliceling | 8 |
| Splicehulk | 5 |
| Splicefiend | 2 |

All patchable. Optional looted facilities modify results — `VQEA_TraitSelectionPrism`
gives a choice of two archite genes instead of one random.

## Three independent gates

1. **The machine.** `VQEA_ArchogenInjector` inherits `neverBuildable: true`, but
   its base sets `minifiedDef: MinifiedThing` and `claimable: true`. You cannot
   build one — you find it in a vault, claim it, uninstall it, haul it home.
   Same for every support facility.
2. **Power.** 400 W running, 50 W idle. Hard requirement — see below.
3. **Ammo.** One `ArchiteCapsule` per injection. Not craftable by anyone at any
   tech level; the item description says so. Trade-only (outlander bases and
   caravans, orbital traders, Empire bases) plus ancient crate loot.

## Blood cannot gate it without C#

`Building_PawnProcessor.PowerOn` dereferences the power comp unguarded:

```csharp
public bool PowerOn => TryGetComp<CompPowerTrader>(this).PowerOn;
```

Read every tick via `ShouldProcessTick()`. Removing `CompProperties_Power`
causes a continuous NullReferenceException.

Adding `CompProperties_Refuelable` with a `HemogenPack` filter is crash-free and
gives a real fuel bar, but **does not gate** — VQEA's code never reads
`CompRefuelable`. Cosmetic only; the rule and its silent failure are
`docs/TRAPS.md` T-24.

The capsule requirement is also not def-driven: `ThingDefOf.ArchiteCapsule` is
hardcoded in seven places, so hemogen cannot be added as a second ingredient.

Real gating requires ~10 lines of Harmony postfixing
`Building_PawnProcessor.get_PowerOn`. Deterministic, no RNG, reads only synced
state — assessed multiplayer-safe, but it means shipping an assembly.

Decay behaviour of the crated injector and of `ArchiteCapsule` is in
`docs/engine/items-and-materials.md` — both keep indefinitely.
