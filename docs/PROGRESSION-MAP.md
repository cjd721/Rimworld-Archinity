# The Progression Map — Neolithic & Medieval

Narrative first. Then capability. Then research.

This is a design target, not an inventory. It assumes nothing about what any mod currently
does, what anything costs, or how long anything takes. Every asset in the loaded set is
treated as raw material that can be renamed, restatted, remade or thrown away. The only
question asked here is:

> **What is the player doing, wearing, eating, building and fighting with at each point in
> the story — and what does he research to get there?**

Balance, points, pacing numbers and tech-gating mechanics are a later pass and are
deliberately absent. Sourcing — which mod supplies which asset — is the pass after this one.

**Supersedes `RESEARCH-NEO-MED.md`**, which was built on a wrong premise. See §9.

---

## 1. The five leaps

Two in the Neolithic. Three in the Medieval.

| | Leap | The one-line story | You have arrived when… |
|---|---|---|---|
| **N1** | **The Primitive Baseline** | Cavemen work out how the world functions, then build the worst version of everything. | You have a camp, a farm, a fire, hide clothes and bows — and every pawn is bad at all of it. |
| **N2** | **The Settled Tribe** | The camp becomes a place. Walls, worked leather, siege, masonry, and contact with the world. | You are Rome without the metal: walled, disciplined, fed, armoured in hardened leather. |
| **M1** | **The Forge** | Metal arrives and every system you own gets remade in it. | Men in metal-scaled armour carrying metal weapons behind stone walls. The place is popping. |
| **M2** | **Mail & Siege** | You stop being new at metal and start being good at it. | Mail hauberks, military arms, castle walls, ballistae, mills that work without you. |
| **M3** | **Plate & Powder** | Mastery of the pre-electric world, and the first crack of gunpowder. | Full plate, noble arms, marble halls, heraldry, and a throne room you will still own in orbit. |

**Relative weight.** N1 is the shortest and the most eventful — it hands over the game
itself. N2 is roughly its equal and is where the tribe earns permanence. M1 is the single
largest leap in the project, because metal touches every domain at once and each one needs
its own rung. M2 and M3 are each smaller than M1, and M3 is the smallest of the three —
by then the player is reaching for the next era.

### The four moments

Each boundary is a named beat, not a progress bar filling up. They should read as events.

| Moment | Where | What happens |
|---|---|---|
| **The First Thought** | mid-N1 | A pawn thinks abstractly for the first time. The ritual circle retires; a research bench goes down. This is the moment the game becomes RimWorld. |
| **The First Wall** | N1 → N2 | The tribe stops surviving and starts holding ground. Something is built that is meant to outlast the people who built it. |
| **The First Ingot** | N2 → M1 | Metal. The single most consequential discovery in a hundred days of play, and it should be presented like one. |
| **The First Spark** | M3 → Industrial | Electricity, and the end of everything this document covers. |

---

## 2. The design law

Five rules. Every node, item and capability below obeys them. A proposal that violates one
is wrong, regardless of how good it sounds.

### 2.1 One core bench per domain, upgraded forever. Augments persist.

The hearth you cook on in the Neolithic is the same hearth, upgraded, on your gravship.
Its augments carry across every upgrade. The player never manages five buildings for one
domain, and never hunts through five bill tabs to find where a recipe lives.

**Bigger unlocks are bench *upgrades*. Smaller unlocks are *augments* bolted onto the
bench.** That is the entire shape of production progression.

### 2.2 The surface grows. The complexity stays linear.

Each tier adds **one generic ingredient class** — never a new processing chain, and never
a named crop. "Any two vegetables," never "corn and potatoes." The player should never be
optimising which plant feeds which recipe, and should never be asked to convert a raw
material into an intermediate material in order to use it.

Wood is wood. Cloth is cloth. Metal is metal. The construction cost of a thing is the
roleplay of shaping the material; there is no plank step, no board step, no ingot step, no
spinning step. Anything that would still be demanding that busywork in the Spacer era does
not ship.

