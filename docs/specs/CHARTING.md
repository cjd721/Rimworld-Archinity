# Charting and the Archon discoveries

## The Archon Spine

The Archon story is the true ordered campaign chain. It should use a small persistent world-state cursor, Deserters-style: beat n+1 cannot become discoverable until beat n succeeds. The player can delay it indefinitely, but it cannot fire out of order or be accidentally skipped by storyteller RNG.

The spine is discovered through Charting, not delivered as arbitrary letters.

Each beat is a physical location or encounter the player travels to and takes something from, learns something from, or changes.

Core rewards are deterministic founder progression: named Archogenes, psychic breakthroughs, methods, devices, unique protocols or other campaign-critical capabilities.

Failure should regenerate or remain recoverable rather than permanently soft-lock the campaign.

## The Waystone and Charting

Discovery becomes labor. Most vanilla quests whose fiction is merely “a place exists somewhere” should leave the natural random pool. Ordinary locations are found through surveying, observation, correspondence and sensing. Archon-related sites have an additional source: at the opening, the Archon leaves the founders a tiny piece of Archotech—the Waystone. It reacts to other Archotech. Each Charting tier is a more sophisticated attempt to interpret and triangulate those returns.

The Waystone is now a locked campaign premise. It is a head start, not a chosen-one password: it is not cosmologically founder-bound, can in principle be stolen or used by others, and does not make ascension exclusive to the marked. It points; it never explains.

| Civilization | Discovery apparatus | Fictional meaning |
| --- | --- | --- |
| Neolithic | Star Table | Crude maps, stars, landmarks and repeated Waystone reactions are compared until direction and distance can be inferred. |
| Medieval / Industrial | Observatory | Formal mapping and celestial observation make regional Waystone returns triangulable while conventional surveying finds ordinary world sites. |
| Late Industrial onward | Sensory Array | Electronic, orbital and deep-range sensing treats the Waystone as an anomalous detector and can resolve Archotech returns across planetary and orbital scale. |

Implementation pattern. The vanilla Long-Range Mineral Scanner already supplies the right grammar: operator labor → ResearchSpeed-scaled work → probabilistic success → guaranteed pity timer → root-special auto-accepted quest → world object. Archinity changes the payload selector from “precious lump” to “what is currently eligible to be discovered?”

| Priority | Pool | Behavior |
| --- | --- | --- |
| Tier 1 | Archon spine | Finite and ordered. If the next core beat is eligible, it takes priority. |
| Tier 2 | Significant side discoveries | Finite authored set: special Archon sites, augments, later capsules, named rewards and other meaningful side objectives. Eligibility is era/progression gated and throttled by Charting work. |
| Tier 3 | World discovery pool | Broad era-banded pool: ruins, hunting/logging/resource sites, faction places, discoverable world events and a small Archon-flavored subset. Effectively repeatable. |

Selection rule: if the next Tier 1 beat is eligible, discover it; otherwise if a Tier 2 discovery is eligible, discover it; otherwise draw Tier 3. This prevents optional play from flooding the colony with campaign rewards while ensuring the Charting apparatus always has useful work.

Distance scales with reach, not calendar time. Search bands expand with transportation and sensing: primitive travel keeps discoveries local, maintained roads and vehicles widen the region, aircraft make continental intervention practical, and the gravship collapses distance. Repeated discoveries can bias outward inside the current reach band. The information horizon and travel horizon should grow together.

Discovery effort remains uncertain. The player should not know whether the next find takes two effective workdays or six, but a guaranteed-find threshold prevents starvation by RNG. Better researchers compress the clock. Exact formulas are tuning, not story.

## Saved state and remaining work

The ordered spine needs a current beat and completion state. Charting needs work
toward the next find, eligible pools, finite Tier-2 exhaustion, current apparatus
and travel reach. Discovering an already-active core objective must not repeatedly
grant it; exact active-site handling is part of the scheduling specification.

The significant-site catalog, travel bands, effort formulas and presentation are
still to be specified. [#39](https://github.com/cjd721/Rimworld-Archinity/issues/39)
finishes delivery and recovery behavior; [#40](https://github.com/cjd721/Rimworld-Archinity/issues/40)
selects and verifies the quest carrier. The scanner pattern above is a proposed
implementation, not evidence that the Chronicle already exists in the build.
