# Religion and politics

## The Human Political Grammar

Archinity deliberately reuses RimWorld’s existing political grammar rather than replacing it with one universal currency. Each number answers a different question and appears only where it has a clear job.

| System                     | How it is earned                                                             | What it means / does                                                                                                                                                        |
| -------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Goodwill                   | Normal faction diplomacy, gifts and quests.                                  | The government’s relationship with you. It remains the ordinary spend lever for normal faction favors.                                                                      |
| Reverence                  | Conversion and religious propagation; public deeds; selected quest outcomes. | How deeply the player’s ideology has penetrated that faction’s population. Persistent but slowly decaying; gates religious/political possibilities rather than being spent. |
| Exaltation → Church Titles | Church service and Church quests.                                            | The Church’s Honor-equivalent. Thresholds unlock rites and titles; titles grant permanent institutional privileges, requisitions and authority.                             |
| Influence                  | A reward choice on Schism operations.                                        | Spendable leverage with the Schism: it buys the missions that advance the Schism's plot, and favors such as defections, covert access, aid and techprints. It is not a global diplomacy currency. |
| Psychic Rank               | Willing-devotion rites and later campaign breakthroughs.                     | Actual channel/psylink capability. Independent of Church title. Ends in the unresolved “?” that becomes the self-authored final title in Ultra.                             |

**The Church and the player faith are different things.** The Church is the
Roman-Catholic-like external faction created by transforming the vanilla Empire wholesale.
The player faith is the colony's player-chosen ideology with Archinity's required roles
and precepts baked in. “Church” never refers to the player faith.

## Reverence — Religious Penetration, Not Goodwill++

