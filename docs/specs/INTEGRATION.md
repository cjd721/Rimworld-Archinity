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

[The capabilities document](https://github.com/cjd721/Rimworld-Archinity/issues/121) found these
requirement clauses unanswered by any spec (2026-09-23).

| Ticket | The capability in question | Answer lands in |
|---|---|---|
| [#190](https://github.com/cjd721/Rimworld-Archinity/issues/190) Research by Practice | A project that consumes authored resources | `RESEARCH.md` |
| [#191](https://github.com/cjd721/Rimworld-Archinity/issues/191) Accepting the Church's offer ends the run | A quest acceptance that ends the game for both players | `RELIGION.md` |
| [#192](https://github.com/cjd721/Rimworld-Archinity/issues/192) Demand asks with no route | A loan without above-era delivery, a protected route, a prisoner released | `POLITICS.md` |
| [#193](https://github.com/cjd721/Rimworld-Archinity/issues/193) Who a faction hates | Withholding and revealing NPC relations | `POLITICS.md` |
| [#194](https://github.com/cjd721/Rimworld-Archinity/issues/194) A road funded to a higher tier | A contribution that raises a route's tier | `WORLD-INFRASTRUCTURE.md` |
| [#195](https://github.com/cjd721/Rimworld-Archinity/issues/195) NPC era vehicles | NPC factions fielding vehicles | `WORLD-INFRASTRUCTURE.md` |
| [#196](https://github.com/cjd721/Rimworld-Archinity/issues/196) Quest presentation | Subplot parent quests, taken beats, challenge rating | `CHARTING.md`, `CURRENCIES.md` |
| [#197](https://github.com/cjd721/Rimworld-Archinity/issues/197) The announcement test widens with era | Charting pool membership changing mid-game | `CHARTING.md` |
| [#92](https://github.com/cjd721/Rimworld-Archinity/issues/92) The ally-aid battle (reopened) | Aid delivered on an ally-owned site | `TERRITORY.md` |

## Open capability claims under the build map

| Ticket | The capability in question |
|---|---|
| [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) Three claims the era gate rests on | Includes whether any World Tech Level filter besides the faction roster reads `TechLevelDatabase<FactionDef>.Levels`. That decides whether `ORBIT.md`'s `Empire → Undefined` exemption conflicts with `requirements/ERA.md`'s "no exempt faction". The exemption matters only while WTL's `Filter_Factions` is on, and ERA § 6b holds it off. |

## Engine entries owed

These facts are already verified. Each needs an entry in `docs/engine/`, which does not exist yet.

- `docs/engine/determinism.md` § *Why threads are the one thing that bars a mod* — cited by
  `WORLD-INFRASTRUCTURE.md` as a proposed entry.
