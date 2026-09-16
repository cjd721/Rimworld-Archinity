# Spacer

Previous: [Industrial](INDUSTRIAL.md) · [Overview](../PLOT.md) · Next: [Ultra](ULTRA.md)

## Early Spacer Transition — Planetary Resolution & the Orbital Gate

Early Spacer begins with the planet still active. The gravship has enough range and capacity to make the founders the decisive mobile power in wars that Industrial civilization set in motion. Tertiary factions enter full-scale conflict; Church obligations become increasingly naked feats of strength; the Schism closes on the Church hierarchy; independent players finish the board through Reverence, diplomacy, revolt, vassalage and conquest.

The political/religious outcome must resolve before the player reveals orbit, because the reveal is what puts the selected surviving institutions into the sky. The planet answers who is coming with the founders before the curtain opens on the larger world.

The implementation constraint is real but runs the other way from what this chapter used to claim, and the difference matters to the world roster: **the orbital powers themselves are created when the world is created, and cannot be added afterwards.** What is deferred is not their existence but their *visibility and their territory* — orbit generates empty, the view-orbit button sits greyed with "No discovered orbital locations.", and the reveal is what places the stations. Any institutions selected from the live planetary outcome need no creating at all; they are already factions on the planet, and the reveal simply gives them orbital ground. See `docs/specs/ORBIT.md`.

The causal concept is locked even though the exact flavor is not: the final planetary power structure controls, inherits or can seize the last infrastructure/knowledge needed for sustained orbital access. Church route receives it through institutional authority; Schism route inherits or captures it when the old hierarchy falls; independent route obtains it through planetary supremacy. The exact device/owner can be authored around the signal-jammer/orbital-access mechanic.

| Planetary resolution | What carries forward |
| --- | --- |
| Church route | A sanctioned religious civilization that follows the founders into space if they refuse the Church’s terrestrial ending. It has titles, resources, hierarchy and missionary reach, but remains fundamentally a planetary institution being dragged upward by the founders. |
| Schism route | A founder-believing successor institution that inherits enough of the old Church’s people and infrastructure to function immediately, then follows into orbit as the founders' permanent ally. |
| Independent route | A founder-centered polity/religious network built through the player’s ideology, Reverence, diplomacy, vassalage, revolt and conquest rather than inherited Church institutions. |

The Church also retains a genuine terrestrial terminal victory. At the top of its title ladder it can offer permanent sanctioned apotheosis, safety, wealth and legitimacy—Archinity’s Royal Ascent analogue. Accepting ends the run. Cosmologically, the founders chose to stop climbing and become gods of one world, but the game never labels the choice “bad.” Refusing allows the campaign to continue into space.

## Spacer Arc — The Planet Stops Being the World

## Crown — Finish the Planet

Spacer opens planetside. The gravship is already the greatest transport platform on the world and keeps gaining range, capacity, defenses and life support. It lets the founders settle conflicts that Industrial civilization made planetary.

Church route: final title stages become deliberately exploitative. The Church sends deathless sacred assets into wars, sieges and crises ordinary rulers would never risk themselves on. The bargain remains real because the rewards and privileges are correspondingly extraordinary.

Schism route: covert opposition becomes open war. Influence and military action are used to expose, fracture and ultimately replace the old hierarchy.

Independent route: the player resolves the same board without either institution and can weaponize high Reverence through vassalage or revolt while also using conventional diplomacy and conquest.

The point is not that Spacer immediately leaves the planet. The point is that the planet has become small enough for the founders to finish.

## Departure — The Gravship Becomes Home

The gravship crosses a qualitative line from vehicle to civilization. It gains reliable oxygen, gravity, food production, cooking, habitation, storage, defenses, shields and enough capacity that the colony can permanently leave the electrified castle behind. The old base becomes history rather than the center of play.

Once the planetary outcome is resolved and the orbital-access gate is obtained, orbit is revealed for the first time. Only then does the offworld political board become visible and occupied — the spacer powers take their stations, and every terrestrial faction captured by the immutable outcome takes ground among them.