Reverence is tied to the player faith. Its leadership must scale beyond two pawns: the
ideology needs one or two founder-specific seats (one shared multi-holder role or two
equivalent roles), several preacher/converter seats for the core disciples, and at least
one crafting-specialist seat. Additional authored specialist roles—armorer, tailor,
stealth or others—are desirable where the role system can express their effects cleanly.
Roles should be unlockable during the campaign so the institution grows with the colony.
[#114](https://github.com/cjd721/Rimworld-Archinity/issues/114) establishes the available
mechanisms; [#116](https://github.com/cjd721/Rimworld-Archinity/issues/116) chooses the
catalogue and milestones. Archinity still does not prescribe the faith's theology or
presentation.

Per-faction Reverence is shown beside Goodwill in the custom political UI. A Global Reverence view summarizes how much of the planet follows the player’s ideology and surfaces the current attention band and major consequences. Diplomatic actions are visibly gated by Reverence so the player can see the carrot before reaching it rather than discovering the system accidentally.

Reverence trends slowly back toward zero if neglected. Religion has inertia, but movements fade when no one carries them. The main acquisition loop should happen through actual people and normal RimWorld events rather than generic religion XP.

Authored introduction: an early faction asks the founders to solve a dangerous problem—such as destroying a raider camp before it attacks. Success publicly demonstrates what the founders can do and introduces Reverence as a concrete reward/consequence.

Faction quests can offer Reverence as an alternative outcome to conventional loot or Goodwill when the deed is publicly attributed to the founders and their faith.

Visitors who sincerely convert before returning home become apostles for the player’s ideology and raise Reverence with their home faction.

Pilgrims from reverent factions become meaningful opportunities: welcoming, protecting and religiously engaging them can strengthen the movement they carry home.

Converted prisoners or rescued outsiders can be released back to their faction as believers, turning individual pawn stories into propagation.

At higher Reverence, the movement can institutionalize. Reverence unlocks the diplomatic option; normal Goodwill remains the spend lever. With sufficient Reverence, the player can spend Goodwill to establish churches, monasteries or equivalent religious institutions inside friendly factions. These institutions deliberately counteract natural Reverence decay and can eventually make the faith self-sustaining. Hostile governments can suppress institutions, persecute apostles and keep Reverence falling unless the player changes the political situation.

Very high Reverence creates a second lever where Goodwill cannot function. A friendly faction whose population overwhelmingly follows the player’s ideology can become eligible for vassalage or submission. A hostile government sitting on top of a highly reverent population can face a [revolt](#revolt).

Reverence gain is independent of Goodwill; Goodwill gain is not independent of
Reverence. At low Goodwill and substantial Reverence, a government becomes wary that the
founders' religion is eroding its control, so positive Goodwill changes are reduced. At
extreme Reverence—provisionally above 90—the faith has penetrated the ruling ranks and
positive Goodwill changes accelerate sharply. The exact curve is balance, but the inverse
middle and high-end reversal are requirements, not tuning accidents.

## Reverence as World Attention

Reverence has benefits and consequences. The Storyteller can use Global and faction Reverence as an attention weight when selecting incidents: higher religious penetration makes founder-related politics louder, increases the chance that threatened enemies act, can scale the frequency/intensity of politically motivated attacks, and also increases positive events such as pilgrims, aid, offerings and volunteers.

The relationship must be explicit to the player. The political UI should show the current Reverence band and what it broadly enables or risks; major hostile incidents should say why the attackers are reacting. The player does not need the hidden formula, but they should be able to connect “the world increasingly worships us” to both the power and the danger that follow.

## The Church Path — Exaltation and Titles

The vanilla Empire becomes the Church wholesale; there is no separate Empire left beside
it. The Church retains or supplies every Empire-bound acquisition route the campaign still
needs, including techprints, unless those requirements are deliberately removed. Church
quests award Exaltation. At Exaltation thresholds, the founders perform a rite and receive
the next sacred title. Exact names and counts are still authoring work; the structural rule
is locked. Church titles are institutional standing, not psychic power.

Titles permanently unlock access to things that should matter: elite equipment, rare resources, military aid, specialists, requisitions and other powers that ordinary RimWorld acquisition routes are deliberately made less trivial. The Church route is attractive because the rewards are legitimately excellent.

**Title perks are vanilla's kind.** A title lets its holder ask the Church for what a vanilla
title lets its holder ask the Empire for — aid, items, trade and the like — authored for the
campaign's flavour. A title never earns trust with another faction and never lets the founders
direct the Church's diplomacy. Safe passage is not a title perk; it belongs to every faction
([faction politics](POLITICS.md#required-behavior)).
[#123](https://github.com/cjd721/Rimworld-Archinity/issues/123)

**Titles carry decrees.** As in vanilla, the Church lays obligations on titled colonists. What
failing one costs is set per decree: a mood penalty, lost Exaltation or lost Goodwill with the
Church. [#137](https://github.com/cjd721/Rimworld-Archinity/issues/137)

The Church also reveals the missing half of the altar. Willingly given blood/anima behaves differently and widens the psychic channel. This is where the first psylink belongs. Early Church titles and early psychic states may share language or symbolism so the institution can plausibly present itself as the source of the founders’ divinity before the two ladders visibly diverge.

Church missions repeatedly create a central temptation: let the Church own the story and receive the stronger institutional/material outcome, or let the deed be attributed to the founders and their ideology, gaining more Reverence while making the Church increasingly nervous.

**Credit is chosen when the quest is accepted.** A public deed's reward choice is its
attribution: the Church (Exaltation), the founders (Reverence) or, once the founders work with
the Schism, the Schism (Influence). Some options mix rewards. Choosing the reward is what
accepting the quest means; the player then carries the deed out on their own judgment.
[#135](https://github.com/cjd721/Rimworld-Archinity/issues/135)

**The bargain**

The Church is not the obviously stupid route. It feeds, equips, protects and exalts the founders because they are useful sacred assets. In return, it wants the founders to remain inside the institution’s interpretation of what they are.

**Betrayal is final.** When Global Reverence passes a threshold, the Church moves against the
founders in authored beats — a mission that gives them the rope to harm it, then the betrayal
itself. There is no suspicion stat behind it. Betrayal turns the Church permanently hostile,
closes the Church path and brings the Schism's offer at once. Titles remain; every perk and
decree ends. Church techprints end with it, and a run that then declines the Schism keeps only
vanilla's other sources, the intended consequence of the player's choice. A run
that keeps Global Reverence low is never betrayed and can win on the Church path.
[#123](https://github.com/cjd721/Rimworld-Archinity/issues/123)

**The Church's ending.** At the top of the title ladder the Church offers sanctioned apotheosis
([Spacer](../plot/SPACER.md)); accepting ends the run. The offer recurs while the top title is
held and closes for good at betrayal or at the orbital reveal. Vanilla's Royal Ascent does not
ship beside it. What accepting takes is narrative.
[#123](https://github.com/cjd721/Rimworld-Archinity/issues/123)

## The Schism Path — Influence + Reverence

**The Schism** is the faction of Church insiders who believe the founders are truly divine.
In the fiction it is part of the Church until it breaks away. In the world it exists from
creation, hidden and holding no ground. It becomes a visible faction when the founders commit
to it, and where the routes allow it takes its first Church settlement then.

**Its faith moves.** It begins with the Church's faith — sincere believers who take the
founders as proof of the doctrine — and turns to the player faith as the founders take the
credit for its victories. The successor holds the player faith, so its people can become aligned
volunteers ([the ending](../plot/ENDING.md#the-alignment-rule--faith-cannot-be-borrowed-dishonestly)).
[#133](https://github.com/cjd721/Rimworld-Archinity/issues/133)

**Contact follows service or spread, never a schedule alone.** The Church reaches out when the
Medieval era begins. Some time after its first quest offer — provisionally thirty to forty
days, a balance number — the Schism becomes eligible to
contact the founders once they have completed a Church quest or Global Reverence has passed a
threshold, and its contact arrives through ordinary quest generation. If the Church betrays the
founders first, the Schism's offer arrives at once. A run that neither serves the Church nor
spreads its faith may never meet the Schism, and that is a valid choice. Declining the Schism
is never final.

**Operations pay Influence, and Influence moves the plot.** The Schism offers ordinary quests
whose reward choices include Influence — a material reward with a little Influence, a lot of
Influence, or Influence with Reverence among the Church's people. Influence is spent with the
Schism: on the missions that advance its plot against the Church, and on favors Goodwill cannot
buy — defections, protected routes, military help, covert resources and techprints, as the
Deserters' shop sells them. Spending on the plot is the player's choice, so the number of
operations between one advance and the next is theirs too.
[#132](https://github.com/cjd721/Rimworld-Archinity/issues/132)

**Commitment is one act, and it is final.** The founders can work with the Schism while still
serving the Church, and can stop and return to the Church path. They cannot bank Influence and
keep the Church's favor: a defined act — the first Influence gained or the first plot spend,
whichever the routes allow — commits them and turns the Church permanently hostile. There is no
way back to the Church after it, and no option to sell the Schism out. On the Church path the
Church still betrays founders whose Global Reverence grows too high (*Betrayal is final*, above).

**The Church falls in stages.** Each advance is a blow against the hierarchy, and the blows vary:
blackmail that turns a leader, a preaching tour where the founders take the credit, a figure of
the hierarchy captured, exposed or killed. Where the routes allow, Church ground passes to the
Schism blow by blow. The finale turns the Church into the Schism; how completely may reflect the
Church's Reverence and the Influence spent, and whatever does not convert remains a permanently
hostile Church remnant the player may finish or leave.
[#130](https://github.com/cjd721/Rimworld-Archinity/issues/130)

**The successor is a permanent ally, not a vassal.** Drift never breaks the alliance; attacking
it can. It worships the founders and shows it — goodwill, tribute, quests — and follows them into
orbit. [#120](https://github.com/cjd721/Rimworld-Archinity/issues/120) owns what a friendly
faction can pay the colony.

**A beat can require the founders.** A Schism or Church deed that shows the founders to the world
can require one or both of them to attend, and says so before the player accepts.
[#134](https://github.com/cjd721/Rimworld-Archinity/issues/134)

## Revolt

A hostile government ruling a highly reverent population can face a revolt. A faction is eligible
when its Goodwill with the colony is below one threshold and its Reverence is above another. **The Church
is never a target** — the Schism is the Church's revolt.

The player takes part and commits to it. Whether a revolt is offered by the faction or started by
the player at a settlement, and whether a fight, a contribution or both decide it, is open to the
routes. What holds whichever route is chosen:

- **A founder can never be given away.** If founders cannot be reliably excluded, a revolt takes
  no pawns at all.
- **What success makes of the faction is open.** Vassalage is one candidate; an ally, a replaced
  government in an independent faction, settlements passing to another faction, or a change of
  faith alone are others. How much of the faction follows may reflect Reverence and what the
  player committed. A revolt never needs a faction the world was not created with.
  [#131](https://github.com/cjd721/Rimworld-Archinity/issues/131) answers what is possible;
  the choice waits for its routes.
- **What a vassal is stays open.** A settlement taken by conquest, a friendly faction that
  submits, and a whole faction after a revolt or a conquest are all candidates, and they may
  coexist. [#120](https://github.com/cjd721/Rimworld-Archinity/issues/120) answers what is
  possible; [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35) states what a vassal
  must be once it has.
- **Failure** drops that faction's Reverence sharply and collapses its Goodwill, and what was
  committed is lost. The faction can revolt again once its Reverence is rebuilt.
- **An offer declined or left to expire stays away for about thirty days**, so an eligible faction
  never floods the quest board.

[#131](https://github.com/cjd721/Rimworld-Archinity/issues/131)

## The Church's Faith in the World

At world creation the Church's faith is the Church's alone. **When the Medieval era begins, it
spreads:** about 40% of eligible factions take the Church's faith. Eligible factions are those in
the Medieval era that are not highly reverent toward the player faith; Neolithic peoples, later-era
powers, hidden factions and the Schism are excluded. Peoples raised in the Church's faith who turn to
living gods are what Reverence and revolt work on. The founders may serve the Church, but the player
faith never becomes the Church's. [#133](https://github.com/cjd721/Rimworld-Archinity/issues/133)

## Political pressure

Moved to [faction politics](POLITICS.md), settled on
[#13](https://github.com/cjd721/Rimworld-Archinity/issues/13). Demands, refusal,
the goodwill ripples along rivalries and alliances, what standing buys, and the
ally-aid battle are faction-generic — they apply to raiders and Glitterites as much
as to the Church — so they are no longer filed here.

What stays religion's business is the **input**: a faction whose population
increasingly follows the founders' ideology reacts politically to that, whether or
not it is allied. Reverence and Goodwill are separate axes and neither substitutes
for the other.

Era/capability threat and Reverence attention are coordinated by
[#9](https://github.com/cjd721/Rimworld-Archinity/issues/9) and [`PRESSURE.md`](PRESSURE.md).
Glitterites instead use [Trace](GLITTERTECH.md#trace--the-glitterites-learn-you-back).

## Saved state and remaining work

Church state includes Exaltation, titles, perks and whether the Church has betrayed the
founders. Before betrayal its hostility is ordinary Goodwill; there is no suspicion, tolerance
or threat state. Schism
state includes contact, whether the founders have committed, Influence and how far its plot has
advanced.
Reverence is per faction, with institutional sustain/decay and derived attention
bands. Wars, alliances, Goodwill and vassal/revolt outcomes are tracked by
[faction politics](POLITICS.md).

Title and favor catalogs, conversion propagation amounts, decay, institutional
effects, Reverence reaction bands, revolt success and UI thresholds still need design or tuning.
Friendly submission and hostile revolt are distinct routes. [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)
specifies their obligations and tithes. [#98](https://github.com/cjd721/Rimworld-Archinity/issues/98)
(Reverence, end to end — superseding closed #52),
[#53](https://github.com/cjd721/Rimworld-Archinity/issues/53) (Exaltation),
[#54](https://github.com/cjd721/Rimworld-Archinity/issues/54) (Influence and Intel together)
and [#56](https://github.com/cjd721/Rimworld-Archinity/issues/56) (Trace) each deliver one of
the political systems, starting from its candidate Empire/Deserters machinery.

The Schism, revolt and the Church's faith were stated on
[#122](https://github.com/cjd721/Rimworld-Archinity/issues/122). Their capabilities are open at
route depth: [the Schism's reveal, ground and alliance](https://github.com/cjd721/Rimworld-Archinity/issues/130),
[revolt](https://github.com/cjd721/Rimworld-Archinity/issues/131),
[Influence moving the plot](https://github.com/cjd721/Rimworld-Archinity/issues/132),
[NPC faith changes](https://github.com/cjd721/Rimworld-Archinity/issues/133),
[founder-required beats](https://github.com/cjd721/Rimworld-Archinity/issues/134),
[credit as a reward choice](https://github.com/cjd721/Rimworld-Archinity/issues/135) and
[vassals](https://github.com/cjd721/Rimworld-Archinity/issues/120).

Title perks, decrees, betrayal and the Church's ending were stated on
[#123](https://github.com/cjd721/Rimworld-Archinity/issues/123). Perks are answered by
`docs/specs/RELIGION.md` §5; betrayal's permanent hostility has a named route (one saved bit and a
goodwill cap, #130 route A);
[decrees with a chosen failure cost](https://github.com/cjd721/Rimworld-Archinity/issues/137)
is open. Whether Church titles grant psylinks is Conrad's to decide later; every shape is
already possible.

Final volunteer alignment is defined in [the ending](../plot/ENDING.md#the-alignment-rule--faith-cannot-be-borrowed-dishonestly).
