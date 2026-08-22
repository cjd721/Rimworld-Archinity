# RimWorld 1.6 — Item decay research (Archinity)

All evidence from vanilla 1.6 defs + ILSpy decompile of
`.../RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll`.

---

## 0. The deterioration engine (background — needed for all 4 answers)

Full-assembly decompile confirms there are **exactly two** call sites that apply
deterioration damage in the whole game:

- `RimWorld/SteadyEnvironmentEffects.cs` — `TryDoDeteriorate()` / `DoDeteriorationDamage()`
- `RimWorld/Genepack.cs` — `Genepack.TickRare()`

(verified via `grep -rl "DoDeteriorationDamage"` over the decompiled project — only those
two files.) `SteadyEnvironmentEffects.FinalDeteriorationRate` is referenced only by
`SteadyEnvironmentEffects` itself and by `Verse/Thing.cs:1396` (inspect-string text only).

### Gate 1 — `ThingDef.CanEverDeteriorate` (`Verse/ThingDef.cs:714`)

```csharp
public bool CanEverDeteriorate
{
    get
    {
        if (!useHitPoints) return false;
        if (category != ThingCategory.Item)
        {
            if (plant != null) return plant.canDeteriorate;
            return false;
        }
        return true;
    }
}
```

So: **only `category == Item` (or plants) can ever deteriorate.** Buildings never do.

### Gate 2 — the `DeteriorationRate` stat

`Data/Core/Defs/Stats/Stats_Basics_General.xml:166`

- `<defaultBaseValue>0</defaultBaseValue>`, `<minValue>0</minValue>`
- All `parts` are **multiplicative**: `StatPart_Quality`, `StatPart_EnvironmentalEffects`,
  `StatPart_Pollution`, `StatPart_NoxiousHaze`, `StatPart_ToxicFallout`,
  `StatPart_NearHarbingerTree`, `StatPart_ShamblerCorpse`.
- Therefore **base 0 ⇒ final 0, always**. Nothing can multiply it back up.

`SteadyEnvironmentEffects.FinalDeteriorationRate`:

```csharp
if (!t.def.CanEverDeteriorate) return 0f;
float num = t.GetStatValue(StatDefOf.DeteriorationRate);
Genepack genepack = t as Genepack;
if (ModsConfig.BiotechActive && genepack != null && !genepack.Deteriorating) num = 0f;
if (num <= 0f) return 0f;
...
```

### Gate 3 — environment (`RimWorld/StatPart_EnvironmentalEffects.cs`)

```csharp
private bool ActiveFor(Thing t)
{
    if (t != null && t.Spawned) return t.def.deteriorateFromEnvironmentalEffects;
    return false;
}
```

When active, `val *= num` where `num` starts at **0** and accumulates
`+0.5` unroofed, `+0.5` outdoor-temperature room, `+terrain.extraDeteriorationFactor`,
`×Lerp(1,5,rainRate)` if unroofed, `×protectedByEdificeFactor (=0)` if on a shelf.

**Consequence:** a normal item that is indoors + roofed gets `num = 0` ⇒ rate 0.
That is why "store it inside" works in vanilla. It only works for defs with
`deteriorateFromEnvironmentalEffects = true` (the ThingDef default,
`Verse/ThingDef.cs:121`).

`SteadyEnvironmentEffects.ProtectedByEdifice` + `building.preventDeteriorationOnTop`
(only `ShelfBase`, `Data/Core/Defs/ThingDefs_Buildings/Buildings_Furniture.xml:1547`)
is applied *through the same StatPart*, so shelves also only help defs that opt into
environmental effects.

### Unspawned things

```csharp
public static float FinalDeteriorationRate(Thing t, List<string> reasons = null)
{
    if (t.Spawned) { ... }
    if (t.SpawnedOrAnyParentSpawned && !t.def.canDeteriorateUnspawned) return 0f;
    return FinalDeteriorationRate(t, roofed: false, roomUsesOutdoorTemperature: false, null, reasons);
}
```

`canDeteriorateUnspawned` (`Verse/ThingDef.cs:123`, default **false**) is referenced
*only* here. Since this overload is called only from `Verse/Thing.cs` (inspect string),
in practice items inside containers/inventories/caravans are never ticked for
deterioration by `SteadyEnvironmentEffects` at all — that loop
(`DoCellSteadyEffects`) walks `c.GetThingList(map)`, i.e. spawned things only.

---

## 1. ArchiteCapsule — **does NOT deteriorate, rot, or decay. Ever.**

Def: `Data/Biotech/Defs/ThingDefs_Items/Items_Various.xml:83-121`

