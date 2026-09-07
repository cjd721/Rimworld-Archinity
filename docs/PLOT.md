*WORKING DESIGN • SEPTEMBER 2026*

# Archinity

*Campaign Plot & Systems Map*

**Purpose**

A chronological map of the Archinity playthrough as currently decided: what the player experiences, which systems drive each phase, how the major faction arcs interlock, and which design questions remain intentionally open. This document avoids inventing quest names, exact rewards, final title names, or unchosen late-game specifics.

Authoring rule: the protagonist is played, not written. The campaign authors the world, pressures, discoveries, factions, temptations, consequences and available paths. It does not prescribe what the founders believe or which path they choose.

| Status | Meaning |
| --- | --- |
| Locked direction | Decided in the current design discussion; use as the working rule. |
| Working structure | Strong current design that can be tuned during implementation. |
| Open | Intentionally unresolved; do not silently fill it in. |

# 1. Campaign Thesis

Archinity is a civilization-scale ascension campaign. Two marked founders awaken at the bottom of technological history and climb through Neolithic, Medieval, Industrial, Spacer and Ultra civilization while discovering three truths that ultimately make transcendence possible: Life supplies anima; Devotion changes what willingly given anima can do; Self gives the transformation a singular subject. The campaign is not a linear sequence of errands. Ordered Archon discoveries form the spine, while faction scales, Reverence, politics, research, technology and player choices determine how the world reacts around it.

| Era | Player-scale fantasy | What the world does back |
| --- | --- | --- |
| Neolithic | “We are learning how to be a civilization.” | Local, strange, curious, cruel. Life/anima is discovered, but psychic progression waits. |
| Medieval | “The world is beginning to bend around us.” | Religious and political institutions court, exploit, worship and fear you. Devotion becomes materially real. |
| Industrial | “The whole planet is within reach.” | Infrastructure, war, trade, roads and mass politics scale up. The gravship begins as extraordinary transport. |
| Spacer | “The planet is too small; the universe is not.” | Finish planetary conflicts, move onto the gravship, reveal orbit, then become small again among mature spacer civilizations. |
| Ultra | “We can steal the fire of the impossible.” | Glittertech is acquired by conquest and reverse engineering; the Glitterites become understandable as failed climbers. |
| Coda | “We finally understand what the climb required.” | Life + Devotion + Self converge in the altar; the founders author the Transcendent Archogene and approach the final threshold. |

**Hidden author lens**

The Archons built lower-dimensional universes as proving grounds. The Administrator overseeing this universe is a mediocre, pressured custodian whose experiment has stalled while the Glitterites consume and farm huge portions of it while pursuing transcendence incorrectly. The Administrator’s interventions are attempts to produce a successful climber and salvage the experiment. This motive is for the writers, not the player-facing text. Players learn what and how through evidence; the ultimate why stays behind the curtain.

# 2. The Systems That Carry the Plot

## 2.1 The Archon Spine

The Archon story is the true ordered campaign chain. It should use a small persistent world-state cursor, Deserters-style: beat n+1 cannot become discoverable until beat n succeeds. The player can delay it indefinitely, but it cannot fire out of order or be accidentally skipped by storyteller RNG.
The spine is discovered through Charting, not delivered as arbitrary letters.
Each beat is a physical location or encounter the player travels to and takes something from, learns something from, or changes.
Core rewards are deterministic founder progression: named Archogenes, psychic breakthroughs, devices, methods or other campaign-critical capabilities.
Failure should regenerate or remain recoverable rather than permanently soft-lock the campaign.

## 2.2 Charting: how locations become known

Discovery becomes labor. Most vanilla quests whose fiction is merely “a place exists somewhere” should leave the natural random pool. Locations are found because a pawn actively studies the world using the civilization’s Charting apparatus. Ordinary sites come from actual surveying, observation, correspondence and sensing. Archon-related sites have an additional source: at the opening, the Archon leaves the founders a tiny piece of Archotech—working name Waystone—that reacts to other Archotech. Each Charting tier is a more sophisticated attempt to interpret and triangulate those reactions. The Waystone is a head start, not a chosen-one lock: it is not founder-bound in cosmology, and another civilization could in principle possess and use it.

| Civilization | Discovery apparatus | Fictional meaning |
| --- | --- | --- |
| Neolithic | Star Table | Crude surveying plus repeated observation of the Waystone: stars, direction, intensity, landmarks and terrain are used to infer where a return originates. |
| Medieval / Industrial | Observatory | Formal maps and celestial observation make Waystone returns triangulable across regions while conventional surveying discovers ordinary world sites. |
| Late Industrial onward | Sensory Array | Electronic, orbital and deep-range sensing integrates the Waystone as an anomalous detector. It can locate Archotech returns across planetary and eventually orbital distances. |

Implementation pattern. The vanilla Long-Range Mineral Scanner already supplies the right grammar: operator labor → ResearchSpeed-scaled scanning → probabilistic success → guaranteed pity timer → root-special auto-accepted quest → world object. Archinity changes the payload selector from “precious lump” to “what is currently eligible to be discovered?”

| Priority | Pool | Behavior |
| --- | --- | --- |
| Tier 1 | Archon spine | Finite, ordered, highest priority when the next beat is eligible. |
| Tier 2 | Significant side discoveries | Finite authored set: special Archon sites, augment infrastructure, later capsules, named rewards and other meaningful side objectives. Throttled by effective charting work and eligibility. |
| Tier 3 | World discovery pool | Broad era-banded site pool: ordinary ruins, hunting/logging/resource sites, faction places, world events that require discovery, plus a small Archon-flavored subset. Effectively repeatable. |

