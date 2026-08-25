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

New, from the 2026-08-23 evening design session:

8. **Augment sunset vs. augment sprawl.** Conrad's position is that era-specific augments should
   be *deprecated* at a bench upgrade — see the bench block below. He then read the counter-argument
   (compactness bought by giving up augment sprawl is a legitimate dependency trade) and called it
   "not a bad point at all." Left genuinely unresolved. It decides whether a spacer kitchen is one
   grav table or a hall of augments, and it is cheap to reverse only before the augment set is authored.
9. **Is the Cult ally, antagonist, or player-determined?** His words: *"We can determine that or let
   the player choose."* Leaning player-choice. Affects whether one branch or two needs authoring.

New, from the 2026-08-24 faction investigation:

10. **Supersedes decision 4 — there are now THREE candidate progression gates, not two.**
    `TechBlock` (active in `ModsConfig.xml`), `Node Research` (decision 4), and **`World Tech Level`**
    (`3414187030`, m00nl1ght), which arrived in the 2026-08-24 download batch and is the
    best-written of the three: a scribed tech level mirrored to a static, ~60 patches filtering
    research, gear, pawns, quests, raids and world-gen against it, zero `System.Random`, and
    `Rand.PushState((int)def.index)` in world-gen so results are reproducible. MP-clean apart from
    one unsynced planet-tab float menu. They cannot coexist. Decide once.
11. **Where does the faction ledger and the Chronicle clock live?** Both are deterministic
    components with no runtime randomness, and `CLAUDE.md` forbids a second assembly without an
    explicit decision. Recommendation: they go in the existing assembly, and it is renamed —
    `Archinity.Altar` stopped being only about the altar. Renaming a shipped assembly has save
    implications; check before doing it.
12. **Vanilla Psycasts Expanded reverses a documented decision.** `VISION.md` records VPE as
    declined and `VREA_Transcendent`'s psycaster path as *"permanently dormant — accepted, not an
    oversight."* Conrad has now added VPE plus the **Hemosage** and **Puppeteer** addons, calling it
    *"insanely cool"* and noting the founders can have a **talent point tree** that levels alongside
    genes and skills. He flagged it *"probably needs a lot of pruning"* and *"noted for later."*
    `VISION.md` §Undecided item 4 and the §Explicitly rejected list both need updating. Its real
    significance: it is a candidate answer to the 400-day dead-air problem — a between-beats
    progression track for the founders that is not the gene lottery. Hemosage lands on the blood
    theme with no reskinning.

---

## Design session — 2026-08-23, evening

Conceptual pass with Conrad on the first two eras: main-story quests, the world, and the colony
map. **Nothing here is built and nothing is a def change yet.** Marked `[CONRAD]` where he decided
it, `[PROPOSED]` where it is an unruled suggestion, `[VERIFY]` where it rests on an unchecked fact.

### The implementation constraint, restated

`[CONRAD]` **"No C#" was never the real rule.** His framing: *"I don't give a shit how we do it,
so long as it's the most simple and elegant solution that actually achieves the goal without
violating constraints."* The actual constraints are **desync** (unsynced `Rand`, per-client cached
state), **save integrity** across a months-long two-player run, and the one-assembly rule.

Working test for any proposal: *does this need a random number or a client-local cache?* If no,
code is cheap — GameComponents, stat parts, ITabs, inspect strings, letters and synced designators
are all free. If yes, think hard or push it into XML. The expensive thing was never writing the
code, it was debugging a desync in a live co-op session.

`[PROPOSED]` This probably wants promoting into `CLAUDE.md` eventually. Not done — he asked for
HANDOFF only.

`[CONRAD]` Every idea gets assessed on two axes: **narrative emotion** and **mechanical
implementation**, and implementation is the **first gate**. Only consider what can actually be built.

### QoL "hunts" become faction quests

`[CONRAD]` The v2 QoL-hunt class is re-framed. Not *"go and fetch a thing"* but **"do this for us
and we will teach you about X."** The research unlock is the **quest reward**, not a research
prerequisite — so no research gating is needed at all. It doesn't matter *who* you ally with, but
you must ally with **someone** to progress far enough to collect these nodes. This is also the
vehicle for fleshing out faction engagement generally: the world matters for more than raids and
stock lists.

