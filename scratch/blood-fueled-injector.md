# Can `VQEA_ArchogenInjector` run on blood (hemogen) via XML patching only?

RimWorld 1.6 / Vanilla Quests Expanded — Ancients (workshop `3618306875`).
All claims below are backed by decompiled IL (ilspycmd 8.2) or by real def files. Anything not
verified is flagged **UNVERIFIED**.

**Bottom line:**
- **Option A (replace power with refuelable) — DEAD.** Guaranteed `NullReferenceException`.
- **Option B (keep power + add hemogen refuelable) — WORKS, but is cosmetic/economic only.**
  It will not gate the injection. No crash.
- **Option C (a Biotech hemogen-consuming comp) — DOES NOT EXIST as a reusable comp.**
  Biotech's hemogen buildings use plain `CompProperties_Refuelable`; the *gating* is done in
  `CompDeathrestBindable`'s C#, which is deathrest-specific and useless on the injector.
- **True blood-gating requires C# (a Harmony patch).** There is no XML-only path.

---

## 1. THE BLOCKER: `Building_ArchogenInjector` hard-requires `CompPowerTrader`

Class hierarchy: `Building_ArchogenInjector : Building_PawnProcessor : Building_Enterable`
(`Building_PawnProcessor` is also a VQE Ancients class, in the same assembly).

### 1a. The fatal line — unguarded deref in the base class

`VanillaQuestsExpandedAncients.Building_PawnProcessor`, decompiled:

```csharp
public bool PowerOn => ThingCompUtility.TryGetComp<CompPowerTrader>((Thing)(object)this).PowerOn;
```

`ThingCompUtility.TryGetComp<T>` returns `null` when the comp is absent. There is **no `?.`, no
`!= null` check, and no fallback**. Remove `CompProperties_Power` and every read of `PowerOn`
throws `NullReferenceException`.

Same file, the tick gate:

```csharp
protected virtual bool ShouldProcessTick()
{
    return PowerOn;
}
```

`ShouldProcessTick()` is called from `Building_PawnProcessor.Tick()`, i.e. **every tick** on a
`tickerType Normal` building. So the NRE is not a rare edge case — it fires immediately and
continuously on spawn.

### 1b. The second fatal line — unguarded deref in the injector itself

`VanillaQuestsExpandedAncients.Building_ArchogenInjector.Tick()`:

```csharp
protected override void Tick()
{
    base.Tick();
    if (Gen.IsHashIntervalTick((Thing)(object)this, 250))
    {
        CompPowerTrader val = ThingCompUtility.TryGetComp<CompPowerTrader>((Thing)(object)this);
        if (State == ArchiteInjectorState.Injecting)
        {
            val.PowerOutput = 0f - ((CompPower)val).Props.PowerConsumption;
        }
        else
        {
            val.PowerOutput = 0f - ((CompPower)val).Props.idlePowerDraw;
        }
    }
    if (processConfirmed && totalInjectionTime == 0 && AllRequiredIngredientsLoaded)
    {
        StartInjection();
    }
    if (base.Occupant != null && base.Occupant.Dead)
    {
        CancelProcess();
    }
}
```

`val` is assigned from `TryGetComp` and then dereferenced twice (`val.PowerOutput`,
`((CompPower)val).Props`) with **zero null checking**. Second guaranteed NRE, every 250 ticks.

### 1c. Every other `PowerOn` consumer in the injector

All of these route through the null-deref property above:

```csharp
// State property
public ArchiteInjectorState State
{
    get
    {
        if (!base.PowerOn)
        {
            return ArchiteInjectorState.Inactive;
        }
        if (base.Occupant == null) { return ArchiteInjectorState.WaitingForPawn; }
        ...
    }
}

// regression gate
protected override bool ShouldRegress => !base.PowerOn;

// CanAcceptPawn
if (!base.PowerOn)
{
    return AcceptanceReport.op_Implicit(Translator.Translate("CannotUseNoPower"));
}

// GetFloatMenuOptions (compiler-generated iterator, state machine)
if (!CS$<>8__locals0.PowerOn)
{
    TaggedString val2 = Translator.Translate("NoPower");
    ...
}
```