Selection rule: if the next Tier 1 beat is eligible, find it; otherwise if a Tier 2 discovery is eligible, find it; otherwise draw Tier 3. Tier 3 fills the time between important discoveries rather than allowing the player to spam finite campaign rewards.
Distance scales with reach, not calendar time. Each apparatus searches within a minimum/maximum travel band appropriate to the civilization’s mobility. Repeated discoveries can bias outward within that band, with variance so the pattern never looks perfectly mathematical. Horses, maintained roads, vehicles, aircraft and finally the gravship progressively enlarge practical reach. The information horizon should expand alongside transportation: the player should not routinely discover sites hundreds of tiles away while limited to primitive travel, nor should every late-game site remain five tiles from a ship that crosses the planet.
Discovery effort should remain uncertain. The player should not know whether the next find will take two effective workdays or six, but a guaranteed-find threshold prevents starvation by RNG. Better researchers compress the clock. The exact research-cost distribution and distance formula remain tuning questions.

## 2.3 Altar, Anima and biological progression

Anima is the life-substance carried by living biological substrate; blood contains it. The founders hunger for blood because their marked biology can use that substrate. The altar is the central apparatus through which the meaning of blood changes over the campaign.
Neolithic: the altar accepts blood and stores a charge, but the player does not yet know how to make the important transformation happen.
Medieval: willing devotion reveals that freely given blood can widen psychic capacity. This is where the first psylink belongs.
Industrial: the player begins to understand the altar as an instrument and unlocks genetic democratization / lottery use for ordinary colonists.
Later eras: the altar becomes increasingly legible as technology catches up to what it was doing all along.
Founder/core vectors and ordinary augments remain separate reward classes. Core founder progression is named and deterministic. Ordinary colonist lottery outcomes are opt-in but randomized once activated. Crucially, repeatable capsules should not flood the Neolithic or Medieval discovery pool before the player understands and can use them; early side discoveries must pay out in era-appropriate rewards instead of creating a warehouse of expensive mystery objects.

# 3. Prologue & Neolithic Arc

## 3.1 Prologue — The Mark and the First Thought

The Archon intervention is not a technology lesson. The mark represents a qualitative change in capacity: the founders become capable of abstraction, planning, imagining circumstances beyond the immediate present, tool-making and cumulative civilization. The Archon also leaves behind the Waystone, a tiny unfathomable piece of Archotech whose only immediately legible behavior is that it reacts to other traces of Archotech. It points; it does not explain. The founders still have to invent civilization and learn how to interpret it.
The founders begin extraordinarily resilient and deathless, but skilled at nothing. The opening progression is therefore the actual discovery of civilization: fire, tools, food security, shelter, production and social scale. No negative mood debuff is needed to force the altar hunt; the Star Table provides the player-facing hook whenever they choose to engage it.

## 3.2 Neolithic I — Awakening

Establish survival and the first verbs of civilization: fire, shelter, hunting, crude tools and basic organization.
Build the Star Table. A pawn operating it begins conventional local surveying and experiments with the Waystone’s directional reactions, turning an incomprehensible object into the first believable source of Archon-site discovery.
The first Archon site leads to the altar or otherwise establishes the altar as the central strange artifact of the campaign.
The altar accepts a victim/blood and visibly stores charge. Nothing transformative happens yet. The point is not “nothing happened”; the point is “the machine clearly did something, but I am missing the other half.”

## 3.3 The Anima-Tree People — optional early worldbuilding

The anima-tree faction is optional and should behave more like an ambient threshold encounter than a mandatory chain. They can contact the colony once the appropriate early conditions are met; the player may visit, trade, learn or ignore them.
They teach the player that anima exists, that living things carry it, that blood releases/concentrates it, and that anima trees interact with it naturally.
They do not grant the first psylink and do not own the campaign-critical path.
Their knowledge explains the founders’ blood hunger and the altar’s charge without explaining the full Archon cosmology.
Ignoring them loses context, relationship and possible rewards, not the ability to finish the campaign.

## 3.4 Neolithic II — Primitive Baseline

Permanent settlement begins: farming, production tables, stone construction, leather armor, cloth clothing and the first reliable infrastructure.
The founders receive the Genius Archogene around this stage. The narrative meaning is “they can now become good at things,” not “they woke up already competent.”
Charting begins producing more side sites, but the reward pool remains immediately useful to a primitive society. No repeatable genetic lottery economy yet.

## 3.5 Neolithic III — Settled Tribe

The local map becomes solved: defensible settlement, food security, walls, organized labor, trained fighters and a recognizable culture.
The campaign does not add a psychic progression axis here. The player finishes learning the primitive game before organized religion arrives.
The closing feeling is that the colony has mastered its immediate world just as the wider political world becomes impossible to ignore.

**Neolithic endpoint**

By the time the era ends, the player knows that the founders are biologically strange, blood contains anima, the altar can hold a charge, the world contains discoverable Archon traces, and civilization is larger than the home tile. They still do not know how worship changes the equation, and they have no psylink yet.

# 4. Medieval Arc — Seduction, Reverence and Schism

Medieval is the first fully authored political act. Organized civilization notices the founders. The dominant Church recognizes them as sacred proof, courts them, teaches them something real, uses their notoriety to expand its own influence, and eventually reacts to the possibility that worship may flow past the institution directly to the founders.

## 4.1 The four independent ladders

| System | What it means | What it unlocks / changes |
| --- | --- | --- |
| Church Rank | Institutional standing inside the Church. | Church quest pool, ceremonial authority, elite gifts, political access, protection and services. It measures cooperation/subordination, not psychic power. |
| Psychic Rank | Actual psychic capacity and the founders’ evolving understanding of what they are becoming. | Psycasts, channel capacity and psychic progression. The final rung is deliberately unknown until Ultra, when “?” becomes the ability to claim a self-authored title. |
| Reverence by Faction | How strongly that faction’s people treat the founders as sacred / worthy of obedience. | Offerings, volunteers, favors, blood/anima supply, military aid, political leverage and eventual subordination. High direct Reverence also increases Church fear. |
| Global Reverence | A derived measure of the civilization-scale body of genuine believers across factions. | Represents the number of people willing to participate in founder-directed rites. In the final ritual it becomes a literal mass voluntary bloodletting requirement. |
| Intel | Actionable evidence and knowledge about Church people, facilities and corruption. | Enables exposure campaigns, covert operations, targeted political attacks and higher-tier anti-Church missions. |