### 2.3 Every rung is a real improvement.

Hide → cured → boiled → hardened must each be better on the stats that matter for armour.
A rung that costs more, needs more research and is not better should not exist. A tier
whose only function is to be skipped is a bug in the design.

### 2.4 A resource must evolve with the player or it does not exist.

The test: *does this thing's use case still matter three eras from now, or does it become
permanent noise in trade stock and quest rewards?* A resource that stops mattering is worse
than one that never existed, because it keeps costing attention forever. Salt fails. Linen
fails. A medieval-only supermetal fails.

### 2.5 Two classes of research, gated differently.

- **Spine** — you must have it to play. Ordinary resource costs and ordinary item
  requirements. It is never behind a fetch quest.
- **Quality-of-life** — the scarecrow, the mine shaft, the crane, the siege engine, the
  trough. Rare, high-value, and it does **not** gate progression. **This is where hunt
  requirements belong.** The resource cost can be near zero; the going and getting is the
  cost.

Two or three hunts per era. More than that and the era becomes a chore list.

---

## 3. The ladders

The same information read sideways: every domain, every rung, in one view. This is the
spine of the whole design — if a domain has a flat or missing rung here, that is a hole to
fill.

| Domain | N1 · Primitive | N2 · Settled | M1 · Forge | M2 · Mail | M3 · Plate |
|---|---|---|---|---|---|
| **Research seat** | ritual circle → primitive bench | *(same)* | simple bench | scriptorium | *(same)* |
| **Hearth** | campfire → primitive stove | + grill, stew pot, mill, smoker | rustic oven | + cheese press | great oven |
| **Loom** | hide-working slab | *(same)* | hand tailor bench | + loom, spindle | + mannequin, master work |
| **Forge** | — | — | fueled smithy + anvil, bellows | + furnace, quenching | master forge |
| **Stoneyard** | knapping slab | stonecutter's table | *(same)* | + chisel rack, clamp | + polisher, sculptor's studio |
| **Armour** | hides, tribalwear | cured → boiled → hardened leather | **scale & lamellar** | **mail** | **plate** |
| **Melee** | shiv, club, sling-staff | spear, axe, shortblade | basic metal arms | military arms | noble arms |
| **Ranged** | thrown rock, throwspikes, short bow | recurve, hunting bow, longbow | war bow | crossbow, arbalest | firearms |
| **Siege** | — | **catapult** | — | **ballista** | **cannon** |
| **Fortification** | stakes, wood walls | trench, palisade, log gate | brick wall, reinforced trench | castle wall, gate, embrasure | heraldic bastion |
| **Food** | one meat → meat + 1 | + any-2-veg stew | + eggs | + flour, cheese | exotic tier, top buffs |
| **Agriculture** | tier-1 plants, garden box | tier-2 plants, scarecrow | large fields | tier-3 plants, mills | exotics |
| **Medicine** | herbal gathering | herbal production, herb table | apothecary, alembic | surgical tools | master apothecary |
| **Light** | campfire, torch | candle, candelabra | oil lamp | wall lamp, brazier | chandelier |
| **Rest & comfort** | sleeping spot → mat → primitive bed | fur bed, bath house | rustic bed, dresser | fine furniture | royal furniture, throne |
| **World reach** | none | **carrier birds** | trade caravans | embassies | heraldic renown |
| **Automation** | trough | scarecrow | **mine shaft** | **crane**, windmill, watermill | sprinkler |

**Read the armour row.** Hide → cured → boiled → hardened → scale → mail → plate. Seven
rungs across two eras, each a visible step up, each using a material the player already
understands. That row is the single best expression of what this whole document is for.

---

## 4. N1 — The Primitive Baseline

### The narrative

You have nothing. Not tools, not fire, not the *concept* of farming. The Archon Gods came
down and blessed a handful of cavemen, and now those cavemen have to work out how a rock
works.