**Verdict on the blocker: YES, it hard-requires `CompPowerTrader`. Option A is dead.**

Also note `SpawnSetup` requires Biotech to even exist:

```csharp
public override void SpawnSetup(Map map, bool respawningAfterLoad)
{
    ((Building)this).SpawnSetup(map, respawningAfterLoad);
    if (!ModLister.CheckBiotech("archogen injector"))
    {
        ((Thing)this).Destroy((DestroyMode)0);
    }
}
```

### 1d. Confirming the power comp is only in the child def (no inherited fallback)

`.../3618306875/1.6/Defs/ThingDefs_Buildings/Buildings_Laboratory.xml`, lines 40–64:

```xml
<comps>
  <li Class="CompProperties_Power">
    <compClass>CompPowerTrader</compClass>
    <shortCircuitInRain>true</shortCircuitInRain>
    <basePowerConsumption>400</basePowerConsumption>
    <idlePowerDraw>50</idlePowerDraw>
  </li>
  <li Class="CompProperties_Flickable" />
  <li Class="CompProperties_AffectedByFacilities">
    <linkableFacilities> ... </linkableFacilities>
  </li>
</comps>
```

Parent chain is `VQEA_LabAncientsBuildingBase` → `VQEA_AncientsBuildingBase`
(`.../1.6/Defs/ThingDefs_Buildings/Buildings_Bases.xml`, line 20). Neither abstract parent
declares any `CompProperties_Power`. So the 400W comp above is the *only* source of
`CompPowerTrader` — removing it removes it for real, and the game crashes.

---

## 2. Why Option B does not actually gate anything

Adding `CompProperties_Refuelable` alongside the power comp is safe (no crash) and will:
- draw a hemogen fuel bar in the inspect pane,
- have haulers deliver `HemogenPack` to the building,
- burn hemogen over time,
- show an out-of-fuel overlay.

It will **not** stop the injection. Three independent reasons, all verified:

### 2a. The injector's C# never queries `CompRefuelable`

Grep of the full decompile of `Building_ArchogenInjector` (1256 lines) and
`Building_PawnProcessor` (450 lines) for `Refuelable|Fuel|Hemogen` returns **zero hits**. The
only comp-related matches are the `CompPowerTrader` lines quoted above. The mod has no fuel
awareness whatsoever.

### 2b. `CompRefuelable` never turns off a power *consumer*

`RimWorld.CompRefuelable` (Assembly-CSharp):

```csharp
public override void CompTick()
{
    base.CompTick();
    CompPowerTrader comp = parent.GetComp<CompPowerTrader>();
    if (!Props.consumeFuelOnlyWhenUsed && (flickComp == null || flickComp.SwitchIsOn)
        && (!Props.consumeFuelOnlyWhenPowered || (comp != null && comp.PowerOn))
        && !Props.externalTicking)
    {
        ConsumeFuel(ConsumptionRatePerTick);
    }
    ...
}

private void Notify_RanOutOfFuel()
{
    if (Props.destroyOnNoFuel) { ... }
    parent.BroadcastCompSignal("RanOutOfFuel");
}
```

`CompRefuelable` *reads* power (to decide whether to burn fuel) but never *writes* it. Running
dry only broadcasts a signal.

Now the receiver, `RimWorld.CompPowerTrader`:

```csharp
public override void ReceiveCompSignal(string signal)
{
    switch (signal)
    {
    case "FlickedOff":
    case "ScheduledOff":
    case "Breakdown":
    case "AutoPoweredWantsOff":
        PowerOn = false;
        break;
    }
    if (signal == "RanOutOfFuel" && powerLastOutputted)
    {
        PowerOn = false;
    }
    UpdateOverlays();
}
```

The `RanOutOfFuel` branch is guarded by `powerLastOutputted`, which is set in
`SetUpPowerVars()`:

```csharp
powerLastOutputted = compProperties_Power.PowerConsumption <= 0f;
```

and maintained by the `PowerOutput` setter:

