# Integration register

What [cross-spec integration](https://github.com/cjd721/Rimworld-Archinity/issues/118) left
open on 2026-09-23, after reading every requirement and spec as one system.

**This register lists capability gaps only**: things we do not yet know whether the game can do.
It does not list choices between routes. A route that exists, has been verified and still needs
choosing is not open here. The build map ([#119](https://github.com/cjd721/Rimworld-Archinity/issues/119))
makes those choices by its own process.

Each row is an open ticket. When a ticket closes, its answer lands in the spec named in the row, and
the row is deleted.

## Open capability tickets

**None are open.** The nine that [the capabilities document](https://github.com/cjd721/Rimworld-Archinity/issues/121)
found (#190–#197, and #92 reopened) were answered on 2026-09-23 in the specs they named.

## Open capability claims under the build map

| Ticket | The capability in question |
|---|---|
| [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) Three claims the era gate rests on | Includes whether any World Tech Level filter besides the faction roster reads `TechLevelDatabase<FactionDef>.Levels`. That decides whether `ORBIT.md`'s `Empire → Undefined` exemption conflicts with `requirements/ERA.md`'s "no exempt faction". The exemption matters only while WTL's `Filter_Factions` is on, and ERA § 6b holds it off. **Partly read** in [`ERA.md` § *The arrival band*](ERA.md#the-arrival-band): the row writes WTL's database, never `FactionDef.techLevel`, so it exempts nothing from an arrival gate; outside worldgen its one reader is `Patch_QuestNode_Root_WorkSite` [V]. The arrival band itself now has routes there. |

## Engine entries owed

These facts are already verified. Each needs an entry in `docs/engine/`, which does not exist yet.

- `docs/engine/determinism.md` § *Why threads are the one thing that bars a mod* — cited by
  `WORLD-INFRASTRUCTURE.md` as a proposed entry.
