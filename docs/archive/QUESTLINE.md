# The Chronicle — working model

**Nothing here is law.** This is a session seed: the current working model, the
reasoning behind it, and the questions still open. It replaces the sixteen-beat
outline, which is preserved at commit `84fb5e0` and still holds useful detail on
beat-level content.

Read `VISION.md` first. This document assumes it.

Every item is marked:

- **[SETTLED]** — agreed, safe to build against.
- **[MODEL]** — current best thinking, not a decision.
- **[OPEN]** — needs Conrad, do not resolve unilaterally.
- **[VARIABLE]** — deliberately unpinned until the research/pacing study lands.

---

## 1. The shape of the story

**[SETTLED]** The altar's meaning per era is unchanged from `VISION.md`: an
object in the Neolithic, a rite in the Medieval, a machine in the Industrial, an
instrument in Spacer/Ultra, a door in the Archotech.

**[SETTLED] Every beat is a site you travel to.** No drop-pod rewards anywhere in
the chain. You go, you fight something, you take the thing home.

**[SETTLED] Rhythm: big site → several small and medium sites → big site.** Each
act opens or closes on a large complex and fills its middle with single rooms and
vaults of varying difficulty.

**[SETTLED] Pacing is denser than the sixteen-beat draft.** More beats, most of
them small. Travel, a short fight, one room. The prior draft's ~45–50 day gaps
were too long — a full year between beats means the player has forgotten the
altar exists.

### Act I — Neolithic, three beats **[SETTLED]**

1. **The altar.** A large overground ancient complex, deserted or very lightly
   guarded — one Archonian can clear it. Inside: the altar, and wall depictions
   of blood sacrifice. No instructions, no text, no explanation. All the player
   knows is that this has something to do with the power they were given.
2. **A small site.** A teaser. Gives capsules and no answers. Skippable at no
   real cost.
3. **The first vector.** A small site. The moment the machine becomes real.

**The gap between beats 1 and 2 is doing real work and is not a beat.** The altar
accepts fuel from day one, so the player feeds it and nothing happens. They will
assume they are doing it wrong. That silence is the Neolithic experience and it
costs nothing to build.

### Act II — Medieval

Small and medium sites through the middle. **[SETTLED]** The act closes on the
Archon encounter:

> A large religious site. A broken, uninteractable altar with an Archon inside
> it. Open it and he falls out, tells you something, encourages you further down
> the path — then uses his Transcendent gene to phase into another universe and
> is simply gone. You loot the ruin afterwards and find a vector among the
> wreckage.

This is the act break into Industrial and the strongest beat in the outline.

### Acts III–VI

**[MODEL]** Same pattern, not re-drafted this session. The prior outline's beat
content for Industrial through Archotech is still the working reference.

---

## 2. Sites available — verified

All of this survives killing VQE's questline, because only the scheduling
extension is being removed, not the content.

| Layout set | Count | Shape | Use |
|---|---:|---|---|
| `VQEA_AncientOvergroundComplex_1..12` | 12 | Surface complex | Big religious sites — act openers and closers |
| `VQEA_VaultLabModules` + `VQEA_SealedVault` | — | Underground, behind a locked vault door and ramp | Medium beats |
| `VQEA_SidequestLabModules_1..10` | 10 | One small lab room | The small beats |

Six `SitePartDef`s ship with difficulty flavour already written: *abandoned* /
*dangerous* / *infested* / *reconnaissance* / *array* / *research vault*. Two map
generators: `VQEA_AncientComplex` (overground) and `VQEA_SealedVault`.

---

## 3. Who can use the altar — **[OPEN]**, and the most important open question

**The constraint** *(restated, because a proposal was rejected this session for
violating it)*: the two founders must stay **extra special permanently**.
Ordinary colonists should become special *slowly, over time*, but must never
reach what the founders are. Two chosen ones who can mint copies of themselves
are not chosen.

### Settled: the marker

**[SETTLED]** A custom gene identifies the founders. Working names: **Chosen of
Archinity**, **Child of Archinity**, **Seed of the Archons**. A plain endogene on
the starting xenotype, `biostatArc 0` so it can never appear in the lottery, with
no mechanical effect of its own. It exists to be keyed off.

Rejected alternatives, with reasons:

- **The absence of `Deathrest`** — means nothing on a pawn that would never have
  had it, so it cannot serve as a general key.
- **`Deathless` / `Ageless`** — every vanilla sanguophage has both. Not a
  distinction, and not ours to touch.

### Rejected this session

**"The Descent Engine lets you make more Chosen."** Reimplantation would copy the
founders' xenotype onto converts and the altar's rule could stay "Chosen only"
forever — mechanically clean, but it is exactly the copy-minting the campaign
exists to prevent. Do not revive it.

### Two candidate models **[OPEN]**

1. **Two altars.** One reserved for the Chosen — the key piece, the campaign
   centre. A second, lesser one for ordinary colonists. Costs the *one machine,
   one philosophy* principle, which was previously load-bearing.
