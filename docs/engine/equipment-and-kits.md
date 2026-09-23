# Equipment and kits

**What reaches a pawn's weapon, what reaches its apparel, and which of those is
authorable.** Verified against `RimWorldWin64_Data/Managed/Assembly-CSharp.dll`
build **1.6.4871**, `Data/Odyssey`, `2606448745/1.6/AssembliesCustom/Multiplayer.dll`
and `2679126859/1.6/Assemblies/Inventory.dll`.

The apparel *scoring* half — `JobGiver_OptimizeApparel`'s thresholds, the utility
layer, `CanWearTogether` and the one-belt rule — lives in
[`items-and-materials.md`](items-and-materials.md) and is not repeated here. This file
owns the **set**: how a whole kit gets authored, assigned and taken off again.

Established by [#28](https://github.com/cjd721/Rimworld-Archinity/issues/28) and
[#155](https://github.com/cjd721/Rimworld-Archinity/issues/155).

## The `Policy` family reaches no weapons

1.6's `RimWorld.Policy` subclasses are **`ApparelPolicy`, `DrugPolicy`, `FoodPolicy`,
`ReadingPolicy`** — there is no weapon policy **[V]**. `RimWorld.ApparelPolicy` has
exactly one field, `public ThingFilter filter`, plus `CopyFrom` and `ExposeData`
**[V]**. `RimWorld.Pawn_OutfitTracker` carries only `curApparelPolicy` and
`forcedHandler` **[V]**. `RimWorld.Policy` itself carries `id`, `label` and
`RenamableLabel` **[V]**.

Vanilla's only weapon-acquisition AI remains `RimWorld.JobGiver_PickUpOpportunisticWeapon`,
an opportunistic think node — not a per-pawn preference **[V]**.

**Weapons are unreachable *from the policy layer*. They are not unreachable from
vanilla** — see the outfit stand, below. #28's resolution and an earlier draft of
`docs/specs/DEFAULTS.md` stated the broader claim; that part is wrong and is corrected
there.

`ApparelPolicy` also has **no `Def` backing** anywhere in vanilla, the DLC or the
corpus: the database is runtime save state scribed by `OutfitDatabase.ExposeData`
**[V]**. `RimWorld.DrugPolicyDef` is the one policy family that *does* have its Def
half, and `DrugPolicyDatabase.GenerateStartingDrugPolicies` is the donor shape for
building the missing one **[V]**.

## The outfit stand is vanilla's authored equipment set, and it includes the weapon

`RimWorld.Building_OutfitStand` — Odyssey. The `ThingDef` is in
`Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Furniture.xml`; the class is in
`Assembly-CSharp` **[V]**.

**It holds apparel and one weapon.** `HeldWeapon`, `TryAddHeldWeapon` (which refuses a
second) and `holdingWeaponCached` **[V]**. `IHaulDestination.Accepts` admits apparel
that passes `GetStoreSettings().AllowedToAccept` and `HasRoomForApparelOfDef`, and one
weapon **[V]**.

**The set is XML-authorable, with two silent traps.** `Building_OutfitStand.PostMake`
copies `def.building.defaultStorageSettings` **[V]**, bounded by `fixedStorageSettings`
(categories `Apparel`, `Weapons`) **[V]**. But **`OutfitStandBase` declares neither
`<thingClass>` nor `<storageGroupTag>`** — both are on the concrete def **[V]** — so a
def derived from the base alone inherits `<thingClass>Building</thingClass>` from
`BuildingBase` **[V]** and loads as a plain building with no gizmo, no contents and
**no error**. And the base's `<defaultStorageSettings>` disallows `ApparelUtility` and
`Weapons` **[V]** in a list that inheritance *appends to* rather than replaces, so
admitting the weapon needs `<disallowedCategories Inherit="False">` or a `<thingDefs>`
filter. See **T-136**.

**Assigning it is one gizmo.** `GetGizmos` yields a *Swap outfit* `Command_Action`
that begins targeting on `TargetingParameters.ForColonist()` and issues
`JobDefOf.UseOutfitStand` at the chosen pawn **[V]**. The same acts are on the pawn
side through `GetFloatMenuOptions`: *Swap outfit*, per-item *Force wear* /
*Force target to wear* (which can also target another stand, via
`JobDefOf.PutApparelOnOutfitStand`), and *Equip* for the held weapon **[V]**.

**`JobDriver_UseOutfitStand.DoTransfer` is the whole transfer, and it is worth reading
before writing anything like it** **[V]**:

- removes every worn item that fails `ApparelUtility.CanWearTogether` against an
  incoming item, and refuses the incoming item outright if the conflicting worn item is
  `pawn.apparel.IsLocked`;
- wears each transferred item and calls
  `pawn.outfits.forcedHandler.SetForced(item, forced: true)` — **so the stand's outfit
  escapes the apparel policy**, because `JobGiver_OptimizeApparel` will not
  automatically drop a forced item;
- puts the displaced apparel back on the stand;
- for the weapon, `pawn.equipment.MakeRoomFor(heldWeapon, out dropped)` then
  `AddEquipment`, and the displaced weapon goes onto the stand.

`Notify_Starting` pre-computes the job duration from each item's `StatDefOf.EquipDelay`
and skips anything failing `PawnCanWear`, `HasPartsToWear` or a biocode check **[V]**.
The private `PawnCanWieldWeapon` gates the weapon on `WorkTags.Violent`,
`WorkTags.Shooting` for ranged, `PawnCapacityDefOf.Manipulation`,
`EquipmentUtility.QuestLodgerCanEquip` and `EquipmentUtility.CanEquip` **[V]**.

**What it is not.** It is a **one-shot swap, not a standing assignment** — a pawn that
loses its weapon does not return to the stand. One stand is one kit for one pawn at a
time, and the previous occupant's cast-offs are left on it. It equips *things*, not
defs, so "wear the best currently reachable" is the apparel policy's property, not the
stand's. And it is gated on research `ComplexFurniture`, techLevel **Medieval** **[V]**
— unavailable on a neolithic start until that era, unless a kit-specific def patches
the prerequisite off.

**Two stands can share one authored filter.** Stands are `IStorageGroupMember` with
`storageGroupTag` `OutfitStand`, and `GetGizmos` yields
`StorageSettingsClipboard.CopyPasteGizmosFor(GetStoreSettings())` — vanilla's
copy-a-configuration-onto-another gizmo pair **[V]**.

### Multiplayer covers the outfit stand deliberately

`Multiplayer.Client.SyncMethods` registers `Building_OutfitStand.TryDrop`,
`Building_OutfitStand.SetAllowHauling`, and
`SyncMethod.Lambda(typeof(Building_OutfitStand), "GetGizmos", 1)` **[V]**. By
declaration order, lambda 1 in `GetGizmos` is the *Swap outfit* targeting callback —
the act that decides which pawn is sent **[I]**. `ITab_ContentsOutfitStand` derives
from `ITab_ContentsBase`, whose `OnDropThing` is registered **[V]**. The float-menu
path terminates in `Pawn_JobTracker.TryTakeOrderedJob`, registered with
`.SetContext(8).ExposeParameter(0)` **[V]**.

## A standing colonist cannot be stripped

`Verse.StrippableUtility.CanBeStrippedByColony` returns true only for a non-pawn
`IStrippable`, a **downed** pawn, or a **secure prisoner of the colony** — a healthy
standing colonist falls through to `return false` **[V]**. So
`RimWorld.FloatMenuOptionProvider_Strip` never offers on one **[V]**.

The shipped per-item verbs are:

- `RimWorld.ITab_Pawn_Gear.InterfaceDrop` — any worn or carried item, one at a time
  **[V]**. MP registers it (`SetContext(10).CancelIfAnyArgNull()`) **[V]**.
- `RimWorld.FloatMenuOptionProvider_DropEquipment` → `JobDefOf.DropEquipment` on
  `pawn.equipment.Primary`, refused for a quest lodger that
  `EquipmentUtility.QuestLodgerCanUnequip` rejects **[V]**. Reaches MP through
  `TryTakeOrderedJob` **[V]**.
- `Verse.Pawn_EquipmentTracker.{TryDropEquipment, DropAllEquipment, MakeRoomFor}` are
  the code-level equivalents **[V]**; `DropAllEquipment` has no player-facing verb.

**There is no vanilla "drop everything" for a colonist.** Anything that wants one is
new code.

## `PawnKindDef` is a full XML kit, at generation time only

`Verse.PawnKindDef` carries `apparelRequired` (`List<ThingDef>`), `apparelTags`,
`apparelDisallowTags`, `specificApparelRequirements`, `minApparelQuality` /
`maxApparelQuality`, `apparelMoney`, `weaponTags`, `weaponMoney`,
`weaponStuffOverride`, `weaponStyleDef`, `forceWeaponQuality`, `biocodeWeaponChance`,
`techHediffsRequired`, `fixedInventory` and `inventoryOptions` **[V]**.

That is a complete authored kit including the weapon, in pure XML — applied at **pawn
generation**. It reaches arrivals, quest pawns and generated starting colonists. It
does not re-kit an existing pawn.

## Compositable Loadouts — the corpus's only loadout mod, and it is unsynced in 1.6

`Wiri.compositableloadouts` (`2679126859`, `1.6/Assemblies/Inventory.dll`). Its
scoring interference with apparel policies is recorded in
`docs/specs/DEFAULTS.md`; the set-level facts:

- `Inventory.Loadout` and `Inventory.Tag` are `IExposable` on
  `Inventory.LoadoutManager : GameComponent`, **not `Def`s**, and the mod ships no
  loadout XML **[V]**. Their public surface is complete enough to seed from outside
  — `public Tag(string name)`, `public List<Item> requiredItems`, `Tag.Add(ThingDef)`,
  `LoadoutManager.AddTag(Tag)`, `LoadoutManager.GetNextTagId()` over
  `UniqueIDsManager.GetNextID`, `LoadoutComponent.AddTag(...)` **[V]**.
- **It equips a weapon only into an empty hand.**
  `Inventory.ThinkNode_LoadoutRealisation.FindItem` issues `JobDefOf.Equip` when
  `count == 1 && item2.def.IsWeapon && pawn.equipment.Primary == null` **[V]** — it
  never swaps a weapon the pawn is already holding.
- `Inventory.LoadoutComponent.CompGetGizmosExtra` yields two `Command_Action`s, gated
  on `!ModBase.settings.hideGizmo` **[V]**: *Satisfy loadout now* →
  `Loadout.RequiresUpdate()`, and *Clear inventory now* →
  `Utility.EnqueueEmptyInventory(pawn)` → `InvJobDefOf.CL_UnloadInventory` via
  `TryTakeOrderedJob` **[V]**. **Clear inventory empties the inventory only** — not
  equipment, not apparel.
- `ThinkNode_LoadoutRealisation.SetPawnLastUpdated` calls `Rand.Range(10000, 15000)`
  inside the think node **[V]**.

**Multiplayer Compatibility carries no compat class for it in 1.5 or 1.6.**
`Wiri.compositableloadouts`, `CompositableLoadouts`, `LoadoutManager`,
`LoadoutComponent` and `Dialog_TagEditor` appear in exactly one file under
`1629973374` — `1.4/Referenced/Multiplayer_Compat_Referenced.dll` — and nowhere in the
1.5 or 1.6 `Assemblies/` or `Referenced/` binaries **[V]**. Both sweep forms were
validated on those same files (`VREAndroids`, null-interleaved UTF-16LE, hits 1.4, 1.5
and 1.6). `Loadout.RequiresUpdate()` writes `needsUpdate`, which `Loadout.ExposeData`
scribes **[V]**, from a gizmo with no synced command behind it — the textbook
divergence shape **[I]**.

## What is absent from the corpus

Sweeps over both mod roots and `Data/`, `-g '!**/obj/**' -g '!**/Referenced/**'`, both
ASCII and null-interleaved UTF-16LE, validated against known hits:

- `-i "Loadout"` returns three mods: Compositable Loadouts (1.4/1.5/1.6), **EdB Prepare
  Carefully (1.2/1.3/1.4 only — nothing in a 1.6 assembly)**, and RimPacts
  (`3762723122`), whose only loadout identifiers are `generateLoadoutFor` and
  `loadoutExtType` — raid composition, not a player kit **[V]**.
- `LoadoutDef`, `KitDef`, `GearSet`, `WeaponPolicy`, `EquipmentPolicy`, `WeaponPreset`,
  `OutfitPreset`, `ApparelPolicyDef` — **zero** **[V]**. The same sweep form returns
  hits for `Sidearm`.
- Enumerating every `<Namespace.TypeDef>` tag across both roots and `Data/` gives 152
  distinct namespaced def tags; **none is a kit, loadout or equipment-preset def**
  **[V]**. Validators from the same table: `<VFEC.Perks.PerkDef>` 152,
  `<VanillaPsycastsExpanded.PsycasterPathDef>` 88, `<VSE.Expertise.ExpertiseDef>` 29.
- Combat Extended, Better Pawn Control, Awesome Inventory, RPG Style Inventory and
  Simple Sidearms are absent from both roots as standalone mods **[V]**.

**Who else names `Building_OutfitStand`:** Multiplayer, Vanilla Expanded Framework
(`VEF.dll`, `MVCF.dll`), Worksites Expanded and Better Traders Guild — metadata hits,
so **[I]** as to behaviour. The XML side shows the mod-side uses are **content, not
behaviour**: Better Traders Guild stocks stands through a `GenStepDef` and armoury
`LayoutRoomDef`s, and two other mods place them in structure layouts and gravship
prefabs **[V]**. **No mod in the corpus ships an XML patch against the stand's ThingDef
or its jobs** **[V]**.
