# Religion and politics

## The Human Political Grammar

Archinity deliberately reuses RimWorld’s existing political grammar rather than replacing it with one universal currency. Each number answers a different question and appears only where it has a clear job.

| System | How it is earned | What it means / does |
| --- | --- | --- |
| Goodwill | Normal faction diplomacy, gifts and quests. | The government’s relationship with you. It remains the ordinary spend lever for normal faction favors. |
| Reverence | Conversion and religious propagation; public deeds; selected quest outcomes. | How deeply the player’s ideology has penetrated that faction’s population. Persistent but slowly decaying; gates religious/political possibilities rather than being spent. |
| Exaltation → Church Titles | Church service and Church quests. | The Church’s Honor-equivalent. Thresholds unlock rites and titles; titles grant permanent institutional privileges, requisitions and authority. |
| Influence | Schism operations and anti-Church missions. | Spendable leverage inside and around the Church: favors, defections, covert access, political pressure and aid. It is not a global diplomacy currency. |
| Psychic Rank | Willing-devotion rites and later campaign breakthroughs. | Actual channel/psylink capability. Independent of Church title. Ends in the unresolved “?” that becomes the self-authored final title in Ultra. |

## Reverence — Religious Penetration, Not Goodwill++

Reverence is tied to the player’s actual ideology. The two founding pawns are mechanically forced into the ideology’s defining leader/preacher roles, so whatever theology the player creates, the founders are its living prophets or exemplars. Archinity never says what that ideology must believe. A serious Archon faith, a bizarre dirt cult or anything else the Ideology system allows can occupy the same campaign structure.

Per-faction Reverence is shown beside Goodwill in the custom political UI. A Global Reverence view summarizes how much of the planet follows the player’s ideology and surfaces the current attention band and major consequences. Diplomatic actions are visibly gated by Reverence so the player can see the carrot before reaching it rather than discovering the system accidentally.

Reverence trends slowly back toward zero if neglected. Religion has inertia, but movements fade when no one carries them. The main acquisition loop should happen through actual people and normal RimWorld events rather than generic religion XP.

Authored introduction: an early faction asks the founders to solve a dangerous problem—such as destroying a raider camp before it attacks. Success publicly demonstrates what the founders can do and introduces Reverence as a concrete reward/consequence.

Faction quests can offer Reverence as an alternative outcome to conventional loot or Goodwill when the deed is publicly attributed to the founders and their faith.

Visitors who sincerely convert before returning home become apostles for the player’s ideology and raise Reverence with their home faction.

Pilgrims from reverent factions become meaningful opportunities: welcoming, protecting and religiously engaging them can strengthen the movement they carry home.

Converted prisoners or rescued outsiders can be released back to their faction as believers, turning individual pawn stories into propagation.

At higher Reverence, the movement can institutionalize. Reverence unlocks the diplomatic option; normal Goodwill remains the spend lever. With sufficient Reverence, the player can spend Goodwill to establish churches, monasteries or equivalent religious institutions inside friendly factions. These institutions deliberately counteract natural Reverence decay and can eventually make the faith self-sustaining. Hostile governments can suppress institutions, persecute apostles and keep Reverence falling unless the player changes the political situation.

Very high Reverence creates a second lever where Goodwill cannot function. A friendly faction whose population overwhelmingly follows the player’s ideology can become eligible for vassalage or submission. A hostile government sitting on top of a highly reverent population can become eligible for a revolt: the player commits resources to the believers, success can replace the hostile regime with a subordinate one, and failure can sharply damage Reverence. Exact thresholds and success math are balance work.

## Reverence as World Attention

Reverence has benefits and consequences. The Storyteller can use Global and faction Reverence as an attention weight when selecting incidents: higher religious penetration makes founder-related politics louder, increases the chance that threatened enemies act, can scale the frequency/intensity of politically motivated attacks, and also increases positive events such as pilgrims, aid, offerings and volunteers.

The relationship must be explicit to the player. The political UI should show the current Reverence band and what it broadly enables or risks; major hostile incidents should say why the attackers are reacting. The player does not need the hidden formula, but they should be able to connect “the world increasingly worships us” to both the power and the danger that follow.

## The Church Path — Exaltation and Titles

The Church uses an Empire-like scale. Church quests award Exaltation. At Exaltation thresholds, the founders perform a rite and receive the next sacred title. Exact names and counts are still authoring work; the structural rule is locked. Church titles are institutional standing, not psychic power.

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

Relationships form through encounters. Factions have interests involving each
other, so helping one can antagonize another. Demands should ask for specific
capabilities: a specialist on loan, a protected route, supplies for an army or
military intervention. Refusal remains viable, with a visible consequence.
Distinct enemy doctrines and non-raid hostility can change what the colony needs
to build. A manageable number of live diplomatic situations prevents notification
fatigue; defeat needs a route back through peace, tribute or subordination.

These are design intentions for [#13](https://github.com/cjd721/Rimworld-Archinity/issues/13),
not a commitment to a continuous background war simulation. Era/capability threat
and Reverence attention must be coordinated by [#9](https://github.com/cjd721/Rimworld-Archinity/issues/9).
Glitterites instead use [Trace](GLITTERTECH.md#trace--the-glitterites-learn-you-back).

## Saved state and remaining work

Church state includes Exaltation, title, privileges and tolerance/threat. Schism
state includes contact, ordered mission progress, Influence and hierarchy targets.
Politics tracks wars, alliances, Goodwill and vassal/revolt outcomes. Reverence is
per faction, with institutional sustain/decay and derived attention bands.

Title and favor catalogs, conversion propagation amounts, decay, institutional
effects, tolerance, revolt success and UI thresholds still need design or tuning.
Friendly submission and hostile revolt are distinct routes. [#35](https://github.com/cjd721/Rimworld-Archinity/issues/35)
specifies their obligations and tithes. [#43](https://github.com/cjd721/Rimworld-Archinity/issues/43)
maps the political systems onto Empire/Deserters machinery.

Final volunteer alignment is defined in [the ending](../plot/ENDING.md#the-alignment-rule--faith-cannot-be-borrowed-dishonestly).