`[PROPOSED]` **Make the ask itself the antagonism.** If A's teaching quest is "hit B's caravan" or
"hold this against B," completing it antagonizes B automatically. No goodwill tax, no exclusivity
bookkeeping, no artificial scarcity — and whoever you burned determines what doctrine you must
build against, which makes the per-faction fighting-style tension real rather than decorative.

`[VERIFY]` **Techprints are the candidate native mechanism.** Vanilla `ResearchProjectDef` appears
to carry techprint fields — an item that gates *starting* a project, faction-scoped, tradeable and
quest-rewardable. That is exactly "someone taught you this," and if it works as believed it is pure
XML. **Must be checked against decompiled source before anything leans on it.** Pair with More
Research Requirements (already loaded) for material cost, giving two distinct gate flavours:
*someone taught you* vs *you practiced it*.

`[CONRAD]` **Study the Royalty Empire questline and the Vanilla Expanded Empire mod** for the best
implementation pattern before authoring anything.

### The Cult — our parallel obligation path

`[CONRAD]` Loved, and it replaces a straight Royalty reskin. The shape:

**A faction that exists *because* of you.** Two visible gods in your colony; your own pawns worship
them; word spreads and a pilgrim body forms out in the world. This is the existing premise scaled
past your own tribe, so it needs no new fiction.

Royalty's obligation machinery reflavoured: they want the gods **seen**. The throne room becomes a
temple or reliquary the founders preside over; they want pilgrimages received, relics housed,
appearances made. Standing buys the **non-material** things `rimworld-design-philosophy.md` §7.4
asks for — a loaned specialist, a granted site, safe passage, tech transfer.

`[CONRAD]` **Why this beats the Empire, in his words:** the Empire are tyrants who *"demand of me
all day as if I'm a lowly weasel."* Here the obligation arrives **through worship** — the people
worship you and that is what brings the responsibility. Same mechanical outcome, opposite emotional
lens.

`[PROPOSED]` **The cult supplies the altar.** Pilgrims come wanting to be near the gods, and the
altar eats people. Early it is a handful of volunteers and reads as grace; late you are consuming
hundreds and eventually somebody notices that pilgrims do not come back. One system doing worship,
logistics and horror at once — genuinely bidirectional, with its own failure mode, which almost
nothing else in the design has. It also solves the altar's late-game sourcing problem honestly:
`VISION.md` currently implies manual raiding, abducting and buying, and a faction that *delivers*
is both easier to play and considerably worse morally.

`[CONRAD]` Ally or antagonist falls out of how you treat them and what they discover — one system,
two branches, no double authoring. See open decision 9.

### Benches — v2's L1 is wrong as written

`[CONRAD]` Several corrections, and one of them contradicts a stated law in
`progression-map-v2.html`. Recorded here; **no edits made to that file.**

- **Recipes come from research, not from augment presence.** If you have unlocked it, the bench can
  make it. It is also unknown whether a bill can even be gated on a linked facility — and it should
  not be regardless, because an invisible gate produces "why can't I make this."
- **Consequence:** augment persistence stops being structural. Nobody can ever lose a *recipe*, so
  losing an augment costs a bonus, not a capability. The promise the player must trust becomes
  *"research is permanent,"* which they already believe.
- **Visual tier progression matters and was under-weighted.** *"I don't want to see a damn rock with
  a hammer as my crafting bench all game."* Benches do get real ThingDef upgrades that look like
  the era.
- **Augments are deliberately sunset, not carried forever.** This directly contradicts **L1**
  (*"every augment bolted to it carries across every upgrade"*). The intended shape: a new bench is
  **as fast as the old fully-augmented bench**, accepts only **1–2** legacy augments, and has its
  own new augments to push further. Era-specific augments are meant to be deprecated. His worked
  example: if five industrial augments give +100%, the next tier's bench starts at +60% and two
  surviving augments bring it back to 100%. Judgement call per item.
