# What It Means to "Play RimWorld"

### A design philosophy document for mod work

**Purpose:** This document exists to align anyone — human collaborator or AI agent — on what RimWorld actually _is_ as a play experience, so that proposed systems, mechanics, and content can be evaluated against it rather than against generic "more content is better" instincts.

**Standing caution:** RimWorld is a well-designed game today. The default assumption for any new idea should be that it is worse than what already exists. The burden of proof is on the addition. Most of this document is a set of tests for meeting that burden.

---

## 1. The core inversion

In Valheim, progress makes you stronger relative to the world. Kill boss → unlock station → farm tier resources → repeat. The gate is a _key_, and the time sink is _acquisition_.

In Palworld, progress is level-locked. The gate is _XP_, and the time sink is _grinding the level curve_.

In RimWorld, **progress makes the world stronger relative to you.** Raid threat scales off colony wealth, population, and elapsed time. Research is gated only by time and labor — there is no key, no boss, no tier lock. Everything you build to get ahead simultaneously raises the difficulty floor.

RimWorld is therefore **not a climbing game. It is a homeostasis problem.** The player is staying ahead of a pressure they generate themselves.

**Implication for design:** Any system that reads as a ladder — tiers, levels, strict power multipliers, gated keys — is fighting the game's grain. This does not mean capability gain is bad. It means capability gain must be _given meaning by demand_, not by rank.

---

## 2. What the player is actually doing

### 2.1 Declarative management, not direct action

The work priority grid and the bill system form a declarative programming interface. "Do until you have 50 packaged meals" is a setpoint on a controller. The player does not swing the axe; the player writes the rules that make the axe swing unattended. The characteristic satisfaction spike is **watching the machine absorb a shock without manual intervention.**

Design consequence: mechanics that demand constant manual clicking are alien to the game's core verb. Automation-friendly interfaces are native.

### 2.2 Bottleneck triage

At any moment exactly one constraint limits the colony: food → temperature → labor-hours → mood → defense → medicine → labor again. Skilled play is identifying the live bottleneck and relieving it before it cascades. Relieving one usually creates the next, and the wealth spent relieving it raises the raid floor.

### 2.3 Tech is lateral, not vertical

Most RimWorld unlocks are **dependency trades, not power multipliers.** Hydroponics does not make you stronger; it swaps a dependency on soil and weather for a dependency on power. This is precisely why the tech tree can be open without breaking — nothing in it is a reward, it is all reconfiguration.

Design consequence: new tech should ask "what does this let the colony stop depending on, and what new dependency does it create?" If the answer is "it's just better," it's a ladder rung.

### 2.4 Pawns are three things at once

A pawn is simultaneously a **resource** (labor), a **tool** (skill vector), and a **narrative payload** (traits, relationships, scars, backstory). Losing one is a labor crisis, an emotional event, and a mood cascade in the survivors, all in the same instant. No comparable game fuses these.

**On pawn improvement:** improve-by-doing makes a pawn's sheet a record of what the colony actually did. That pawn is 14 Shooting because she survived things.

Vanilla is narrow here, not absent — horseshoe pins train Shooting, chess tables train Intellectual — so the principle of deliberate practice is already accepted; only its coverage is thin.

A pawn's worth runs along several axes: **skills, passion, traits, genes, age, and health**. What must be protected is that none of these becomes fast, cheap, universal, or indifferent to cost. Note that this is a test of price, not outcome. A devastating pawn at the end of a long, expensive, risky chain is a triumph — the cost is the payoff. The identical pawn off a repeatable bench converts biography into chore and drains the charge from recruitment, prisoner conversion, and genetic work.

## Any system touching pawn improvement should sit deliberately on the intended progression path and be priced to match it: what does it cost, what does it trade away, and what decision does it force?

## 3. The mid-game sag — the central problem

The mid-game is where purpose evaporates: food is solved, the killbox works, research ticks, and newly gained capabilities do not change what the player does.

**This is not a content shortage. It is a demand shortage.**

Early game, the world asks constant questions — it's cold, you're starving, that pawn is bleeding out. Capabilities feel like progress because they are _answers to questions the world just posed_. By mid-game the world has stopped asking new _kinds_ of questions. It asks the same question louder. Bigger raids are a quantitative escalation that the existing killbox already answers.

**The correct goal is not "add more capability." It is "add reasons to want capability the player can already build."**

---

## 4. Taxonomy of existing progression mods

Useful for evaluating what an addition is actually doing:

1. **Subtraction** (e.g. Medieval Overhaul). Doesn't fix the sag; postpones it by deleting the tech that ends the desperate phase. Effective — and note that it works by _removing_.
2. **Unlocking a dormant system** (e.g. Vehicles). The transformative part is not the vehicle; it's that the world map stops being a menu nobody opens. Converts existing dead content into live content. **Highest value per byte.**
3. **Pressure variety** (e.g. faction/raid mods). New raid _shapes_ force reconfiguration rather than a bigger box. Genuine value, but treats a symptom.
4. **More stuff.** New benches, new apparel. Adds micromanagement, not progression. Most content marketed as category 2 is actually category 4.

---

## 5. Projects: the missing structure

