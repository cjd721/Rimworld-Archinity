# The trap register

**Read this index before writing a def or a `.cs` file. Flag every occurrence in
review, and cite the ID.**

Every trap listed here fails **without an error message**. None is caught by running
the game; several are not caught by reading the log either. `CODING_STANDARDS.md`
owns the rule ("check the register"); this file is the whole register at a glance,
and each group's file carries the mechanism, the evidence and the fix.

Read the index whole — it is short on purpose, and the traps cross domains: an
unscoped xpath (T-03) is what bites in a mod patch (T-26), and settings sync (T-18)
is what bites in faction work. When a row looks like it might be you, open its file.

Cite `T-14`, never a line number. IDs are stable and never reused.

## Defs and patching — [`docs/traps/defs-and-patching.md`](traps/defs-and-patching.md)

| ID | Trap |
|---|---|
| T-01 | `--` inside an XML comment drops the entire file, unnamed |
| T-02 | PatchOperations run *before* `ParentName` inheritance resolves |
| T-03 | Patch xpaths apply to the whole merged database; `PatchOperationFindMod` does not scope |
| T-04 | Unresolvable cross-references are omitted, not nulled — a stripped prerequisite reads as "none" |
| T-05 | `XmlInheritance` appends list children rather than replacing them |
| T-06 | `Def.GetModExtension` returns the FIRST match; a second is inert |

## World creation and factions — [`docs/traps/world-creation.md`](traps/world-creation.md)

| ID | Trap |
|---|---|
| **T-07** | **The faction roster must be final BEFORE world creation — not repairable by patch** |
| T-08 | `maxCountAtGameStart` / `canMakeRandomly` are `[Obsolete]` no-ops in 1.6 |
| T-09 | `requiredCountAtGameStart` is dead code |
| T-10 | The `replacesFaction` prune runs over defs you excluded, deleting ones you kept |
| T-11 | Writing `FactionDef.techLevel` at runtime silently reverts on load |
| T-12 | `Settlement.cachedMat` is never invalidated |
| T-13 | `FactionUtility.DefaultFactionFrom` returns null once a faction climbs |
| T-14 | VFE Empire blacklists every other raid strategy on its deserter faction |
| T-15 | `VFET_OpportunitySite_WildMen` generates a faction at runtime, unguarded — breaks T-07 |
| T-16 | `RaidStrategyDef` / `QuestScriptDef` have no `minTechLevel` field at all |
| T-17 | Raid faction selection is fail-open and fail-quiet |

## Multiplayer and determinism — [`docs/traps/multiplayer.md`](traps/multiplayer.md)

| ID | Trap |
|---|---|
| T-18 | Mod settings are part of the sync surface — the third thing people miss |
| T-19 | Medieval Overhaul forces a setting from a *draw method* |
| T-20 | MO's schematic cache is unkeyed and UI-poisoned — a live desync bug |
| T-21 | Filter at draw time, never at list-membership time |
| **T-22** | **77 mods have a second copy on disk under one `packageId`; six have drifted apart — VEF among them — and `corpus.py --check` reports the corpus clean** |
| **T-33** | **KCSG generates settlements from an unseeded `System.Random` — two clients get different maps, and MP's checksum cannot see it** |

## Buildings, items, rituals and titles — [`docs/traps/content-and-buildings.md`](traps/content-and-buildings.md)

| ID | Trap |
|---|---|
| T-23 | `statFactors` on a facility is a silent no-op; facilities are additive-only |
| T-24 | `CompRefuelable` does not gate a `Building_PawnProcessor` — the fuel bar is decoration |
| T-25 | Genepacks decay in 20 days and roofs give zero protection |
| T-26 | An unscoped `PatchOperationSetName` reaches 395 ThingDefs |
| T-27 | `MeditationFocusDef` gates are *backstory* gates; a failed gate looks like nothing |
| T-28 | `RoyalTitleDef.Awardable` is believed to derive from `favorCost > 0` |

## Worldgen layouts — [`docs/traps/worldgen-layouts.md`](traps/worldgen-layouts.md)

| ID | Trap |
|---|---|
| T-29 | Layout rows and cells beyond `layouts[0]` are dropped silently |
| T-30 | `defenseOptions` is dead below Industrial |
| T-31 | `DankPyon_MedievalSiege` cannot fire as shipped — empty intersection |
| T-32 | Rotated KCSG symbol variants are runtime-generated and cannot be patched |

---

## Adding an entry

A finding earns a slot **only if it fails silently**. A crash, a red error or a
startup exception is loud and belongs in the relevant `docs/engine/` file instead —
loudness is the whole selection criterion.

- Take the next free ID; **never renumber**, and never reuse a retired one.
- Add the entry to its group file, and a one-line row here. Both, or it is invisible.
- **Correct an entry in place** and update its provenance line. Do not append "an
  earlier draft said…" under superseded text.
- Every entry carries the build it was verified against.

A group file that passes roughly a dozen entries is a candidate for splitting
further; this index stays one file regardless, because it is the thing that gets
read whole.