```xml
<ThingDef>
  <defName>ArchiteCapsule</defName>
  <thingClass>ThingWithComps</thingClass>
  <statBases>
    <MaxHitPoints>200</MaxHitPoints>
    <MarketValue>700</MarketValue>
    <Mass>0.5</Mass>
    <Flammability>0</Flammability>
  </statBases>
  <stackLimit>25</stackLimit>
  <category>Item</category>
  <comps>
    <li Class="CompProperties_Forbiddable"/>
  </comps>
</ThingDef>
```

Evidence, point by point:

| Property | Value | Source |
|---|---|---|
| `deteriorationRate` / `<DeteriorationRate>` statBase | **absent** ⇒ 0 (stat `defaultBaseValue` 0) | `Stats_Basics_General.xml:171` |
| `tickerType` | **absent** ⇒ `TickerType.Never` (field `public TickerType tickerType;`, `Verse/ThingDef.cs:17`, no initializer ⇒ enum 0 = Never) | decompile |
| `CompRottable` | **absent** — only comp is `CompProperties_Forbiddable` | def |
| Needs shelter / roof / cold storage | **No.** Rate is 0 before any environmental StatPart runs (`if (num <= 0f) return 0f;` precedes everything) | `SteadyEnvironmentEffects.FinalDeteriorationRate` |
| Flammability | 0 — cannot burn | def |
| No mod/DLC patch touches it | `grep -rl ArchiteCapsule` over `Data/` hits only `Items_Various.xml`, TraderKindDefs and ThingSetMakerDefs; VQE-Ancients has no patch on it | grep |

**Verdict: definitive — an archite capsule left on bare dirt, outdoors, unroofed, in
rain, for 20 in-game years takes zero decay damage.** It is still destructible by
ordinary damage (explosions, raider fire) because `useHitPoints` defaults true, but
there is no passive decay of any kind.

## 2. Genepack — **YES, it decays. Confirmed. And it is nastier than normal items.**

Def: `Data/Biotech/Defs/ThingDefs_Items/Items_Various.xml:30-58`
(parent `GeneSetHolderBase`, same file lines 4-28)

```xml
<ThingDef ParentName="GeneSetHolderBase">
  <defName>Genepack</defName>
  <thingClass>Genepack</thingClass>
  <tickerType>Rare</tickerType>
  <useHitPoints>true</useHitPoints>
  <canDeteriorateUnspawned>true</canDeteriorateUnspawned>
  <deteriorateFromEnvironmentalEffects>false</deteriorateFromEnvironmentalEffects>
  <statBases>
    <MarketValue>100</MarketValue>
    <DeteriorationRate>5</DeteriorationRate>
  </statBases>
</ThingDef>
```
`GeneSetHolderBase` supplies `<MaxHitPoints>100</MaxHitPoints>`.

### Mechanism / classes

- **Class:** `RimWorld.Genepack : GeneSetHolderBase` (`RimWorld/Genepack.cs`).
- The decisive property:

```csharp
public bool Deteriorating
{
    get
    {
        CompGenepackContainer parentContainer = ParentContainer;
        if (parentContainer == null || !parentContainer.PowerOn) return true;
        return false;
    }
}
```
`ParentContainer` is `base.ParentHolder as CompGenepackContainer` — i.e. **only** being
inside a `CompGenepackContainer` **that is powered on** stops decay.

- **Two decay paths:**
  1. Lying on the map (stockpile, shelf, floor, indoors or out) → spawned →
     `SteadyEnvironmentEffects.TryDoDeteriorate` → `Rand.Chance(rate / 36f)` per cell
     visit, `DoDeteriorationDamage` → 1 damage.
  2. Inside an **unpowered** gene bank → `CompGenepackContainer.CompTickRare()` calls
     `innerContainer[i].TickRare()` → `Genepack.TickRare()`:
     ```csharp
     deteriorationPct += statValue * 250f / 60000f;
     if (deteriorationPct >= 1f) { deteriorationPct -= 1f;
         SteadyEnvironmentEffects.DoDeteriorationDamage(this, PositionHeld, MapHeld, sendMessage: true); }
     ```

- **Roofs, walls, indoor rooms and shelves do NOT help.** `deteriorateFromEnvironmentalEffects=false`
  makes `StatPart_EnvironmentalEffects.ActiveFor()` return false, so the ×0 indoor/shelf
  multiplier never applies. The flat 5 HP/day always stands.

### Grace period

