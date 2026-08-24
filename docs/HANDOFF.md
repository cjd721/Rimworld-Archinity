# Handoff

**Read this before starting anything.** `CLAUDE.md` points here for open decisions and this
file did not exist until 2026-08-23. Everything below is either waiting on Conrad or waiting
on someone to do it.

Detail lives elsewhere: `VISION.md` for intent, `sys/NN-*.md` for workstreams,
`sys/08-progression-recon.md` for the Progression Modpack teardown, `technical-findings.md`
for anything verified against decompiled source.

---

## Open decisions — need Conrad, do not resolve unilaterally

Carried from `VISION.md` §Undecided:

1. **How much of the starting xenotype to strip.** Partly decided — `Deathrest` and
   `XenogermReimplanter` are out and both removals are load-bearing. How many remaining
   archite genes move into the quest chain is open. Last word: *"I'm gonna give a few more
   upfront,"* and settle it **after** the quest cadence is fixed. Every archite gene is
   annotated `<!-- [ARCHITE] -->` so the split stays mechanical.
2. **Faction diplomacy and ideology across the world map.** Flagged at world creation,
   untouched since.
3. **Whether to buy Anomaly.** Paid DLC, his call. Nothing else in the load order supplies
   eldritch or reality-warping content, and void material fits "the universe is a
   simulation" better than anything available. Vanilla Psycasts Expanded is declined, so
   VRE-Archon's `VREA_Transcendent` psycaster path stays permanently dormant — accepted,
   not an oversight.

New, from 2026-08-23:

4. **Node Research or TechBlock — not both.** `Node Research` (`3729878405`) cannot coexist
   with any other research-tree mod, and its foundation-node gate replaces TechBlock's
   capstone. It solves the 101-node legibility problem and already implements two decisions
   `VISION.md` reached independently (disables VFE-Tribals' ritual advancement, grants a
   Cornerstone point on era advance). Against it: **MP compatibility unverified in either
   direction**, and its per-era costs are flat constants where TechBlock's scale with the
   era's project count — better for us while the node count is still moving. Needs an MP
   smoke test before it can even be considered.
5. **Vanilla Weapons Expanded — in or out?** Nine N1 weapons in `progression-map-v2.html`
   have no asset in the load order (shiv, shard, hand axe, throwing shards, sling,
   sling-staff, light and heavy club). VWE supplies the whole set and fixes Toolmaking,
   The Sling and Knapping in one move. The alternative is authoring nine weapons.
6. **Keep `Dark Ages: Medieval Tools` for the crane?** `sys/01` recommends dropping the mod
   (11 things, zero research). It is the **only** source of the medieval crane, which is the
   longest-tailed QoL reward in the design. Keep the mod, lift the asset, or cut the node.
7. **The trough — author C# or redefine the benefit?** Nothing in the load order reduces
   animal food consumption and there is no vanilla stat for it, so as specified it needs
   Harmony. That means a second assembly or an addition to `Archinity.Altar`, which
   `CLAUDE.md` forbids without an explicit decision. Cheapest honest alternative: redefine
   the trough as something a `CompProperties_Facility` or a storage building can express.

---

## Action list — 2026-08-23

Ranked. Nothing here is blocked on anything else except where noted.

- [ ] **Ship our ModSettings as a mod.** The `Fernys-Mod-Configs` (`3256902751`) pattern:
      bake `config/ModSettings/` into a versioned artifact instead of re-snapshotting by
      hand. Turns the multiplayer footgun `CLAUDE.md` calls *"the one people miss"* into
      something git tracks. **Cheapest real win available — do this first.**
- [ ] **Granularity gut-check on the 101 nodes.** One pass, one question per node: *does
      this earn a project, or is it clutter with a name?* Progression draws a "too granular"
      complaint from its own players with 843 mods spread across six eras; we have 101 nodes
      across two. Prime suspects: The Trough, The Sling, Candlemaking, The Dye Vat.
