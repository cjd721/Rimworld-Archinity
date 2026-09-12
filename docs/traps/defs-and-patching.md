# Traps: defs and patching

How a patch or a def file fails without saying so. The mechanism behind these is
`docs/engine/def-loading.md`.

Part of the trap register. **The index at `docs/TRAPS.md` is the file you read
before a diff**; this one carries the full entries for this group. Every entry here
fails with no error message. Cite by ID.

## Defs and patching

### T-01 — Never put `--` inside an XML comment

The entire file vanishes from the database, with no error naming the file, the def
or the cause: `--` terminates an XML comment early, and RimWorld drops the whole
file rather than reporting a parse failure against it. Use `=` for divider rules.

*Has bitten this project twice — once by an agent that had just written the warning
into a doc. 1.6.4871.*

### T-02 — PatchOperations run before `ParentName` inheritance resolves

Patches operate on raw XML, so a field declared only on an Abstract parent exists
only on the parent at patch time. A predicate written against a field you can see
in the merged database matches one abstract node instead of the twelve children you
meant. Match on `@ParentName` instead, and run `python tools/xpath.py '<xpath>'`
first — it prints the count and flags `ABSTRACT` nodes.

*`tools/xpath.py`; the def red–green loop in `CODING_STANDARDS.md`. 1.6.4871.*

### T-03 — Patch xpaths apply to the whole merged def database

There is no file or mod scoping on an xpath. `PatchOperationFindMod` only checks
that a mod is *active*; it does not scope the xpath it guards. An operation
intended for one mod's files silently edits defs from Core, the DLC and every other
mod that shares the shape. Confirm the node count before shipping, and annotate the
operation `<!-- expect: N -->` so `patch_check.py` holds it there.

*`tools/patch_check.py`. T-26 is the canonical victim, at 395 defs. 1.6.4871.*

### T-04 — Unresolvable cross-references are omitted, not set to null

The loader drops a reference it cannot resolve rather than nulling the field, so a
prerequisite list loses its entry and reads as "no prerequisite". Deleting a
`ResearchProjectDef` therefore leaves everything that required it buildable with
**no research prerequisite at all** — the exact opposite of the intent, and nothing
reports it. Order matters: neuter the referencing defs first, delete the research
last, and re-run `python tools/audit_research.py` after either half.

*Def-load behaviour; `tools/check_refs.py` exists for this class. 1.6.4871.*

### T-05 — `XmlInheritance` appends list children rather than replacing them

`XmlInheritance.RecursiveNodeCopyOverwriteElements` appends, so a `ParentName`
child's list silently contains the parent's entries as well as its own — a child's
`allowedStructures` merges with the parent's instead of overriding it.
`Inherit="False"` clears first. Assume merge, not override, whenever you inherit a
list.

*Same mechanism gives `Substructure` its full affordance list —
`docs/engine/gravship-and-substructure.md`. 1.6.4871.*

### T-06 — `Def.GetModExtension` returns the FIRST match

The lookup returns on first match rather than erroring on ambiguity, so a second
extension of the same type is silently ignored. Never
`PatchOperationAddModExtension` a second extension of a type a def already carries
— in particular a second `KCSG.CustomGenOption` onto a faction. Patch its
settlement def instead.

*`docs/engine/mods/kcsg.md`. 1.6.4871.*

### T-37 — `Verse.DefMap<D,V>` scribes positionally, and `def.index` is load order

`DefMap<D,V>` looks like a Def-keyed dictionary and is not one. It stores a bare
`List<V>` indexed by `def.index`, and `ExposeData` writes only that list —
`Scribe_Collections.Look(ref values, "vals", LookMode.Undefined)` — then on load pads
with `new V()` or trims with `RemoveLast()` until the count matches
`DefDatabase<D>.DefCount`. The keys are never written. Indices are positional:
`DefDatabase<T>.Add` assigns `def.index` from insertion order, and `SetIndices()`
reassigns every one of them inside `Remove` and on each `ResolveAllReferences`. Add a
def of that type, remove one, or let another mod insert one anywhere ahead of yours,
and every stored value silently rebinds to a different key — no error, no count
mismatch, no version stamp. Vanilla draws the line in one file: `ResearchManager`
scribes `progress`, `techprints` and `anomalyKnowledge` with `LookMode.Def` and
reserves `DefMap` for `tabInfoVisibility`, a UI bool where the damage is cosmetic.
For a stored balance or any campaign state, use
`Scribe_Collections.Look(…, LookMode.Def, LookMode.Value)` instead.