So you sit in a circle and figure it out together. Every discovery hands you a **verb** —
you cannot farm until you learn farming, because the tool to mark a field does not exist
yet. You cannot tame, hunt, mine, or put a roof on anything until someone in the circle
works out how. Ten days of this and you can do all of it, and one of you is finally capable
of abstract thought — which means you can put down a research bench and stop sitting in
circles. **The First Thought.**

Then you build the primitive version of everything. Beds that are woven mats. A stove that
is a hole with stones round it. A tailoring slab that is a flat rock and a bone needle. A
research bench made of sticks. By the end you have a camp, a farm, a fire, hide clothing
and bows — and your pawns are bad at all of it.

That is correct. That is the point.

### What the colony looks like

A fire in the middle. Sleeping mats around it. A scratched-out field of the four plants you
know. A pen with three tamed animals and a trough. A rack of drying meat. Torches on
sticks. A handful of people in hides carrying clubs, and one of them just built a bench and
sat down at it for the first time.

### Capabilities

| Category | What the player has |
|---|---|
| **Jobs & designators** | Firefighting, Growing (+ field tool), Handling (+ tame, slaughter), Mining (+ mine, smooth), Hunting (+ hunt tool), Construction (+ roof, floor tools), Intellectual. **The whole base job set, and none of it was free.** |
| **Shelter** | Sleeping spot → bedroll → primitive bed and double bed. Slab seats, sitting spots, primitive tables. Wood and stone walls, doors, roofs. |
| **Food** | Tier-1 plant set — a grain, a root, a medicinal, a fibre, and little else. Garden box. Campfire → primitive stove. Food tiers 1–2: dried meat; meat plus one thing. Drying rack. |
| **Benches** | Primitive research bench, stove, hide slab, knapping slab, butcher table, art bench, styling station. **Every core bench exists in its worst form.** |
| **Apparel** | Tribalwear, light and heavy. Fur coats and hats, hide hoods, desert robes and wraps, trophy helms taken off large insects. No armour worth the name. |
| **Weapons** | Shiv, shard, throwing shards, sling and sling-staff, light and heavy club, stone axe, throwspikes, spear. Short bow, then recurve. |
| **Defence** | Stakes. Wooden walls. Traps. That is all — you are not defensible, and you should feel it every time a raid lands. |
| **Medicine** | Herbal medicine, grown and processed at a herb table. Tend and treat. No surgery worth the name. |
| **Animals** | Tame, train, slaughter, butcher. Fences, gates, pens. **Trough** — the first QoL item in the game. |
| **Light & mood** | Torches, campfire, candles, candle stands, candelabra. Floor paintings. Crude art. |
| **World reach** | **None.** You cannot talk to anyone. Trade is whoever happens to walk up to you. |

### The research

**The Awakening — the verb set.** Gathering-ritual research, no bench. Each of these hands
over a job, a designator or a work tag, and they are the model the whole project is built
on: *research grants capability, not recipes.*

```
Fire ─┬─ Growing ── Cultivation ── Herblore ─┐
      ├─ Beast-Handling ────────────────────┤
      ├─ Stoneworking ── Shelter ── Furnishing ─┼─ CULTURE
      ├─ Hidewear ─────────────────────────────┤   → abstract thought
      └─ Hunting ── Weapon-Making ── The Bow ──┘   → the research bench
```

**The Primitive Tier — bench research.** Opens with shelter, food and farming so the queue
is never empty in the first week off the circle. Closes with the comfort and craft nodes.

*Opening:* Primitive Shelter · Primitive Cookery *(the stove — first core bench)* · Basic
Agriculture

*Middle:* Knapping *(the stone bench, and the shiv/shard weapon line)* · Firecraft &
Preserving *(drying rack, travel rations)* · Butchery *(the butcher bench)* · Hidework
*(tanning, the hide slab, tier-1 apparel)* · Herbcraft *(herb table, medicine production)*
· Slings & Clubs