Goodwill still exists. Reverence is deliberately not goodwill with a religious skin. Goodwill asks whether a government likes you. Reverence asks what its people will do because of what they believe you are. A government can be friendly while its population is indifferent, or politically wary while its population would riot to protect you.

## 4.2 What Reverence does

Reverence must be an attractive reward on its own. “Take the credit and gain Reverence” only works if Reverence materially changes the game. Archinity tracks it per faction for politics and benefits, while a derived Global Reverence represents the total scale of people across civilization who genuinely revere the founders. Per-faction Reverence pays throughout the campaign; Global Reverence becomes narratively decisive in the final rite.
Recognition: improved hospitality, minor gifts, favorable social outcomes and easier conversion/recruitment.
Offerings: recurring food, textiles, silver, blood/anima resources or other faction-appropriate tribute from believers.
Volunteers: pilgrims, workers, recruits, specialists or willing ritual participants who present themselves because of the founders’ reputation.
Political favors: requests that would be implausible on goodwill alone—safe passage, military aid, emergency supplies, votes/decisions, prisoner release or refusal to obey hostile orders.
Levies and obligations: sufficiently reverent factions will risk lives, contribute troops, resources and logistics, and accept costly requests without treating them as an ordinary trade of goodwill points.
Subordination: at very high levels, Reverence can become one route toward vassalage, religious alignment or accepting the founders as the higher authority.
Reverence is primarily earned through publicly interpretable acts, not generic “religion XP.” Saving settlements, defeating impossible enemies, public rites, visible supernatural acts, conversions, winning wars, fulfilling costly promises and choosing to take public credit can all increase it. Church quests repeatedly create the central temptation: let the Church own the story and receive exceptional institutional rewards, or let the witnesses understand that the founders themselves did it and gain direct Reverence. At the end of the campaign, Global Reverence is revealed to mean something literal: a civilization-scale population can be called to spill blood willingly as part of the same rite.

## 4.3 Medieval I — The Forge / Seduction

Metalworking transforms the colony. The Expert Social Archogene is a strong working candidate for the first Medieval founder vector because the new bottleneck is no longer survival; it is people, conversion, diplomacy and scale.
The Church reaches out when the colony is eligible. Unlike Empire, the fantasy is not “serve nobles to become noble.” The Church flatters the founders as living proof of its doctrine while attempting to make them dependent on its institution.
The Church reveals the missing half of the altar: willing devotion changes the quality of the offering. This delivers the first psylink and opens psychic progression in the Medieval era.
Early Church titles and early psychic states may intentionally share names or symbolism. This creates the appearance that institutional status and true divinity are the same ladder before later events expose the divergence.
The defining Church quest choice: after the founders perform something publicly meaningful, the resolution frequently lets the player choose who owns the story. If the Church takes credit, the player receives the superior institutional reward and progresses safely inside the Church. If the founders take credit, the material reward is smaller but direct Reverence rises—often sharply—with the affected faction.

**The temptation**

The Church route should be genuinely good. Palaces, elite equipment, soldiers, knowledge, protection, rare materials and political privileges are the reason a rational player might accept subordination. Staying in the Church is not “the stupid option”; it is the comfortable option.

## 4.4 Medieval II — Tension

The central Church relationship is systemic rather than a fixed six-quest betrayal chain. The Church can continue offering rank quests as long as the player’s independent Reverence remains inside the institution’s tolerance. The more credit the Church absorbs, the farther the player can climb its ladder. The more directly the world worships the founders, the sooner the Church becomes threatened.
A player who ignores Church progression for years but becomes enormously revered elsewhere may receive only one or two Church ranks before the institution reacts.
A player who continually redirects credit toward the Church can climb much farther and may remain allied indefinitely.
Other Medieval factions key their behavior off the same state: era, research, Church rank, direct Reverence, goodwill, previous choices and the current political phase. Alliances and wars are authored around those thresholds so the political board feels alive without giving every faction a bespoke chain.
This is also where roads become political infrastructure. The vanilla world should not begin covered in fully developed paved roads. Neolithic movement uses paths and dirt tracks. Medieval powers begin maintaining serious roads and can request, finance, contest or control routes. Trade corridors become visible evidence that the world is becoming connected.

## 4.5 The Schism — the believers inside the Church

The anti-Church faction emerges from inside the Church because it believed the Church’s own claims about the founders. Senior clergy and their followers have been told that the founders are sacred proof. They witness the founders, believe the claim, and then watch Church leadership prepare to contain or destroy the very beings it taught them to revere. That contradiction creates the break.
The faction name is open. “Witnesses” is only a placeholder and is not preferred as final naming.
The schism can include one or two high-ranking Church officials, a militant/religious order and their subordinate network. This gives them immediate institutional knowledge and operational reach.
They do not need secret Archon cosmology. Their belief can be sincere and wrong in details while still correctly identifying the Church’s hypocrisy.
Their core proposition is personal: “They are using you. We believed what they taught us about you, and now we know what they intend to do.”
The contact point is threshold-driven. When the player’s direct Reverence becomes dangerous to the Church, the schism offers warning and assistance before the Church moves. Accepting lets the player break on favorable terms. Rejecting does not preserve the status quo forever; if the Church’s threat threshold is already crossed, the Church can later initiate the betrayal itself. The player can then still work with the schism—or reject both and go independent.

## 4.6 Anti-Church campaign: Intel + Reverence

The Deserters blueprint remains useful, but Archinity’s pressure meter becomes positive as well as dangerous. Anti-Church operations can offer more Intel at the cost of increasing the founders’ public Reverence. High Reverence strengthens the player socially and materially, while simultaneously making concealment impossible and pushing Church response upward.
Covert evidence gathering: high Intel gain, small public effect, lower immediate Church response.
Public exposure: consumes evidence, strongly shifts Reverence away from Church authority and toward the founders, and accelerates confrontation.
Direct violence: removes an enemy quickly but may fail to change hearts; used carelessly, it can create martyrs rather than collapse belief in the institution.
Higher operations target increasingly important clergy, institutions or political nodes using one parameterized quest family rather than dozens of one-off scripts.
The schism route is therefore not “help these rebels.” It is an apparatus through which believers help the founders reveal, subordinate or overthrow the institution that claimed them. Its endpoint can be reform, takeover, replacement, vassalage or a founder-centered religious order depending on player choices and final implementation.