2. **One altar, split by ammunition.** Named gene vectors only ever work on a
   Chosen. Archite capsules — the lottery — work on anyone. The founders get
   deterministic, chosen, escalating power; everyone else gets the dice.

Model 2 preserves one machine and draws the founder/colonist line along the
vector-versus-capsule axis that already exists in the design. Neither is decided.

---

## 4. Vectors versus capsules

**[SETTLED] Named vectors never fail.** You travelled, you fought, you paid a
life — you get the gene. `VISION.md` already says this: uncertainty about *how
well* is acceptable, uncertainty about *what you are getting* is not.

> **Defect.** `Building_Altar.PerformRite` currently rolls a flat 25% critical
> failure on named vectors. That contradicts the stated design and should be
> removed. All risk belongs on the capsule path.

**[SETTLED]** Coma and spent blood remain the downside — they move to the
lottery, where the player opted into a gamble.

**[OPEN] When do capsules become usable?** Conrad leaned toward Industrial,
alongside ordinary colonists gaining access. The counter-argument is that
capsules on the founders from the Neolithic are the *between-beats loop* — the
answer to "how do I make my Archonians stronger right now" — and without it the
altar is untouched between quest beats for 400 days, which is the dead-air
problem in a different costume. Capsules are trade-and-loot only, so early rolls
are rare enough that each is an event. Unresolved.

---

## 5. The lottery

**Nothing of this exists in code.** `CanAcceptPawn` refuses any recipient when no
vector is loaded, so today an archite capsule is an inert item. This is the
largest unbuilt surface in the project and it now drives several beat placements.

**[SETTLED] The draw pool is not archite-only.** It includes a curated selection
of the best *and worst* ordinary genes. A poor roll should offer a couple of
genuinely bad options and one or two merely okay ones, none of which you want.
That is the price of gambling, and it is what makes the augmenting buildings
matter.

Consequences:

- `GenePool_Archite.xml` is archite-only — 50 genes, hand-tiered 1–5. It needs a
  second curated section. The load order carries Biotech plus VRE Sanguophage,
  Waster, Saurid, Archon, Hussar and Starjack: several hundred candidates. **This
  is its own authoring pass.**
- **[OPEN] Can the player decline all four options?** This decides whether the
  bad band has teeth. Bad genes are effectively permanent — vanilla has no clean
  single-gene removal. If you can decline, a rational player always declines and
  the band collapses into "wasted capsule." If you cannot, a dice roll
  permanently disfigures a founder, which trips the *never lose a good pawn to
  RNG* rule. Suggested compromise: **you may decline, and the capsule and the
  blood are spent anyway.**
- **[MODEL]** Reskin the **Aberration Redirector** — natively "choose between two
  negative side genes" — into **gene removal**, unlocked late. Early you live
  with your mistakes; late you can undo them. Gives the bad band teeth without
  permanence.
- **[MODEL]** `Archinity_ArchiteSustenance` applies a flat `hungerRateFactor 0.5`
  to anyone who has used the altar. Most genuinely bad ordinary genes are bad
  *via* metabolism, so this would quietly cancel the downside being introduced.
  It probably needs to cancel archite metabolism specifically rather than all
  hunger.

---

## 6. Progressive unlocks of the machine

**[MODEL]** The altar's capability opens in stages rather than arriving whole:

| Era | Unlock |
|---|---|
| Neolithic | Fuel and named vectors |
| Industrial | Ordinary colonists and/or capsules — exact split **[OPEN]**, see §3–4 |
| Spacer | **You can see the actual roll percentages** and how your linked buildings changed them |

The percentage reveal is `VQEA_SpliceframeUplink`: *"Reveals all outcome chances
in the archogen injector and slightly increases the odds of mutation outcomes."*
Keep both halves — you finally see the truth, and looking at it makes things
slightly worse.

**Knock-on:** the prior outline assigned the Spliceframe Uplink to the Descent
Engine. Moving it to Spacer leaves the hinge without a building, so **[MODEL]**
the Descent Engine takes the **Archogen Injector** instead. Its native function
is literally injecting archites into ordinary humans, it is the most visually
important building in VQE's set, and reskinning it removes the rival machine by
absorbing it — nothing currently stops the injector being claimed from a
generated vault and used as a second path to the same goal.

---

## 7. The thirteen buildings

**[SETTLED]** Unique buildings are core-quest milestones. Stackables are ordinary
and side-quest rewards, and may also appear in main beats. Split read from
`maxSimultaneous`.

### Stackable — five

| Def | Max | Role |
|---|---:|---|
| `VQEA_NeurostabilizerArray` | 10 | Improve the odds |
| `VQEA_RapidInfusionPump` | 9 | Speed |
| `VQEA_CognitiveRecoveryArray` | 6 | Shorten the coma |
| `VQEA_RejectionBufferCoil` | 5 | Reduce the penalty |
| `VQEA_GenomicAttenuator` | 4 | Reduce the blood cost |