*Closing:* Candlemaking · Pens & Troughs *(and the trough — first QoL hunt)* · Primitive
Artistry *(art bench, styling station)*

---

## 5. N2 — The Settled Tribe

### The narrative

You survived. Now you take root. **The First Wall.**

This is where the tribe stops being a camp and becomes a place. You learn to cure leather
properly, then to boil it, then to harden it — the same hides you have been wearing for
fifty days, worked three times better, and your fighters stop dying to the first raid. You
learn to build things that stop people: ditches, spiked lines, palisades, a gate made of
whole logs. You learn to throw a rock the size of a person at somebody else's palisade.

You learn masonry — real blocks, real bricks, real floors, cement that sets hard. You learn
to cook a stew instead of chewing a strip of dried meat, to mill grain into flour, to smoke
a haunch so it keeps through winter. You build a bath house and a stage, because a
civilisation that only survives is not a civilisation.

And you train birds to carry messages, so for the first time in the game **the world
exists**. There are other people out there and you can reach them.

By the end your tribe looks like Rome before the metal came: walled, disciplined, fed,
armoured in hardened leather, throwing javelins from behind a ditch. Everything except
metal.

And then somebody finds metal. **The First Ingot.**

### What the colony looks like

A palisade ring with a log gate and a ditch outside it. A catapult on the high ground. A
stone granary and a smoker. Fields big enough to need a scarecrow. A bath house with steam
coming off it and a stage next to it. A bird post with a keeper. Fighters in dark, hardened
leather with tall shields and javelins, and not one piece of metal on the map.

### Capabilities

| Category | What is added |
|---|---|
| **Armour — the headline** | The leather ladder. **Cured leather** → **boiled leather** → **hardened leather**, three real rungs on one material, plus laminated plate-of-leather torso armour, tall shields, and fur-lined cold gear. |
| **Weapons** | Hunting bow, longbow, war-grade recurve. Javelin, throwing axe, long spear, shortblade. Fire arrows, firebombs, smoke pots — an opt-in incendiary line for players who want it. |
| **Defence** | Trench, spiked line, stake wall. Palisade, palisade embrasures, log wall, log gate, reinforced gate. Brick and stone walls. |
| **Siege** | **The catapult.** First ranged siege capability in the game and a genuine "we can attack *them* now" moment. |
| **Stonework** | Masonry proper: blocks, bricks, kilns, cement, mosaic floors, the stone bench upgrade. |
| **Food** | Tier-2 plants and the scarecrow. Mill → flour. Grill, stew pot, oven and smoker as **augments on the same stove**. Food tier 3: any two vegetables plus any meat. Real meals with real mood value. |
| **Comfort** | Bath house. Stage. Heat stones and passive cooling — the first temperature control. A proper crematorium. Fur beds. |
| **World reach** | **Carrier birds.** Build a bird post, keep birds of any kind, and the mechanic opens. No paper, no cartography, no messenger table — research it, build it, own birds, done. Signal beacons for line-of-sight. |
| **Benches** | **No new core benches.** Every gain in this leap is an augment, a material rung or a structure. That restraint is what makes the forge land so hard in M1. |

### The research

*Opening:* Intermediate Agriculture · Cured Leather · Earthworks *(ditch and spike lines —
the cheapest defence, so it comes first)*

*Middle:* Stewcraft *(grill and stew pot augments)* · Milling & Baking *(the mill, flour,
bread)* · Smoking & Curing · Masonry · Cement & Structures · Boiled Leather · Palisades &
Gates · The Long Bow · Skirmishers *(javelin, throwing axe, tall shield)*

*Closing:* Hardened Leather · Laminated Armour *(the lorica rung — the best armour a tribe
can make)* · **Siege Engines** *(the catapult — QoL hunt)* · **Carrier Birds** *(the world
opens)*

*Optional, gates nothing:* Incendiaries *(fire bow, fire arrows, smoke)* · Baths & Stage ·
Dyes & Ceremonial Dress

---

## 6. M1 — The Forge