## 4.7 Medieval III — Schism / War

Political pressure becomes open conflict: specialized faction armies, sieges, demands to choose sides, wars between powers and large-scale obligations.
The Church can remain an ally if the player accepts institutional subordination and keeps direct Reverence below its threat threshold.
The schism can become the founder-aligned religious apparatus if the player helps it expose/overthrow the Church.
The player can reject both and force the issue through independent Reverence, diplomacy and conquest.
The exact Archon encounter/electricity beat previously discussed is not treated as immutable here; its placement and details can be reworked to fit the now-clearer Medieval arc.

**Three valid Medieval outcomes**

1) Sanctioned Divinity — the founders remain inside the Church and accept its interpretation of their power.  2) Schism Victory — the founder-believing breakaway movement exposes/overthrows the hierarchy and becomes a major allied or subordinate institution.  3) Independent Divinity — the founders reject both and build authority directly through Reverence, diplomacy and conquest.

# 5. Industrial Arc — Reach, Infrastructure and Planetary War

Industrial is the least locked era at the beat-by-beat level. The correct approach is to let the story/system requirements determine the final leap boundaries rather than preserving an old leap schedule. The era’s identity, however, is now strong: the player stops solving one settlement and starts solving the planet.

## 5.1 The industrial transformation

Electricity remakes the base and creates extreme demand for steel, components, power and skilled labor.
Ordinary genetics becomes legible. This is the natural era for genetic democratization and repeatable altar lottery capsules for non-founder colonists.
Tier-2 Charting can now legitimately reward Archon capsules and augment systems because the player knows what they are and can use them immediately.
Trade becomes a strategic dependency rather than convenience. The colony cannot sensibly produce every input at scale.
Outposts, allied settlements and eventually subordinate territories must provide meaningful resources, people or logistics rather than token vanilla outputs.

## 5.2 Roads and mobility

The world physically becomes connected. Industrial factions begin paving routes between settlements. The player can finance, build, protect, capture and benefit from those roads. Vehicle speed should make paved infrastructure transformational rather than cosmetic: dirt roads remain useful, but automobiles on proper roads collapse travel times.
Early vehicles change local and regional travel.
Armored vehicles turn roads into military logistics.
Helicopters and aircraft partially escape the road network and make continental intervention practical.
Late Industrial gravship acquisition is a strong direction: at first it is an extraordinary transport and military platform, not yet the colony’s permanent home. Its existence lets wars and diplomacy expand to truly planetary distance, but the major political/religious conflicts are allowed to climax in early Spacer rather than being artificially finished before the era changes.
The key progression is not raw movement speed; it is the size of the political world the player can practically participate in. A 30-day journey by horse becomes a road trip, then a flight, then essentially no distance at all.

## 5.3 Industrial politics

Faction requests scale up from local favors into military and logistical obligations: defend a city, reinforce a war, seize a route, supply an army, hold territory or intervene far from home.
The political state inherited from Medieval persists. Church, schism-successor or independent religious authority does not vanish when factories appear.
Reverence becomes one of the systems that makes these alliances worth maintaining: highly reverent populations can supply blood/anima, manpower, resources, levies, safe routes and compliance at scales goodwill alone cannot justify.
The exact number and identity of Industrial leaps remain open and should be fitted to this planetary-reach arc rather than treated as already settled.

# 6. Early Spacer Transition — Planetary Resolution & the Orbital Gate

Early Spacer begins with the planet still active. The gravship now has enough range and capacity to make the founders the decisive mobile power in wars that Industrial civilization set in motion. This is where tertiary factions enter full-scale conflict, Church obligations become blatant feats of strength, the schism route closes on the Church hierarchy, and an independent player finishes the planetary board by Reverence, diplomacy, vassalage or conquest.
The political/religious question must nevertheless resolve before the player first reveals orbit for a real implementation reason: the orbital world has to be instantiated with the factions and settlements that will exist there. The gravship can operate planetside beforehand, but the signal-jammer/orbital-access author beat is the moment history crystallizes. The game now knows which human institution accompanies the founders, then reveals the orbital board for the first time.

| Planetary resolution | What carries forward |
| --- | --- |
| Church route | A sanctioned religious civilization that continues to treat the founders as sacred assets. Its late quests openly use the deathless founders as political/military instruments, but its rewards remain exceptional. If the player refuses the terrestrial ending, the institution follows them into space. |
| Schism route | A founder-believing replacement/reformed religious institution built by insiders who broke when the Church turned on the beings it taught them to worship. It carries testimony, missionary infrastructure, Intel networks and political organization into orbit. |
| Independent route | A founder-centered polity/religious network built through direct Reverence, conquest, vassalage and chosen allies rather than Church institutions. It follows because the founders created it, not because another institution licensed them. |

Three resolutions remain valid. A Church-aligned founder can continue accepting institutional ownership of the story and reach the end of its title ladder; a founder-believing schism can expose and overthrow the hierarchy; or the founders can reject both and impose an independent order. Whichever non-terminal route survives becomes the terrestrial institution that follows the founders into space and learns Spacer technology alongside them.
A Church terminal ending should also exist as a genuine temptation. At the top of the Church route, the institution can offer an Archinity analogue to Royal Ascent: permanent terrestrial apotheosis, safety, wealth, legitimacy and a completed “victory.” Accepting ends the run. Cosmologically it is a failure because the founders chose to become gods of a tiny world rather than continue climbing, but the game should not label it a bad ending. The player simply chose to stop.
If the player reaches the top of the Church route and refuses the terrestrial terminal ending, the Church is allowed to accompany the founders into space. It is not secretly an ancient interstellar empire; it is a powerful planetary institution being dragged into the stars by the beings it chose to sanctify and exploit. The same principle applies to the schism-successor or independent founder-centered polity.