- `[PROPOSED]` **All augments should be multiplicative on the bench's base, never flat constants.**
  A +4% grinding wheel is meaningful on a fueled smithy and invisible beside a grav table. This is
  L4 (a thing must evolve with the player) applied to bonuses rather than to resources.
- **Grav tables** — mods now in the load order add compact versions of every bench type. Their base
  throughput must be balanced against *previous tier plus augments*, or the player ends up with a
  hyper-advanced alchemy table next to a dusty wooden lectern. Theme disconnect, not a stat problem.

### The one-bench rule was overstated

`[CONRAD]` The real intent is **"don't give me more shit to manage if it neatly fits into what I
already have to manage"** — subjective, which is why it got written as a harsh rule.

`[PROPOSED]` The sharpened version: **the constraint is on distinct bill tabs, not on building
count.** Two identical hearths is not more to manage; two different buildings with two different
recipe lists is. So the parallel-work hole Conrad identified closes by itself — a large colony
builds three hearths and a forge hall with three forges, parallelism comes free, and scale becomes
*visual* instead of becoming a menu problem.

`[PROPOSED]` Facility **link limits and radius** then become the interesting constraint: expanding a
kitchen means laying out a workshop rather than queueing more bills. A one-time spatial decision
with a visible payoff, not a recurring chore. This is free tuning on numbers we are already setting.

### The founders

`[CONRAD]` **No hard founders-only rule for Chronicle beats.** Proposed and rejected. They are a
free narrative anchor and deserve special consideration, but *"assuming they'll always be crushing
challenges solo is a big mistake"* — if he wants to send an army on a quest, he can, and the player's
use of them cannot be anticipated. The design principle instead: **challenge them, and punish
cowardice and greed alike.**

`[PROPOSED]` Levers that work regardless of party composition:

- **Haul weight** — the founders can carry themselves, not a vault. A real haul needs bodies, so a
  greedy run wants an army, and an army is ordinary pawns who can actually die. That is the stated
  target experience in `VISION.md`, not a failure state.
- **Opt-in depth** — a section past the main room with visibly better loot behind a real danger
  jump, committed to knowingly. Same shape as the archite-injection roll he liked.
- **Faction flavour text** does party-composition variety for free — some asks come with *"come
  quietly,"* others with *"bring your war band."*

### Travel, and the Chronicle's distances

`[CONRAD]` **Long caravan trips are boring, full stop.** *"If you make me take my two god pawns for
6 days I basically hit fast forward and watch TV."* **Vehicles in the Industrial era are what
actually open the map.** A trip-duration cost lever was proposed and is **dropped**.

`[PROPOSED]` **Distance scales with the era's mobility, not with the beat's importance.** Neolithic
and Medieval beats sit two or three tiles out — which is not a compromise but the premise: the
Archons seeded this place and put the thing there *for you*, so of course it is close. Industrial
vehicles then genuinely open the map and beats can be far, because by then crossing distance is the
fun part rather than the tax.

`[PROPOSED]` Two supporting moves. **Not every beat needs to be a world-map site** — some can
surface on the home map (dig into something, something opens). Same verb, one room, no travel, and
it varies the rhythm. And when the party *is* away, **the quest should put something at home on a
timer**, so the trip is a split-attention problem rather than a fast-forward. That is what leaving
costs now that duration is not carrying it.

### Carried proposals not yet ruled on

`[PROPOSED]` **Gate Chronicle beats on state, not on days.** Tech era + altar state + a day floor to
stop beats stacking, owned by a small deterministic `GameComponent` in `Archinity.Altar` that fires
XML `QuestScriptDef`s by name. Retires the "days between beats" variable in `QUESTLINE.md` §9 —
converts it from a number into a floor — and makes every beat arrive when it is *meaningful* rather
than when the calendar says so, which is `VISION.md`'s timing principle done structurally. It may
also retire the **Story Framework** evaluation on the action list: if the altar is the state machine,
no mission-authoring dependency is needed.