**The largest leap in the project.** Metal touches every domain at once, so this leap is
wide rather than deep — many rungs, each one shallow.

### The narrative

Metal. Everything you have built for a hundred days gets remade in it.

You build a smithy and you are immediately bad at it, so you research an anvil and get
better, then a bellows and get better again. Your fighters put down clubs and pick up
swords. Your armourers take the hardened leather they spent a whole era perfecting and
start **riveting metal scales onto it** — your Neolithic mastery is not thrown away, it
becomes the foundation the metal sits on.

You put down a real tailoring bench and for the first time make *clothes* rather than
hides. Your fields get big. Your kitchen gets eggs in it, which means the animal pen is now
a food supply chain rather than a novelty. You build an apothecary with an alembic and
start making medicine you would actually hand to someone you liked.

By the end you have men in scaled armour carrying metal weapons behind stone walls, eating
good food, wearing decent clothes. The place is popping.

### What the colony looks like

Smoke from a forge that never goes out. A tailoring bench with bolts of cloth stacked
beside it. Fields that need a second grower. A stone hall with proper beds and dressers in
it. A mine shaft chewing slowly through a hillside without supervision. Soldiers in scale
and gambeson with shortswords and round shields.

### Capabilities

| Category | What is added |
|---|---|
| **The forge** | **Fueled smithy** — the defining object of the era — plus its augments: anvil, bellows, grinding wheel, quenching trough, tool rack. |
| **Tools** | Pickaxe, mining tools, felling axe, building hammer, scythe, cleaver, bonesaw, mason's tools. Every job in the colony gets faster. |
| **Weapons** | Basic metal arms across all three families: shortsword, gladius, falchion, mace, heavy mace, throwing axe, hatchet, militia spear, warfork, hooked blade, flail. |
| **Armour** | **Scale and lamellar** — metal riveted onto the leather substrate. Round shields, simple helms, coifs, arming caps. Gambesons and padded chausses underneath. Heater and kite shields. |
| **Tailoring** | **Hand tailor bench.** Cloth working proper. Shirts, trousers, dusters, jackets, hoods, hats, parkas, robes, rugs. Silk enters as a straight cloth upgrade — no spinning chain. |
| **Furniture** | The rustic rung: real beds, dressers, end tables, shelving, hearths, braziers, dining sets, display cases. |
| **Food** | Tier-4: eggs enter, so husbandry becomes an input to the kitchen. Cold storage. |
| **Medicine** | Apothecary — herb table, alembic, vials, tinctures. Medicine production worth the name. |
| **Research** | The simple bench, with note and board augments. |
| **QoL** | **Mine shaft** — place it, forget it, mine slowly forever. The model citizen of the QoL class. |
| **Defence** | Brick and tudor walling, reinforced trenches, tank traps. |

### The research