The most satisfying self-reported mid-game goals are player-invented projects — e.g. _"deck out 8 knights in full armor and weapons."_ These work because they have a defined end state, are visible in the world, carry real cost, and are chosen.

RimWorld is bad at _seeding_ projects. Quests are ephemeral errands, not ambitions — they arrive, get resolved or ignored within a season, and leave no residue. Nothing in the game plants a goal that takes twenty hours to reach.

Because this is a themed mod, the commitment is already made — the player subscribes to the premise at install, so the mod does not need to offer identities to choose between. The work is **making quests, factions, and events seed long-horizon ambitions within that theme**. Concretely, content that:

- Names an end state the player can hold in their head for many hours ("field a retinue capable of taking that hold," "supply the coast through winter").
- Escalates in stages rather than resolving in one delivery, so progress is legible.
- Points at capability the player could build but hasn't yet, giving already-available tech a reason to be wanted.
- Leaves residue in the world — territory, standing, a rival who remembers — so completion changes the board rather than paying out and vanishing.

---

## 6. Regime change vs. the maintenance trap

The sag exists because **solving is terminal** in RimWorld. Once the killbox works, it works forever. The structural fix is a world that _changes_ so old solutions stop working. This is why late-game mechanoids feel good — and why they arrive too late. Sappers and breachers gesture at this and never follow through.

**Do:** introduce qualitative threat shifts at wealth or time thresholds that render a defensive doctrine obsolete and force a _rebuild_, not a bigger version.

**Do not:** implement decay and upkeep so nothing is ever solved. That is the chore trap — it produces busywork rather than decisions.

Test: **does this make the player rethink, or just redo?** Regime change → rethink. Maintenance → redo. More stuff → click.

---

## 7. Example Flagship Design Direction: factions as a real force

Factions are currently a vending machine plus a raid spawner. Goodwill is a number bought with silver. This is the largest block of dormant, story-native content in the game, and activating it solves several problems at once.

### 7.1 The load-bearing requirement

**Factions must want things from each other, not just from the player.** A purely bilateral goodwill slider collapses back into a vending machine — the player allies with everyone. If factions are in wars that progress with or without the player, then every demand becomes a choice with a cost: helping one _is_ refusing another. Winning factions take territory, grow stronger, and field new doctrine — which delivers regime change (§6) as a byproduct of politics rather than as a bolted-on difficulty spike.

### 7.2 What makes a demand good

Specific, inconvenient, and pointed at capability the player _could_ build but hasn't. Silver is fungible and therefore boring. "200 fine meals by the 15th of Jugust" is a project with a deadline.

Good demand targets: a surgeon on loan for a season; right-of-way through your land; a pawn as hostage-guest; exclusivity (stop trading with X); a fortification built at a named location; military aid against a rival.

**Refusal must be genuinely viable**, or the system is a tax rather than a decision. Preferred shape: **demand → deadline → telegraphed consequence.** The dread of a countdown the player chose to ignore does more work than any raid.

### 7.3 Supporting mechanics

- **Territory on the world map**, interlocking travel with politics: tolls, safe passage, corridors raids travel down, land granted or lost.
- **Distinct military doctrine per faction**, so _who_ you angered determines what you must build — trebuchets vs. drop pods vs. sappers vs. siege starvation. Anger the wrong people and the killbox is scrap.
- **Non-raid hostility**: embargo, blockade, caravan poaching, bounties, hiring a _third_ faction against you.
- **Standing that buys non-material things**: tech transfer, pawn loans, marriage pacts, granted settlement sites. Goodwill should unlock relationships, not discounts.

### 7.4 Two failure modes to design against

- **Notification fatigue.** Ten factions each asking every two weeks is a chore treadmill. Budget hard — roughly two or three live diplomatic situations at a time; the rest simmer in the background.
- **The death spiral.** If alliance is scarce, players end up universally hostile with no path back. Provide a floor: tribute status, vassalage, a humiliating peace that costs dearly but exists. Losing at politics should be a story, not a soft loss screen.

---

## 8. Evaluation tests

Apply these to every proposed addition.

1. **Can it go wrong in a way that produces a story?** Nearly every RimWorld system is bidirectional: food feeds or rots, pawns hero or break, prisoners recruit or riot. A mod that only adds capability flattens the curve. A mod that adds a new _tension with its own failure mode_ multiplies.
2. **Does it create demand, or capability?** Demand is scarce and valuable. Capability is abundant. The moment a faction feature becomes "unlock better trade goods," it has slipped back into the ladder.
3. **Does it make the player rethink, or redo?**
4. **Does it activate dormant content, or pile on new content?** Prefer activation.
5. **Is it a dependency trade or a power multiplier?** Prefer trades.
6. **Does it survive delegation?** If it requires constant manual clicking rather than rule-setting, it fights the core verb.
7. **Does it preserve pawn scarcity?** The test is price, not outcome. Genetics and other manufacture paths are fine — the cost and work required to build a great pawn is the payoff. What devalues the currency is making great pawns cheap, fast, or trivially repeatable.

---

## 9. Player mindset (the thing being protected)

**Anticipatory anxiety plus opportunistic greed.** The player watches the wealth number and thinks _"can I afford to want this."_ The joy is not achieving a tier — it is recovery from a disaster barely survived.

Every addition should feed that mindset. None should replace it with a ladder.