# 7. Spacer Arc — The Planet Stops Being the World

## 7.1 Crown — Finish the Planet

Spacer opens planetside. The gravship is already the greatest transport platform on the world and keeps gaining range, capacity, defenses and life-support capability. The player uses that reach to settle the conflicts Industrial civilization made planetary: wars between tertiary factions become regular map events, allies demand large interventions, and the founders can carry meaningful forces anywhere on the globe.
Church route: the final title stages become deliberately exploitative. The Church sends deathless sacred assets into wars, sieges and political crises because it knows the founders can survive work ordinary rulers would never risk themselves on. The bargain remains real because the rewards, privileges and support are correspondingly extraordinary.
Schism route: covert opposition becomes open war. The player gathers the final Intel needed to expose the hierarchy while fighting the Church and its aligned factions at military scale.
Independent route: the player resolves the same planetary board without either institution, using direct Reverence, conquest, alliances and vassalage to determine who answers to the founders.
The point is not that Spacer immediately leaves the planet. The point is that the planet has become small enough for the founders to finish.

## 7.2 Departure — The Gravship Becomes Home

The gravship crosses a qualitative line from vehicle to civilization. It gains reliable oxygen, gravity, food production, cooking, habitation, storage, defenses, shields and enough internal capacity that the colony can permanently leave the electrified castle behind. The old base becomes history rather than the center of play.
Once the planetary religious/political outcome is resolved, the signal-jammer/orbital-access requirement can be completed. Orbit is revealed for the first time only after the game knows which terrestrial institution is coming with the founders.

## 7.3 Orbit — Small Again

The first orbital reveal is a status reset, not a power reset. On the planet the founders were famous enough to reorganize kingdoms; in orbit they meet mature Spacer civilizations that have been trading, fighting and living above them for generations. Their gravship is formidable, but no longer cosmically unique.
The Trader’s Guild is a galaxy- or system-spanning commercial network with depots, missions, unusual goods, orbital stops and leisure sites. A few terrestrial strongholds existed only because this was always a tiny edge of a much larger network.
The Starjacks are a distinct spacer culture with their own equipment, ships and social identity.
At least two additional house-like spacer powers should use the visual, armor and weapon systems supplied by the existing house mods, but their original names and lore are discarded. They become entirely new Archinity civilizations with different military doctrines and political identities.
Advanced mechanoids and other offworld threats immediately establish that orbit has a higher baseline of danger and technology than the planet.
Reverence carries forward asymmetrically. Factions and populations that came from the planet retain what they already believe. New spacer civilizations begin with little or no Reverence because they have never heard a convincing reason to care. The founders remain gods to Earth and strangers to the stars.

## 7.4 The Forbidden Territory — Glitterites as a Fact of the Universe

Other orbital factions warn the player about the Glitterites before the main plot forces contact. Glitterite territory is treated as poisoned space: they are hostile to everyone, do not conduct normal diplomacy, field terrifying mechanoids and consume organic life. Most civilizations simply route around their holdings rather than challenge them.
At this stage the player does not know what the Glitterites ultimately want. They only know that a civilization dramatically beyond normal Spacer capability exists, that everyone sensible avoids it, and that its enclaves are uncommon but absolute where they appear.

## 7.5 The Waystone Points Into Hell

The Sensory Array eventually resolves an Archotech return from inside a Glitterite-held site. This is the first unavoidable collision between the Archon spine and the Glitterites. The campaign does not tell the player to fight them because they are the final villain; it tells the player that the same signal they have followed since the Star Table is coming from behind their defenses.
The first raid should feel like an impossible heist. The player arrives in the best vanilla-tier equipment, with mature psychic power, a fully capable gravship and elite colonists, and still discovers that Glitterite defenses are on another scale.
The reward proves two things at once: the Glitterites possess Archotech, and their own equipment is beyond anything the player can yet manufacture.
Subsequent Archon returns intersect Glitterite holdings often enough that coincidence becomes untenable. The player realizes they are deliberately collecting Archotech, but not yet why.

## 7.6 Spacer Capstone — Steal Fire

Spacer ends with a deliberate second incursion. This time the player is not merely following a return and hoping to survive; they go back because they have identified the Glitterite component or core needed to understand their engineering. The capstone raid produces the first Glitterheart (working name) or equivalent analytical key.
Obtaining it does not grant Glittertech directly. It makes Glitterite engineering analyzable. Ultra unlocks with a new rule: advanced technology beyond vanilla cannot be researched from nothing. The player must first capture an example from the civilization that already knows how to build it.

# 8. Ultra & Coda — The Failed Climbers and the Final Rite

| Phase | Direction |
| --- | --- |
| Spacer capstone — Steal Fire | Deliberately raid a Glitterite site and recover the first Glitterheart / analytical key. This unlocks the ability to understand, not instantly possess, Glittertech. |
| Ultra I — Exemplars | Acquire → analyze → research → manufacture. Each major Glittertech branch requires captured examples from Glitterite targets. |
| Ultra II — Anatomy | Learn that the Glitterites are persona-derived androids, control advanced mechanoids and still depend on anima-rich biological processing. |
| Ultra III — Failed Climbers | Discover their Archotech hoards and transcendence experiments. Understand that their civilization erased singular continuity of self through copying and optimization. |
| Ultra IV — Claim Yourself | The final psychic “?” becomes a self-authored title. Claiming it unlocks the final altar ritual; no new ritual object exists. |
| Coda — Life + Devotion + Self | Mass life, intimate willing sacrifice, Global Reverence and the claimed self converge at the altar. With no gene inserted, the altar authors the Transcendent Archogene. |

Ultra is the deliberately manufactured post-vanilla era. Spacer ends at the ceiling of normal RimWorld equipment; Ultra begins when the founders can finally reverse-engineer Glittertech. Archotech remains categorically different: it is never researched or manufactured, only found, captured, inherited or used.

## 8.1 Reverse Engineering Through Conquest