`[PROPOSED]` **Fix the 400 days of dead air with speech, not with a mechanic.** The altar should
visibly *want* what it cannot have yet — escalating refusal strings that name an absence without
naming the answer. Silence is correct for the first twenty days and corrosive for four hundred. This
costs a string table and gives two players something to argue about, which is a better between-beats
loop than an early gene lottery. Capsules can then stay in Industrial where Conrad leaned.

`[PROPOSED]` **Move the first real faction demand to N2, on the back of Carrier Birds**, rather than
landing the whole system in M2. M2 is already the crowded leap. *"Twenty dried meat by the 15th"* is
an existential crisis for a tribe and a joke for a castle — teach the class while the ask is small,
the same argument v2 already makes for the trough being the tutorial hunt. Standing & Embassy in M2
then *deepens* a system the player already fears instead of introducing one.

`[PROPOSED]` **Do not simulate inter-faction war.** `rimworld-design-philosophy.md` §7.1 calls it
load-bearing, and the full version is a second project. The cheap version that carries most of the
emotional payload: **paired demands from rivals that arrive together, where satisfying one auto-fails
the other.** Make consequences real only at act breaks — a settlement appears or disappears, a
faction's raid composition changes by faction-def substitution (`Lemmy's Progression Mod`'s technique).

`[VERIFY]` **"Raiders start bringing tools instead of torches"** (v2, Reinforced Works) is prose, not
a mechanism — vanilla raid composition does not respond to your walls. Vanilla *does* partly deliver
this free via wealth- and time-scaled sappers and breachers. **Check what already happens before
building anything**, and either restat the claim or accept it as vanilla behaviour.

---

## Faction investigation — 2026-08-24

Conrad downloaded ~40 mods without enabling them and asked for an assessment of the faction set,
plus an explanation of how RimWorld's tick loop and storyteller actually work. Six parallel recon
agents ran; a seventh (storyteller architecture) died on an auth error and that work was redone in
the main thread.

**Full detail lives in `scratch/`. Do not re-derive it:**

| File | Covers |
|---|---|
| `recon-rimwar.md` | Rim War — settlement economy, sampled action loop, the abstract↔concrete bridge |
| `recon-vassalage-territory.md` | Faction Territories & Vassalage, Map Mode Framework |
| `recon-factional-war.md` | [SR]Factional War (fork) |
| `recon-faction-support-mods.md` | Sensible Factions, Faction Customizer, Lemmy, World Tech Level, VOE |
| `recon-vanilla-faction-baseline.md` | Vanilla faction capability, 1334 lines, VERIFIED/INFERRED tagged |
| `recon-faction-mod-status.md` | Maintenance status, dependency graph, risk ranking |
| `recon-storyteller-architecture.md` | The tick loop and storyteller, decompiled 2026-08-24 |

### The framing decision — `[CONRAD]`, and it is load-bearing

> *"I don't need random factions going to war behind the scenes. If I don't even know they exist,
> why do I give a shit."*

**Wars only exist once the player has been told about them.** A war is acceptable as a notification,
a goodwill change, and a map tile you can travel to. It is an **event, not a simulation**.

This collapses the problem by an order of magnitude and it is the reason our approach can be cheap
where every assessed mod is expensive. Those mods pay their whole cost simulating things the player
never sees — Rim War maintains an economy for every settlement on the planet, FTV recomputes
territory for factions you have never met. It also removes the genre's characteristic failure mode
by construction: you cannot have a war the player never notices if wars are created by being
announced.

`[CONRAD]` He also explicitly deferred load-order and missing-mod questions for this pass:
*"We're just looking at mods and farming what we want. We'll fix all that stuff later."* The
config divergence recorded below is therefore **noted, not blocking**.

### Verdicts

**Install:** `World Tech Level` (`3414187030`) and `Sensible Factions` (`3531306011`). Keep
`Faction Customizer` (`3336572602`, already in the load order) under a **pre-game-only, host-only
usage rule** — it is pure GUI with zero randomness and inert while dormant, but every mutation it
makes fires from an unsynced dialog. `Map Mode Framework` (`3296654393`) only if territory needs
drawing; it is MP-inert (its only `Rand` matches are commented out) and its threading feeds
rendering only, so the risk is a data race rather than divergence.

**Reject as shipping mods:** Rim War, Faction Territories & Vassalage, Lemmy Progression,
[SR]Factional War. All four are hard MP fails and three write unremovable state into the save.

- **Rim War** — three independent desync mechanisms: raw OS threads for the faction sim with a
  **client-local setting** toggling the threading model; `Rand` consumed off-thread; and `Rand`
  consumed **on the GUI thread**, so *merely opening its tab while your partner does not* desyncs.
  Also `restrictEvents` defaults **on** and blanket-blocks vanilla `RaidEnemy`, `RaidFriendly` and
  `TraderCaravanArrival` — it takes the storyteller over and would fight era gating head-on.
  Patches a comp onto every `Settlement` def and scribes its own world objects: adding then removing
  it mid-save orphans those refs.
- **FTV** — the most dangerous mod in the folder. About.xml claims it "draws territory regions"; the
  DLL ships autonomous invasions, AI settlement construction, vassalage and outposts across six
  ticking `GameComponent`s, **all on by default**, one of which calls `Find.TickManager.Pause()` and
  mutates `CurTimeSpeed` from inside a tick wrapped in a bare `catch {}`. No licence, no source, no
  README. Undeclared reflection dependency on Rim War.
- **Lemmy Progression** — self-declared v0.0.1, one day of git history including *"Major refactor -
  still not working entirely"*. Two unsynced `System.Random` instances directly in the
  faction-upgrade decision path. Also functionally broken against World Tech Level: it writes the
  wrong backing field, so WTL silently reverts every era advance on load. **Steal the idea — factions
  teching up alongside the player is right for Archinity — not the code.**
- **[SR]Factional War** — not a war simulation. A battle-scene generator with **zero persistent
  state**: no `WorldComponent`, no tick loop, and across 62 source files not one write to faction
  goodwill, strength or `defeated`. Hostility is read as a precondition and never produced, so
  nothing progresses, nobody wins, and the same war refires forever. MP fail via a per-client
  settings slider feeding `pawnGroupMakerParms.points`. Up to **5000 threat points per side with no
  tech gate**, which is a spacer-scale battle capable of landing beside a Neolithic colony.

  > **Correction to an earlier claim in this file's 2026-08-23 section:** Factional War was listed on
  > the action list as a candidate for the §7.1 *"factions must want things from each other"*
  > requirement. It only appears to satisfy it. It delivers the visual and none of the mechanics.

**Defer as out-of-category:** `Vanilla Outposts Expanded` is player-owned colony outposts riding on
VEF's already-installed Outposts framework, not faction behaviour. It also ships *less* on 1.6 than
1.5 — Fishing absent, Factory commented out in `loadFolders.xml`.

### Why the whole genre is perpetually beta

Vanilla offers tiles plus bilateral relations, single-threaded, storyteller-paced. So every one of
these mods builds a **shadow world model** alongside the real one, then pays that model's two taxes
forever: repairing its own invariants on every load, and colliding with whatever other mod built a
different shadow model over the same static managers. Rim War reflection-reaches into vanilla's
*private* `Faction.relations` list on every load to synthesize missing entries; FTV ships six Harmony
patches that temporarily lie to `FactionManager` about which factions exist.

Then the shadow model gets expensive, performance forces threading, threading destroys
reproducibility, and a bug that cannot be reproduced cannot be closed. Rim War reads **0.9.9.8**
seven years in. That is a trap the architecture set, not author negligence.

**The lesson we take: do not build a shadow world.** Two things follow — the parts we keep are the
ones that need no persistent parallel state, and the reason those mods needed threads at all is that
they scanned the planet. A world layer with ten factions ticking once a game-day costs nothing.

### The two crux findings

**1. NPC↔NPC relations already work and nothing contests them.** VERIFIED in
`recon-vanilla-faction-baseline.md`. `Faction.RelationWith`, `TryAffectGoodwillWith`,
`CheckKindThresholds` and `Notify_RelationKindChanged` are fully symmetric and work end to end
between two NPC factions — including invalidating `attackTargetsCache` and re-evaluating `Lord` AI
so their pawns genuinely fight. What is missing is only that **every one of the ~60 mutation call
sites in the assembly has `Faction.OfPlayer` on one side**, and `CalculateAdjustedGoodwillChange` and
`CheckReachNaturalGoodwill` both short-circuit on non-player pairs.

So NPC↔NPC goodwill is a working, persisted, fully-honoured channel that **vanilla never writes to
and will never contest.** We do not need a shadow model. Vanilla already has the world model; it
simply never uses the half we want.

Supporting: `Faction.defeated` is a single bool honoured by 12 systems — *"a faction fell"* is one
assignment. Settlements can be created and destroyed at runtime through entirely public APIs.

**2. The storyteller is a roster of independent generators, and the world is a legal target.**
VERIFIED in `recon-storyteller-architecture.md`. `Storyteller.StorytellerTick()` runs inside
`TickManager.DoSingleTick()`, does work every 1000 ticks (**60 evaluations per game day**), and
`MakeIncidentsForInterval()` loops every `StorytellerComp` independently. `AllIncidentTargets` is
every map, every caravan, **and `Find.World`**. Comps declare `allowedTargetTags` /
`disallowedTargetTags` / `minDaysPassed` in pure props.

**Therefore adding a comp is additive, not competitive.** We would not blanket-block anything, which
is precisely what Rim War had to do.

Two further findings from that pass:

- **An ongoing quest is also an incident generator.** `MakeIncidentsForInterval()` walks every
  `QuestState.Ongoing` quest and asks any `IIncidentMakerQuestPart` for incidents on the same
  interval. A demand quest can apply continuing pressure while live. This was not previously known
  to the project and is directly relevant to both the Chronicle and faction demands.
- **Threat points are computed on demand, not cached.** `DefaultParmsNow` builds a fresh
  `IncidentParms` every call. There is no snapshot the storyteller reads — it is pull, not push, so
  nothing needs maintaining on its behalf. Incidentally `GetProgressScore` is
  `freeColonists * 1f + wealth * 0.0001f` and nothing else, which is why `rootMinProgressScore`
  ignores research.

**MP conclusion — the decisive one.** Because the storyteller sits inside the synced tick,
randomness consumed inside a `StorytellerComp` is deterministic across clients **by construction**,
in exactly the way randomness in a settings window or on a worker thread is not. This sidesteps the
entire class of failure that killed the four rejected mods rather than trying to solve it.
`[VERIFY]` The tick placement is verified; that MP syncs `DoSingleTick` is a sound inference — the
MP assembly did not resolve by package ID during this pass and was not read directly.

### The recommended build

`[PROPOSED]` Nothing here is decided. Estimated smaller than the 600–800 lines the Rim War teardown
put on rebuilding its useful 20%, because we are not building a parallel world.

- **A ledger** — one `WorldComponent` holding a few numbers per faction the player has actually met:
  who they resent, how tense it is. **Written to only by things the player does.** No autonomous
  drift, nothing happening off-screen.
- **A custom `StorytellerComp`** filtered to the world target, reading the ledger and proposing
  faction incidents alongside vanilla's comps. Roughly 50–100 lines plus props.
- **Custom `IncidentDef`s** — border dispute, declaration of war, ally calls for aid, a rival's raid
  arriving in the other faction's gear. Mostly XML; reuse vanilla `IncidentWorker`s wherever one
  already does the job.
- **Consequences written through vanilla's own relations API**, per crux finding 1.
- **Territory** — lift the *idea* from FTV's `TerritoryOwnershipCache.cs` (553 lines): a deterministic
  hash-seeded cost-weighted multi-source Dijkstra over world tiles, seeded off the world seed string,
  four-way tiebreak, **zero `Rand`**, and **never saved** — recomputed rather than persisted. It has
  no MapModeFramework imports, so the mechanical half lifts cleanly from the rendering half. It is
  the single best artefact found on 2026-08-24: MP-safe by construction, no save-migration risk, and
  it composes for free — territory is a pure function of settlement positions, so if an event moves
  or removes a settlement the map redraws itself with no coupling.
- **The bridge** — Rim War's best idea and the answer to the invisibility problem: when the player
  participates, the abstract war converts into a real vanilla raid whose threat points come from the
  attacker's accumulated strength, and losses flow back to the world object on map exit.
- **~40 lines of custom `QuestPart` + `QuestNode`** to let a quest change NPC↔NPC relations —
  verified as the one thing the vanilla quest layer cannot express
  (`QuestPart_FactionGoodwillChange` and `QuestPart_FactionRelationChange` each hardcode
  `Faction.OfPlayer`).

No Harmony patches are required for any of it.

### Verified in passing

**Techprints are real and usable — VERIFIED.** `ResearchProjectDef` carries `techprintCount`,
`techprintCommonality`, `techprintMarketValue` and `heldByFactionCategoryTags`. The techprint
`ThingDef` is auto-generated by `ThingDefGenerator_Techprints` — we never author the item. Quest
reward confirmed via `QuestNode_GiveTechprints` (which has `fixedProject`, so a named project can be
a named quest's reward straight from XML) → `QuestPart_GiveTechprints` → `ResearchManager.ApplyTechprint`.
Faction ownership keys off `heldByFactionCategoryTags` ∋ `faction.def.categoryTag`.

**They require Royalty** — `PostLoad()` silently zeroes `techprintCount` when Royalty is absent.
`ludeon.rimworld.royalty` **is** in `ModsConfig.xml`, so this is live. The
2026-08-23 *"do this for us and we will teach you about X"* proposal is therefore solved in pure XML.

**Two assumptions were wrong.** `naturalColonyGoodwill` does not exist in 1.6 at all, and
`mustStartOneEnemy` is a dead field with no behavioural reader.

### Config divergence — noted, deliberately not acted on

Conrad deferred this. Recording it so it is not rediscovered:

- `ModsConfig.xml` contains **no Medieval Overhaul, no VFE Tribals, no Vanilla Cooking Expanded** —
  yet `VISION.md` treats MO and VFE-Tribals as reversed-in and load-bearing, and the entire 101-node
  v2 tree is designed against MO as the parts bin.
- `archinity.altar` is still absent (known defect 1). The four DLCs are still duplicated (defect 2).
- **`rwmt.compatibility` is not installed.** `rwmt.multiplayer` is present; these are different mods,
  and the core one carries no per-mod sync patches. Every "MP-verified" entry on the action list
  assumes the compatibility layer is there.
- Docs say **More Research Requirements**; what is active is `sae.researchmod`, *More Realistic
  Research*. Possibly doc drift, possibly the wrong mod. `tools/check_availability.py` validates
  against it.

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

From the 2026-08-23 evening session — see that section above for the reasoning:

- [ ] **L1 is wrong as written.** *"Every augment bolted to it carries across every upgrade"* is not
      the intent. Augments are deliberately sunset at a bench upgrade: the new bench matches the old
      fully-augmented one, accepts 1–2 legacy augments, and brings its own. Rewriting L1 is blocked
      on open decision 8.
- [ ] **L1's second clause needs the parallel-work correction.** *"The player never manages five
      buildings for one domain"* reads as one physical bench per domain, which removes parallel work
      entirely. The rule is about distinct bill tabs, not building count — multiple identical benches
      are fine and expected.
- [ ] **The bench system implies recipes are gated by augments; they are not.** Recipes come from
      research. §03 and several §05 cards should stop implying that an augment is what makes a recipe
      available.
- [ ] **The QoL-hunt class is now the faction-quest class.** §02 L5, the §05 legend, every `qol`
      card and the §04 "QoL hunts" row all describe fetch errands. The reward is unchanged; the
      framing, the giver and the cost all change.
- [ ] **Reinforced Works** — see the `[VERIFY]` note above. Same error class as the mine shaft card.

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