- [ ] **Adopt "rename the stub, don't delete it" into `CLAUDE.md`.** When a research project
      is gutted down to one remaining unlock, rename and repurpose it rather than deleting
      and re-parenting. `Progression: Agriculture` does exactly this (MO's "Basic
      Agriculture" → "Planter Boxes"). It sidesteps the documented re-parent → neuter →
      delete trap entirely.
- [ ] **MP smoke-test Node Research.** Blocks open decision 4. Zero `Multiplayer` references
      in its source; it mutates `Faction.def.techLevel` and `DefDatabase` inside a
      `ResearchManager.FinishProject` postfix — plausibly deterministic, unconfirmed.
- [ ] **Evaluate `[SR]Factional War (fork)`** for the faction-demand requirement. Factions
      fighting *each other* on and near our map is the load-bearing half of
      `rimworld-design-philosophy.md` §7.1, and it is confirmed to exist.
- [ ] **Evaluate `Story Framework`** — pure-XML mission and objective authoring, no C#
      assembly. The only candidate found for authoring the Chronicle under the one-assembly
      rule. Not confirmed in Progression; stands on its own.
- [ ] **Verify VFE-Tribals' ritual tech-advancement is actually suppressed in our build.**
      `VISION.md` says it is disabled and TechBlock is the single lever. Node Research ships
      a dedicated patch to do this, which implies it does not switch itself off. Confirm
      ours does.
- [ ] **Do not take ferny's code.** ~119 repos, **no LICENSE file found in any checked**.
      Publicly readable ≠ licensed. Read the technique, write our own, ask if we want more.

### Lower priority, same session

- [ ] Consider a ceremonial full-screen beat at era boundaries — steal Progression's
      presentation, keep our four named moments as the text. They ship generic strings for
      all six eras; the presentation is the reusable part.
- [ ] Look at `Lemmy's Progression Mod For World Tech Levels` (`3548896697`) — map factions
      tech up over time via faction-def substitution. Makes the world age forward instead of
      freezing at spawn tier.
- [ ] Architect-category splitter mods (11 small XML mods, no save state, ~zero MP risk) and
      the MP-verified QoL set: `LWM's Deep Storage` (`1617282896`), `Dubs Mint Menus`
      (`1446523594`), `Work Tab`, `Pick Up And Haul`, `Common Sense`, `Performance Fish`.
- [ ] A `Consistent-Text`-style XML pass over our own and MO's defs — capitalization,
      terminology, and stripping meta references out of flavour text.
- [ ] **Avoid `Pawn Editor`** (`3219801790`). The Progression maintainers themselves say to
      avoid it: duplicate pawn IDs, upstream developer gone. Save-integrity risk before it
      is a desync risk.

---

## Pending corrections to `progression-map-v2.html`

Found after the doc was committed (`fd11ac3`). **Conrad asked that no edits be made yet** —
these are queued, not done.

- [ ] **Deep Mining card is wrong.** It claims the mine shaft "produces ore forever with no
      pawn assigned." `DankPyon_MineShaft` is `Building_WorkTable` with `ITab_Bills` — a
      pawn stands there and runs a mining bill. The card's argument for the whole QoL class
      rests on that false claim. Either convert the building to a `ThingProducer`-style
      comp, or rewrite the card to claim what it does: *mine without a mountain*, not
      *without a pawn*.
- [ ] **Milling card is wrong.** It says the mill is "a place, not a bill."
      `DankPyon_Millstone` is `Building_WorkTable` + `ITab_Bills`. The corrected version is
      a better story: the hand mill **is** a bill, and Millworks is the node that deletes it.
- [ ] **Grinding Wheel card invents a mechanic.** "Weapon sharpening as a standing job" does
      not exist. `DankPyon_Grinder` is `CompProperties_Facility` with
      `<WorkTableWorkSpeedFactor>0.04</WorkTableWorkSpeedFactor>` — a passive stat offset.
      The rest of the card is accurate.
- [ ] **Add the wheat/windmill hazard as a design note.** Processor Framework has **no
      quantity setpoint** — `WorkGiver_FillProcessor.HasJobOnThing` stops only when the box
      is full or no allowed ingredient remains on the map. A windmill with wheat in its
      filter will grind the entire grain stock into flour. Either keep the hand mill's bill
      as the controllable path, or make flour rather than wheat the storable form.
- [ ] **Put `targetQuality` into the food ladder.** Processor Framework's `Command_Quality`
      is a genuine declarative setpoint — leave the cheese longer, get better cheese. It is
      already implemented and unused by our design. Natural fit for Grand Cookery.
- [ ] **Add a §03 note naming the two real mechanisms** the bench system rests on:
      `ProcessorFramework.CompProperties_Processor` (haul in → timer → haul out, no bill;
      15 MO buildings use it) and vanilla `CompProperties_Facility` (every augment).
- [ ] Add the mine shaft and millstone to §06 tagged `restat`. They were specifications
      written in the indicative mood, which is the same error class v1 made.

---

## Notes for whoever picks this up

**"No bills" means two different things and the v2 doc conflates them.** For
Processor-Framework buildings it describes real behaviour. For the mine shaft and millstone
it was a spec written as a description. A processor gives you *less* control than a bill,
not more — a bill has `repeatMode: TargetCount`, a processor has nothing equivalent.

**Progression's conclusion, in one line:** they prune research projects, they never prune
content, and they never authored a story. Our route stands on two things they structurally
cannot provide — two-player multiplayer, and an authored campaign. If either stops
mattering, the honest answer flips. See `sys/08-progression-recon.md`.