*Opening:* **Smelting** *(the ingot itself — the era's first node and its most important)* ·
The Smithy · Metal Toolcraft

*Middle:* The Anvil *(augment; opens the arms line)* · **The Bellows** *(augment — QoL
hunt)* · Basic Arms · Scale & Lamellar · Padded Underlayer · Tailoring · Complex Furniture

*Closing:* Intermediate Cookery · Apothecary · **Deep Mining** *(the mine shaft — QoL hunt)*

Two hunts in the leap. That is the dose.

---

## 7. M2 — Mail & Siege

### The narrative

You know how metal works. Now you get good at it.

Mail. Every fighter gets a hauberk and a coif and splinted limbs, and raids stop being
frightening and start being *work*. Military-grade arms — longswords, pikes, bardiches,
morning stars — replace the basic set entirely. Ballistae go on the walls, and the walls
themselves become castle walls with gates and embrasures and murder holes.

Mills start doing work you used to stand there and do: a windmill and a watermill grind
your flour while everyone else is asleep. Your farms hit their final tier and your kitchen
gets cheese and flour, which is the point where food stops being fuel and becomes a stat
buff worth planning your whole agriculture around.

And an alchemist sets up in the corner making things that are frankly a bit suspicious.

### What the colony looks like

A castle. Not a metaphor — a stone curtain wall with a gatehouse, embrasures, and a
ballista on the tower. A watermill turning on the stream. Fields to the horizon. A workshop
row: forge, loom, mason's clamp, alchemy bench. Soldiers in mail with pikes standing a real
watch rotation.

### Capabilities

| Category | What is added |
|---|---|
| **Armour** | **Mail.** Hauberk, heavy hauberk, chain coif, kettle helm, nasal helm, flat-top, chainveil, bascinet, splinted limbs. |
| **Weapons** | Military arms: longsword, arming sword, bardiche, longaxe, pike, billhook, boar spear, spetum, swordlance, morning star, polehammer, winged mace, war pick. |
| **Ranged** | Crossbow, arbalest, war bow, wall-mounted arbalest. |
| **Siege** | **Ballista** and bolts. Wall-mounted heavy weapons. |
| **Architecture** | Castle wall, low wall, embrasures, castle doors and gates at three sizes, timbered walling. |
| **Production** | Forge furnace augment. Loom and spindle on the tailor bench. Chisel rack, clamp and carving board on the stone bench. Cheese press on the hearth. |
| **Food** | Tier-3 plants. Food tier 5 — flour and cheese, the top of the ingredient ladder. Fondue, ragout, real cooking. |
| **Automation** | **Windmill and watermill** — production that happens without a pawn standing at it. |
| **Alchemy** | Alchemy bench, cauldron, battle elixirs, stimulants, tonics, tar. |
| **Trade** | Jewelry bench and a full range of gemwork. Pure trade value, zero dilution risk — it is *supposed* to be sold. |
| **Research** | The scriptorium — the advanced bench. |
| **QoL** | **The crane** — mining and hauling speed, and it scales all the way to the end of the game. |

### The research

*Opening:* Advanced Smithing *(furnace)* · Military Arms · Mail

*Middle:* The Crossbow · Siege Engines II *(ballista)* · Castle Architecture · Loom &
Spindle · Chisel & Clamp · Advanced Agriculture · Millworks

*Closing:* Advanced Cookery · Alchemy · Scriptorium · Gemwork · **The Crane** *(QoL hunt)*

---

## 8. M3 — Plate & Powder

The smallest of the three, and the most ornamental. By now the player is leaning toward the
next era, so this leap is about *finishing* rather than expanding.

### The narrative

This is the top of the pre-electric world and it should look like it.

Full plate — articulated, fitted, gilded if you want it. Greatswords and zweihanders and
halberds carried by people who have been fighting for two hundred days and are finally
good at it. Your masons stop making walls and start making cathedrals: marble columns,
polished stone, royal furniture, heraldic banners over a throne room.

And that throne room matters more than it looks. You will still have it in three hundred
days, bolted to the deck of a ship in orbit, because you never tore it down. The furniture
you make here is the archaeological record of your own playthrough.

Your tailors make court dress. Your cooks make food that grants a serious combat buff. And
somebody works out what happens when you set fire to the right powder.

You have no electricity. You will not miss it for very much longer. **The First Spark.**

### What the colony looks like

A hall with marble floors and banners on the walls. Knights in full harness. A cannon on
the gatehouse. A cook making something out of berries that costs more than a suit of mail.
A throne at the end of the room with a harpsichord beside it.

### Capabilities

| Category | What is added |
|---|---|
| **Armour, rung 1** | Breastplate, brigandine, plate limbs, bascinet, sallet, klappviser, heater shield. |
| **Armour, rung 2** | Full harness, heavy plate, armet, great helm, hounskull, gilded variants, exotic scale. |
| **Weapons** | Greatsword, claymore, zweihander, dane axe, greataxe, fencing sword, noble sword, halberd, warhammer, flanged mace, fighting spear. |
| **Firearms** | Arquebus, musket, flintlock, hand cannon, wall-mounted arquebus, **cannon**. |
| **Heraldry** | Tabards, standards, standing banners, heraldic rugs. Your colony gets a *coat of arms*. |
| **Furniture** | Royal furniture, grand throne, display cabinets, master sculpture. Stone polisher and art tool stand augments. |
| **Apparel** | Court dress — noble and royal apparel, gowns, chaperons, formal wear. |
| **Music** | Harp, harpsichord, piano. |
| **Food** | The exotic tier and the top buff band. The most valuable meal in the pre-electric game. |

### The research

*Opening:* Plate Harness I · Noble Arms

*Middle:* Plate Harness II · Master Masonry · Master Tailoring · Heraldry · Royal Furnishing

*Closing:* **Gunpowder** · Grand Cookery · Courtly Music

**The plate line must be two rungs, not one.** A breastplate and a gilded full harness are
not the same achievement, and collapsing them into a single unlock throws away the entire
top of the armour ladder in one click — a direct violation of §2.3, at the most visible
point in the game.

---

## 9. What the previous pass got wrong

Recorded so it is not repeated.

1. **It relocated the Roman-flavoured content into the Medieval era.** Backwards. A
   stone-and-leather civilisation with engineering, discipline and siege *is* the late
   Neolithic — that is exactly the N2 fantasy. What has to go is the bronze, not the Rome.
2. **It treated a sketched point total as an approved budget** and cut content to hit it.
   The number was a sketch of a *structure*, never a cap. The shape wanted here is wider,
   not narrower.
3. **It read the Neolithic as a short intro.** The Neolithic is two full leaps and roughly
   40% of everything this document covers. The "short intro" is only the Awakening — the
   first half of the first leap.
4. **It cut on arithmetic instead of on design.** Items were removed because a total said
   so, not because they failed a test. §2 supplies the tests. Every future cut cites one.

---

## 10. Open questions

Narrative and taste only. Nothing here is a mechanics question.

| # | Question | Recommendation |
|---|---|---|
| **P1** | **How much Rome is visible in N2?** Bath houses, stages, ceremonial dress and lorica read unmistakably Roman against a dark-fantasy medieval M-era. | Keep them, but as **optional nodes that gate nothing**. A player who wants the austere version simply never researches them, and loses no capability. |
| **P2** | **Does the catapult belong in N2, or is siege a metal-era idea?** | N2. "We can hit them now" is the single best beat available in a leap that is otherwise about defence, and a rock-throwing engine is genuinely pre-metal technology. |
| **P3** | **Gunpowder as thrown incendiaries, or as firearms?** | Firearms. M3's beat is the first crack of gunpowder; thrown fire pots read as N2 content, and the incendiary fantasy is already served there by the fire bow. |
| **P4** | **Does M1 armour want to be scale-on-leather, or straight to mail?** | Scale. It makes the entire Neolithic leather arc *load-bearing* rather than superseded — your primitive mastery becomes the substrate for your first metal, which is a better story than throwing it away. |
| **P5** | **Should the four moments get real in-game presentation** — a letter, a ritual, a Chronicle beat — rather than just a completed research project? | Yes, and this is the cheapest narrative win in the project. The First Ingot in particular should not arrive as a progress bar quietly filling. |

---

## 11. What happens next

Two passes, in order.

**Pass A — sourcing.** Lay this target against everything available across the loaded mod
set and the base game, and decide for each capability line where the asset comes from:
already exists as wanted, exists and needs restatting, exists as art only and needs
rebuilding, or has to be made. Assume nothing is off limits.

**Pass B — bucketing.** Everything in the live database that does *not* map to a capability
line in §3–§8 goes into the four buckets: keep as is, keep with changes, on the fence, not
keeping. Every verdict cites either a §2 rule or a specific capability line. A cut with no
citation is a cut made on arithmetic, which is the mistake that produced the last pass.

Balance — costs, durations, buff magnitudes, gating weights — comes after both, and only
after both.
