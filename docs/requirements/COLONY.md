# Colony management

## Purpose

The colony's own people, benches and gear, and the friction of running them.

This document exists because four specced systems had no requirement behind them at all.
[#87](https://github.com/cjd721/Rimworld-Archinity/issues/87) established that **no
requirements document owned menu legibility or crafting defaults**, and `docs/progression/`
holds only a README; `docs/specs/ITEMS.md` records the same gap for item deprecation in its
own words. Four stub documents would have been worse than one, so they share this one.

Nothing here is a campaign system, and nothing here is fiction. These are the requirements
that keep a long two-player playthrough from being spent re-entering the same number at
every bench and rebuilding the same outfit in every colony.

Authored by [#129](https://github.com/cjd721/Rimworld-Archinity/issues/129).

## Meaning

**A pawn is committed to a role, the commitment is visible, and changing it costs
something.** This is the through-line of the first two sections. A colonist who has been
invested in — in gear, in progression, or in both — is a specialist and not a
general-purpose body. That is deliberately the mid-game's engine and not a convenience: a
pawn carrying everything that makes them a better cook is not also the farmhand, and a
captive at skill four is worth taking because a kit and a few advances make them
serviceable.

**Deprecation and reclamation are a pair, and deprecation is never confiscation.** An era
advance does not touch what the colony owns — [era](ERA.md) is explicit that no building,
item, pawn or research the player holds is retiered, upgraded or invalidated at a boundary,
and nothing in this document softens that. What changes is everything *around* it: better
materials and better recipes arrive, and yesterday's plate armour is surpassed rather than
taken away. Reclamation is what lets the player act on being surpassed, so that a wardrobe
of superseded gear is a stock of material and not dead weight.

**Configuration is not gameplay.** Where the player is repeating an act they have already
decided — the same floor on the twentieth bill, the same outfit in the second colony — the
repetition is friction and the campaign removes it. Where the player is *choosing*, the
choice stays.

## Required behavior

### A pawn's gear can be assigned as a set

- **Gear sets are authored and shipped**, and are present in a fresh colony without being
  rebuilt by hand: Cook, Farmer, Smith, Miner, Doctor, melee soldier, ranged soldier.
- **A set covers what the pawn carries, including its weapon.** Apparel alone is the floor,
  not the target — the point of the system is that a pawn kitted as the cook *is* the cook.
- **Assigning a set is one act**, after which the pawn equips itself without further
  instruction.
- The player can **force a pawn to re-equip to its set**, and **force it to drop what it is
  carrying**.
- **A set naming gear from an unreached era is not a failure.** It is intended: the set
  names the destination, and the pawn wears the best it can currently reach.
- **Vanilla work priorities are not part of this.** RimWorld already supplies them, they
  already work, and nothing here replaces or wraps them.

### A pawn can advance within a skill

- **A pawn that becomes good at something can specialise inside it**, without inventing new
  skills: a smith may go toward weapons or toward armour, on the same skill and the same
  experience.
- The advance is **earned by use and chosen by the player**, at intervals as the skill
  rises, and **limited to skills the pawn is deeply passionate about**. A pawn cannot
  specialise in everything.
- **Individual advances are small and numeric** — a working speed, a yield, a quality
  chance. None of them unlocks content, and none is required to play.
- **Pawns the player did not train arrive already specialised.** A recruit or a captive with
  high skill and the wrong specialisations is a real disappointment; one with the right
  specialisations is a real prize. This is the clause that makes looking at a pawn
  interesting.

**This behavior may be delivered by scarcity instead of by progression.** A bounded set of
named posts, each held by one pawn at a time and each carrying the same kind of bonus,
satisfies the commitment requirement without a progression surface at all. Both shapes are
in scope. Player-chosen progression is the preferred experience, bounded posts are the
guaranteed fallback, and the choice waits for the routes.

### Bills arrive configured, and a configuration can be reused

- **A new bill opens with its count and both its floors already in front of the player**,
  the first time that bill is opened, rather than at values the player must go looking for.
- **The defaults are per-recipe, not one number for everything.** A durability or quality
  floor that is right for plate armour is wrong for steel, and a target count is different
  for almost every recipe. The shared default is the mode; the floors are per recipe.
- **The player's edits are never re-imposed.** Defaults are written once, when the bill is
  created, and never consulted again.
- **A bill's configuration can be copied and applied to another bill, carrying the settings
  and not the recipe.** Setting up a chest-armour bill correctly and then repeating it for
  the gloves, the helmet and the boots must cost a paste, not ten clicks each. **This is the
  requirement; the defaults above are the floor beneath it, and both ship.**
- The configuration carries: repeat mode and target count, the durability range, the quality
  range, the material restriction, the allowed worker skill range, the pawn restriction and
  the destination.

The defaults half is already verified: [#95](https://github.com/cjd721/Rimworld-Archinity/issues/95)
established the mechanism in `docs/specs/DEFAULTS.md`, and what it lacked was this document
saying which values belong on which row. **Copy-paste is new ground.**

### The add-bill menu shows what matters now

- **A bench's add-bill list foregrounds the recipes that matter in the colony's current
  era**, rather than every recipe the bench has ever carried in one unsorted list.
- **This is presentation, never a content gate.** What the colony can make is gated by
  research alone ([era](ERA.md) § *The acquisition gate*); nothing below the era ceiling is
  ever made unreachable by a menu. Older recipes stay available, only less prominent.
- **The research tab is settled:** one tab per era, and the whole tree visible from the start
  ([era](ERA.md) § *Player information and agency*).

Established on [#96](https://github.com/cjd721/Rimworld-Archinity/issues/96). Whether this is
a filter, a grouping, era-limited benches or search alone waits for the routes.

### Recreation follows a pawn's passions

- **A pawn at recreation prefers recreation that trains a skill it is passionate about**,
  major passion first. A deeply passionate shooter who goes to relax goes and shoots.
- **Recreation that trains a skill exists** and is not the new part: vanilla already carries
  it in XML. The requirement is the preference.
- How much experience recreation grants, whether room quality multiplies it, and which
  recreation trains which skill are balance and content, not this document's.

Established on [#76](https://github.com/cjd721/Rimworld-Archinity/issues/76), from
`docs/playtest-notes.md`.

### Obsolete gear goes back to the material it was made of

- **Reclaiming returns the material itself**, at a bench, with no intermediate resource.
  No scrap, no rags, no salvage — [the plot](../PLOT.md)'s no-chains rule.
- **Half comes back.** Less reads as a punishment for having equipped the colony at all;
  more makes reclaiming strictly better than keeping anything.
- **The return does not depend on the item's condition or its quality.** What the player
  chooses is *which items to feed the bench* — only the tattered, only the awful — not how
  much each one is worth once fed.
- **It works in the era the colony is actually in.** A Neolithic colony reclaims cloth,
  leather and wood at the bench it has; this is not an electric-age privilege.
- **Relics are never reclaimed, and reclaiming never produces a manufactured resource.**
  Taking apart power armour must not print free components.

[#82](https://github.com/cjd721/Rimworld-Archinity/issues/82) verified the mechanism in
`docs/specs/ITEMS.md` and left two parameters explicitly unowned: the return fraction, and
whether yield depends on condition or quality. **The second and third clauses above are this
document answering them.**

## Campaign progression

Gear sets and bill configuration are available from the first day and do not change across
the campaign. Their *content* grows as the eras supply better materials, but the behavior
does not.

Specialisation wants to be reachable early enough that a low-skill recruit is worth taking,
because that is what makes weak captures worth the cost of keeping them.

Reclamation is tied to the [era](ERA.md) boundary that makes gear obsolete in the first
place. Which bench carries it, and from which era, belongs to
[#22](https://github.com/cjd721/Rimworld-Archinity/issues/22) and
[#30](https://github.com/cjd721/Rimworld-Archinity/issues/30).

## Player information and agency

The player can see what a pawn is committed to, and can change it — at a cost where the
commitment was earned, freely where it was only assigned.

A bill's settings are visible on the bill, and copying a configuration is an explicit act.
Nothing here silently changes a value the player has set.

**The player can find out what proportion a reclaim returns before committing an item to
it.** A number the player has to discover by experiment is not acceptable, and a number
displayed somewhere that does not actually govern the outcome is worse.

## Constraints

- **Nothing here may be carried in mod settings.** A value read from a client-local slider
  is a multiplayer divergence source, not a default. See
  [T-18](../TRAPS.md); `docs/specs/DEFAULTS.md` records two live instances of exactly this
  mistake in the corpus, one on each of these seams.
- **Authored content must survive as content.** A gear set or a specialisation the player
  cannot receive without rebuilding it by hand in every save has not been delivered. This is
  a real constraint and not a formality: neither `ApparelPolicy` nor the one loadout mod in
  the corpus has any `Def` backing, so both are runtime save state.
- **No new skills and no new experience currency.** Specialisation rides RimWorld's existing
  skills and the experience the pawn already earns.
- **No specialisation may unlock content**, gate a recipe, or advance an era. These are
  bonuses. The era arc belongs to [era](ERA.md) and nothing in this document touches it.
- **The preset roster is not this document's** — which sets ship, holding what. That belongs
  to the progression grids ([#19](https://github.com/cjd721/Rimworld-Archinity/issues/19),
  [#20](https://github.com/cjd721/Rimworld-Archinity/issues/20),
  [#41](https://github.com/cjd721/Rimworld-Archinity/issues/41),
  [#42](https://github.com/cjd721/Rimworld-Archinity/issues/42)).

## Open questions

- **A pawn's whole kit as one authored set, weapon included** —
  [#155](https://github.com/cjd721/Rimworld-Archinity/issues/155). The apparel half is
  already answered by [#28](https://github.com/cjd721/Rimworld-Archinity/issues/28); the
  weapon, the authorability and the two verbs are not.
- **A pawn specialising inside a skill it already has** —
  [#156](https://github.com/cjd721/Rimworld-Archinity/issues/156), which also owns the
  bounded-posts fallback and whether generated pawns can arrive specialised.
- **Copying a bill's configuration onto another bill** —
  [#157](https://github.com/cjd721/Rimworld-Archinity/issues/157).
- **The add-bill menu, filtered or grouped by era** —
  [#161](https://github.com/cjd721/Rimworld-Archinity/issues/161).
- **A pawn favouring recreation that trains its passions** —
  [#159](https://github.com/cjd721/Rimworld-Archinity/issues/159).
- **The quality and durability floor values**, and whether they vary by era, are balance.
  They belong to [the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119)
  and an era-varying floor additionally waits on progression grids that do not yet exist.
- **Whether a dedicated reclaim bench ships**, as against reusing existing benches, is a
  build question for #119 once #22 and #30 place the eras.