**There is none.** Decay starts immediately and is linear:
`100 MaxHitPoints ÷ 5 DeteriorationRate = 20 in-game days` from pristine to destroyed.
(Destruction is via `TakeDamage(DamageDefOf.Deterioration, 1f)`; `messageOnDeteriorateInStorage`
defaults true, so you get the "deteriorated away" message.)

### What prevents it — `GeneBank`

Def: `Data/Biotech/Defs/ThingDefs_Buildings/Buildings_Misc.xml:217-272`
Its in-game description literally says: *"When powered, gene banks prevent genepacks from
deteriorating and will slowly repair deterioration."*

| Field | Value |
|---|---|
| defName | `GeneBank` |
| Parent | `GeneBuildingBase` (same file, line 137) |
| **Research prerequisite** | **`Xenogermination`** (label in-game: *xenogenetics*), inherited from `GeneBuildingBase` line 138-140 |
| Research tech level / cost | `Industrial`, `baseCost 1000`, prerequisite research **`Electricity`** (`Data/Biotech/Defs/ResearchProjectDefs/ResearchProjects_Misc.xml:29-38`) |
| **Power draw** | **`basePowerConsumption 40`** W, `CompPowerTrader` (lines 261-264). No `idlePowerDraw`, so 40 W constant. |
| Cost | 50 Steel, 1 ComponentIndustrial; ConstructionSkill 4 |
| Capacity | `CompProperties_GenepackContainer maxCapacity 4` |
| Also minifiable | `<minifiedDef>MinifiedThing</minifiedDef>` |

**Neolithic implication:** the gene bank is hard-gated behind `Electricity` → `Xenogermination`
research AND needs 40 W of continuous power. There is no non-powered, no-research way to
preserve a genepack in vanilla. A genepack acquired in the neolithic era is dead in 20 days.
(An unpowered gene bank gives no protection — `PowerOn` is false ⇒ `Deteriorating` true,
same 5 HP/day via `Genepack.TickRare`.)

**Repair when powered:** `Genepack.TickRare()` else-branch, `hpRecoveryPct += 0.004166667f`
per rare tick ⇒ const `HitPointRecoveryPerDayInGeneBankPerDay = 1` HP/day.

## 3. Minified buildings — **do NOT deteriorate, indoors or outdoors.**

- The uninstalled thing is a `RimWorld.MinifiedThing` (class in `RimWorld/MinifiedThing.cs`;
  note the 1.6 namespace is `RimWorld`, not `Verse`) whose own ThingDef is
  `MinifiedThing` — `Data/Core/Defs/ThingDefs_Items/Items_Unfinished.xml:232-254`.
- That def has **no `<statBases>` block at all** ⇒ `DeteriorationRate` = 0
  (stat default 0) ⇒ `FinalDeteriorationRate` returns 0 at `if (num <= 0f)`.
- `MinifiedThing` does **not** override `GetStatValue`; its only overrides are
  `Graphic`, `LabelNoCount`, `DescriptionDetailed`, `DescriptionFlavor`, `ContentSource`,
  `Tick`, `TickInterval`, `SplitOff`, `CanStackWith`, `ExposeData`,
  `DrawExtraSelectionOverlays`, `DrawAt`, `Print`, `Destroy`, `PreTraded`, `GetGizmos`,
  `GetInspectString`. Nothing redirects the deterioration stat to `InnerThing`.
- The `InnerThing` (the building) is unspawned inside `innerContainer`, is
  `category == Building` ⇒ `CanEverDeteriorate` is false, and is never visited by
  `DoCellSteadyEffects` (which iterates spawned things per cell only).

**General rule: minified things never deteriorate.** (Exception by design:
`MinifiedTree`, `thingClass MinifiedTree` — a minified *plant* dies of thirst/age via its
own logic, cf. `Alert_MinifiedTreeAboutToDie`. Not deterioration, and not relevant here.)

### `VQEA_ArchogenInjector` specifically

`.../workshop/content/294100/3618306875/1.6/Defs/ThingDefs_Buildings/Buildings_Laboratory.xml:3-72`
— `ParentName="VQEA_LabAncientsBuildingBase"`, which sets
`<minifiedDef>MinifiedThing</minifiedDef>` (`Buildings_Bases.xml:20-21`).
So an uninstalled archogen injector is a plain vanilla `MinifiedThing`:
**zero deterioration, anywhere, indefinitely.** It is still a physical item with hit
points that can be damaged by fire/explosions (its installed form has
`Flammability 0.5`; the MinifiedThing wrapper takes MaxHitPoints from the `MinifiedThing`
def default of 100 since it declares no statBases).

## 4. Pure-XML immunity — **yes, several ways, all patchable.**

Ranked by cleanliness:

1. **Set `DeteriorationRate` to 0 in `statBases`** — the canonical fix.
   `FinalDeteriorationRate` bails at `if (num <= 0f) return 0f;` *before* any StatPart,
   and `Genepack.TickRare` guards on `if (statValue > 0.001f)`. So this kills **both**
   decay paths, including the genepack-specific one.
   ```xml
   <Operation Class="PatchOperationReplace">
     <xpath>/Defs/ThingDef[defName="Genepack"]/statBases/DeteriorationRate</xpath>
     <value><DeteriorationRate>0</DeteriorationRate></value>
   </Operation>
   ```
   For a def that has a `statBases` block but no `DeteriorationRate` node, use
   `PatchOperationAdd` on `/Defs/ThingDef[defName="X"]/statBases`.
   Safe: all seven StatParts on the stat are multiplicative and `minValue` is 0.
   *(Caveat: `ThingDef.ConfigErrors` at `Verse/ThingDef.cs:1812` only warns in the
   opposite case — rate > 0 with `CanEverDeteriorate` false — so rate 0 produces no
   log noise.)*

2. **`<useHitPoints>false</useHitPoints>`** — `CanEverDeteriorate` returns false
   immediately. Total immunity to deterioration *and* to all damage/destruction.
   Heavy-handed: the item loses its HP bar, can't be damaged, and quality/HP-based
   pricing (`healthAffectsPrice`) becomes moot. Use only if you want a truly
   indestructible item.

3. **`<deteriorateFromEnvironmentalEffects>false</deteriorateFromEnvironmentalEffects>`**
   — this does **not** grant immunity; it *removes* the ×0 indoor bonus and leaves the
   flat base rate. This is exactly what makes genepacks decay indoors. Do not use it as
   a protection measure.

4. **`<canDeteriorateUnspawned>false</canDeteriorateUnspawned>`** (the default) — only
   affects the unspawned branch of `FinalDeteriorationRate`, which in 1.6 is reached only
   from the inspect-string path. Cosmetic; not a real protection lever.

5. **Rot:** rot is a separate system (`RimWorld.CompRottable`, damage def `Rotting`).
   Pure XML fix = `PatchOperationRemove` the `<li Class="CompProperties_Rottable">`
   element from the def's `comps` list. (`ArchiteCapsule` has no such comp, so nothing
   to remove.) In-game, `CompRottable.ShouldTakeRotDamage()` also returns false when the
   parent holder is a building with `building.preventDeteriorationInside` — in vanilla
   only `Grave` and `Sarcophagus`
   (`Data/Core/Defs/ThingDefs_Buildings/Buildings_Misc.xml:797, 902`).

6. **Non-XML in-game mitigations, for reference:** roofed+enclosed room (rate ×0 via
   `StatPart_EnvironmentalEffects`), or a shelf
   (`building.preventDeteriorationOnTop` ⇒ `protectedByEdificeFactor 0`,
   `Buildings_Furniture.xml:1547` on `ShelfBase`). **Neither works on genepacks**
   because of `deteriorateFromEnvironmentalEffects=false`.

### Recommendation for the Archinity scenario

- Archite capsules and any minified archotech building already survive indefinitely with
  no player action, no roof, no power. **No patch needed.**
- Genepacks are the only real problem, and no vanilla XML-legal *gameplay* solution exists
  pre-electricity. A one-line `PatchOperation` setting `Genepack`'s `DeteriorationRate` to
  0 (or a mod-specific `ArchiteGenepack` copy-def with rate 0) is the pure-XML answer.
  Anything that leaves the rate > 0 will kill the pack in 20 days regardless of storage.

---

### Files cited

- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Biotech\Defs\ThingDefs_Items\Items_Various.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Biotech\Defs\ThingDefs_Buildings\Buildings_Misc.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Biotech\Defs\ResearchProjectDefs\ResearchProjects_Misc.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\Stats\Stats_Basics_General.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Items\Items_Unfinished.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Buildings\Buildings_Furniture.xml`
- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Buildings\Buildings_Misc.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3618306875\1.6\Defs\ThingDefs_Buildings\Buildings_Laboratory.xml`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3618306875\1.6\Defs\ThingDefs_Buildings\Buildings_Bases.xml`

Decompiled classes: `RimWorld.SteadyEnvironmentEffects`, `RimWorld.Genepack`,
`RimWorld.CompGenepackContainer`, `RimWorld.MinifiedThing`,
`RimWorld.StatPart_EnvironmentalEffects`, `RimWorld.CompRottable`, `Verse.ThingDef`,
`Verse.Thing`.