Ultra research follows an acquire → analyze → research → manufacture loop. The research tree exists, but many Glittertech projects remain locked until the colony physically brings home an exemplar. A better rifle requires a captured rifle. Advanced armor requires armor. Reactors, ship systems and mechanoid technologies require the corresponding recovered hardware or cores.
This makes late-game knowledge expedition-driven. Researchers matter, but the colony cannot sit safely at a bench and reason its way into technology whose operating principles it has never seen. Each technological branch asks the player to choose a Glitterite target, survive it, recover something meaningful and then turn conquest into domestic capability.
Ultra also opens the option to manufacture advanced androids. The campaign does not declare artificial bodies inherently lesser; that distinction matters to the final cosmology.

## 8.2 What the Glitterites Are

The Glitterites are an android civilization descended from human persona cores. Over immense spans of time they copied, forked, edited, optimized and replicated those persona patterns across artificial bodies. They control the mechanoid forces associated with their civilization, including boss-scale variants used to anchor major Glitterite strongholds.
Their artificial existence never freed them from anima. They consume living biological material, process the anima-bearing substrate into an anima-rich neutroamine economy, and use it to sustain systems that remain dependent on life despite having discarded ordinary biology. Their great mistake is not that they became machines; it is what they did to personhood while doing so.

## 8.3 Why They Hoard Archotech

The Glitterites correctly discovered that Archotech violates the limits of in-universe engineering. They therefore spent ages finding, stealing, cataloguing and fortifying it. Some of their strongest sites exist because an Archotech object or installation is inside. This is why the Archon spine increasingly crosses Glitterite territory: the breadcrumbs were not waiting untouched for the founders. Another civilization found and hoarded them first.
Spacer only reveals the collection. Ultra gradually reveals the motive. Major raids, laboratories and boss encounters expose a pattern of experiments whose purpose cannot be explained by military or economic needs. The Glitterites are not simply collecting superweapons. They are trying to become something beyond themselves.

## 8.4 The Revelation of Transcendence

Transcendence becomes an explicit concept only in Ultra. The player reconstructs it from Glitterite behavior and Archotech experiments rather than receiving an explanatory speech from an Archon. The Glitterites have accumulated staggering anima reserves, impossible technology and ages of experimentation, yet the operation never resolves. This is when the campaign finally asks not merely “how do we become stronger?” but “what are they trying to do, and why can they not do it?”
The decisive late-Ultra stronghold should be one of the campaign’s hardest encounters: a major Glitterite site, advanced mechanoid defenders, and a boss mech controlled or coordinated by a Glitterite android. Beating it grants access to persona architecture and transcendence research normally kept hidden even from other spacer powers.
The records reveal that Glitterite identity has become recursive data. Ancient root personas have been copied, forked, edited, merged, restored and duplicated until “which one is the person?” no longer has a meaningful answer inside their civilization. Their intelligence, memories and capabilities survived. Singular continuity of self did not.

## 8.5 The Three Truths

The final cosmology is the synthesis of three truths learned in three different civilizational contexts. None is enough alone; each earlier society mistook one piece for the whole.
Life — the Neolithic truth. Living biological existence carries anima. Blood releases and concentrates it. Technology can gather, refine and redirect anima but cannot create life-substance from nothing. The final transformation therefore requires an enormous quantity of sacrificed life.
Devotion — the Medieval truth. Anima willingly given by a genuinely devoted person behaves differently from anima taken by force. Intention gives the offering coherence toward its recipient. The final transformation therefore requires intimate willing sacrifice and civilization-scale voluntary participation, not merely a mountain of prisoners.
Self — the Ultra truth. Transcendence requires a singular continuous subject to whom the transformation can happen. The Glitterites did not fail because android bodies are invalid; they failed because endless copying, pruning and replication made the self interchangeable. They possess substance and machinery but cannot answer the operation’s deepest question: who, exactly, is crossing?
The founders succeed because they lived through all three partial answers. Primitive anima traditions teach Life. The Church reveals Devotion while demonstrating how an institution can corrupt it into extraction. The Glitterites master mind as data so completely that their failure finally reveals the necessity of Self.

## 8.6 Claim Yourself — the Final Psychic Rank

The psychic ladder should end for most of the campaign with an unresolved final rung: “?”. After the Glitterite revelation, that question mark becomes an action rather than a bestowed rank. For the first time in the campaign, the founder does not receive a title from the Church, a psychic tradition, a faction or an Archon. The player names the founder’s final state themselves.
Mechanically, the player claims a self-authored title—any epithet or name the player chooses. The wording has no hidden correct answer. The act matters because it is the founder asserting a singular identity that cannot be delegated to an institution or reduced to a copied data pattern.
No physical token is created. Claiming the title itself unlocks the final altar ritual. The ritual is gated on having reached and claimed this final psychic title, which gives “Self” a concrete gameplay representation without inventing a new quest object.

## 8.7 The Final Altar Ritual — Life + Devotion + Self

The altar has been performing incomplete versions of its true function since Neolithic. At the end, the player finally knows how to satisfy the complete operation. No Archogene capsule is inserted. The altar supplies the transformation when all three requirements are true.
Life: a large number of lives are sacrificed to provide the raw anima requirement. Exact numbers are tuning, not lore.
Devotion, intimate: a small number of pawns with genuine personal relationships to the founder and extremely high ideological conviction willingly give their lives at the altar. These individuals prove that the devotion is real rather than merely political obedience.
Devotion, global: Global Reverence must exceed the final threshold. Narratively this represents thousands, millions or more believers across many factions willingly spilling blood in a synchronized rite because the founder asked them to. They need not all die; their participation makes the civilization-scale relationship literal.
Self: the founder must have claimed the final self-authored psychic title. This is not an item placed in the altar; it is the prerequisite that makes the complete ritual conceptually available at all.
The founder enters the altar with no gene loaded. Life supplies the substance. Devotion directs it. Self provides the singular subject. The altar then authors the Transcendent Archogene from the founder rather than installing a preexisting gene.
This is the only Archogene in the campaign that does not preexist its owner. The Administrator gave the founders a head start—mark, unusual biology, a Waystone and a trail—but the final gene is not a chosen-one password. In principle another continuous person with the same understanding, apparatus, anima and devotion could perform the same operation.