*`Verse.DefMap<D,V>.ExposeData`; `Verse.DefDatabase<T>.Add` / `.Remove` /
`.SetIndices`; `RimWorld.ResearchManager.ExposeData`. Caught in review before
`docs/specs/CURRENCIES.md` used it for currency balances. 1.6.4871.*

### T-40 — `requiredAnalyzed` is nulled without Biotech, and the project becomes free

`ResearchProjectDef.PostLoad` executes
`if (!ModLister.BiotechInstalled) requiredAnalyzed = null;`. The Analysis gate does not
warn, does not error and does not degrade — it ceases to exist:
`RequiredAnalyzedThingCount` becomes 0, `AnalyzedThingsRequirementsMet` returns true,
and a project gated on having analysed a named item is free to start. Two precisions
worth carrying. **The test is ownership, not activation** —
`ModLister.BiotechInstalled` is set in `RecacheExpansionsInstalled` from
`modsByPackageId.ContainsKey("ludeon.rimworld.biotech")`, and `modsByPackageId` is
filled by `RebuildModList` over every mod found on disk, so it reads Biotech *owned and
installed*, never Biotech active in `ModsConfig.xml`. **And the ConfigError cannot
fire** — `ConfigErrors`' "requires analyzing X but X cannot be analyzed" sits behind
`if (!requiredAnalyzed.NullOrEmpty())`, but `PostLoad` runs at deserialisation
(`DirectXmlToObject.TryDoPostLoad`) while `ErrorCheckAllDefs` runs far later in
`PlayDataLoader`, and only under `Prefs.DevMode`; by then the list is already null.
`techprintCount` is zeroed on the adjacent lines when Royalty is absent, with the same
consequence for its own error. Biotech is in this project's DLC floor
([#6](https://github.com/cjd721/Rimworld-Archinity/issues/6)), so record this as a
floor dependency rather than a bug to fix — but every def we ship that leans on
`requiredAnalyzed` is leaning on Biotech, and nothing in the game will ever say so.

*`Verse.ResearchProjectDef.PostLoad` / `.ConfigErrors` /
`.AnalyzedThingsRequirementsMet`; `Verse.ModLister.RecacheExpansionsInstalled`;
`docs/specs/RESEARCH.md`. 1.6.4871.*

### T-50 — A budget computed from un-patched def values is wrong once mods merge

Any arithmetic over `statBases` or `statOffsets` must be done against the **merged**
database. A figure read out of the base def files is not conservative and not roughly
right — it is a different game's number, and nothing announces the divergence.

The gravship substructure budget is the worked case. Odyssey ships `GravEngine`
`statBases/SubstructureSupport` 500 and `GravFieldExtender`
`statOffsets/SubstructureSupport` 250 at `maxSimultaneous` 6, so the base files read
500 + 6×250 = **2,000**. With VGE loaded, its `Patches/VanillaGravEngineLinking.xml`
replaces the engine's 500 with **250** (and its `CompProperties_SubstructureFootprint`
radius 18.9 → 11.9), and its `Patches/GravFieldExtender.xml` replaces the extender's
250 with **100**, `maxSimultaneous` 6 → 10 and `maxDistance` → 500. The same pair now
reads 250 + 10×100 = **1,250**. The mod set that looks like it raises the budget
lowers it.

**The copy that wins can be shipped by neither mod you are reading.** A compat patch
shipped *by one mod for another* is the authority: GravTech's own
`1.6/Mods/VanillaGravshipExpanded/Patches/VGE_Patch_GravTech.xml` — a
`PatchOperationSequence` guarded `MayRequire="vanillaexpanded.gravship"` — restats
GravTech's `GravFieldPylon` from 500 to **130** and `AdvShip_GravReactor` from 1000 to
**500**, compensating through `VGE_SubstructureSupportMultiplier` offsets (0.10 and
0.50) that route into a VGE statFactor. Read either mod's own def folder alone and you
get neither number.

`tools/defdb.py` is the tool you would reach for to check this, and it cannot be
trusted for it yet: `_apply_leaf` evaluates patch xpaths relative to the `<Defs>`
element, so an ordinary `Defs/ThingDef[…]` matches nothing while
`report.patch_ops_applied` still increments — a partly unpatched tree reported as a
clean apply. Treat any `defdb.py`-derived number as un-merged until
[#102](https://github.com/cjd721/Rimworld-Archinity/issues/102) lands.

*`Odyssey/Defs/ThingDefs_Buildings/Buildings_Gravship.xml`; `vanillaexpanded.gravship`
`1.6/Patches/VanillaGravEngineLinking.xml` and `1.6/Patches/GravFieldExtender.xml`;
`als.gravtech` `1.6/Defs/ThingDefs_Buildings/GravFieldPylon_GT.xml`,
`1.6/Defs/ThingDefs_Buildings/AdvShip_GravReactor.xml` and
`1.6/Mods/VanillaGravshipExpanded/Patches/VGE_Patch_GravTech.xml`; mod versions pinned
by `docs/data/MOD-SNAPSHOT.md`. The audit of
[#71](https://github.com/cjd721/Rimworld-Archinity/issues/71) found this exact error in
the same document that proposed the trap. 1.6.4871.*

### T-55 — `GenTypes` resolves short names from an ignored-namespace dictionary, last writer wins

`Verse.GenTypes.TryGetTypeInIgnoredNamespace` builds
`typesInIgnoredNamespacesByName[allType.Name] = allType` over **every loaded type whose
namespace is null or listed in `IgnoredNamespaceNames`** — `RimWorld`, `Verse`, `LudeonTK`,
`Verse.AI`, `Verse.AI.Group`, `Verse.Sound`, `Verse.Grammar`, `RimWorld.Planet`,
`RimWorld.BaseGen`, `RimWorld.QuestGen`, `RimWorld.SketchGen`, `System` — and
`GetTypeInAnyAssembly` consults that dictionary **before anything else**. Two consequences,
both silent.

**A bare XML node name always binds to the ignored-namespace type.** Two unrelated classes
are called `StructureLayoutDef`: `RimWorld.StructureLayoutDef` and
`KCSG.StructureLayoutDef`. `<StructureLayoutDef>` is always the vanilla one, and KCSG
content has to write `<KCSG.StructureLayoutDef>` — which GTE does. Write the bare form for
the vanilla class; never the qualified one.

**And the assignment is unguarded, so the last writer wins.** There is no ambiguity check
and no collision warning. A mod type declared in the `RimWorld` namespace — or in **no
namespace at all** — that shares a short name with a vanilla type simply **replaces the
vanilla type in the resolver, for every `workerClass`, `thingClass` and `Class=` lookup in
the game**. Nothing is logged, and the symptom is a vanilla def quietly running someone
else's code.

**Vanilla's own `LayoutWorker`, `LayoutWorker_Structure` and `LayoutWorker_OrbitalPlatform`
have no namespace at all**, which is exactly the bucket a new class with no `namespace`
declaration falls into — and `docs/specs/ORBIT.md` has us authoring `LayoutWorker_*`
subclasses. Declare every Archinity type in an `Archinity.*` namespace and reference it
fully qualified from XML, as Better Traders Guild does
(`BetterTradersGuild.LayoutWorkers.Settlement.LayoutWorker_Settlement`). A namespace is not
house style here; it is the only thing keeping our type out of a dictionary vanilla writes
to first.

*[#66](https://github.com/cjd721/Rimworld-Archinity/issues/66).
`Verse.GenTypes.TryGetTypeInIgnoredNamespace`, `.GetTypeInAnyAssembly`,
`.IgnoredNamespaceNames`. 1.6.4871.*

### T-69 — `AccessTools.Field(...)?.SetValue(...)` is a silent no-op after a rename

The idiom reads as defensive and is the opposite. `HarmonyLib.AccessTools.Field` returns
**null** on a miss rather than throwing, the null-conditional swallows the call, and a
wrapping `try`/`catch` that logs on a throw never fires — because nothing throws. Reflection
into a private field by string name therefore stops working the moment the field is renamed,
with a clean log and no behaviour left behind.

**The shipped instance is Ushanka's Hacking Expansion.**
`USH_HE.CompHackableExtensions.ResetHackProgress` reflects into **ten** private fields of
`RimWorld.CompHackable` in exactly this shape, inside exactly that `try`. It is correct
against the build on disk; one vanilla rename retires it in silence, and the visible
consequence is a seized turret stuck at `hacked == true` and permanently un-re-hackable,
with nothing in the log to connect the two.

**This one is not about a third party.** The pattern is what an agent reaches for when it
needs a private field, and it fails the *Loudness* gate in `CODING_STANDARDS.md` outright:
a Harmony patch against a missing *method* throws at startup, and this against a missing
*field* does not. In Archinity code, resolve the `FieldInfo` once and fail loudly when it is
null — `AccessTools.Field(...) ?? throw` — or use `AccessTools.FieldRefAccess`, which throws
on a miss. Never `?.SetValue`.

*[#58](https://github.com/cjd721/Rimworld-Archinity/issues/58).
`USH_HE.CompHackableExtensions.ResetHackProgress` from `HackingExpansion.dll`
(`3573344880/1.6/Assemblies/`); `HarmonyLib.AccessTools.Field`. 1.6.4871.*

---
