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

| Ticket | The capability in question | Answer lands in |
|---|---|---|
| [#181](https://github.com/cjd721/Rimworld-Archinity/issues/181) Android psylinks by kind | Can psylinks be allowed for androids, forbidden outright, or restricted by kind (built, awakened, arrived, jailbroken)? Can the altar's rite reach an android? Can Glitterites stay psychically deaf under every route? | `ANDROIDS.md` |
| [#182](https://github.com/cjd721/Rimworld-Archinity/issues/182) Ending the game from Transcendence under Multiplayer | Which endings can *Enter the new reality* produce on both clients at once? Only the non-terminal credits path is verified. | `TRANSCENDENCE.md` |
| [#183](https://github.com/cjd721/Rimworld-Archinity/issues/183) Giving a founder away | Can banishment, prisoner release and kidnapping each be permitted or forbidden for a founder? | `RELIGION.md` § Founders |
| [#184](https://github.com/cjd721/Rimworld-Archinity/issues/184) Who can hold Church titles and Exaltation | Can favour be kept off non-founders across every way it is paid, the bestowing ceremony's spectators included? | `RELIGION.md` § Exaltation |
| [#185](https://github.com/cjd721/Rimworld-Archinity/issues/185) An era's start under Async Time with two colonies | Can an era's start be stamped consistently for both colonies when each map keeps its own clock? | `ERA.md` |
| [#186](https://github.com/cjd721/Rimworld-Archinity/issues/186) The Glitterite pursuit with two colonies | Can the pursuit track each colony separately, only one, or both as one target? | `TRACE.md` |
| [#187](https://github.com/cjd721/Rimworld-Archinity/issues/187) Withholding what a settlement shows | Can a settlement's tech tier and trade-permission line be hidden until the colony has learned them? | `TERRITORY.md` |
| [#188](https://github.com/cjd721/Rimworld-Archinity/issues/188) A settlement changing hands while its map is loaded | Can the transfer wait for the map to close, and can the player's pawns be moved off first? At an era advance only the second fits the single-act rule. | `TERRITORY.md` |
| [#189](https://github.com/cjd721/Rimworld-Archinity/issues/189) Ending or easing a war the colony is losing | Can the colony end or ease a losing war by peace, payment or owed obligations? | `POLITICS.md` |

## Open capability claims under the build map

| Ticket | The capability in question |
|---|---|
| [#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) Three claims the era gate rests on | Includes whether any World Tech Level filter besides the faction roster reads `TechLevelDatabase<FactionDef>.Levels`. That decides whether `ORBIT.md`'s `Empire → Undefined` exemption conflicts with `requirements/ERA.md`'s "no exempt faction". The exemption matters only while WTL's `Filter_Factions` is on, and ERA § 6b holds it off. |

## Engine entries owed

These facts are already verified. Each needs an entry in `docs/engine/`, which does not exist yet.

- `docs/engine/determinism.md` § *Why threads are the one thing that bars a mod* — cited by
  `WORLD-INFRASTRUCTURE.md` as a proposed entry.