```csharp
set
{
    powerOutputInt = value;
    if (powerOutputInt > 0f) { powerLastOutputted = true; }
    if (powerOutputInt < 0f) { powerLastOutputted = false; }
}
```

The injector has `basePowerConsumption = 400` (> 0), so `powerLastOutputted` starts `false`; and
the injector's own `Tick()` writes a **negative** `PowerOutput` every 250 ticks, pinning it
`false` forever. `powerLastOutputted` is a producer-vs-consumer flag — the `RanOutOfFuel`
shutdown is a **generator-only** mechanic (fuelled power plants). It is unreachable for a
consumer.

### 2c. The `basePowerConsumption = 0` trick also fails

Considered and rejected: if you patched `basePowerConsumption` and `idlePowerDraw` to `0`, then
`powerLastOutputted = (0 <= 0) = true`, the `RanOutOfFuel` branch fires, and `PowerOn` goes
`false`. But `RimWorld.PowerNet.PowerNetTick()` immediately turns it back on:

```csharp
public void PowerNetTick()
{
    float num = CurrentEnergyGainRate();
    float num2 = CurrentStoredEnergy();
    if (num2 + num >= -1E-07f && !Map.gameConditionManager.ElectricityDisabled(Map))
    {
        float num3 = ((batteryComps.Count <= 0 || !(num2 >= 0.1f)) ? num2 : (num2 - 5f));
        if (num3 + num >= 0f)
        {
            partsWantingPowerOn.Clear();
            for (int i = 0; i < powerComps.Count; i++)
            {
                if (!powerComps[i].PowerOn && FlickUtility.WantsToBeOn(powerComps[i].parent)
                    && !powerComps[i].parent.IsBrokenDown())
                {
                    partsWantingPowerOn.Add(powerComps[i]);
                }
            }
            if (partsWantingPowerOn.Count > 0)
            {
                int num4 = 200 / partsWantingPowerOn.Count;
                if (num4 < 30) { num4 = 30; }
                if (Find.TickManager.TicksGame % num4 == 0)
                {
                    ...
                    compPowerTrader.PowerOn = true;
```

A 0W consumer on a live net is re-powered within 30–200 ticks. The shutdown lasts a fraction of
a second, then the injector resumes. Not a gate.

### 2d. No fuel-aware `CompFlickable` either

`RimWorld.CompFlickable` has **no** `ReceiveCompSignal` override and **no** occurrence of the
string `fuel`. It cannot relay a fuel outage into a power-off.

---

## 3. Option C: what Biotech's hemogen buildings actually use

Full survey of `Data/Biotech/Defs/ThingDefs_Buildings/Buildings_Deathrest.xml`:

| defName | comps |
|---|---|
| `DeathrestCasket` | `CompProperties_AssignableToPawn`, `CompProperties_Power`, `CompProperties_Flickable`, `CompProperties_DeathrestBindable` |
| `Hemopump` | inherits `DeathrestBuildingHemogenFueled` + `CompProperties_DeathrestBindable` |
| `HemogenAmplifier` | inherits `DeathrestBuildingHemogenFueled` + `CompProperties_DeathrestBindable` |
| `GlucosoidPump` | inherits `DeathrestBuildingHemogenFueled` + `CompProperties_DeathrestBindable` |
| `PsychofluidPump` | inherits `DeathrestBuildingHemogenFueled` + `CompProperties_DeathrestBindable` |
| `DeathrestAccelerator` | `CompProperties_Power`, `CompProperties_Flickable`, `CompProperties_DeathrestBindable` |

### The precedent (this is the answer to "is there a working hemogen-fuel building?")

**Yes.** `Data/Biotech/Defs/ThingDefs_Buildings/Buildings_Deathrest.xml`, lines 125–150, abstract
def `DeathrestBuildingHemogenFueled` — parent of `Hemopump`, `HemogenAmplifier`,
`GlucosoidPump`, `PsychofluidPump`:

```xml
<ThingDef ParentName="DeathrestBuildingBase" Name="DeathrestBuildingHemogenFueled" Abstract="True">
  <comps>
    <li Class="CompProperties_Power">
      <compClass>CompPowerTrader</compClass>
      <basePowerConsumption>100</basePowerConsumption>
      <idlePowerDraw>0</idlePowerDraw>
      <alwaysDisplayAsUsingPower>true</alwaysDisplayAsUsingPower>
    </li>
    <li Class="CompProperties_Flickable"/>
    <li Class="CompProperties_Refuelable">
      <fuelConsumptionRate>0.5</fuelConsumptionRate> <!-- Empty in one year -->
      <fuelCapacity>5</fuelCapacity>
      <fuelLabel>Hemogen</fuelLabel>
      <fuelFilter>
        <thingDefs>
          <li>HemogenPack</li>
        </thingDefs>
      </fuelFilter>
      <initialFuelPercent>1</initialFuelPercent>
      <showAllowAutoRefuelToggle>true</showAllowAutoRefuelToggle>
      <externalTicking>true</externalTicking>
      <autoRefuelPercent>0.05</autoRefuelPercent>
      <canEjectFuel>true</canEjectFuel>
    </li>
  </comps>
</ThingDef>
```

Note vanilla itself uses **power AND hemogen together** — i.e. exactly Option B's shape. That is
the *only* hemogen-fuel pattern in the game.

### But the gating is C#, not XML

The reason the Hemopump actually stops when out of blood is `RimWorld.CompDeathrestBindable`:

```csharp
private CompRefuelable RefuelableComp
{
    get
    {
        if (cachedRefuelableComp == null)
        {
            cachedRefuelableComp = parent.TryGetComp<CompRefuelable>();
        }
        return cachedRefuelableComp;
    }
}

// inside CanUseNow-style property:
    if (RefuelableComp != null && !RefuelableComp.HasFuel)
    {
        return false;
    }
```

and the fuel is only burned while actually in use (`externalTicking = true` above):

```csharp
RefuelableComp?.Notify_UsedThisTick();
```

`CompProperties_DeathrestBindable` on the injector would do nothing useful — it makes the
building a deathrest facility that binds to a `DeathrestCasket`; it does not touch
`Building_PawnProcessor`'s state machine. **UNVERIFIED whether it would error on a non-bed
building — not tested; but it is definitionally the wrong mechanic regardless.**

### No generic hemogen comp exists

Full grep of `Data/**/*.xml` for comp classes matching `Hemogen|Blood|Deathrest` yields only:

```
CompProperties_AbilityBloodfeederBite
CompProperties_AbilityHemogenCost          (ability comp — pawn abilities, not buildings)
CompProperties_DeathrestBindable
CompProperties_UseEffectOffsetDeathrestCapacity
HediffCompProperties_SeverityFromHemogen
IngestionOutcomeDoer_OffsetHemogen
JobGiver_GetDeathrest
JobGiver_GetHemogen
StatPart_Deathresting
```

None is a drop-in "this building runs on blood" comp. And there is no fuel-gated power
`compClass` in the game — the full set of `<compClass>` values used across all vanilla defs
includes `CompPowerTrader`, `CompPowerTransmitter`, `CompPowerPlant*` (generators only), and
nothing that makes a *consumer* depend on fuel.

---

## 4. Recommended patch (Option B — the honest best XML-only result)

This is safe, uses the exact vanilla hemogen-fuel precedent, makes the injector cost real blood
to run, and drops power from 400W to 200W so blood is a meaningful part of its upkeep. It does
**not** halt injection at zero hemogen.