> The sixteen-beat draft listed only four stackables and placed the Attenuator as
> a unique Ultra milestone. It is capped at 4 and is stackable.

**[MODEL]** Award **one** at first introduction, not three. The lesson is
"buildings change the altar"; three at once, before the player knows what the
altar does, teaches nothing.

### Unique — eight

Seven linkable facilities plus `VQEA_AncientBioBattery`, which is **not** one of
the twelve `linkableFacilities` and is the thirteenth building: Rendering Vat,
Galvanic Coil, Reliquary Sump, Descent Engine, Prism, Redirector, Harmonizer,
Pathing Array. Assignments are in flux — see §5 and §6.

---

## 8. The founders — **[OPEN]**

- **Why two rather than one?** One god ruling the colony for the whole
  playthrough is a real alternative and has never been examined.
- **Does a vector serve one founder or both?** One vector and a choice creates a
  decision on every beat and lets Adam and Eve diverge into two different gods
  over 700 days. Two vectors keeps them symmetric at double the blood.
- **Is Transcendent one vector or two?** Fifty lives or a hundred — or only one
  of them walks through the door at the end.

---

## 9. Held as variables — do not pin yet

- **Days between beats.** Pending the research and pacing study. Changing them is
  a cheap edit once real progression rates are known.
- **Which gene at which beat.** Pending the same, plus the decision on the total
  set of genes the player should end with.
- **All power-curve numbers.** The table below is the balance reference, not a
  target.

| Era | Failure chance | Listed cost | Effective cost |
|---|---:|---:|---:|
| Neolithic | 25% | 1 | 1 |
| Medieval | ~19% → ~15% | 2–3 | ~1.5 |
| Industrial | ~11% | 4 | ~2 |
| Spacer | ~7% | 6–8 | ~3.5 |
| Ultra | ~2% | 12–20 | ~6–9 |
| Archotech | ~0% | 50 | ~23 |

**Risk falls monotonically while cost rises superlinearly.** By the Ultra era the
altar can barely fail and the body count is at its highest. Efficiency never
means mercy; it means scale.

---

## 10. Decisions carried in from this session

**[SETTLED] Kill VQE Ancients' questline by removing the `QuestChainExtension`
modExtension from all six quest defs.**

> **Trap.** Removing the *trigger* does the opposite of killing it.
> `GameComponent_QuestChains.TryScheduleQuest` ends by falling through to
> `quest.CreateQuest()` when no condition matches — so stripping
> `conditionMinDaysSinceStart` fires the quest on day 1. Deleting the root def
> alone is worse: the other five name it in `conditionSucceedQuests`,
> unresolvable cross-references are omitted rather than nulled, their lists go
> empty, and all five fall through and fire at once. Removing the extension is
> the only clean kill — `QuestsInChains` filters on the extension being non-null,
> and `rootSelectionWeight` defaults to 0 so the storyteller cannot pick them up
> either. Both verified against the decompile.

**[SETTLED] No custom storyteller is needed.** Chain quests call `CreateQuest()`
directly and bypass the storyteller entirely, so Chronicle's pacing is already
fully under our control. A storyteller would only suppress *competing* quest
noise, and the cheap lever for that is quest incident frequency and
`rootSelectionWeight` patches. Not worth a second assembly.

**[SETTLED] No work-suitability, combat, or psycast genes as named vectors.**
Better genes exist, and leaving them in the lottery means they can be declined
rather than forced.

---

## 11. Defects found this session

1. **`archinity.altar` is not in `config/ModsConfig.xml`.** The mod is built and
   committed but not in the load order, which is why it has never loaded in game.
   Everything in this document depends on it.
2. **All four DLCs are listed twice** in `ModsConfig.xml` — Royalty, Ideology,
   Biotech and Odyssey. Harmless in practice, but configs must match byte-for-byte
   between both players.
3. **Named vectors roll a 25% critical failure**, contradicting `VISION.md`. See §4.
4. **`VQEA_AncientBioBattery` cannot link to the altar.** It has no
   `CompProperties_Facility` and is absent from the altar's `linkableFacilities`.
   Two patches.
5. **Eight of the thirteen building effects have no field to express them.**
   `AltarFacilityExtension` covers `chargeCostFactor`, `durationFactor`,
   `outcomeBonus`, `biasCategory`, `biasStrength`, `extraOptions` — and nothing
   else. The Vat, Sump, Descent Engine, Shroud, Redirector, Harmonizer and
   Pathing Array all need new fields. That is an assembly pass, not a patch.

---

## 12. Where the next session should start

The lottery, §5. It is the largest unbuilt surface, it is the founders' only
between-beats interaction with the altar, and its shape now determines several
beat placements. Settling §3 (who can use the altar) and §4 (capsule timing)
unblocks it.

Do not rewrite the beats until those land — they will move.