## 8.8 Coda — The Threshold

By the Coda, the founders possess the strongest manufacturable technology available inside the universe, captured Archotech that the Glitterites themselves hoarded, mature psychic capability, a civilization capable of mass voluntary devotion, and the Transcendent Archogene they authored through the altar. Glitterites remain dangerous rather than becoming trivial, but the founders can now attack their strongest holdings on deliberate terms by combining avenues the Glitterites could never fully use.
The exact presentation of the final Archon threshold/door/ascension scene remains an authored ending detail rather than a solved systems question. What is now fixed is what the player must have learned and become before that scene can happen: they do not ascend because an Archon finally hands them the answer. They arrive carrying the answer they assembled from Life, Devotion and Self.

# 9. Full Playthrough Map at a Glance

| Phase | Primary plot beat | System emphasis | Player-facing question |
| --- | --- | --- | --- |
| Prologue | Archon marks founders, triggers the First Thought and leaves the Waystone. | Capacity for cumulative civilization; Archotech direction without explanation. | Survive, learn, and eventually figure out what the strange object is reacting to. |
| N1 Awakening | Star Table; first Archon return; altar discovered; charge without transformation. | Primitive Charting + altar mystery. | Build basic survival and investigate when desired. |
| N2 Primitive | Permanent settlement; Genius Archogene. | Early Archon spine + era-banded discoveries. | Become capable of learning rapidly. |
| N3 Settled Tribe | Local map solved; optional anima-tree contact explains anima. | Mature Star Table; no psylink yet. | Finish primitive civilization before psychic/religious complexity arrives. |
| M1 Seduction | Church courts founders; willing blood revelation; first psylink. | Church Rank, Psychic Rank, Reverence, Observatory. | Who gets credit for the miracle: the institution or you? |
| M2 Tension | Direct Reverence begins threatening Church control. | Threshold-driven Church behavior; living faction politics. | Remain subordinate, cultivate worship, or balance both. |
| M3 Schism / War | Founder-believing insiders offer help; Church may betray; open conflict begins. | Intel + Reverence operations; faction wars. | Church, schism or independence becomes a real strategic path. |
| Industrial | Roads, vehicles, aircraft, trade, genetics and outposts make the whole planet reachable. | Genetic democratization; capsules; large logistics; Observatory → Sensory Array. | Build the network and become capable of intervening anywhere. |
| Late Industrial | Gravship acquired as superior transport; planetary wars escalate rather than instantly resolve. | Planetary reach; ship development. | Can you turn mobility into decisive power? |
| Early Spacer — Crown | Use the gravship to settle Church/schism/independent conflict and tertiary wars. | Large military obligations; final planetary political state. | Who controls or follows humanity when you leave? |
| Spacer — Departure | Gravship becomes permanent home; signal-jammer/orbital access unlocks; orbit instantiated. | Chosen terrestrial institution follows the founders. | Leave the castle and reveal the larger world. |
| Spacer — Small Again | Meet Trader’s Guild, Starjacks and new house-like Spacer powers. | New diplomacy; new Reverence starts near zero. | What are planetary gods worth to people who never heard of them? |
| Spacer — Forbidden Territory | Everyone warns against Glitterites; Sensory Array resolves an Archon return inside their territory. | Waystone-guided Archon spine; first terrifying Glitterite contact. | Is the next rung worth going where nobody sane goes? |
| Spacer Capstone | Deliberate Glitterite heist recovers first Glitterheart / analytical key. | Best vanilla-tier gear versus post-vanilla enemy. | Can you steal enough of their fire to understand it? |
| Ultra I — Exemplars | Raid for weapons, armor, reactors, mechs and other examples before each advanced research branch. | Acquire → analyze → research → manufacture. | What do you need badly enough to attack them for? |
| Ultra II — Anatomy | Discover android/persona civilization, mechanoid control and anima-dependent economy. | Glittertech, android production, stronger raids. | What are these beings, and why do they still need life? |
| Ultra III — Failed Climbers | Archotech hoards and experiments reveal pursuit of transcendence; persona history reveals loss of singular self. | Archon spine converges with Glitterite endgame. | What are they trying to become, and why can they not cross? |
| Ultra IV — Claim Yourself | Final psychic “?” becomes player-authored title; claiming it unlocks the complete altar ritual. | Self as a mechanical prerequisite, not an item. | After everyone else named you, who do you say you are? |
| Final Rite / Coda | Life + intimate Devotion + Global Reverence + Self converge; altar authors Transcendent Archogene. | Full campaign synthesis. | Can you perform the operation every prior civilization only partially understood? |
| Final Threshold | Founders approach the last Archon/ascension author beat with the answer they assembled themselves. | Ending presentation still open; requirements are fixed. | What do you do when the door finally opens? |

# 10. Recommended Quest / State Architecture

Do not build one giant quest manager for everything. The Empire/Deserters comparison points to a cleaner decomposition: use a tiny ordered component only where order genuinely matters, and let scales/thresholds drive the rest.

| Subsystem | Pattern | Persistent state needed |
| --- | --- | --- |
| Archon campaign spine | Deserters-style ordered list/cursor. | Current Archon beat; completion state. |
| Waystone / Charting | Long-Range Scanner-style operator comp + era-banded payload selector; Waystone influences Archon-site resolution. | Effective work toward next find; eligible pools; Tier-2 completion/exhaustion; reach band; current apparatus. |
| Church | Empire-style progression scale + ambient/milestone quests. | Church Rank; relationship; threat/tolerance state. |
| Psychic progression | Independent capability ladder ending in a hidden/unknown final rung. | Founder psylink/channel progression; final self-authored title claimed or not. |
| Reverence | Per-faction social/religious scalar plus derived Global Reverence. | Reverence value per faction; benefit thresholds; global aggregation used by final rite. |
| Schism / anti-Church operations | Deserters-style parameterized operations keyed to Church hierarchy. | Contact state; Intel; targeted hierarchy progress; final outcome. |
| Faction politics | System-driven thresholds + authored major state changes. | Wars/alliances, prior choices, era, relevant ranks/reverence. |
| Planet → orbit transition | One-time author beat after early-Spacer planetary resolution. | Resolved terrestrial outcome; chosen institution; orbital board not-yet-revealed / revealed. |
| Ultra reverse engineering | Research prerequisites keyed to recovered exemplars. | Glitterheart unlocked; exemplar flags/items per research branch. |
| Final rite | Ritual gated on final self-authored title plus Life/Devotion/Reverence requirements. | Claimed title; intimate volunteer eligibility; Global Reverence threshold; final ritual completion. |