```xml
<?xml version="1.0" encoding="utf-8"?>
<Patch>

  <!-- 1. Halve the electrical draw, since blood now carries part of the load. -->
  <Operation Class="PatchOperationReplace">
    <xpath>/Defs/ThingDef[defName="VQEA_ArchogenInjector"]/comps/li[@Class="CompProperties_Power"]</xpath>
    <value>
      <li Class="CompProperties_Power">
        <compClass>CompPowerTrader</compClass>
        <shortCircuitInRain>true</shortCircuitInRain>
        <basePowerConsumption>200</basePowerConsumption>
        <idlePowerDraw>25</idlePowerDraw>
      </li>
    </value>
  </Operation>

  <!-- 2. Add the hemogen tank, mirroring DeathrestBuildingHemogenFueled.
          externalTicking is deliberately FALSE here: nothing in VQEA calls
          Notify_UsedThisTick(), so with externalTicking=true the fuel would never
          be consumed at all. consumeFuelOnlyWhenPowered ties the burn to uptime. -->
  <Operation Class="PatchOperationAdd">
    <xpath>/Defs/ThingDef[defName="VQEA_ArchogenInjector"]/comps</xpath>
    <value>
      <li Class="CompProperties_Refuelable">
        <fuelLabel>Hemogen</fuelLabel>
        <fuelGizmoLabel>Hemogen</fuelGizmoLabel>
        <fuelFilter>
          <thingDefs>
            <li>HemogenPack</li>
          </thingDefs>
        </fuelFilter>
        <fuelCapacity>10</fuelCapacity>
        <fuelConsumptionRate>6.0</fuelConsumptionRate>
        <initialFuelPercent>0</initialFuelPercent>
        <consumeFuelOnlyWhenPowered>true</consumeFuelOnlyWhenPowered>
        <externalTicking>false</externalTicking>
        <destroyOnNoFuel>false</destroyOnNoFuel>
        <drawOutOfFuelOverlay>true</drawOutOfFuelOverlay>
        <showAllowAutoRefuelToggle>true</showAllowAutoRefuelToggle>
        <autoRefuelPercent>0.3</autoRefuelPercent>
        <canEjectFuel>true</canEjectFuel>
        <fuelIsMortarBarrel>false</fuelIsMortarBarrel>
      </li>
    </value>
  </Operation>

</Patch>
```

Guard it with `<Operation Class="PatchOperationFindMod"><mods><li>Vanilla Quests Expanded -
Ancients</li></mods><match>...</match></Operation>` if your mod does not hard-depend on VQEA.
**UNVERIFIED: the exact `packageId`/name string to match — check VQEA's `About/About.xml`.**

Tuning note: `fuelConsumptionRate` is per in-game **day**. `6.0` with `fuelCapacity 10` means a
full tank lasts ~1.67 days while powered. The base injection is `baseInjectionTicks 300000` =
**5 in-game days** (verified in `ArchogenInjectorExtension`), so one cycle burns roughly 30
hemogen packs. Scale to taste.

**UNVERIFIED: `fuelGizmoLabel` and `fuelIsMortarBarrel` field names were not confirmed against
the decompiled `CompProperties_Refuelable` in this pass. If the game throws an XML field error
on load, delete those two lines — every other field above is copied verbatim from the shipping
`DeathrestBuildingHemogenFueled` def.**

---

## 5. If you want real blood-gating (out of scope: requires C#)

The minimal Harmony patch would be a `Postfix` on
`VanillaQuestsExpandedAncients.Building_PawnProcessor.get_PowerOn` (or on
`ShouldProcessTick`) returning `__result && (refuelable == null || refuelable.HasFuel)`. Patching
`PowerOn` gets you everything for free — `State` collapses to `Inactive`, `ShouldRegress`
flips true, and `CanAcceptPawn` refuses the pawn — because all four call sites route through
that one property. That is ~10 lines of C#. There is no XML equivalent.

---

## Evidence provenance

- `ilspycmd -t VanillaQuestsExpandedAncients.Building_ArchogenInjector`
  on `.../3618306875/1.6/Assemblies/VanillaQuestsExpandedAncients.dll` (1256 lines)
- `ilspycmd -t VanillaQuestsExpandedAncients.Building_PawnProcessor` (same dll, 450 lines)
- `ilspycmd -t VanillaQuestsExpandedAncients.ArchogenInjectorExtension` (same dll)
- `ilspycmd -t RimWorld.CompRefuelable | CompPowerTrader | CompFlickable | PowerNet |
  CompDeathrestBindable` on
  `.../RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll`
- Defs read directly from `.../RimWorld/Data/Biotech/Defs/ThingDefs_Buildings/Buildings_Deathrest.xml`
  and `.../3618306875/1.6/Defs/ThingDefs_Buildings/{Buildings_Laboratory,Buildings_Bases}.xml`
