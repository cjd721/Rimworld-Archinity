# Shipped defaults and presets

## Purpose and scope

**What this document owns:** the values the campaign puts in front of the player *already
set*, so that a two-player session is not spent re-entering the same number at every bench
and rebuilding the same outfit in every colony.

Two surfaces, one mechanism:

- **Every new bill arrives configured** — repeat mode, target count, durability floor,
  quality floor — instead of at vanilla's defaults.
  [#95](https://github.com/cjd721/Rimworld-Archinity/issues/95).
- **Kit presets are authored and shipped** — Cook, Farmer, Smith, Miner, Doctor, melee
  soldier, ranged soldier — instead of hand-built once per colony.
  [#28](https://github.com/cjd721/Rimworld-Archinity/issues/28).

They share a document because they share an answer. Vanilla builds both objects in C# with
hardcoded field initialisers and exposes **no XML seam** to either; both therefore want the
same shape — *authored data in a Def we define, applied by a small deterministic hook at the
one place vanilla hardcodes the value.* Neither may live in `ModSettings`.

**Where adjacent systems take over.**

- The recycling bench and its recipes — `ITEMS.md`. That document's § *Quality and damage*
  contains an error this one corrects; see *Corrections to standing documents* below.
- Whether the add-bill menu is **legible** with this many recipes on it, and the era filter —
  [#96](https://github.com/cjd721/Rimworld-Archinity/issues/96). #87 carried the mod survey
  and is closed.
- **Which items are in which kit, and the exact preset roster** — downstream of the ladders
  ([#19](https://github.com/cjd721/Rimworld-Archinity/issues/19),
  [#20](https://github.com/cjd721/Rimworld-Archinity/issues/20)) and the era fills
  ([#41](https://github.com/cjd721/Rimworld-Archinity/issues/41),
  [#42](https://github.com/cjd721/Rimworld-Archinity/issues/42)). This document owns the
  mechanism that carries a roster, not the roster — but see *The one-belt rule*, which the
  roster must obey.
- **What the quality floor should be** is a requirement, not a mechanism. See
  *Outstanding decisions*.

---

## The build

### Mechanism — the shared decision

**A Def for the data, a hook for the application, and nothing in `ModSettings`.**

Vanilla constructs `Bill_Production` with `repeatMode = RepeatCount, targetCount = 10,
hpRange = ZeroToOne, qualityRange = All` as field initialisers **[V]**
(`RimWorld.Bill_Production`), and constructs `ApparelPolicy` objects in
`RimWorld.OutfitDatabase.GenerateStartingOutfits` against a hardcoded list of five tag
strings — `Worker`, `Soldier`, `Nudist`, `Slave`, `Spacefarer` **[V]**. Neither is reachable
by `PatchOperation`: an `ApparelPolicy` is not a `Def` at all (`RimWorld.ApparelPolicy :
RimWorld.Policy`, an `IExposable` scribed into the save by `OutfitDatabase.ExposeData`
**[V]**), and a `Bill_Production` is constructed fresh per bill.

So both halves need code. The question the grouping exists to settle is *where the numbers
live*, and the answer is the same for both: **a Def type we declare, loaded from our own
XML.** A Def is read from the same files on both clients in the same load order, so its
values are identical by construction — which constants also achieve, but a Def additionally
lets the table carry per-recipe and per-role rows without a rebuild, and the campaign wants
both. `ModSettings` is rejected outright for both halves: it is per-client state on a shared
path, which is **T-18**, and the corpus contains **two live instances of exactly that
mistake**, one on each of our two seams (see *Available mechanisms*).

Both halves use only Defs and the incoming `RecipeDef` as inputs, so both pass
`CODING_STANDARDS.md`'s **Divergence** gate outright — no `ModSettings`, no
`Find.CurrentMap`, no `Find.Selector`, no `Prefs`, no `Rand`.

### Half one — bill defaults (#95)

**One Harmony postfix on `RimWorld.BillUtility.MakeNewBill`.** (Note the namespace:
`RimWorld`, not `Verse`.) It is an extension method on `RecipeDef` returning `Bill` **[V]**.

```csharp
[HarmonyPatch(typeof(BillUtility), nameof(BillUtility.MakeNewBill))]
public static class BillDefaultsPatch
{
    public static void Postfix(RecipeDef recipe, ref Bill __result) { /* below */ }
}
```

The body owes **three gates, each copied from a condition vanilla already enforces**, and
one that the corpus forces on us:

1. **Type allowlist, not `is Bill_Production`.** `MakeNewBill` returns five vanilla types
   and every one of them descends from `Bill_Production` — `Bill_ProductionWithUft`,
   `Bill_Autonomous`, and `Bill_Mech : Bill_Autonomous` (both `Bill_ProductionMech` and
   `Bill_ResurrectMech`) **[V]**. Worse, a second mod prefixes this method and substitutes
   *its own* subclasses: `USH_GE.Patch_BillUtility_MakeNewBill` returns `Bill_ModifyCell :
   Bill_Production`, `Bill_Glittertech : Bill_Autonomous` and `Bill_Overclock :
   Bill_Glittertech` **[V]**, and a postfix still runs when a prefix returns `false`
   (Harmony's documented behaviour, the reason `__runOriginal` exists — **[I]**, not
   verified against `0Harmony` here). A naive `is Bill_Production` therefore rewrites the
   repeat mode of Glittertech overclock bills — a system this campaign has a requirements
   document for. **Act only when `__result.GetType()` is `typeof(Bill_Production)` or
   `typeof(Bill_ProductionWithUft)`**; the UFT case must be included, because every smithing
   recipe that uses an unfinished thing lands there.

2. **`recipe.WorkerCounter.CanCountProducts(bill)` before switching the mode.** Vanilla
   refuses `TargetCount` on a recipe it cannot count and says so —
   `RimWorld.BillRepeatModeUtility.MakeConfigFloatMenu` messages
   `"RecipeCannotHaveTargetCount"` rather than setting the field **[V]**. The base counter
   requires `specialProducts == null && products.Count == 1` **[V]**
   (`Verse.RecipeWorkerCounter.CanCountProducts`), which is **T-58**. Skipping this gate
   puts bills into a mode vanilla will not allow, on the same recipes T-58 already names.

3. **The two range gates, matching where the sliders render.** `hpRange` is drawn only when
   `recipe.products.Any(p => p.thingDef.useHitPoints)` and `qualityRange` only when
   `recipe.ProducedThingDef.HasComp(typeof(CompQuality))` **[V]**
   (`RimWorld.Dialog_BillConfig.DoWindowContents`). Note `ThingDef.useHitPoints` defaults
   **true** **[V]**, so the first gate passes for almost everything — it is the second that
   actually narrows.

**What those two fields actually do, because the ticket and `ITEMS.md` both describe them
wrongly.** `Bill_Production.hpRange` and `.qualityRange` are **product-counting filters**,
not ingredient filters. They are consumed in exactly one place:
`Verse.RecipeWorkerCounter.CountProducts` / `CountValidThing`, which decide *which existing
items on the map count toward `targetCount`* **[V]**. They appear nowhere in `Bill` and
nowhere in the ingredient path; ingredient selection runs through
`Bill.IsFixedOrAllowedIngredient` → `bill.ingredientFilter.Allows(thing)` **[V]**, and the
ingredient-side equivalents are `ThingFilter.AllowedHitPointsPercents` and
`.AllowedQualityLevels` — a *different pair of fields on a different object*.

The campaign's intent survives the correction: *"keep making longswords until I have five
that are Good or better"* is precisely what `qualityRange` expresses. But it must be wired
to the counting semantics, or the implementer will reach for the wrong field.

#### What the mode switch costs, and what it does not

`CountProducts` has an O(1) fast path through `bill.Map.resourceCounter.GetCount(...)`,
taken only when **all** of: `thingDef.CountAsResource`, `!includeEquipped`,
`includeTainted || !IsApparel || !apparel.careIfWornByCorpse`, no include slot group,
`hpRange` full 0–1, `qualityRange` Awful–Legendary, and `!limitToAllowedStuff` **[V]**.

**The two floors are not symmetrical, and that asymmetry is the whole argument.**
`ThingDef.useHitPoints` defaults **true** **[V]**, so the `hpRange` slider renders on almost
every recipe — including recipes producing plain counted resources, where the fast path is
live. `qualityRange` renders only where the product has `CompQuality`, which in practice
means apparel, weapons and art. **So a quality floor is free and a durability floor is not**,
and the reason is that on every recipe where the quality slider renders, the fast path was
already unreachable before we touched anything:

- **Apparel.** `ApparelProperties.careIfWornByCorpse` defaults **true** and
  `Bill_Production.includeTainted` defaults **false** **[V]**, so that conjunct is already
  false for every apparel product.
- **Weapons and most gear.** `CountAsResource` is `resourceReadoutPriority !=
  Uncounted` **[V]**, and `resourceReadoutPriority` has **no initialiser**, so it defaults
  to `Uncounted`. Only 16 vanilla def files set it at all, and the only apparel among them is
  `Apparel_PsychicShockLance` / `Apparel_PsychicInsanityLance` — both `ApparelNoQualityBase`,
  so the quality slider never renders for them anyway, and both still apparel, so the
  `careIfWornByCorpse` conjunct kills their fast path regardless **[V]**. No weapons file
  sets it.

The one place a floor genuinely costs something is therefore **`hpRange` on a counted
resource** — a recipe producing steel or cloth, where `useHitPoints` carries the slider in
and the fast path *was* live. **Never set a durability floor on the global row.**

**What actually costs ticks is the mode switch itself.** `Bill_Production.ShouldDoNow`
calls `CountProducts` **only** in the `TargetCount` branch; in `RepeatCount` mode it returns
`repeatCount > 0` and counts nothing **[V]**. `RepeatInfoText` calls it again for display
**[V]**. So putting every eligible bill into `TargetCount` introduces a count per bill-scan
where there was none, and **per-recipe range rows do not mitigate that** — it is the honest,
bounded price of the feature, not something the table can tune away.

**The table is still per-recipe**, for two reasons that survive: `hpRange` must be set
selectively, per the counted-resource case above; and a quality floor is a gameplay value
that differs per recipe, not one number.

**Def.** `Archinity_BillDefaultsDef : Def`, in `Archinity.Altar/Defs/BillDefaults/`. One
`global` row plus optional rows keyed by `recipe` or by `recipeUsers`. Every field nullable,
so a row can set the target count without disturbing the floors.

**State and persistence.** *None, and this is the whole appeal.* All four fields already
exist on `Bill_Production` and are already scribed by its `ExposeData` — `repeatMode`,
`targetCount`, `hpRange` and `qualityRange`, each with a default argument **[V]**. There is
no new save key, no migration, and nothing to remove if the feature is dropped. Bills in a
save that predates the mod keep their scribed values untouched; changing the table later
affects only bills created afterwards. **The player's edits are never re-imposed** — we
write once, at creation, and never look at the bill again.

**Display.** `Dialog_BillConfig`, unchanged and immediately. The point of switching the mode
in the postfix is that the two sliders are drawn *inside* the
`repeatMode == TargetCount` branch **[V]**, so a bill created in `RepeatCount` shows neither.
Arriving in `TargetCount` means the target box and both sliders are on screen the first time
the player opens the bill. Zero new UI.

### Half two — kit presets (#28)

**The blocking question, answered: yes, a vanilla apparel policy makes a pawn equip tool
belts and backpacks. No loadout mod is required for that** — and, as it turns out, one
loadout mod can actively prevent it. The reasoning is three verified links:

1. **Utility items are ordinary `Apparel` on *vanilla* layers, overwhelmingly `Belt`.**
   Vanilla and all five DLC put shield belt, smokepop, firefoam pack, both psychic lances,
   jump pack, low-shield pack, control/bandwidth/tox packs, hunter pack and cerebrex node on
   `<layers><li>Belt</li></layers>` with `<bodyPartGroups><li>Waist</li></bodyPartGroups>`
   and `<thingCategories><li>ApparelUtility</li></thingCategories>` **[V]**. The modded ones
   that matter here behave the same: `VAEA_Apparel_ToolBelt` (`Belt`/`Waist`) and
   `VAEA_Apparel_Backpack` (`Belt`/`Torso`) from Vanilla Apparel Expanded — Accessories
   (`2521176396`), Medieval Overhaul's quiver (`Belt`/`Shoulders`) and pot belts, GravTech's
   grav shield belt **[V]**.

   **Three qualifications, none of which touch the conclusion.** The layer is not
   universal: of ~52 `ApparelUtility` defs in 1.6 **[I]**,
   at least three are not on `Belt` — `VPE_Psyring` (`OnSkin`, `MiddleFingers`),
   `IC_MK3_Tacticloak` (`Shell`) **[V]**, and `Apparel_NoBody` (`Middle` + `OnSkin`) **[I]**.
   Body-part groups are not uniformly `Waist` — `Torso`, `Shoulders` and `MiddleFingers` all
   occur **[V]**. And custom `thingClass`es are not confined to vanilla's two
   (`SmokepopBelt`, `BroadshieldPack`): `VPE_Psyring` ships
   `VanillaPsycastsExpanded.Technomancer.Psyring` **[V]**, and others do too **[I]**.

   **The negative the build actually rests on is unaffected and was re-verified
   independently: no utility item in the corpus sits on a mod-defined `ApparelLayerDef`.**
   Only Vanilla Expanded Framework (`VFEC_OuterShell`) and Medieval Overhaul (six layers)
   define layers at all, and none of their uses carries `ApparelUtility` **[V]**.
   `Verse.ApparelLayerDef.IsUtilityLayer` is literally `this == ApparelLayerDefOf.Belt`
   **[V]** — "utility layer" *is* the belt layer, one def, hardcoded.

2. **`ApparelPolicy` is a bare `ThingFilter` with no layer awareness** — one field,
   `public ThingFilter filter` **[V]**. Vanilla's own Worker, Soldier and Spacefarer starting
   outfits explicitly allow *every* def in `ThingCategoryDefOf.ApparelUtility`, unconditionally,
   alongside their tag matches **[V]**. Utility items are not outside the policy system; they
   are hand-carried into it.

3. **The auto-equip path contains no layer test.**
   `RimWorld.JobGiver_OptimizeApparel.TryGiveJob` filters candidates on
   `currentApparelPolicy.filter.Allows(apparel2)` and accepts any score `>= 0.05f` **[V]**.
   `ApparelScoreRaw` starts at `0.1f + apparel.scoreOffset`, and `ApparelScoreGain`
   multiplies by `10f` when nothing already worn conflicts **[V]** — so a plain tool belt
   with no armour and no stat offsets scores **~1.0 against a 0.05 threshold**, twenty times
   over. The pawn walks to it and wears it.

#### The gates that can stop it anyway

**The full list matters for a roster**, because three of these are reachable by gear a
preset would plausibly name. In `ApparelScoreGain` **[V]**:

- `Apparel_ShieldBelt` → `-1000f` for a pawn whose primary is a projectile weapon.
- `apparel.ignoredByNonViolent` → `-1000f` for a pawn with `WorkTags.Violent` disabled.
- **A third, missed before:** if any worn item fails `ApparelUtility.CanWearTogether` **and**
  is force-worn (`!outfits.forcedHandler.AllowedToAutomaticallyDrop`) or
  `pawn.apparel.IsLocked`, the candidate returns `-1000f` outright. Directly reachable for
  soldier presets, where players force-wear gear.

And four `-10f` early-outs in `ApparelScoreRaw` **[V]** — `!PawnCanWear(ignoreGender: true)`,
`blocksVision`, `slaveApparel && !pawn.IsSlave`, `mechanitorApparel && pawn.mechanitor == null`.
Multiplied by 10 these land far under the threshold. **`mechanitorApparel` is load-bearing for
us**: the control pack and bandwidth pack in link 1's list are exactly that, so a non-mechanitor
on a preset naming them wears neither.

`TryGiveJob` also has non-score gates no draft mentioned **[V]**: `apparel.IsInAnyStorage()`
— **a belt lying on open ground is never fetched** — plus `!IsForbidden`, `!IsBurning`, gender,
`developmentalStageFilter`, biocoding, `ApparelUtility.HasPartsToWear`, reachability and
reservation, and no quest lodger or apparel-disabled mutant. The whole check runs on a
`Rand.Range(6000, 9000)`-tick interval per pawn **[V]**, so "assign the preset and watch"
is not an instant observation.

#### The one-belt rule

`ApparelUtility.CanWearTogether` returns false when two defs **share a layer** and their
body-part groups interfere **[V]**. Every `Belt`/`Waist` item therefore excludes every other
`Belt`/`Waist` item: **a preset naming both a tool belt and a shield belt yields one worn
item and no message.** The pair named above happens to stack — `VAEA_Apparel_ToolBelt` is
`Waist`, `VAEA_Apparel_Backpack` is `Torso` — but the roster tickets must apply this rule
deliberately rather than by luck.

#### The two things that are not true, and they reshape the ticket

- **A preset cannot ship as plain XML.** `ApparelPolicy` has no `Def` backing anywhere in
  vanilla, the DLC or the corpus **[V]**; the database is runtime state scribed by
  `Scribe_Collections.Look(ref outfits, "outfits", LookMode.Deep)`. There is nothing for a
  `PatchOperation` to add to. The ticket's preferred answer — *"`ApparelPolicy` defs we can
  ship as plain XML"* — does not exist.
- **Weapons are not reachable by this layer at all.** The `Policy` family in 1.6 is
  `ApparelPolicy`, `DrugPolicy`, `FoodPolicy`, `ReadingPolicy` **[V]** — there is no weapon
  policy, and `ApparelPolicy.filter` is an apparel filter. Vanilla's only weapon-acquisition
  AI is `JobGiver_PickUpOpportunisticWeapon`, an opportunistic 8-tile think node gated on
  `!AlreadySatisfiedWithCurrentWeapon` **[V]** — not a per-pawn preference and not something a
  preset can drive.

#### The donor that makes this cheap

Vanilla already ships the exact architecture the presets want — for drugs.
`DrugPolicyDef : Def` **[V]**, and
`RimWorld.DrugPolicyDatabase.GenerateStartingDrugPolicies()` is, in full:

```csharp
foreach (DrugPolicyDef allDef in DefDatabase<DrugPolicyDef>.AllDefs)
    NewDrugPolicyFromDef(allDef);
```

with `NewDrugPolicyFromDef` setting `policy.label = def.LabelCap`, `policy.sourceDef = def`,
and copying the def's entries **[V]**. Apparel is the one policy family missing its Def half.
**We build that missing half**, and vanilla's shape is the specification.

**Mechanism.** Two pieces, no Harmony patch.

- **`Archinity_ApparelPresetDef : Def`** — `label`, `List<ThingDef> allow`,
  `List<ThingCategoryDef> allowCategories`, `bool allowDeadmansApparel = false`. Mirrors
  `DrugPolicyDef`.
- **`ArchinityPresetsGameComponent : GameComponent`**, seeding in `FinalizeInit()`. For each
  def not already in a scribed `HashSet<string> seeded`: build an `ApparelPolicy` with the
  next id (`outfits.Any() ? outfits.Max(o => o.id) + 1 : 1`, vanilla's own formula **[V]**),
  `filter.SetDisallowAll()` first — `MakeNewOutfit` otherwise leaves `ThingCategoryDefOf.Apparel`
  allowed **[V]** — then `SetAllow` per entry, then add to `Current.Game.outfitDatabase.AllOutfits`,
  which returns the live private list **[V]**.

  **Add to the list directly rather than calling `MakeNewOutfit()`.**
  `SyncMethod.Register(typeof(OutfitDatabase), "MakeNewOutfit")` puts that method on
  Multiplayer's sync surface **[V]**. It happens to be inert at `FinalizeInit` — MP's
  `ShouldSync` is `InInterface && !dontSync`, and `InInterface` requires
  `LongEventHandler.currentEvent == null` **[V]**, while load and worldgen are long events —
  but relying on that is relying on a predicate in someone else's assembly. Constructing the
  object ourselves costs two extra lines and depends on nothing.

**The soldier presets ship apparel-only.** "Melee soldier" and "ranged soldier" name the
pawn, not the weapon: the preset carries plate and a shield belt, or flak and a smokepop pack,
and says nothing about what is in the pawn's hands. That is what the mechanism supports, and
pretending otherwise would mean building a second behaviour. The weapon half is priced and
deferred below.

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| `Archinity_BillDefaultsDef` + lookup | new C# | ~35 lines | `Archinity.Altar/Source/BillDefaults.cs` |
| `MakeNewBill` postfix, four gates | new C# | ~45 lines | same file |
| Bill defaults table | XML | ~25 lines | `Archinity.Altar/Defs/BillDefaults/` |
| `Archinity_ApparelPresetDef` | new C# | ~20 lines | `Archinity.Altar/Source/ApparelPresets.cs` |
| `ArchinityPresetsGameComponent` | new C# | ~55 lines | same file |
| Preset roster | XML | ~12 lines per preset | `Archinity.Altar/Defs/ApparelPresets/` |
| Startup validation for both tables | new C# | ~20 lines | `Archinity.Altar/Source/Patches.cs` |

**~175 lines of C# and two XML files, in the assembly we already ship.** No new assembly, no
new dependency, nothing pinned about the mod set.

The startup validation is not optional. **T-04**: an unresolvable `<li>` inside a def list is
*omitted, not nulled*, so a preset naming a ThingDef that a since-removed mod supplied loses
that item silently and the policy simply comes up short. The assembly already carries the
right pattern — `ArchinityMod.WarnAboutGenesMissingFromPool` warns at
`StaticConstructorOnStartup` for exactly this class of hole — and both tables should be
checked the same way.

---

## Persistence and multiplayer

**Bills.** `RimWorld.BillUtility.MakeNewBill` is reached on two synced paths, and our postfix
is safe on both because it reads nothing that can differ.

- **The add-bill float menu** is a synced *delegate*:
  `SyncDelegate.Lambda(typeof(ITab_Bills), "FillTab", 2).SetContext(SyncContext.MapSelected)
  .CancelIfNoSelectedMapObjects()` **[V]**. The delegate body — including `MakeNewBill` — is
  replayed on every client. (`Multiplayer.Client.SyncMethods.AddBill_Prefix` assigns
  `bill.loadID` from the shared `UniqueIDsManager` when `ExecutingCmds && bill.loadID < 0`,
  but it is a **backstop**, not the mechanism: the `Bill` constructor already assigns the id
  from the same manager **[V]**.) Anything the postfix reads must be identical on both
  machines.
- **Every other caller** — clipboard paste in `ITab_Bills.FillTab`, and Nice Bill Tab's
  replacement tab — goes through
  `SyncMethod.Register(typeof(BillStack), "AddBill").ExposeParameter(0)` **[V]**, which
  serialises the finished `Bill` and ships it, so `MakeNewBill` ran once.

**With Nice Bill Tab loaded, only the second path exists.** Its
`ITab_Bills_FillTab_Patch.Prefix` returns `false` whenever its own `Settings.EnabledMod` is
true **[V]**, so vanilla `ITab_Bills.FillTab` never runs and the lambda MP registered inside
it never fires. Bill creation then rests entirely on the `BillStack.AddBill` SyncMethod.

Our postfix reads `recipe` (a Def), our table (Defs), `recipe.WorkerCounter.CanCountProducts`
and `recipe.ProducedThingDef` (both Def-derived). **Deterministic on every path, no synced
command needed, nothing new on the sync surface.** The four fields are already on it anyway:
MP registers `repeatMode`, `repeatCount`, `targetCount`, `pauseWhenSatisfied`,
`unpauseWhenYouHave`, `hpRange` and `qualityRange` as synced *fields* applied from
`Dialog_BillConfig.DoWindowContents` **[V]**, so player edits after creation are handled.

**Presets.** The seeding runs in `GameComponent.FinalizeInit` from `DefDatabase` order, which
is identical on two clients running the same mod set — the only configuration Multiplayer
permits. No command, no `Rand`, no map or selection state. Assigning a pawn to a policy is
already synced: `SyncMethod.Register(typeof(Pawn_OutfitTracker), "CurrentApparelPolicy")` —
a sync **method** on the property setter, not a SyncField — as are `OutfitDatabase.MakeNewOutfit`,
`SetDefault`, `TryDelete` and `Policy.RenamableLabel` **[V]**. Everything the *player* does
with a preset afterwards is covered by the existing layer.

**Neither half may ever read `ModSettings`.** That is **T-18**, and the corpus contains two
live instances, one on each seam — see *Available mechanisms*.

---

## Failure and recovery

Evidence marks are on the mechanism cited, not on the mitigation, which is [I] by construction.

| Failure | Detection | Recovery |
|---|---|---|
| A def in either table names a ThingDef or RecipeDef that no longer exists | **Silent** (**T-04** — the entry is omitted, not nulled) **[V]** | Startup validation walks both tables and `Log.Warning`s each hole, per `WarnAboutGenesMissingFromPool`'s pattern |
| Bill postfix forces `TargetCount` on a recipe that cannot count | Loud, but broken: `CountProducts` indexes `recipe.products[0]` **[V]** | Gate 2 above. The failure mode is **T-58**'s |
| Bill postfix rewrites a Glittertech or mech bill | Silent — the bill just behaves oddly **[V]** on the type hierarchy | Gate 1's type allowlist |
| Another mod's prefix skips vanilla `MakeNewBill` and returns an unfamiliar `Bill` | Silent **[I]** | Gate 1 again: an allowlist fails closed, `is Bill_Production` fails open |
| A caller mutates the bill *after* `AddBill` — Nice Bill Tab does **[V]** | Silent | Out of reach of any Harmony priority on `MakeNewBill`. Accepted: it writes the ingredient filter and the name, neither of which we touch |
| `hpRange` set globally kills the O(1) count fast path on counted resources | Silent until profiled **[V]** | Per-recipe rows for `hpRange` |
| A preset names two `Belt`/`Waist` items | **Silent** — one is worn, no message **[V]** (`ApparelUtility.CanWearTogether`) | The one-belt rule, applied by the roster tickets |
| A preset names `mechanitorApparel` for a non-mechanitor | Silent — scored `-10f` and skipped **[V]** | Roster's; named here so it is known |
| Compositable Loadouts present with `onlyItemsFromLoadout` set | **Silent** — presets stop working entirely **[V]** | See the conditional incompatibility below |
| Compositable Loadouts present with the setting **off** | **Silent** — apparel scores are still rescaled for any pawn with a `LoadoutComponent` **[V]** | Not a failure so much as a competing scorer; same section |
| A player deletes a preset and it returns next load | n/a — cannot happen **[V]** | `seeded` records defNames, not policies |
| A preset names gear from an era the colony has not reached | Not a failure | Intended (#28) |

Neither half can corrupt a save. #95 writes only fields vanilla already scribes; #28 adds one
`HashSet<string>`, and removing the mod leaves ordinary apparel policies behind.

---

## Status

**Evidence class: READ.** Both halves were settled against the 1.6 assembly
(`RimWorldWin64_Data/Managed/Assembly-CSharp.dll`, build **1.6.4871 rev590**) and against
decompiled mod assemblies and read defs. Nothing here needs the game launched. Established by
[#95](https://github.com/cjd721/Rimworld-Archinity/issues/95) and
[#28](https://github.com/cjd721/Rimworld-Archinity/issues/28) and re-verified by the
adversarial audit of 2026-09-12, which returned **SOLID WITH FIXES**; the fixes are folded
into this document.

**Verified available mechanism** for both halves. Neither is an implementation commitment
yet: #28's roster and #95's quality floor are both requirement-side and unset.

- #95 — [#95](https://github.com/cjd721/Rimworld-Archinity/issues/95), splitting
  [#87](https://github.com/cjd721/Rimworld-Archinity/issues/87) (closed). Three of #87's four
  inherited claims re-verified and confirmed; the fourth (the injection point) confirmed with
  a namespace correction and three collision hazards #87 did not see.
- #28 — [#28](https://github.com/cjd721/Rimworld-Archinity/issues/28). The blocking question
  is answered **yes** for apparel and utility items and **no** for weapons.

**The proposed build is [I] by construction.** Every mechanism it composes is [V]; the claim
that they compose into what we want is untested until something is compiled.

---

## Available mechanisms

### Vanilla and DLC

| Mechanism | What it gives | Limit |
|---|---|---|
| `Bill_Production.{repeatMode,targetCount,hpRange,qualityRange}` | Public fields, already scribed with defaults **[V]** | Set per bill at construction; no XML seam |
| `RimWorld.BillUtility.MakeNewBill` | The single construction point for all five bill types **[V]** | Extension method on `RecipeDef`; **three** other mods already patch or call it |
| `Verse.RecipeWorkerCounter.CountProducts` | Consumes `hpRange`/`qualityRange` **[V]** | Product counting only, never ingredients; its O(1) fast path is already unreachable for apparel and uncounted gear |
| `RimWorld.BillRepeatModeUtility.MakeConfigFloatMenu` | Vanilla's own `CanCountProducts` gate, with a player-facing message **[V]** | The behaviour our postfix must copy; also transpiled by Compositable Loadouts |
| `RimWorld.ApparelPolicy` | A `ThingFilter` over apparel, layer-agnostic, reaches `Belt` **[V]** | Not a `Def`; runtime save state; no weapons |
| `RimWorld.OutfitDatabase.GenerateStartingOutfits` | Seeds **4 to 6** policies from five hardcoded tag strings — Anything, Worker, Soldier, Nudist always; `+Slave` with Ideology; `+Spacefarer` with Odyssey **[V]** | Tag list is in C#; new tags are unreachable from XML |
| `ApparelProperties.defaultOutfitTags` | XML-patchable — puts an item into vanilla's Worker/Soldier/Spacefarer outfits **[V]** | Can change what vanilla's outfits *contain*; cannot create a new outfit |
| `ThingCategoryDefOf.ApparelUtility` | Vanilla bulk-allows this whole category in three starting outfits **[V]** | — |
| `RimWorld.DrugPolicyDef` + `DrugPolicyDatabase.NewDrugPolicyFromDef` | **The donor.** Def-authored policies instantiated at game start, with `sourceDef` back-reference **[V]** | Drugs only; apparel has no equivalent |
| `RimWorld.JobGiver_OptimizeApparel` | Fetches and wears any policy-allowed apparel scoring ≥ 0.05 **[V]** | Three `-1000f` cases, four `-10f` early-outs, and the non-score gates listed above |
| `RimWorld.ApparelUtility.CanWearTogether` | The exclusion rule behind the one-belt constraint **[V]** | Shared layer + interfering body-part group ⇒ mutually exclusive, silently |

### The corpus — what shaped the build

**Four 1.6 mods reference `MakeNewBill`, not two.** `rg -a -l "MakeNewBill" -g '*.dll'
-g '!**/obj/**'` over both mod roots returns Better Workbench Management, Ushankas Glittertech
Expansion, Compositable Loadouts and **Nice Bill Tab** **[V]**. A null-interleaved UTF-16LE
pass (escapes typed literally into the pattern, never built through `$(…)`) returned zero,
confirming no mod reaches it by reflected string **[V]**.

**Better Workbench Management** (`falconne.BWM`, `935982361`, `1.6/Assemblies/ImprovedWorkbenches.dll`)
already postfixes this exact method. `ImprovedWorkbenches.Detours.BillUtility_MakeNewBill_Detour.Postfix`
casts to `Bill_Production`, sets `storeMode` when its own setting says so, and applies a
worktable pawn restriction from a `WorldComponent` **[V]**. Three things follow:

1. **The ordering question in #95 is moot against BWM, and for a better reason than ordering.**
   BWM writes `storeMode` and the pawn restriction; we write `repeatMode`, `targetCount`,
   `hpRange`, `qualityRange`. **Disjoint field sets — the order genuinely does not matter.**
   Which is fortunate, because the assembly carries **no** `[HarmonyPriority]`, `HarmonyBefore`
   or `HarmonyAfter` anywhere **[V]**, so with equal priority the order follows mod load order
   and is not declared by anyone. **But the seam is wider than ordering** — see Nice Bill Tab.
2. **It is a live T-18 instance, on the path we are about to join.** Its postfix calls
   `Main.Instance.ShouldDropOnFloorByDefault()`, which reads
   `ModSettings_ImprovedWorkbenches._dropOnFloorByDefault` **[V]** — and the add-bill delegate
   is replayed on *every* client **[V]**, so two players with different settings write different
   `storeMode` onto the same scribed bill. Multiplayer transmits the map *selection* as command
   context for that delegate **[V]**, which rescues the postfix's other divergent read
   (`Find.Selector.SingleSelectedThing`), but nothing restores a mod setting. This is a
   different defect from the count-setting hazard already recorded against BWM in
   `docs/data/MOD-VERDICTS.md`, on a different method.
3. It is the proof that the injection point works, which is what #87 claimed it for.

**Nice Bill Tab** (`Andromeda.NiceBillTab`, `3520130671`, `1.6/Assemblies/NiceBillTab.dll`)
matters twice. `NiceBillTab.ITab_Bills_FillTab_Patch.Prefix`
**returns `false`** whenever its own `Settings.EnabledMod` is true, replacing the tab wholesale
**[V]**; `NiceBillTab.TabBillsDrawer.TryAddBillToQueue` then calls
`BillUtility.MakeNewBill(recipe, selection.style)` itself and adds the result **[V]**. So our
postfix still fires — good — but:

- **A caller can mutate the bill *after* `AddBill`, and no Harmony priority reaches there.**
  `TryAddBillToQueue` calls `SetMaterialToBill(...)` — which does
  `bill.ingredientFilter.SetDisallowAll()` then `SetAllow(selection.material, true)` — and
  `AutoRenameBill(val)` under its own `Settings.EnableAutoNaming`, both **after**
  `billStack.AddBill(val)` **[V]**. Neither touches a field we write, so we are safe today —
  but "disjoint field sets" settles only BWM, not the seam. A future caller writing
  `repeatMode` after `AddBill` would silently win, and no Harmony declaration could stop it.
- **It removes the synced delegate.** With vanilla `FillTab` skipped, MP's
  `SyncDelegate.Lambda(typeof(ITab_Bills), "FillTab", 2)` never fires and creation falls
  entirely onto the `BillStack.AddBill` SyncMethod **[V]**. Whether a post-`AddBill` mutation
  survives that interception is Nice Bill Tab's problem, not ours **[I]**.

**Ushankas Glittertech Expansion** (`Ushanka.GlittertechExpansion`, `3522676478`) *prefixes*
the same method in **`3522676478/1.6/Assemblies/GlittertechExpansion.dll`** and returns `false`
for its own recipes, substituting `Bill_ModifyCell`, `Bill_Glittertech` or `Bill_Overclock`
**[V]**. Cite the 1.6 path specifically: the 1.5 build is a differently named
`GlitterworldUprising.dll` carrying one of the three branches and neither `Bill_ModifyCell`
nor `Bill_Overclock` **[I]**. This is what forces the type allowlist.

**Compositable Loadouts** (`Wiri.compositableloadouts`, `2679126859`,
`1.6/Assemblies/Inventory.dll`) is the only loadout mod in the corpus — Combat Extended,
Awesome Inventory, RPG Style Inventory and Simple Sidearms are all absent **[V]**. The first
mod is cited below for its weapon handling, but the load-bearing fact is that **it patches both
of our seams**:

- **`Inventory.OptimizeApparel_ApparelScoreGain_Patch` is a postfix on
  `JobGiver_OptimizeApparel.ApparelScoreRaw`** that sets `__result = -1000f` when
  `ModBase.settings.onlyItemsFromLoadout` is set and the pawn's `LoadoutComponent` does not
  desire the item **[V]**. **A colonist on an Archinity apparel preset with no matching loadout
  tag refuses to pick up the tool belt** — which is exactly the behaviour #28 exists to
  deliver. **And the setting gates only the hard kill.** The other branch of the same postfix
  fires whenever the pawn's loadout *does* desire the item — adding `0.24f`, applying a
  load-bearing-item bonus, and multiplying the score by the loadout weight **[V]** — so the
  mod perturbs apparel selection for **any** pawn carrying a `LoadoutComponent`, setting or
  no setting.
- **`Inventory.OptimizeApparel_TryGiveJob_Patch`** transpiles `TryGiveJob` so pawns *drop*
  apparel outside the loadout, on the same setting **[V]**.
- Both read `ModBase.settings` from inside AI that ticks on every client. **That is a second
  live T-18 instance, and unlike BWM's it is on the simulation path rather than a synced
  command** — there is no command context to rescue it.
- **`Inventory.MakeConfigFloatMenu_Patch`** transpiles `BillRepeatModeUtility.MakeConfigFloatMenu`
  to inject a mod-defined `BillRepeatModeDef` ("X per tag") **[V]**. It adds an option; it does
  not remove vanilla's `CanCountProducts` gate, so gate 2 above is unaffected.

Its own loadouts are **not Defs** either — `Inventory.Loadout` and `Inventory.Tag` are
`IExposable`, held by `Inventory.LoadoutManager : GameComponent`, built in `Dialog_TagEditor`
**[V]**, and it ships no loadout XML. It *is* the only thing in the corpus that reaches weapons
from a preset: `Inventory.ThinkNode_LoadoutRealisation` issues `JobDefOf.Equip` when
`item.def.IsWeapon && pawn.equipment.Primary == null` **[V]**.

**So the relationship is a conditional incompatibility, not an optional bridge.** If
Compositable Loadouts ships, either `onlyItemsFromLoadout` stays off on every client, or the
presets must be mirrored into its `Tag` objects — and the first is a per-client setting we
cannot enforce. See *Outstanding decisions*.

**Nothing in the corpus defines a `Def` subclass for equipment presets.** Sweeps for
`LoadoutDef`, `PresetDef`, `KitDef`, `OutfitDef` and `ApparelPolicyDef` across every `.dll`
(`rg -a -g '*.dll' -g '!**/obj/**'`, both mod roots plus `Data`) and every `.xml` return only
vanilla's own `IdeoPresetDef` — in type-reference tables and as real XML instances under
`Data/Ideology` and one mod — plus incidental substring hits in `Multiplayer.dll` and
`WorldTechLevel.dll` **[V]**. No hit is a mod-defined preset Def. The hit count varies with
how the sweep is spelled and is not quoted here; the negative does not.

### Corrections to standing documents

**`docs/specs/ITEMS.md` § *Quality and damage* is wrong and should be amended.** It states that
"`Bill.hpRange` and `Bill.qualityRange` filter which items are picked as **ingredients**, so
*'recycle only tattered gear'* … are already expressible on the bill", and that those sliders
"render only after the repeat mode is switched to `TargetCount`".

The capability is real; both field names are wrong, and the consequence is the opposite of
what is written:

- The ingredient-side gates are `bill.ingredientFilter.AllowedHitPointsPercents` and
  `.AllowedQualityLevels` **[V]** — `ThingFilter` fields, not `Bill_Production` fields.
- They are drawn by `Dialog_BillConfig.DoIngredientConfigPane`, a **separate method with no
  repeat-mode gate**, called with `forceHideHitPointsConfig: false, forceHideQualityConfig:
  false` **[V]**. Two further conditions apply and are easy to miss: the pane draws at all only
  when the recipe has at least one **non-fixed** ingredient **[V]**, and inside
  `ThingFilterUI.DoThingFilterConfigWindow` the two sliders are additionally gated on
  `ThingFilter.allowedHitPointsConfigurable` / `allowedQualitiesConfigurable` — both default
  `true` and recomputed from the allowed defs at `ResolveReferences` **[V]**.

So *"recycle only tattered gear"* is available on a reclaim bill **with no repeat-mode click at
all**, and does not wait on #95. The proposed replacement text is on
[#95](https://github.com/cjd721/Rimworld-Archinity/issues/95).

---

## Verification

**Settled by reading**, against RimWorld 1.6.4871 rev590:

`RimWorld.Bill_Production` (fields, `ExposeData`, `ShouldDoNow`, `RepeatInfoText`),
`RimWorld.BillUtility.MakeNewBill`, `RimWorld.Dialog_BillConfig.DoWindowContents` and
`.DoIngredientConfigPane`, `RimWorld.BillRepeatModeUtility.MakeConfigFloatMenu`,
`Verse.RecipeWorkerCounter.CanCountProducts` and `.CountProducts`, `RimWorld.ITab_Bills.FillTab`,
`Verse.ThingFilter`, `Verse.ThingDef` (`CountAsResource`, `resourceReadoutPriority`,
`useHitPoints`), `RimWorld.ApparelProperties.careIfWornByCorpse`, `Verse.Game.ExposeData` /
`.ExposeSmallComponents` / `.FillComponents`;
`RimWorld.ApparelPolicy`, `RimWorld.Policy`, `RimWorld.OutfitDatabase`, `Verse.ApparelLayerDef`,
`RimWorld.ApparelLayerDefOf`,
`RimWorld.JobGiver_OptimizeApparel.{TryGiveJob,ApparelScoreGain,ApparelScoreRaw,SetNextOptimizeTick}`,
`RimWorld.ApparelUtility.CanWearTogether`, `RimWorld.DrugPolicyDef`, `RimWorld.DrugPolicyDatabase`,
`RimWorld.JobGiver_PickUpOpportunisticWeapon`, `Verse.GameComponent`;
`ImprovedWorkbenches.Detours.BillUtility_MakeNewBill_Detour`, `ImprovedWorkbenches.Main.ShouldDropOnFloorByDefault`,
`USH_GE.Patch_BillUtility_MakeNewBill`, `NiceBillTab.ITab_Bills_FillTab_Patch`,
`NiceBillTab.TabBillsDrawer.{TryAddBillToQueue,SetMaterialToBill}`,
`Inventory.{Loadout,Tag,Item,ThinkNode_LoadoutRealisation,OptimizeApparel_ApparelScoreGain_Patch,OptimizeApparel_TryGiveJob_Patch,MakeConfigFloatMenu_Patch}`,
`Multiplayer.Client.{SyncMethods,SyncDelegates,SyncFields,Multiplayer}`.

**Observable checks once built.**

1. Add any crafting bill at a bench. Expect it to open on *"Do until you have N"* with the
   target box and both sliders already drawn, at the table's values.
2. Add a butchery or smelting bill. Expect it to stay on *"Repeat N times"* — gate 2 holding,
   and **T-58** not tripped.
3. With Glittertech Expansion loaded, add an overclock bill. Expect its repeat mode untouched.
4. Add a smithing bill that uses an unfinished thing. Expect the defaults **applied** —
   `Bill_ProductionWithUft` is in the allowlist, and a failure here is the allowlist being
   too narrow.
5. With Nice Bill Tab loaded, add a bill through its replacement tab. Expect the same defaults,
   and expect its material selection to survive alongside them.
6. Start a new colony. Expect the presets in the Assign tab's dropdown, and no pawn assigned
   to one.
7. Assign a pawn to the Smith preset with a tool belt **in a stockpile** — not on open ground,
   per `IsInAnyStorage()` — and wait up to ~9000 ticks. Expect the pawn to fetch and wear it.
   **This is the observation that closes #28's blocking question in play**, and the one that
   would falsify the score arithmetic above.
8. Repeat 7 with Compositable Loadouts loaded and `onlyItemsFromLoadout` **on**. Expect the
   pawn to refuse, confirming the conditional incompatibility rather than discovering it in a
   playtest.
9. Repeat 7 again with that setting **off** but the pawn carrying a loadout. Expect it to
   work, but check the chosen item against the no-loadout run — a different pick is the
   score-rescaling branch, and it is the half that no setting turns off.
10. Give a preset both a tool belt and a shield belt. Expect one worn item, silently — the
    one-belt rule.
11. Delete a preset, save, reload. Expect it gone and staying gone.
12. Load a save made before the mod. Expect the presets to appear and no existing bill to change.

---

## Outstanding decisions

> **Partly answered by [#129](https://github.com/cjd721/Rimworld-Archinity/issues/129).**
> `docs/requirements/COLONY.md` § *Bills arrive configured, and a configuration can be
> reused* now owns crafting defaults, and settles **which row carries what**: the global row
> carries the **repeat mode only**, and both floors live on **per-recipe rows** — which
> honours this document's own "do not set it globally" constraint by construction. The two
> floor *values*, and whether they vary by era, remain open exactly as described below.
>
> #129 also adds a requirement this document does not cover: **a bill's configuration can be
> copied onto another bill, carrying the settings and not the recipe.** That is
> [#157](https://github.com/cjd721/Rimworld-Archinity/issues/157), and it lands here when it
> resolves.

**The quality floor is a requirement, not a mechanism, and nothing owns it.** #95 names the
problem exactly: *"Good status" is not a number*, and `QualityCategory.Good` is index 4 of 0–6.
The mechanism takes any `QualityRange`; which one the campaign wants is a gameplay rule. It
belongs to [#96](https://github.com/cjd721/Rimworld-Archinity/issues/96), the open owner of
the crafting surface — #87 established that **no requirements document owns menu legibility or
crafting defaults at all**, and `docs/progression/` holds only a README. Two sub-questions for
whoever sets it: the floor value, and whether it varies by era (an era-varying floor also wants
`docs/progression/`'s grid, which does not exist).

**The durability floor has the same shape** and the same owner, plus one mechanical constraint
this document does own: **do not set it globally**, because on a counted-resource recipe it is
the one case that costs a real fast path.

**The preset roster is #19/#20/#41/#42's**, explicitly out of scope for #28. This document
carries the mechanism; the rows are theirs — subject to **the one-belt rule** and the
`mechanitorApparel` and `ignoredByNonViolent` gates above, which are roster constraints
discovered here.

**Compositable Loadouts is a conditional incompatibility, not an optional bridge.** Its
`ApparelScoreRaw` postfix does two things, and the second is the one that is easy to miss:

- **With `ModBase.settings.onlyItemsFromLoadout` set**, it returns `-1000f` for anything
  outside a pawn's loadout **[V]**, which disables our presets outright; its `TryGiveJob`
  transpiler additionally makes pawns drop what they are already wearing.
- **With the setting off, it still perturbs scoring for every pawn that has a
  `LoadoutComponent` at all.** The `num != 0f` branch adds `0.24f`, applies a
  load-bearing-item bonus, and multiplies the whole score by the loadout weight **[V]**.
  So the mod's effect on apparel selection is **not** gated behind its setting — the setting
  gates only the hard kill. The presets and the mod therefore compete over scoring in every
  configuration, and only the severity changes.

Three options:

- **Ship the presets and require the setting off** (recommended). Zero code, and it removes
  the hard kill — but per the second bullet it does not make the two systems agree, only stop
  them fighting outright. The residual risk is that this is a *per-client* setting we cannot
  enforce from a Def, so the two players must agree — and disagreeing is itself the T-18
  divergence described above, which is Compositable Loadouts' defect either way, present with
  or without our presets.
- **Mirror each preset into an `Inventory.Tag` by reflection when the mod is present**, ~40
  lines, degrading to silence when absent — the pattern
  `ArchinityMod.NeutraliseArchonEquipmentGate` already uses against VRE-Archon. This makes the
  two systems agree instead of fight, and would also carry the weapon half. Worth doing **only
  if the mod survives playtest**, and now with a stronger reason than convenience.
- **Treat the mod as excluded.** A sourcing decision, not ours —
  [#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s.

**Whether the soldier presets get a weapon half.** Ship apparel-only (recommended, zero extra
cost); or take the Compositable Loadouts bridge above, which supplies weapons as a side
effect; or build a per-pawn weapon preference ourselves — ~150+ lines of new AI surface
duplicating a mod already on disk, **not recommended**, and properly a separate behaviour with
its own ticket.

**What `defaultOutfitTags` could do instead, and why it is not the build.** Patching
`<defaultOutfitTags>` onto ThingDefs is pure XML and needs no code at all — but it can only
change what vanilla's four-to-six existing outfits contain, since the tag strings are hardcoded
**[V]**. It is the right tool for *"our new tool belt should be in the Worker outfit"* and the
wrong one for *"ship a Miner preset"*. If the roster collapses onto vanilla's Worker/Soldier
split, this becomes the cheaper answer and the GameComponent is unnecessary. That is a roster
question, so it resolves with #19/#20/#41/#42.