# 11. Open Design Questions

These are deliberately unresolved. They should be answered when the surrounding systems are concrete enough to make the choice meaningful.

| Question | Current boundary |
| --- | --- |
| Final name and identity of the Church schism faction | Core narrative is decided: senior and junior insiders break because the Church turns against the sacred beings it taught them to worship. “Witnesses” is not the final name. |
| Exact Church title ladder | Church Rank is separate from Psychic Rank. Early title language may overlap with real psychic stages before diverging. Exact names/count/reward tiers are implementation work. |
| Exact psychic progression between first psylink and final “?” | Medieval delivers the first psylink; Ultra reveals the final self-authored title. The precise middle progression—rites, use, Archon beats, congregation thresholds or a mix—remains open. |
| Reverence formula, benefits and Global Reverence aggregation | Per-faction purpose and final narrative payoff are fixed. Exact sources, population weighting, decay/caps, benefit breakpoints and how faction values combine into Global Reverence require tuning. |
| Church tolerance function | Betrayal is driven by direct Reverence versus Church control, not a fixed quest number. Exact interaction among Church Rank, Reverence and tolerance remains implementation/tuning. |
| Tier-2 discovery count and content | Finite significant pool, probably enough for roughly 10–20 meaningful optional finds in an engaged campaign. Exact catalog and era gating remain open. |
| Charting distance / effort formulas | Reach scales with mobility and apparatus; discovery work uses probabilistic success plus a pity timer. Exact radii, distance bias and research-time distributions require testing. |
| Waystone exact form / presentation | Function is decided: Archotech detector that makes the spine discoverable from Neolithic through space and is not cosmologically founder-locked. Exact art, name and interaction UI can change. |
| Industrial leap boundaries | Industrial identity is strong but exact I1–I4 sequencing should be retrofitted to research, roads, vehicles, faction wars and gravship acquisition. |
| Orbital faction roster | Trader’s Guild, Starjacks and at least two rewritten house-like Spacer powers are intended. Final names, doctrines, relationships and which existing equipment kits map to each are open. |
| Exact Ultra exemplar catalog | Glittertech is Ultra-only and exemplar-gated. Which projects require which captured items/cores and how the first Glitterheart gates the system need implementation design. |
| Final rite numbers | Structure is fixed: mass Life, a small group of personally connected highly convicted willing sacrifices, a high Global Reverence threshold, and the claimed final title. Exact numbers are balance. |
| Final ascension presentation | The altar authors the Transcendent Archogene; the final Archon threshold/door/ending scene after that remains to be authored without turning Archon purpose into explicit exposition. |

# 12. Design Invariants

The current conversation overrides older “settled” labels. Prior documents are context, not a veto on new decisions.
No forced calendar race. Progression pressure can key off era, research, rank, capability and player action, but parking an era should remain valid unless the player triggers the next author beat.
Every major discovery should have a believable information source. Physical locations do not appear because the storyteller decided the player somehow knows about them.
The player should never hoard large quantities of high-value objects for years without understanding their purpose. Mystery is useful as a singular teaser, not as repeatable inventory clutter.
Reverence must pay. It cannot exist only as the stat that makes the Church angry.
The Church route must be materially tempting. Its theme works only if accepting subordination is a reasonable strategic choice.
The schism is not the morally correct questline. It is one path created by people who genuinely believe in the founders and reject the institution that turned on them.
Religion does not end when technology advances. The meaning and organizational scale of worship evolve from altar rite to political institution to interstellar network.
Archon intent stays behind the curtain. The game may reveal mechanisms, patterns and evidence without explaining the Administrator’s true professional motive.
The campaign authors conditions and consequences, never the founders’ inner beliefs. The player decides what their civilization thinks all of this means.
The first psylink belongs in Medieval, not Neolithic. Neolithic teaches anima and blood while letting the player finish learning primitive civilization.
The Waystone explains Archon-site Charting at every scale but is a head start, not proof that only the marked can ascend.
Glittertech begins in Ultra. Spacer ends at the best conventional/vanilla technology plus the first successful theft that makes Glitterite engineering analyzable.
Ultra research beyond vanilla is conquest-linked: advanced Glittertech requires captured exemplars before it can be researched and manufactured.
Archotech is never researched or manufactured. The Glitterites hoard it; the founders find or capture it.
The final requirement is Life + Devotion + Self. Global Reverence becomes literal mass voluntary participation in the final rite.
Self is represented by the player claiming the founder’s own final title. Claiming that title unlocks the ritual; there is no additional ritual object.
The altar authors the Transcendent Archogene with no gene inserted. It is the only Archogene in the campaign that cannot preexist its owner.

**Current campaign sentence**

Two deathless founders learn to build civilization, discover that life carries anima and willing devotion changes it, become entangled with a Church that profits from their divinity, make the whole planet reachable, finish its wars from a gravship, then enter orbit as gods to one world and strangers to the stars. A Waystone leads them into Glitterite strongholds where they steal Archotech and eventually Glittertech, discover that the universe’s strongest civilization is a persona-derived android society that has spent ages failing to transcend, and learn why: Life supplies the substance, Devotion directs it, and a singular Self must cross. The founders finally name themselves, unlock the complete altar rite, call a civilization to spill blood willingly, and enter the altar with no gene loaded. The altar writes the Transcendent Archogene from the person who arrived there.
