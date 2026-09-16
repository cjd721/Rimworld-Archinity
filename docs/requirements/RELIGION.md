# Religion and politics

## The Human Political Grammar

Archinity deliberately reuses RimWorld’s existing political grammar rather than replacing it with one universal currency. Each number answers a different question and appears only where it has a clear job.

| System                     | How it is earned                                                             | What it means / does                                                                                                                                                        |
| -------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Goodwill                   | Normal faction diplomacy, gifts and quests.                                  | The government’s relationship with you. It remains the ordinary spend lever for normal faction favors.                                                                      |
| Reverence                  | Conversion and religious propagation; public deeds; selected quest outcomes. | How deeply the player’s ideology has penetrated that faction’s population. Persistent but slowly decaying; gates religious/political possibilities rather than being spent. |
| Exaltation → Church Titles | Church service and Church quests.                                            | The Church’s Honor-equivalent. Thresholds unlock rites and titles; titles grant permanent institutional privileges, requisitions and authority.                             |
| Influence                  | Schism operations and anti-Church missions.                                  | Spendable leverage inside and around the Church: favors, defections, covert access, political pressure and aid. It is not a global diplomacy currency.                      |
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

Very high Reverence creates a second lever where Goodwill cannot function. A friendly faction whose population overwhelmingly follows the player’s ideology can become eligible for vassalage or submission. A hostile government sitting on top of a highly reverent population can become eligible for a revolt: the player commits resources to the believers, success can replace the hostile regime with a subordinate one, and failure can sharply damage Reverence. Exact thresholds and success math are balance work.

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

Titles permanently unlock access to things that should matter: elite equipment, rare resources, military aid, specialists, political privileges, safe passage, requisitions and other powers that ordinary RimWorld acquisition routes are deliberately made less trivial. The Church route is attractive because the rewards are legitimately excellent.

The Church also reveals the missing half of the altar. Willingly given blood/anima behaves differently and widens the psychic channel. This is where the first psylink belongs. Early Church titles and early psychic states may share language or symbolism so the institution can plausibly present itself as the source of the founders’ divinity before the two ladders visibly diverge.

Church missions repeatedly create a central temptation: let the Church own the story and receive the stronger institutional/material outcome, or let the deed be attributed to the founders and their ideology, gaining more Reverence while making the Church increasingly nervous.

**The bargain**

The Church is not the obviously stupid route. It feeds, equips, protects and exalts the founders because they are useful sacred assets. In return, it wants the founders to remain inside the institution’s interpretation of what they are.

## The Schism Path — Influence + Reverence

Influence is the Schism’s equivalent of Deserters Intel. It is not another global relationship score. The player earns it primarily by completing Schism operations that create usable leverage inside or around the Church, and then spends it through the anti-Church network. Plot progression is tracked separately, so spending Influence never reverses the ordered campaign.

The same mission family can support radically different approaches. A covert operation might produce high Influence and little public Reverence; a public miracle or exposure might produce less reusable leverage but sharply increase Reverence; direct violence can remove a target quickly while failing to change the beliefs that made that target powerful. The selected approach determines the reward/consequence profile rather than forcing every mission into the same exact arithmetic.

Influence can buy anti-Church actions that Goodwill cannot: compromised access, defections, protected routes, covert resource acquisition, Schism military help, political pressure on Church nodes and other favors that consume leverage. Exact catalogs are implementation work.

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

Church state includes Exaltation, title and privileges. Its suspicion and eventual
hostility are derived from Global Reverence rather than stored as separate tolerance or
threat currencies: broad penetration makes the Church progressively more hostile until
betrayal or open attack. Schism
state includes contact, ordered mission progress, Influence and hierarchy targets.
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

Final volunteer alignment is defined in [the ending](../plot/ENDING.md#the-alignment-rule--faith-cannot-be-borrowed-dishonestly).