## Orbit — Small Again

The first orbital reveal is a status reset, not a power reset. On the planet the founders were famous enough to reorganize kingdoms; in orbit they meet mature Spacer civilizations that have been trading, fighting and living above them for generations. Their gravship is formidable, but no longer cosmically unique.

The Trader’s Guild is a system- or galaxy-spanning commercial network with depots, missions, unusual goods, orbital stops and leisure sites. Its few terrestrial strongholds existed because the planet was merely a tiny edge of a larger network.

The Starjacks are a distinct spacer culture with their own equipment, ships and social identity.

At least two additional Spacer powers use the excellent visual/weapon/armor systems supplied by the existing house mods, but all original faction names and lore are discarded. They become new Archinity civilizations with their own doctrines and politics.

Advanced mechanoids and other offworld threats establish that orbit has a higher baseline of danger and technology than the planet.

Reverence carries forward only where belief actually exists. The terrestrial populations and institutions that came with the founders retain their faith; new spacer factions begin near zero because they have never heard a convincing reason to care. The founders are gods to one world and strangers to the stars. The same conversion/pilgrimage/institution logic can spread the player’s ideology into the new board.

## The Forbidden Territory — Glitterites as a Fact of the Universe

Other orbital factions warn the player about the Glitterites before the Archon spine forces contact. Glitterite territory is treated as poisoned space: they are hostile to everyone, do not conduct normal diplomacy, field terrifying mechanoids and consume organic life. Most civilizations simply route around their holdings.

The Glitterites are uncommon but absolute where they exist. At this stage the player does not know their ultimate objective. The important first impression is that everyone else has learned not to touch them.

## The Waystone Points Into Hell

The Sensory Array eventually resolves a powerful Archotech return from inside a Glitterite-held site. This is the first unavoidable collision between the Archon spine and the Glitterites. The campaign does not say “fight the final villain.” It says the same signal followed since the Star Table is behind those defenses.

The first raid should feel like an impossible heist. The colony arrives in the best conventional/vanilla-tier gear, with mature psychic capability, a fully functional gravship and elite colonists, and still discovers that Glitterite defenses are on another scale.

The reward proves two things: Glitterites possess Archotech, and their own technology is beyond anything the player can manufacture.

Subsequent Waystone returns intersect Glitterite holdings often enough that coincidence becomes impossible. The player realizes they are systematically collecting Archotech, but not yet why.

## Spacer Capstone — Steal Fire

Spacer ends with a deliberate second incursion. This time the player goes back because they have identified the Glitterite core/component needed to make their engineering analyzable. The capstone produces the first Glitterheart—working name—or equivalent analytical key.

Obtaining it does not grant Glittertech. It changes the rules of research. Ultra begins when the colony can finally understand captured Glitterite systems well enough to reverse engineer them. Spacer ends at the best conventional RimWorld technology; Glittertech starts after this line.

The Starjack Free Companies hold that a ship belongs to the people aboard it,
with no authority owed to planetside rulers. They can be allies or enemies.
Their people and the Archons do not bleed into ordinary planetside faction rosters.

The orbital gate's exact device and owner, the new Spacer powers' names and
doctrines, and the first heist's site remain authoring work — but the powers'
**names are now on a deadline**, because they cannot be added after the world is
generated.

The architecture is verified and is not the one this chapter originally described
([#70](https://github.com/cjd721/Rimworld-Archinity/issues/70), `docs/specs/ORBIT.md`).
Orbit is **generated at world creation and revealed later**: every orbital power is
created with the world, hidden, holding nothing; the reveal unhides them and places
their stations. Deferring the *creation* of an orbital faction is impossible and fails
silently (`docs/TRAPS.md` T-07). Deferring their *appearance* is what vanilla already
does, and the greyed view-orbit button is Odyssey's own.

So the faction roster work must name every orbital power before worldgen. The
save-state work is small but not nothing: the reveal writes one already-scribed field
and places ordinary world objects, and one small new component remembers that it
happened.
