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
- **A kit covers the whole pawn, weapon included**, and the player can force a pawn to
  re-equip to it or drop what it carries.
  [#155](https://github.com/cjd721/Rimworld-Archinity/issues/155). This is the clause #28
  could not reach; its answer is *The whole kit, weapon included*, below, and it
  **corrects** one claim #28 left standing.
- **A bill's configuration can be pasted onto another bill**, carrying the settings and
  not the recipe, across recipes and benches.
  [#157](https://github.com/cjd721/Rimworld-Archinity/issues/157). Its answer is *A bill's
  configuration, pasted onto another bill*, below. It sits on top of the #95 defaults.

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

## The whole kit, weapon included

Answers `docs/requirements/COLONY.md` § *A pawn's gear can be assigned as a set* in
full, where *Half two* below answers only its apparel clause. Established by
[#155](https://github.com/cjd721/Rimworld-Archinity/issues/155), evidence class
**READ**. This section follows the routes rule in `docs/specs/README.md`; the two
halves below it predate that rule and lead with a build instead.

### Verdict

- **Possible?** **Yes**, and by more than one route — but **no single shipped mechanism
  satisfies all five clauses of the requirement.** Vanilla splits it: the **apparel
  policy** is the standing, fresh-colony-present, era-tolerant half and carries no
  weapon; **Odyssey's outfit stand** carries the weapon and both "do it now" verbs and is
  a one-shot physical swap. Composing the two covers every clause except a single
  "drop it all" act, which has no vanilla verb at any price. One route covers all five,
  at Hard.
- **Multiplayer?** **Yes for every vanilla route.** Multiplayer registers
  `Building_OutfitStand.TryDrop`, `Building_OutfitStand.SetAllowHauling`, a lambda inside
  `Building_OutfitStand.GetGizmos`, `ITab_ContentsBase.OnDropThing`,
  `ITab_Pawn_Gear.InterfaceDrop`, `Pawn_JobTracker.TryTakeOrderedJob` and
  `Pawn_OutfitTracker.CurrentApparelPolicy` **[V]**. **No** for the Compositable Loadouts
  route — MP Compat ships no compat class for it in 1.5 or 1.6 **[V]**.

### The claim this corrects

**#28 concluded that "weapons are not reachable by this layer at all", and half of that
survives.** Re-read against 1.6.4871:

- ✅ **The `Policy` layer reaches no weapons — confirmed [V].** `RimWorld.ApparelPolicy`
  has exactly one field, `public ThingFilter filter`; `RimWorld.Policy` carries only
  `id`/`label`/`RenamableLabel`; `RimWorld.Pawn_OutfitTracker` carries only
  `curApparelPolicy` and `forcedHandler`; the family is
  `ApparelPolicy`/`DrugPolicy`/`FoodPolicy`/`ReadingPolicy` and there is no fifth
  subclass **[V]**.
- ❌ **"Compositable Loadouts is the only thing in the corpus that reaches weapons from a
  preset" — FALSE in 1.6 [V].** Vanilla Odyssey's `RimWorld.Building_OutfitStand` holds
  apparel **and one weapon** and transfers both **[V]**, and it is the better carrier of
  the two, because Multiplayer ships explicit sync for it and none for the mod. The
  sentence in *Available mechanisms* below is corrected accordingly.

The accurate statement is narrower: **weapons are unreachable from the policy layer;
they are not unreachable from vanilla.**

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A** | Authored kits **including the weapon**, shipped as `ThingDef`s; one-click force-re-equip onto any colonist | vanilla (Odyssey) `Building_OutfitStand` | XML — one `ThingDef` per kit | **Easy** | **Yes** |
| **B** | Standing, fresh-colony-present apparel sets that survive era drift — *Half two* below, **apparel only** | our code, donor `RimWorld.DrugPolicyDef` | C# | **Medium** | **Yes** |
| **C** | Standing kits with weapon, inventory and quality filters, and two "do it now" gizmos | Compositable Loadouts (`Wiri.compositableloadouts`, `2679126859`) | dependency + C# reflection to seed | **Medium** | **No — not recommended** |
| **D** | Every clause, standing and authored, with both verbs | our code, donors `JobDriver_UseOutfitStand` + `Inventory.ThinkNode_LoadoutRealisation` | C# | **Hard** | With work |
| **E** | An authored kit incl. weapon on **generated** pawns — arrivals, quest pawns, starting colonists | vanilla `PawnKindDef` | XML | **Easy** | **Yes** |

**Every route is [I] as a route.** The mechanisms each composes are [V] and cited in
`docs/engine/equipment-and-kits.md`; the claim that they compose into the requirement is
untested until something is compiled.

**Clause coverage, because no single route is complete.**

| Requirement clause | A (stand) | B (policy) | C (CL) | D (build) | E (kind) |
|---|---|---|---|---|---|
| Authored, shipped, present in a fresh colony | partial — the *def* ships; the player must build and stock the stand | **yes** | only if seeded | yes | yes |
| Covers the weapon | **yes**, one | **no** | yes, but **never swaps an existing weapon** | yes | yes |
| One act, then the pawn equips itself | one act, **one-shot** — not standing | standing, **not** one act | standing | yes | n/a |
| Force re-equip | **yes** — re-target the stand | no | yes (gizmo, unsynced) | yes | no |
| Force drop | partial — conflicting apparel only | no | **inventory only** | yes | no |
| Unreached-era gear is not a failure | yes — the stand just stays empty | **yes** — a `ThingFilter` allows unreached defs and the pawn wears the best it can reach | yes | yes | n/a |

#### Route A — Odyssey's outfit stand, one `ThingDef` per kit

**What it gets us.**

- **A weapon in an authored set, in vanilla, today.** The stand's contents are apparel
  plus one weapon, and `JobDriver_UseOutfitStand.DoTransfer` moves both — including
  `pawn.equipment.MakeRoomFor` + `AddEquipment`, putting the pawn's old weapon back on
  the stand **[V]**.
- **The set is authorable in pure XML, but the recipe has two silent traps in it.**
  `Building_OutfitStand.PostMake` copies `def.building.defaultStorageSettings` **[V]**,
  and `OutfitStandBase`'s `<fixedStorageSettings>` bounds any derived def to categories
  `Apparel` and `Weapons` **[V]**. So a `ThingDef` per role ships a stand that already
  asks for the Smith's kit the moment it is built, and haulers fill it **[V]**. Two
  things the recipe must get right, **both of which fail with no error at all**:

  1. **`ParentName="OutfitStandBase"` is not enough — the def must declare
     `<thingClass>Building_OutfitStand</thingClass>` itself.** `OutfitStandBase` is
     `ParentName="FurnitureBase" Abstract="True"` and declares **neither `<thingClass>`
     nor `<storageGroupTag>`**; both sit on the concrete `Building_OutfitStand` def
     **[V]**. The inherited class comes from `BuildingBase`, which declares
     `<thingClass>Building</thingClass>` **[V]**, and `Verse.Building : ThingWithComps`
     implements no `IStoreSettingsParent`, no `IThingHolder` and no `IApparelSource`
     **[V]**. A base-derived def therefore loads cleanly as a **plain building**: no
     *Swap outfit* gizmo, no contents, no storage settings applied to anything, and
     **nothing logged**. The inherited `<inspectorTabs>` still name
     `ITab_ContentsOutfitStand`, whose `SelThing as Building_OutfitStand` is then null
     **[V]** — so the tab has no valid target either **[I]**.
  2. **The shipped `<defaultStorageSettings>` disallows `Weapons` *and* `ApparelUtility`,
     and a child def cannot un-disallow them by listing something else.**
     `OutfitStandBase`'s default filter allows category `Apparel` and puts `ApparelUtility`
     and `Weapons` under `<disallowedCategories>` **[V]** — so the shipped default admits
     neither the weapon this route exists for nor the tool belts *Half two* exists for,
     even though `fixedStorageSettings` permits both. And per
     [`docs/engine/def-loading.md`](../engine/def-loading.md) § *Inheritance appends lists,
     it does not replace them*, `XmlInheritance.RecursiveNodeCopyOverwriteElements`
     **appends** list children **[V]**, so a child's `<disallowedCategories>` adds to the
     parent's rather than replacing it. Admitting the weapon needs
     `<disallowedCategories Inherit="False">`, or an authored filter that names
     `<thingDefs>` instead of categories. Getting this wrong produces a kit stand that
     silently never receives its weapon.

  Neither is a blocker and neither changes the weight — this is still XML, still **Easy**
  — but the recipe is *"derive, **declare `thingClass`**, and override the default filter
  with `Inherit="False"`"*, not *"derive"*.
- **"Force re-equip" is the gizmo.** *Swap outfit* on the stand targets a colonist and
  issues `JobDefOf.UseOutfitStand` **[V]**. The pawn side offers the same through
  `GetFloatMenuOptions`, plus per-item *Force wear* and *Equip* for the held weapon
  **[V]**.
- **The kit escapes the apparel policy.** `DoTransfer` calls
  `forcedHandler.SetForced(item, forced: true)` on everything it puts on **[V]**, and
  `JobGiver_OptimizeApparel` will not automatically drop a forced item — see *The gates
  that can stop it anyway* below. This is the clean answer to "the policy keeps undoing
  my kit".
- **The kit's filter is copy-pasteable between stands.** `GetGizmos` yields
  `StorageSettingsClipboard.CopyPasteGizmosFor(GetStoreSettings())` **[V]**, which needs
  only the `thingClass` from trap 1 above. **Storage *groups* are a separate opt-in** —
  `<storageGroupTag>OutfitStand</storageGroupTag>` sits on the concrete vanilla def, not
  on `OutfitStandBase` **[V]**, so a derived kit def joins no group unless it declares the
  tag, and `Building_OutfitStand.StoreSettings` then falls through to its own `settings`
  **[V]**. For kit stands that is arguably the behaviour we want — two Smith stands
  sharing one filter is useful, a Smith stand and a Cook stand sharing one is not — but it
  is a decision the def has to make, not a default.

**What it cannot do.** It is **not a standing assignment** — one transfer, then nothing;
a pawn that loses its weapon does not go back. One stand is one kit for one pawn at a
time, and the previous occupant's cast-offs are left on it. One weapon only
(`TryAddHeldWeapon` refuses a second) **[V]**. It equips *things*, not defs, so "wear the
best currently reachable" is the policy's property, not the stand's. **No full strip** —
only apparel that *conflicts* with an incoming item comes off **[V]**.

**Consequences.** Kits become *places*, not settings: the colony grows an armoury. That
fits the campaign's "kits are assembled, not granted" line, but it forecloses "assign the
Smith preset from the Assign tab" as the interaction, and it is visible to the player in a
way a policy is not. Two drags: the stand is gated on research `ComplexFurniture`,
techLevel **Medieval** **[V]** — **unavailable on a neolithic start until the second era**
unless a kit-specific def patches the prerequisite off, which is pure XML — and a stand
defaults to storage `priority: Important` **[V]**, so a kit stand competes with real
stockpiles for the items it names. It also requires **Odyssey**: the `ThingDef` is under
`Data/Odyssey` **[V]**, though the class and its hardcoded texture paths are in
`Assembly-CSharp` **[V]**.

#### Route B — the apparel presets (the floor this must beat)

*Half two* below, unchanged and still correct. **It gets us the two clauses Route A
cannot**: present in a fresh colony as a selectable list entry, and standing — with the
era-tolerance clause free, because a `ThingFilter` allows defs the colony has not reached
and `JobGiver_OptimizeApparel` takes the best that exists **[V]**. **It gets us no weapon
and neither verb.**

**A and B compose cleanly and do not fight.** The policy governs the wardrobe; the stand
overrides it with force-worn items and hands over the weapon. That is the cheapest honest
answer to the requirement, and **the one I would cost out first** — though a spec never
selects, and #119 does.

#### Route C — Compositable Loadouts, ruled out on Multiplayer

The three things the ticket asked, answered.

1. **The weapon seam is narrower than it looked.**
   `Inventory.ThinkNode_LoadoutRealisation.FindItem` issues `JobDefOf.Equip` only when
   `count == 1 && item2.def.IsWeapon && pawn.equipment.Primary == null` **[V]** — **it
   never swaps a weapon the pawn is already holding**, which is the wrong half of "force a
   pawn to re-equip to its set". `JobDefOf.Equip` itself is vanilla; the seam is not the
   mod's to own.
2. **Seeding its types does work, and buys less than it costs.** `Inventory.Tag` is fully
   public (`public Tag(string name)`, `public List<Item> requiredItems`, `Add(ThingDef)`),
   and `Inventory.LoadoutManager : GameComponent` exposes `public static void AddTag(Tag)`
   and `GetNextTagId()` over `UniqueIDsManager.GetNextID` **[V]**. So the #28 seeding trick
   reaches them through the `ArchinityMod.NeutraliseArchonEquipmentGate` reflection pattern
   **[I] as a composition**. The cost is a hard dependency on a third party's internal class
   shape with no API contract, on top of the two live **T-18** instances already recorded
   below.
3. **Both gizmos confirmed, and neither is what the requirement says.**
   `Inventory.LoadoutComponent.CompGetGizmosExtra` yields exactly two `Command_Action`s,
   gated on `!ModBase.settings.hideGizmo` **[V]**: *Satisfy loadout now* →
   `Loadout.RequiresUpdate()`, which sets `needsUpdate`, a field `Loadout.ExposeData`
   scribes **[V]**; and *Clear inventory now* → `Utility.EnqueueEmptyInventory(pawn)` →
   `InvJobDefOf.CL_UnloadInventory` via `TryTakeOrderedJob` **[V]** — which **empties the
   inventory only**, touching neither equipment nor worn apparel.

**And Multiplayer Compatibility does not cover this mod in 1.6.**
`Wiri.compositableloadouts`, `CompositableLoadouts`, `LoadoutManager`, `LoadoutComponent`
and `Dialog_TagEditor` appear in exactly one file under `1629973374` —
`1.4/Referenced/Multiplayer_Compat_Referenced.dll` — and nowhere in the 1.5 or 1.6
`Assemblies/` or `Referenced/` binaries **[V]**; both sweep forms were validated on those
same files. So *Satisfy loadout now* writes a scribed field on one client with no synced
command behind it — **[V]** on the mechanism, **[I]** on the divergence — while *Clear inventory
now* survives only because it terminates in a method MP registers **[V]**. Add the two
simulation-path `ModSettings` reads and `SetPawnLastUpdated`'s `Rand.Range(10000, 15000)`
inside the think node **[V]**, and this route means writing the compat ourselves. **Not
recommended.** Whether the mod ships at all is
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s.

#### Route D — build the kit layer ourselves, no third-party dependency

**Every seam is shipped and read.** `JobDefOf.Equip` and
`Verse.Pawn_EquipmentTracker.{MakeRoomFor, AddEquipment, TryDropEquipment,
DropAllEquipment}` for the weapon **[V]**; `JobDefOf.DropEquipment` via
`FloatMenuOptionProvider_DropEquipment` and `ITab_Pawn_Gear.InterfaceDrop` for the drop
verb, both already on MP's sync surface **[V]**; `OutfitForcedHandler.SetForced` to stop
the apparel policy undoing the kit **[V]**; `ApparelPolicy.filter` for the apparel half,
from Route B.

**The donors are exact.** `JobDriver_UseOutfitStand.DoTransfer` is a complete, shipped
"make this pawn's kit match this set, weapon included" routine, including the awkward
parts — `CanWearTogether` conflict resolution, `IsLocked` refusal, biocode checks, and
`PawnCanWieldWeapon`'s violent / shooting / manipulation / quest-lodger /
`EquipmentUtility.CanEquip` gates **[V]**. The piece to replace is *where the set comes
from*: a Def we author instead of a physical `ThingOwner`. For the standing half,
`Inventory.ThinkNode_LoadoutRealisation` is the shipped shape of "a think node that
periodically closes the gap between a pawn and its set" **[V]** — read it, do not depend
on it.

**What it drags in:** one synced command per verb, a per-pawn assignment stored somewhere,
and a UI to pick a kit. Those three are why it is Hard rather than Medium, and all three
are build questions for #119.

#### Route E — `PawnKindDef`, for pawns that arrive rather than pawns that change

`Verse.PawnKindDef` carries `apparelRequired`, `apparelTags`, `apparelDisallowTags`,
`specificApparelRequirements`, `weaponTags`, `weaponMoney`, `weaponStuffOverride`,
`forceWeaponQuality`, `techHediffsRequired`, `fixedInventory` and `inventoryOptions`
**[V]** — a complete authored kit including the weapon, in pure XML, applied at
generation. The right tool for *"the Waystone's acolytes arrive carrying this"*, the wrong
one for *"re-kit my smith"*. Named because it is the cheapest thing here and a narrative
session will want it.

### Constraints on every route

- **A standing colonist cannot be stripped.** `Verse.StrippableUtility.CanBeStrippedByColony`
  returns true only for a downed pawn, a secure prisoner of the colony, or a non-pawn
  `IStrippable` **[V]**, so `FloatMenuOptionProvider_Strip` never offers on a healthy
  colonist **[V]**. **There is no vanilla "drop everything" verb.** Any route that wants
  one writes it.
- **The one-belt rule** (below) applies to a stand's contents exactly as it applies to a
  preset: `Building_OutfitStand.HasRoomForApparelOfDef` runs `ApparelUtility.CanWearTogether`
  against everything already on the stand and **refuses the second belt** **[V]**.
- **Route A's XML recipe fails silently in two places** — a def derived from
  `OutfitStandBase` without `<thingClass>` loads as a plain `Building`, and the inherited
  `<defaultStorageSettings>` disallows `Weapons` and `ApparelUtility` in a list that
  inheritance *appends to* rather than replaces. Both are set out under Route A above;
  both produce a stand that builds, looks right and does nothing.
- **Force-worn is sticky.** Everything the stand puts on is force-worn **[V]**, so the
  apparel policy stops managing it until the player clears forced apparel —
  `OutfitForcedHandler.Reset`, which MP registers **[V]**.
- **No mod in the corpus defines an equipment-preset `Def`.** Enumerating every
  `<Namespace.TypeDef>` tag across both roots and `Data/` gives 152 distinct tags, none of
  them a kit or loadout def **[V]**; validators from the same table are
  `<VFEC.Perks.PerkDef>` 152, `<VanillaPsycastsExpanded.PsycasterPathDef>` 88,
  `<VSE.Expertise.ExpertiseDef>` 29. Compositable Loadouts is the only loadout mod in the
  corpus; EdB Prepare Carefully's loadout strings exist only in its 1.2–1.4 assemblies
  **[V]**.

The full evidence — every method read, both sweep encodings, and who else names
`Building_OutfitStand` — is in
[`docs/engine/equipment-and-kits.md`](../engine/equipment-and-kits.md).

### Open questions

**Requirement gaps, handed to [#129](https://github.com/cjd721/Rimworld-Archinity/issues/129),
which owns `docs/requirements/COLONY.md`.**

1. **"Force it to drop what it is carrying" does not say what "carrying" means.**
   Inventory, weapon, apparel, or all three? Each has a different shipped verb and a
   different price — the weapon is one vanilla click, apparel is per-item, and "all three
   at once" is new code on every route, because nothing strips a standing colonist.
2. **"Assigning a set is one act, after which the pawn equips itself without further
   instruction" does not say whether the assignment is standing.** One-shot (the stand)
   and standing (a policy, a tag) are different features at different weights, and the
   sentence reads either way. **This is the clause that decides between A+B and D.**

**Unverified route claims.** Multiplayer's `Building_OutfitStand.GetGizmos` lambda index 1
is the *Swap outfit* targeting callback **by declaration order** **[I]** — the
registration itself is **[V]**. Whether the stand's textures load without Odyssey **[I]**.
What VEF, MVCF, Worksites Expanded and Better Traders Guild do with `Building_OutfitStand`
beyond placing it **[I]** — four metadata hits, none depth-read.

**Build questions, deferred to #119.** Where a kit's per-pawn assignment lives if Route D
is taken; whether Route A's kit stands ship with `ComplexFurniture` patched off; whether
Route A's stand filters and Route B's presets are authored from one table or two; whether
kit stands declare a `storageGroupTag`, and if so whether it is shared or per role.

**And if Route A is selected, the first thing to demonstrate is the two silent traps in
its recipe, not the feature.** A kit stand that omits `<thingClass>` and one that leaves
`Weapons` in the inherited `<disallowedCategories>` both build, both look right, and
neither works — so a selected Route A owes a check that a freshly built kit stand shows the
*Swap outfit* gizmo and actually accepts its weapon, before any check about what a pawn
does with it. Listing those checks is #119's act, not this document's.

**Sibling.** [#157](https://github.com/cjd721/Rimworld-Archinity/issues/157) — copying a
bill's configuration — shares a mechanism after all:
`StorageSettingsClipboard.CopyPasteGizmosFor` is vanilla's shipped "copy this
configuration onto that one" gizmo pair, and the outfit stand already carries it **[V]**.
*(#157 narrows this: the storage clipboard takes a `StorageSettings`, which a bill does not
have. Bills use their own `BillUtility.Clipboard`. The storage clipboard is a pattern to copy,
not a mechanism the two share. See* A bill's configuration, pasted onto another bill*.)*

---

## A bill's configuration, pasted onto another bill

This answers `docs/requirements/COLONY.md` § *Bills arrive configured, and a configuration can be
reused*, in its copy-paste clause. It was established by
[#157](https://github.com/cjd721/Rimworld-Archinity/issues/157), evidence class **READ**, against
RimWorld 1.6.4871 rev590 and the corpus pinned in `docs/data/MOD-SNAPSHOT.md`. The #95 defaults
(*Half one*, below) are the layer underneath it, and neither replaces the other.

### Verdict

- **Possible?** **Yes, and one mod already ships it.** Better Workbench Management puts a
  *"Paste all settings (except output product) from copied bill into this one"* button on every
  bill row and in the bill dialog. It works across recipes and across benches **[V]**. It fails
  the requirement in one place: **it copies the material restriction only when the two recipes'
  fixed ingredient filters are identical**. In the ticket's own example, plate armour is
  `Metallic`+`Woody` and the simple helmet is `Metallic`, so *"steel only"* is dropped with no
  message **[V]** by reading (**T-156**).
- **Multiplayer?** **With work.** None of the shipped paths is synced. Multiplayer watches bill
  fields only inside `Bill.DoInterface` and `Dialog_BillConfig.DoWindowContents`. A paste writes
  some fields that are not watched in either scope, and neither MP nor MP Compat carries a
  command for BWM **[V]**. One synced command taking *(source bill, target bill)* would make a
  paste safe. MP already knows how to serialise a live `Bill` **[V]**.

### Routes

| Route | What it gets us | Carrier | Kind | Weight | Multiplayer |
|---|---|---|---|---|---|
| **A** | A per-bill *Paste settings* button, across recipes and benches. Also: paste the bills as new ones, optionally **linked** so that later edits mirror | Better Workbench Management (`falconne.BWM`, `935982361`) | dependency, no code | **Easy** | **No.** It partly desyncs, and no compat exists |
| **B** | Route A's behaviour, with the paste routed through one synced command of ours | BWM, plus a compat patch in `Archinity.Altar` | dependency + C# (Harmony + MP API) | **Medium** | **With work** |
| **C** | Our own configuration paste. We choose the translation rules and take no dependency | our code. Donors: BWM `MirrorBills`, vanilla `Bill.Clone`, `BillRepeatModeUtility`, MP's timetable paste | C# | **Medium** | **With work.** One SyncMethod |
| **D** | Route C's paste with no command of our own. It relies on MP's existing field watches and synced setters | our code | C# | Medium | **No, not recommended** |
| **E** | Named bill configurations: a stored library the players author once and then apply anywhere | our code. Donor: the `OutfitDatabase`/`Policy` shape | C# | **Hard** | With work |

**Every route is [I] as a route.** The mechanisms each one composes are [V] and cited below.
Whether they compose into the requirement stays untested until something is compiled.

#### Route A — Better Workbench Management as it ships

**What it gets us.**

- **Configuration-only paste onto an existing bill, today.** The flow has three steps:
  - Vanilla's copy icon sets `BillUtility.Clipboard`.
  - BWM's `ITab_Bills_TabUpdate_Detour` moves the moused-over bill into its own handler and
    nulls vanilla's clipboard.
  - `BillCopyPaste.DoPasteInto(Bill_Production)` calls
    `ExtendedBillDataStorage.MirrorBills(source, target, preserveTargetProduct: true)` **[V]**.

  The button is drawn on every bill row (a postfix on `Bill_Production.DoConfigInterface`) and
  in the bill dialog (a postfix on `Dialog_BillConfig.DoWindowContents`). It shows whenever
  exactly one bill is copied and the target is a different bill **[V]**. **There is no recipe
  check and no bench check.** The clipboard holds a reference to the *live* source bill, not a
  clone **[V]**.
- **All seven configuration fields are handled** by `MirrorBills` **[V]**:
  - **Always copied:** search radius, store mode and group (`SetStoreMode`), `paused`, the pawn
    restriction and skill range. The last two are skipped when BWM's own per-bench restriction
    is on for the target.
  - **Copied only when the target can count** (see the next bullet): target and repeat counts,
    the pause pair, the include group and `hpRange`.
  - **Copied only when both products qualify:** `qualityRange`, `includeEquipped`,
    `includeTainted` and `limitToAllowedStuff`.
  - **Behind a mod setting:** `suspended`.
  - **Never copied:** the bill's name.
  - **The ingredient filter:** see *What it cannot do*.
- **It never forces `TargetCount` onto a target that cannot count. The gate covers that one
  mode and no other.** `MirrorBills` runs `if (sourceBill.repeatMode != TargetCount || flag)`
  **[V]**, so every other mode is copied without a check. That includes Compositable Loadouts'
  `W_PerTag`, which also counts products (`Inventory.BillUtility.Satisfied` →
  `WorkerCounter.CountProducts`) **[V]**. BWM will therefore paste `W_PerTag` onto a recipe that
  cannot count **[V]** by reading. For `TargetCount`, `MirrorBills` copies the mode only when
  `CanOutputBeFiltered(target)` holds. That check is `specialProducts == null &&
  products.Count == 1`, or the target's counter is `RecipeWorkerCounter_MakeStoneBlocks` or
  `RecipeWorkerCounter_ButcherAnimals` **[V]**. This hand-copies vanilla's two
  `CanCountProducts` overrides (both return `true`) **[V]**. It errs safe: Medieval Overhaul's
  `RecipeWorkerCounter_GrindWheat` counts `products.Count >= 1` and `MakeWoodPlanks` returns
  `true` **[V]**, so BWM *under*-pastes onto those recipes and never over-forces them. **T-58 is
  respected for `TargetCount` only.**
- **Extras beyond the requirement:** paste all of a bench's bills as new bills onto another
  bench; **linked** bills, which mirror each other's settings from then on; a product output
  filter; count-away; and a per-bench worker restriction **[V]**.
- **Nice Bill Tab** (`Andromeda.NiceBillTab`, `3520130671`) has no paste of its own. When BWM is
  loaded, it reaches BWM's `DoCopy` / `CanPasteInto` / `DoPasteInto` by reflection from its own
  float menus (`BetterWorkbenchesIntegration`) **[V]**. So Route A also works inside Nice Bill
  Tab.

**What it cannot do.** It loses the material restriction whenever the fixed filters differ, as
described under *The material restriction* below. It gives no feedback when a field is skipped.
It pastes onto one bill at a time, with no "apply to all bills on this bench". It has **no bill
type check**: `CanPasteInto(Bill_Production)` accepts Glittertech's `Bill_Glittertech` /
`Bill_Overclock` and the mech bills. That is the same hazard #95's gate 1 exists for **[V]**.

**Consequences.** Shipping BWM brings in its whole feature set. It also brings its standing
Multiplayer debts:

- the **T-18** read in its `MakeNewBill` postfix (see *The corpus — what shaped the build*);
- linked-bill mirroring that runs from **UI code every frame**
  (`MirrorBillToLinkedBills`, called from the `ITab_Bills.TabUpdate` prefix and the dialog
  postfix) **[V]**;
- the paste gap described next.

**Multiplayer: No.** BWM ships no `0MultiplayerAPI` reference and MP Compat has no class for it.
`falconne.BWM`, `ImprovedWorkbenches` and `NiceBillTab` return zero across every
`1629973374` binary, including `Referenced/`, in both encodings. The only `falconne.*` string
is `falconne.AFF` **[V]**. A row paste runs inside `Bill.DoInterface`'s watch scope, so some
fields are synced and some are not (see *What Multiplayer already syncs*). The same paste made
from Nice Bill Tab's float menu runs **outside every watch scope**. The mechanism is **[V]**.
That the initiating client diverges is **[I]**, and one two-client test would settle it.

#### Route B — BWM, with the paste routed through one synced command

The idea: patch `BillCopyPaste.DoPasteInto(Bill_Production)` so that it calls a static method
of ours, `(Bill_Production source, Bill_Production target)`, registered with
`MP.RegisterSyncMethod`. That method then calls `MirrorBills`. Both arguments are live bills,
which MP's `Bill` sync worker serialises as `billStack` + `loadID` **[V]**.

**Why the registration can't sit on `MirrorBills` itself:** it is also called every frame by the
linked-bills mirror, so a registration there would send a command per frame per linked bill
**[V]** on the call sites. The per-bench worker restriction `WorldComponent`, the extended-data
store and `paused` are all written inside `MirrorBills`, so they ride the same command.

**What it gets us:** Route A's behaviour, synced, including its safe T-58 gate.

**What it cannot do:** everything Route A cannot do. It inherits the strict filter rule. It also
does not fix linked bills, which stay a separate unsynced mechanism.

**Consequences:** a hard dependency on BWM's internal method shape, with no API contract. It
adds the first `0MultiplayerAPI` reference to our assembly. Whether BWM ships at all is
[#14](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s call.

#### Route C — our own configuration paste

A copy action and a *paste configuration* action on a bill row and in the bill dialog. The
clipboard is per-player UI state that the simulation never reads, so it is not a **T-18**. The
paste is one static method `(source, target)` registered with `MP.RegisterSyncMethod`. Its body
reads only the two bills and Defs, so it passes the **Divergence** gate. Every setter the
method needs is public in vanilla:

- `SetStoreMode`, `SetIncludeGroup`;
- `SetPawnRestriction`, `SetAnySlaveRestriction`, `SetAnyMechRestriction`,
  `SetAnyNonMechRestriction`, `SetAnyPawnRestriction`;
- the public fields on `Bill_Production` **[V]**.

The donors are exact:

- BWM's `MirrorBills` is a complete, shipped field-by-field gating of exactly this job **[V]**.
- Vanilla's `Bill.Clone` / `Bill_Production.Clone` give the list of what a bill carries **[V]**.
- `BillRepeatModeUtility.MakeConfigFloatMenu` shows the `CanCountProducts` refusal and its
  player message **[V]**.
- MP's own `PawnColumnWorker_CopyPasteTimetable.PasteTo` prefix is the shipped shape of "sync a
  clipboard paste as target + clipboard" (`SyncTimetable.DoSync(p, clipboard)`) **[V]** on the
  registration.

**What it gets us.**

- **We choose the material rule**, which is the one thing Route A gets wrong.
- The T-58 gate can call the virtual `recipe.WorkerCounter.CanCountProducts(target)` instead of
  a hand-copied rule.
- A bill-type allowlist, as in #95's gate 1.
- A player message when a field is skipped.
- A bulk lever: "paste onto every bill on this bench" is the same command in a loop.

**What it cannot do:** linked bills. That is a different feature, and nothing requires it.

**Consequences:** the same first `0MultiplayerAPI` reference as Route B. It is also a third
bill-row UI element on the surface that BWM, Nice Bill Tab and Glittertech already draw on.

#### Route D — our paste, riding MP's existing surface (not recommended)

It is possible in principle to issue the paste from inside `Dialog_BillConfig.DoWindowContents`,
so that MP's watches catch the writes. The store and include-group changes would go through
the synced `SetStoreMode` / `SetIncludeGroup`, and the filter would go through
`ThingFilter.SetAllow` while a `ThingFilterContext` is drawn. **The coverage has holes that no
placement closes:**

- No single scope watches every field. The row scope misses `hpRange`, `qualityRange` and the
  include criteria, and the dialog scope misses `paused` **[V]**.
- The pawn-restriction fields are watched only inside the worker dropdown's own option actions
  **[V]**.
- `SyncThingFilters` intercepts per-def `SetAllow` calls only while a filter is being drawn
  **[V]**.

Not recommended: it costs as much C# as Route C and syncs less.

#### Route E — named bill configurations

A stored list of player-authored configurations, such as *"Armour, Good+, steel, crafter
12+"*. The players author each entry once and apply it to any bill. It could be seeded from the
#95 defaults table. The donor is the policy shape: `OutfitDatabase` holds `Policy` objects
scribed in the save, and MP registers its mutators **[V]** (see *Persistence and multiplayer*).

**What it gets us:** configurations that outlive the clipboard, are shared by both players, and
have names.

**Costs:** new saved state, a management UI, and one synced command per mutation. **Hard.**
Named because a narrative session may want the "house standard" framing. The requirement asks
only for paste.

**Recommendation — not a selection.** **Route C**, unless BWM ships for other reasons, in which
case B is the cheaper way to reach the same point. C and B cost the same. C owns the material
rule and the T-58 call, and does not inherit BWM's Multiplayer debts. Selection is
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

### Which fields paste flat, and which need translating

**The ticket's premise, corrected.** A bill's `ingredientFilter` is not built from the recipe's
`fixedIngredientFilter`:

- It is **copied from `recipe.defaultIngredientFilter`** in the `Bill` constructor **[V]**.
- A recipe's default falls back to a copy of its fixed filter **only when none is authored**
  (`RecipeDef.ResolveReferences`) **[V]**.
- Vanilla authors many defaults. `ApparelMakeableBase` and `ArmorSmithableBase` disallow Gold,
  Silver, Plasteel, Jade, Uranium and Bioferrite. The meal recipes disallow `Meat_Human`,
  `Meat_Megaspider` and `InsectJelly`. The weapon bases disallow Silver and Gold **[V]**.

The fixed filter is the **ceiling**. The bill's own filter sits inside it, and an ingredient is
used only if both allow it (`Bill.IsFixedOrAllowedIngredient`) **[V]**.

| Configuration clause | `Bill` member(s) | Across recipes | Why |
|---|---|---|---|
| Repeat mode | `repeatMode` | **Gated** | `TargetCount` is legal only where `recipe.WorkerCounter.CanCountProducts(target)`. **T-58**. The method is virtual and overridden in vanilla (2 counters) and in Medieval Overhaul **[V]** |
| Target count | `repeatCount`, `targetCount`, `pauseWhenSatisfied`, `unpauseWhenYouHave` | Flat | Plain numbers, counted per product. The `unpause < target` invariant is enforced only by the dialog **[V]** |
| Durability range | `hpRange` | Flat | A counting filter (#95). Its slider renders on almost every product. On counted resources it is not free (*What the mode switch costs*) |
| Quality range | `qualityRange` | Flat, but inert unless the target product has `CompQuality` | `CountValidThing` tests it only on things with the comp **[V]**. BWM copies it only when both products have the comp |
| Material / ingredient restriction | `ingredientFilter` (and `limitToAllowedStuff`, which counts products *by* that filter) | **Needs translating** | See below |
| Worker skill range | `allowedSkillRange` | Flat, **but its meaning moves** | It is read against the *target* recipe's `workSkill`: "12+" pasted from smithing onto cooking means Cooking 12+. It is inert when `workSkill` is null, and hidden while a pawn restriction is set **[V]** |
| Pawn restriction | `pawnRestriction`, `slavesOnly`, `mechsOnly`, `nonMechsOnly` (all private) | Flat, through the public setters | The four modes exclude each other. `ValidateSettings` clears a dead or departed pawn **[V]** |
| Store destination | `storeMode`, `storeGroup` (private) | Flat within a map. **It needs a check across maps** | `SetStoreMode` is public **[V]**. A specific stockpile is map-bound, and `ValidateSettings` turns a group not on the target's map into *Drop on floor* **[V]**. `CanPossiblyStore` flags a stockpile that will not accept the target's product as *(incompatible)* **[V]** |

**Adjacent fields the requirement does not name:** `includeGroup` (map-bound, like the store
group), `includeEquipped` / `includeTainted` (meaningful only for weapons and apparel),
`ingredientSearchRadius`, `suspended` and `paused` **[V]**.

**Must never paste:** `recipe`, `precept`, `style`, `globalStyle`, `graphicIndexOverride`,
`xenogerm` and `playerCustomName`, the bill's label. `Bill.Clone` copies `precept`, `style` and
`xenogerm`, and `Bill_Production.Clone` copies the name **[V]**. So **"clone the source, then
swap the recipe" is the wrong build**. Configuration paste writes onto the target; it does not
replace it.

#### The material restriction — the one field that needs translating

**`ingredientFilter` holds an absolute allowed set, not the player's edits.** A `ThingFilter`
carries:

- `allowedDefs` (a `HashSet<ThingDef>`) and `disallowedSpecialFilters`;
- its own *ingredient-side* hit-point and quality ranges;
- two flags, `allowedHitPointsConfigurable` / `allowedQualitiesConfigurable`.

`CopyAllowancesFrom` overwrites all of it **[V]**. A flat paste therefore gives
*target fixed ∩ source's whole set*, and the outcome depends on how the two recipes relate:

| Case | Example | Flat paste gives | BWM's rule gives |
|---|---|---|---|
| Identical fixed filters | two `Metallic`-only smithing recipes | **Exactly the intent** | Exactly the intent |
| Overlapping | plate armour (`Metallic`+`Woody`) → simple helmet (`Metallic`) **[V]** defs | **The intent**. "Steel only" narrows to steel | **Nothing copied.** The helmet keeps its own default, and "steel only" is lost silently |
| Disjoint | plate armour → parka (`Fabric`+`Leathery`) **[V]** defs | **Allows nothing.** The bill never starts, with no message **[I]** outcome | Nothing copied (safe) |
| Source untouched | a default meal filter pasted elsewhere | **The source recipe's defaults** overwrite the target's, which can widen or narrow it | Copied only when the fixed filters match |

Two smaller effects:

- The two `…Configurable` flags come from the *source*, so a flat paste can hide the target's
  ingredient HP/quality sliders **[V]** that they are copied; **[I]** that the sliders then
  hide.
- `Bill.ExposeData` strips any def the recipe's fixed filter forbids when the game saves
  **[V]**. Out-of-range entries do not persist, but an empty intersection does.

**The translation rules a build could choose between.** These are levers for #119, not a
design:

- **Strict equality**, which is BWM's rule. Safe and silent, but it fails the ticket's own
  example.
- **Intersect, with an empty-result guard.** Keep the target's filter and message the player if
  nothing would survive.
- **Replay the player's edits.** Take what the player removed from the source's default and
  apply it to the target's current filter.

### What Multiplayer already syncs on a bill, and what a paste adds

All of this is **[V]** from `2606448745/1.6/AssembliesCustom/Multiplayer.dll` (`SyncFields`,
`SyncMethods`, `SyncFieldUtil`, `SyncDictRimWorld`).

| Mechanism | Bill members | Active where |
|---|---|---|
| Sync **fields**, watched in `Bill.DoInterface` | `suspended`, `allowedSkillRange`, `ingredientSearchRadius`, `repeatMode`, `repeatCount`, `targetCount`, `pauseWhenSatisfied`, `unpauseWhenYouHave`, `paused` (also watched in `ShouldDoNow`) | Bill row |
| Sync **fields**, watched in `Dialog_BillConfig.DoWindowContents` | the row's set **minus `paused`**, plus `includeEquipped`, `includeTainted`, `limitToAllowedStuff`, `hpRange` and `qualityRange` when the recipe has a `ProducedThingDef` | Bill dialog |
| Sync fields, re-watched inside each repeat-mode menu option (MP's `MakeConfigFloatMenu` transpiler → `SyncBillConfigFloatMenuOptions`) | `repeatMode`, `repeatCount`, `targetCount`, `pauseWhenSatisfied`, `unpauseWhenYouHave` | Repeat-mode menu |
| Sync fields, watched only inside the worker dropdown's option actions (a `WatchDropdowns` wrapper from a `GeneratePawnRestrictionOptions` postfix) | `pawnRestriction`, `slavesOnly`, `mechsOnly`, `nonMechsOnly` | Worker dropdown |
| Sync **methods** | `Bill_Production.SetStoreMode`, `Bill_Production.SetIncludeGroup`, `BillStack.AddBill` (`ExposeParameter(0)`), `BillStack.Delete`, `BillStack.Reorder` | Anywhere in the interface |
| `SyncThingFilters` | per-def / category / special `SetAllow`, `SetAllowAll`, `SetDisallowAll` | Only while a `ThingFilterContext` is being drawn |
| Nothing | `CopyAllowancesFrom` on a filter; the pawn restriction outside its dropdown; `hpRange`, `qualityRange` and the include criteria outside the dialog | — |

**How a watch works, and why placement decides everything.** MP wraps each `[MpPrefix]` target
with `SyncFieldUtil.FieldWatchPrefix` (priority 801) and `FieldWatchPostfix` (priority -2). The
postfix compares every watched field with its value at entry. A changed field is **reverted
locally and sent as a command**, and anything unwatched simply stays changed on one machine
**[V]**. So a paste is safe only if every field it writes is either watched in the scope where
it runs, or written through a synced method (**T-155**).

**A new command needs only one thing MP already has.** The `Bill` sync worker writes the bill's
`BillStack` and `loadID` and finds the bill again on read **[V]**. A **live** source bill is
therefore a legal argument. A *detached* clone is not, because it sits in no stack; it would
travel by `ExposeParameter`, which the 1.6 `0MultiplayerAPI.dll` exposes on `ISyncMethod`
**[V]**. The API also carries `RegisterSyncMethod`, `RegisterSyncField` and `WatchBegin` **[V]**.
MP has sync workers for `WorldComponent`, `MapComponent` and `GameComponent` too **[V]**, which
is what makes a Route B registration against BWM's `WorldComponent` possible if it were ever
wanted.

### Constraints on every route

- **T-58.** Never set `TargetCount` without asking the target's counter. Ask the **virtual**,
  because it is overridden by vanilla and by Medieval Overhaul **[V]**.
- **Bill types.** Paste onto `Bill_Production` and `Bill_ProductionWithUft` only, as in #95's
  gate 1. Otherwise Glittertech's overclock bills and the mech bills get repeat modes they were
  never built for **[V]** on the type hierarchy.
- **Recipe identity is not stable under VFE Medieval 2.** On benches linked to a mannequin stand,
  `VFEMedieval.RecipePatches` replaces `bill.recipe` with a runtime clone ("contracted", 90%
  ingredients) in `BillStack.AddBill`, `Bill_Production.Clone` and `ExposeData` **[V]**. The
  clone shares the original's filters (a memberwise `Clone`) **[I]**. Any "same recipe?" test in
  a paste must not compare by reference.
- **The store destination is map-bound.** A paste across maps loses a specific stockpile to
  *Drop on floor* at the next validation **[V]**.
- **A repeat mode can carry state that lives outside the bill.** Compositable Loadouts'
  `W_PerTag` mode keeps its tag in `LoadoutManager` and patches BWM's `MirrorBills` to carry it
  **[V]**. A paste of our own that copies `repeatMode` without that state produces a per-tag
  bill with no tag **[I]**. Paste only vanilla's three modes, or carry the tag the same way.
  `W_PerTag` also counts products (`Inventory.BillUtility.Satisfied` → `CountProducts`) **[V]**.
  **So a paste's T-58 check must cover every mode that counts, not only `TargetCount`.** BWM's
  check does not.

### Survey — bill-management mods on disk

The wide pass covered both mod roots. Every sweep excluded `obj/`, and `Referenced/` was
excluded when hunting implementers. Sweeps run:

- ASCII `Dialog_BillConfig`, `ITab_Bills`, `Bill_Production`, `allowedSkillRange`,
  `SetPawnRestriction`, `unpauseWhenYouHave`;
- case-insensitive `clipboard` in both encodings, with the null-interleaved patterns typed
  literally;
- `pastebill` and `billtemplate` over `.dll` and `.xml`;
- `.cs` source.

Validators came from the same heaps:

- the ASCII sweeps return BWM, which is known to carry all three field names;
- the UTF-16 `clipboard` sweep returns Nice Bill Tab and HugsLib;
- `CopyBillTip` hits vanilla in UTF-16, and `allowedSkillRange` hits `Multiplayer.dll` as a
  literal.

Paths the tool left unattributed were the second copies under
`common/RimWorld/Mods`, which are **T-22** duplicates.

| Mod | packageId | Workshop | What it does to bills | Configuration-only paste? | Multiplayer |
|---|---|---|---|---|---|
| Better Workbench Management | `falconne.BWM` | `935982361` | Copy one or all bills; paste as new (optionally linked); **paste settings into an existing bill**; `MakeNewBill` postfix (store mode, bench restriction); `CountProducts` detour; output filter; drag reorder. The 1.6 dll is byte-identical to its root copy **[V]** | **Yes** | No compat, no API **[V]** |
| Nice Bill Tab | `Andromeda.NiceBillTab` | `3520130671` | Replaces `ITab_Bills.FillTab`. Its add-bill flow preselects a material. Vanilla's whole-bill paste becomes a float option. It fronts BWM's copy/paste by reflection **[V]** | Only through BWM | No compat **[V]** |
| Ushankas Glittertech Expansion | `Ushanka.GlittertechExpansion` | `3522676478` | Its own bill types. `ITab_MemoryCellMods` has a vanilla-shaped whole-bill `PasteClipboardBill` **[V]** (1.6 dll; the `Source/ITab_BillsMemoryCell.cs` on disk is stale) | No | — |
| Vanilla Factions Expanded - Medieval 2 | `OskarPotocki.VFE.Medieval2` | `3444347874` | A `FillTab` prefix/postfix at `int.MaxValue`/`int.MinValue` priority swaps `def.allRecipesCached` for mannequin-linked benches. Recipe swaps on add, clone and load **[V]** | No | — |
| Compositable Loadouts | `Wiri.compositableloadouts` | `2679126859` | Adds a `W_PerTag` `BillRepeatModeDef` whose loadout tag lives in its own `LoadoutManager`. `BillProduction_Clone_Patch` carries the tag on a clone, and `ExtendedBillDataStorage_Patch` postfixes **BWM's `MirrorBills`** to carry it on a paste. A `BillStack.DoListing` button **creates** configured bills (filter, quality, HP, `limitToAllowedStuff`) from colonists' loadout items **[V]** | No. It **extends** BWM's paste | No compat (existing record) |

**Not bill mods, despite hits:** Replimat and VEF's `PipeSystem` (the storage clipboard), Vehicle
Framework's `SmashTools` and Vanilla Gravship Expanded (their own clipboards), HugsLib (log
sharing). VFE Power's `ITab_Bills` references exist only in its 1.1–1.3 assemblies **[V]**.
**Vanilla's own copy/paste is the wholesale clone the ticket rules out.** `ITab_Bills.FillTab`
greys the paste icon unless the bench's `AllRecipes` contains the clipboard's recipe, then adds
`Clipboard.Clone()` as a **new** bill **[V]**.

### Open questions

**Requirement gaps, for Conrad via [#2](https://github.com/cjd721/Rimworld-Archinity/issues/2).**
[#129](https://github.com/cjd721/Rimworld-Archinity/issues/129), which wrote
`docs/requirements/COLONY.md`, is closed.

1. **When the target cannot be made of the source's material**, should the paste leave the
   target's restriction alone, refuse, or tell the player? Plate armour → parka is the case.
   Each translation rule above answers this differently.
2. **Does "the configuration" include suspended, paused, search radius and count-from
   stockpile?** The requirement lists seven clauses; a bill carries these four as well.
3. **One bill per paste, or "every bill on this bench"?** The worked case is three pastes, and a
   bulk paste is a cheap lever on Route C.
4. **Pasting "do until you have X" onto a bill that cannot count** (T-58): should the target
   keep its own mode, as BWM does, or drop to "repeat N" with the pasted number?

**Unverified.** That BWM's paste desyncs the initiating client in a live two-client session
is **[I]**; the watch mechanism is **[V]**. That MP's `Bill` worker resolves a `Bill_Production`
argument through its worker tree is **[I]**. That `ExposeParameter` resolves a detached bill's
cross-references (pawn, stockpile) is **[I]**, though vanilla clipboard paste already relies on
it through `AddBill`.

**Build questions, deferred to #119:**

- the material translation rule;
- whether the clipboard holds a live reference (a dangling source must be handled) or a
  snapshot (which then needs `ExposeParameter`);
- the first `0MultiplayerAPI` reference in `Archinity.Altar`;
- where the buttons sit next to BWM and Nice Bill Tab if either ships.

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
  preset can drive. **Re-verified by #155 and still true — but read it as written: it is a
  statement about the *policy layer*, not about vanilla.** Odyssey's outfit stand reaches
  weapons from an authored set; see *The whole kit, weapon included* above.

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
  is answered **yes** for apparel and utility items and **no** for weapons *from the policy
  layer*.
- #155 — [#155](https://github.com/cjd721/Rimworld-Archinity/issues/155), **READ**, settled
  against the same 1.6 assembly plus `Data/Odyssey`,
  `2606448745/1.6/AssembliesCustom/Multiplayer.dll`,
  `2679126859/1.6/Assemblies/Inventory.dll` and
  `1629973374/{1.4,1.5,1.6}/**/Multiplayer_Compat*.dll`, with a two-encoding wide pass over
  both corpus roots. It **corrects one claim #28 left standing** (see *The claim this
  corrects*) and confirms the rest. Its routes are [I] by construction; the mechanisms they
  compose are [V] and catalogued in
  [`docs/engine/equipment-and-kits.md`](../engine/equipment-and-kits.md).

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
**[V]**, and it ships no loadout XML. It is the only **mod** in the corpus that reaches weapons
from a preset: `Inventory.ThinkNode_LoadoutRealisation.FindItem` issues `JobDefOf.Equip` when
`count == 1 && item.def.IsWeapon && pawn.equipment.Primary == null` **[V]** — so it arms an
empty hand and **never swaps a weapon the pawn is already holding**.

**An earlier draft of this paragraph said it was the only thing in the corpus that reaches
weapons from a preset. That is wrong, and the correction is load-bearing:** vanilla Odyssey's
`RimWorld.Building_OutfitStand` holds apparel **and one weapon** and transfers both **[V]**,
and unlike this mod it is covered by Multiplayer's sync surface **[V]**. See *The whole kit,
weapon included* above, and
[#155](https://github.com/cjd721/Rimworld-Archinity/issues/155).

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
`Inventory.{Loadout,Tag,Item,LoadoutComponent,LoadoutManager,Utility,ThinkNode_LoadoutRealisation,OptimizeApparel_ApparelScoreGain_Patch,OptimizeApparel_TryGiveJob_Patch,MakeConfigFloatMenu_Patch}`,
`Multiplayer.Client.{SyncMethods,SyncDelegates,SyncFields,Multiplayer}`.

**Added by #155:** `RimWorld.Building_OutfitStand` (whole type, including `PostMake`,
`GetGizmos`, `GetFloatMenuOptions`, `HasRoomForApparelOfDef`, `TryAddHeldWeapon`,
`IHaulDestination.Accepts`, `ExposeData`), `RimWorld.JobDriver_UseOutfitStand`
(`Notify_Starting`, `DoTransfer`, `PawnCanWieldWeapon`), `RimWorld.ITab_ContentsOutfitStand`,
`RimWorld.ITab_Pawn_Gear.InterfaceDrop`, `RimWorld.FloatMenuOptionProvider_DropEquipment`,
`RimWorld.FloatMenuOptionProvider_Strip`, `Verse.StrippableUtility.CanBeStrippedByColony`,
`Verse.Pawn_EquipmentTracker`, `Verse.PawnKindDef`, `RimWorld.Policy`,
`RimWorld.ApparelPolicy`, `RimWorld.Pawn_OutfitTracker`;
`Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Furniture.xml`,
`Data/Odyssey/Defs/JobDefs/Jobs_Misc.xml`,
`Data/Core/Defs/ResearchProjectDefs/ResearchProjects_1.xml` (`ComplexFurniture`),
`Data/Core/Defs/ThingDefs_Buildings/Buildings_Base.xml` (`BuildingBase`),
`Data/Core/Defs/ThingDefs_Buildings/Buildings_Furniture.xml` (`FurnitureBase`).

**#155 adds no observable checks.** It resolved at route depth and nobody has selected a
route, so there is nothing built to observe. What a selected Route A would have to
demonstrate is named as an open build question above, not priced as an acceptance list
here.

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
> [#157](https://github.com/cjd721/Rimworld-Archinity/issues/157). Its routes are in *A bill's
> configuration, pasted onto another bill*, above.

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

**Whether the soldier presets get a weapon half — answered by #155, and the answer is not
the one this paragraph assumed.** It read as a two-way choice between apparel-only and a
Compositable Loadouts bridge, with "build it ourselves" priced as duplicating a mod on disk.
**There is a third carrier and it is vanilla**: Odyssey's outfit stand ships an authored set
that includes the weapon, with a one-click force-re-equip gizmo, and Multiplayer syncs it —
while the Compositable Loadouts bridge is **unsynced in 1.6** and arms only an empty hand.
The routes, their clause coverage and their weights are in *The whole kit, weapon included*
above; selection is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

**What `defaultOutfitTags` could do instead, and why it is not the build.** Patching
`<defaultOutfitTags>` onto ThingDefs is pure XML and needs no code at all — but it can only
change what vanilla's four-to-six existing outfits contain, since the tag strings are hardcoded
**[V]**. It is the right tool for *"our new tool belt should be in the Worker outfit"* and the
wrong one for *"ship a Miner preset"*. If the roster collapses onto vanilla's Worker/Soldier
split, this becomes the cheaper answer and the GameComponent is unnecessary. That is a roster
question, so it resolves with #19/#20/#41/#42.
