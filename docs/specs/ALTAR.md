# The altar

## Purpose and scope

How the altar grants the shipped `VRE_Transcendent` gene to the founder standing in it,
plus the separate repeatable augmentation lottery.

Requirements this implements:

- [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *One apparatus and separate
  rewards* — "Stored charge does not spoil. The sacrificial donor dies; the ordinary gene
  recipient is not killed by the operation." Both are already built and are verified below.
- [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *Saved state and remaining
  work* — the final rite grants the existing `VRE_Transcendent` gene and adds no custom
  return-after-death system.
- [`docs/plot/ENDING.md`](../plot/ENDING.md) § *Transcendence* — the transformation and
  the enter-or-stay ending choice.

Established by [#59](https://github.com/cjd721/Rimworld-Archinity/issues/59).

**This document owns granting the existing gene and the lottery draw.** It does not own the
per-founder state store — that is [`TRANSCENDENCE.md`](TRANSCENDENCE.md)'s
`CompFounderRecord`, which this design reads rather than duplicating, under that document's
rule 1. It does not own the victory, the Administrator or the enter-or-stay choice (also
`TRANSCENDENCE.md`); who counts as a willing giver, which
[#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) answered at capability depth and left to
[the build map](https://github.com/cjd721/Rimworld-Archinity/issues/119); or which genes sit in which
pool ([#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) — open, and titled
*The power grid* rather than anything about pools; its rows are the vector pools).

The lottery draw is owned by [#110](https://github.com/cjd721/Rimworld-Archinity/issues/110) and its build is the
second half of *The build*, below. What the draw **costs** — the band curve, the capsule's
charge price, the offer deadline — is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s (balance);
see *Outstanding decisions*.

Additional requirement this implements:

- [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *Altar, Anima and Biological
  Progression* — "Ordinary colonist lottery outcomes are opt-in but randomized once
  activated", and § *One apparatus and separate rewards* — "Random augmentation is a
  separate, explicitly chosen lottery, including genuinely bad outcomes."

The same requirement section's **optional encounter that teaches what anima is** is answered in
[`ENCOUNTERS.md`](ENCOUNTERS.md) ([#158](https://github.com/cjd721/Rimworld-Archinity/issues/158)), not here.

---

## The final rite

**The altar's no-vector arm is the final rite, and it grants the shipped `VRE_Transcendent`
gene.** A founder who has claimed a title (clause 3 under *Four clauses in `CanAcceptPawn`*)
enters with no vector loaded. On completion `PerformRite`, on the altar's already-synced tick,
adds `VRE_Transcendent` through `Pawn_GeneTracker.AddGene`, sets
`CompFounderRecord.transcendedTick` and opens the Administrator scene
([`TRANSCENDENCE.md`](TRANSCENDENCE.md) §4). Endogene or xenogene is the build map's
([`PSYCHIC.md`](PSYCHIC.md) § *A psycaster path only the founders can take* › *Open
questions*). No gene is authored and nothing returns a founder from death
([`plot/ENDING.md`](../plot/ENDING.md) § *The Final Altar Ritual — Life + Devotion + Self*;
[`COSMOLOGY.md`](../COSMOLOGY.md) § *The complete operation*). The founders' survival before
the rite is vanilla Deathless and its brain clause
([`docs/engine/health-and-death.md`](../engine/health-and-death.md)).

**The gene is the rite's alone in shipped content.** `GenePool_Archite.xml` marks it
`reserved`, and `Archinity.Pacing/Patches/ArchiteInjection_Blacklist.xml` keeps it out of
archite injection. The leaks that remain — random genepacks, captured `VRE_Archon` pawns, More
Archotech Garbage's extractors — are `PSYCHIC.md` § *Where each key leaks*; sealing them is
[#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

**A transcended founder is never fuel.** `Building_Altar.DrainAndKill` calls
`victim.Kill(null)` directly [V], and `Pawn.Kill` is unguarded
([`docs/engine/health-and-death.md`](../engine/health-and-death.md) § *Death is intercepted on
the damage path, not in `ShouldBeDead`*), so a transcended founder hauled in as a prisoner or
slave would die by our own code. The refusal sits inside `CanAcceptPawn`'s existing
`if (IsFuel(p))` branch — the branch `TryAcceptPawn` latches into `draining` and `Finish()`
reads [V] — returns `Archinity_AltarTranscendentNotFuel`, and keys on
`CompFounderRecord.transcendedTick >= 0` only. It does not key on `VRE_Transcendent`: every
`VRE_Archon` carries that gene (`PSYCHIC.md` F3), so a gene key would refuse captured Archon
prisoners as fuel. **Scope it to the fuel branch, never to the pawn** — a refusal on the pawn
also turns a transcended founder away as a rite recipient.

The custom-gene build this section replaces, and the engine evidence gathered for it, is
[`docs/archive/altar-transcendent-gene-build.md`](../archive/altar-transcendent-gene-build.md).

---

## The build — the repeatable lottery

Established by [#110](https://github.com/cjd721/Rimworld-Archinity/issues/110). Sections 6–10 are the
lottery. It shares `PerformRite`, `CanAcceptPawn` and the altar's `ThingDef` with
*The final rite* above — see *Four clauses in `CanAcceptPawn`*.

**The draw is a weighted sample, without replacement, from the pool the assembly already
ships, taken on the altar's already-synced tick; the offer is scribed state on the altar
until the player resolves it; the choice travels as an index through Multiplayer's own
`PersistentDialog`.** Nothing here is a new subsystem. The pool machinery exists and is
**reused**, not replaced: its only defect is that nothing calls it.

| | |
|---|---|
| **Mechanism** | One `Rand.Value` roll on `Building_Altar.Tick` selects a **tier band**, handed straight to the existing `GenePoolDef.Available(Pawn, int minTier, int maxTier)`; a new `GenePoolDef.Draw` takes `4 + mods.extraOptions` entries from it by weight, weighting the capsule's category up by `mods.categoryBias`. `Available()`, `EntryFor()`, `categoryBias` and `extraOptions` are **reused verbatim** (§6). |
| **State** | `pendingOptions`, `pendingRecipient`, `offerDeadlineTick` on `Building_Altar`. A repeat costs the existing charge debit plus the capsule. Between draws the altar remembers **nothing**; per-pawn exclusion is already free inside `Available()` (§7). |
| **Persistence** | Three new `Scribe` keys on `Building_Altar.ExposeData`, plus a `PostLoadInit` null-strip. A save predating the feature reads no keys, gets a null offer, and behaves exactly as today. **No migration code** (§8). |
| **Change** | `Building_Altar.PerformRite` — the existing hook, already on the synced tick, already debiting the charge. The `ext.gene == null` arm stops being a silent success and becomes the draw. **This closes T-64** (§9). |
| **Display** | A vanilla `Dialog_NodeTree` opened from that same tick, one `DiaOption` per drawn gene, no Close option, actions hosted on `CompAltarLottery : ThingComp`. **The options are fully legible; the distribution that produced them is not** — and §10 states why, with the shipped counter-example. |
| **Cost** | ~136 lines of new C# in `ArchinityAltar.dll` and ~50 lines of XML. No new assembly, no third-party reference, **no Harmony patch**. |

### 6. The draw reuses the pool machinery; it does not replace it

`Archinity.GenePoolDef` already carries the whole data model and two of the three functions
the draw needs [V, `Archinity.Altar/Source/GenePool.cs`]:

- `Available(Pawn pawn, int minTier, int maxTier)` yields entries that are in the pool, not
  `reserved`, inside the tier band, and **not already carried by the pawn**.
- `EntryFor(GeneDef)` resolves a gene back to its tier and category through a lazily built
  dictionary.
- `AltarModifiers.For(Thing)` sums `categoryBias` and `extraOptions` across linked, powered,
  unbroken facilities.

**All four have zero readers.** #59's finding is re-verified here at source: the only
mentions of `Available(` and `EntryFor(` in the tree are their own declarations, and
`categoryBias` / `extraOptions` are written in `AltarModifiers.For` and read nowhere [V].
The scaffolding is not merely present — it is the right shape, and `Available`'s signature
taking `minTier, maxTier` is evidence that the band was the intended design all along.

**"Coherent with the roll" is the band, not a second filter.**
[#10](https://github.com/cjd721/Rimworld-Archinity/issues/10) § *The lottery* fixes the
rule: *"a good roll must not offer four bad genes and a bad roll must not offer four good
ones."* One roll, taken on the tick, picks `[minTier, maxTier]`; every option inside a band
is of comparable worth, so coherence falls out of the band rather than out of a
post-filter that would have to be tuned against itself. **The band edges are a Balance
number and are an open parameter** — see *Outstanding decisions*.

**Category is a weight and must never be a filter.** `GeneVectorExtension` gains one field,
`GeneCategory category`; entries whose category matches score `1 + categoryBias[c]`,
everything else scores `1`. This is not a stylistic preference. Counted against
`GenePool_Archite.xml` as it stands — **50 entries, 9 `reserved`, 41 drawable** — the
drawable split by category is `Survival 11, Work 9, Body 8, Combat 8, Mind 4, **Social 1**`,
and every drawable entry carries a category [V]. A category *filter* cannot fill a
four-option offer in `Mind` or `Social`, and in `Social` would fail by silently offering
one option. A weight degrades gracefully in every category the pool will ever have.

```csharp
// GenePool.cs — the pure half of the seam CODING_STANDARDS.md names:
// "which gene the lottery draws" is values in, values out.
public List<GeneDef> Draw(Pawn pawn, int minTier, int maxTier, int count,
                          GeneCategory biasTo, Dictionary<GeneCategory, float> bias)
```

`count` is `4 + mods.extraOptions`, clamped to what `Available()` actually returned; if the
band yields fewer than `count` entries the band widens by one tier and retries,
deterministically, until it does or the whole pool is in scope.

**Widening is the normal path at the bottom of the ladder, not a fallback, and the pool is
why.** Drawable entries by tier today are `1 → **1**, 2 → 13, 3 → 13, 4 → 10, 5 → 4` [V] —
**tier 1 holds exactly one drawable gene, `VQEA_PerfectVision`**. A band of `[1,1]` can
therefore never fill a four-option offer and will always widen upward, which quietly makes
the worst band indistinguishable from the next one up. Two consequences, and neither is
this document's to settle:

- The band curve must be written against the tier *populations*, not against tier numbers
  in the abstract. It is an open parameter either way — see *Outstanding decisions*.
- If the bad band is to have the teeth [#10](https://github.com/cjd721/Rimworld-Archinity/issues/10)
  asks of it, **tier 1 needs more genes**. That is
  [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31)'s, and it is a build
  prerequisite rather than a nice-to-have: the mechanism is correct with one tier-1 gene and
  the *feature* is not.

**One drawable entry does not resolve.** `GenePool_Archite.xml` carries
`<gene>Resurrect</gene>` at tier 5, and the vanilla `GeneDef Resurrect` is **commented out**
in `Data/Biotech/Defs/GeneDefs/GeneDefs_Abilities.xml` — the `<!--` opens immediately before
its `<defName>` and the `-->` closes before `</Defs>` — and no mod in either corpus root
defines that defName [V]. By **T-04** an unresolvable cross-reference is omitted rather than
nulled, so the entry's `gene` field loads as null. `Available()` already skips
`e.gene == null` [V], so the draw is safe today by accident rather than by design. `Draw`
must keep that guard and `MissingArchiteGenes()`'s startup log is the place the entry should
become visible. The entry itself is [#112](https://github.com/cjd721/Rimworld-Archinity/issues/112)'s to fix.

### 7. What a repeat costs, and what is remembered

- **Cost of a repeat**: `ext.chargeCost * mods.chargeCostFactor` — the existing debit in
  `PerformRite`, unchanged [V] — plus the lottery capsule, destroyed by the existing
  `vector.Destroy()` [V]. No new cost mechanism, and the `chargeCostFactor` floor of `0.25f`
  in `AltarModifiers.For` still holds the blood floor [V].
- **Remembered**: only what the pawn now carries. `Available()` already skips
  `pawn.genes.HasActiveGene(e.gene)` [V], so a pawn is never offered a gene they hold and
  repeat draws on one pawn converge without any memory of their own.
- **Not remembered, deliberately**: options offered and declined. Storing them would let a
  player enumerate the pool by repeated draws, which is the opposite of #10's *"knows the
  domain of the gamble but not the outcome."*
- **Not weighted down across draws.** No diminishing-returns curve is built here.
  Anti-habituation is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s
  (#49 closed and left it there); this design leaves the hook **absent** rather than inventing a decay rate, and
  adding one later is a weight multiplier inside `Draw`, not a redesign.

### 8. Persistence

```csharp
Scribe_Collections.Look(ref pendingOptions,   "archinity_lotteryOptions", LookMode.Def);
Scribe_References.Look (ref pendingRecipient, "archinity_lotteryRecipient");
Scribe_Values.Look     (ref offerDeadlineTick,"archinity_lotteryDeadline", -1);
if (Scribe.mode == LoadSaveMode.PostLoadInit) pendingOptions?.RemoveAll(g => g == null);
```

- **The null-strip is not defensive padding.** A pool gene removed with a mod leaves a null
  in a `LookMode.Def` list and the offer would draw a blank option. Vanilla does exactly
  this in `RimWorld.ChoiceLetter_GrowthMoment.ExposeData`, which strips nulls from
  `traitChoices` and `passionChoices` in `PostLoadInit` [V].
- **A save predating the feature** carries none of the three keys, so `pendingOptions` loads
  null and every lottery branch is unreachable. The altar behaves exactly as it does today.
  Nothing to migrate, nothing to version.
- **A save reloaded after the deadline passed** needs no special case: the timeout branch in
  §10 fires on the next tick.
- The `archinity_` prefix satisfies `TRANSCENDENCE.md` rule 2 verbatim.

### 9. What spends the charge — and the trap it closes

The change is one branch in a method that already exists, already runs on the synced tick,
and already spends the charge:

```csharp
// Building_Altar.PerformRite, replacing   if (ext.gene != null) GrantGene(recipient, ext.gene);
if (ext.gene != null) { GrantGene(recipient, ext.gene); FinishNamedRite(recipient, ext); }
else                  { OfferLottery(recipient, ext); }   // charge already debited above
```

**This is the fix for [T-63's sibling, T-64](../TRAPS.md).** Today `PerformRite` guards the
grant with `if (ext.gene != null)` and then, *outside* that guard, unconditionally destroys
the vector, keeps the debited charge, and posts `Archinity_AltarRiteSucceeded` rendering the
gene as `ext.gene?.LabelCap ?? "?"` [V, re-read at source]. A `gene: null` extension —
documented in our own source as *"Null means the lottery"* — therefore consumes a rite,
consumes the item, grants nothing and reports success. Routing that arm into `OfferLottery`
removes the silent no-op by giving the branch the behaviour its comment always claimed.

The success message and `EjectRecipient` move **inside** the named-gene arm. While an offer
is pending the recipient stays in the altar and is ejected only by the resolution path —
which is also the anti-decline: you cannot walk the pawn away and keep them.

`docs/traps/content-and-buildings.md`'s T-64 closes with *"Until the lottery is built, an
extension with a null `gene` must be refused loudly at the rite"*. That instruction is
correct and is superseded by this section, not contradicted by it: the refusal was the
interim measure, and this is the build it was waiting for.

### 10. Where the player sees it, and how two players resolve one draw

**The surface is a vanilla `Dialog_NodeTree`, opened from `Building_Altar.Tick`.** Four
facts, each read at source in `2606448745/1.6/AssembliesCustom/Multiplayer.dll`, make that
the whole of the multiplayer design:

1. `Multiplayer.Client.Multiplayer.MapContext` is
   `AsyncTimeComp.tickingMap ?? AsyncTimeComp.executingCmdMap` [V]. During the altar's tick
   the first is our map, so **`MapContext` is non-null on the only path that opens the
   dialog.** This is the premise `TRANSCENDENCE.md` §4 rests on, now read at source rather
   than carried as an inherited claim.
2. `Multiplayer.Client.CancelDialogNodeTree` prefixes `WindowStack.Add`; with a non-null
   `MapContext` and a `Dialog_NodeTree` it builds a `PersistentDialog` into
   `mapContext.MpComp().mapDialogs` and **suppresses the local add** [V]. Both clients get
   the dialog from `ForceShowDialogs`.
3. The click is `Multiplayer.Client.DiaOptionActivate.Prefix` →
   `PersistentDialog.Click(int ver, int opt)`, a `[SyncMethod]` running
   `Dialog.curNode.options[opt].Activate()` behind a `ver` guard that drops a click made
   against a stale node [V]. **Only the index travels. The draw is never re-rolled per
   client.**
4. `Multiplayer.Client.ForceShowDialogs` prefixes `MapDrawer.DrawMapMesh` and re-adds
   `mapDialogs.First().Dialog` whenever no `Dialog_NodeTree` is open [V]. So under
   Multiplayer a closed offer **re-opens by itself — but only while that map is being
   rendered**, because `DrawMapMesh` is the only trigger. A player looking at the other
   colony, or at the world map, sees nothing until they come back. #10's *"you may not
   decline"* is therefore *mostly* free under MP and is **not** free in single-player; the
   scribed deadline in this section is what actually guarantees it in both.
5. `Multiplayer.Client.WindowStackTryRemove` postfixes `WindowStack.TryRemove(Window, bool)`
   and calls `mapDialogs.Remove(persistentDialog)` when
   `Multiplayer.Client != null && !Multiplayer.InInterface` [V]. **This is the only cleanup
   path**, and the design depends on it — see *The offer is added once and must be removed
   once*, below.

**Use `Dialog_NodeTree` itself, and do not subclass it here.**
`PersistentDialog.CreateInstance` keys a static `bindings` dictionary on the window's
**exact runtime type**, and MP populates it from the `PersistentDialog<T>` proxies in its own
assembly — `Dialog_NodeTree`, `Dialog_NodeTreeWithFactionInfo`, `Dialog_Negotiation` [V]. A
subclass of ours misses the dictionary, `CreateInstance` returns null,
`CancelDialogNodeTree` lets the local add through, and the dialog becomes client-local and
unsynced.

**This is a constraint on *us*, not an engine limit**, and the distinction matters:
`PersistentDialog.Bind(Type target, Type proxy)` and `PersistentDialog.BindAll(Assembly)`
are both **public** [V], so a mod that takes a `Multiplayer.API` reference can register its
own subclass and its own proxy. This project takes no such reference
(`Archinity.Altar.csproj` references only `Assembly-CSharp`, Unity modules and Harmony [V]),
so for us the vanilla type is the only bound one. Proposed as a trap on those terms.

**The delegate allowlist governs each option's action.** `DelegateSerialization` requires the
action's outermost declaring type to walk up to one of 15 types;
`Building_Altar` walks `Building → Thing → object` and is **not** among them
([`docs/engine/determinism.md`](../engine/determinism.md) § *MP serialises the comms-console
dialogue, options included*). The lottery's options therefore host their action on
`CompAltarLottery : ThingComp` on the altar's own `ThingDef` — the same move
`TRANSCENDENCE.md` §4 makes with `CompAltarThreshold` — and capture only the altar `Thing`,
the recipient `Pawn` (both `ILoadReferenceable`) and an `int` index.

**T-82 is satisfied by construction.** The option list is built once, on the synced tick,
from the scribed `pendingOptions`, in list order, with no membership filtering. Both clients
build the same list in the same order from the same data, so the index MP transmits means
the same thing on both.

#### The offer is added once and must be removed once

`WindowStackTryRemove` removes a `PersistentDialog` from `mapDialogs` **only when
`Multiplayer.InInterface` is false** [V]. `Multiplayer.InInterface` is itself
`Client != null && !Ticking && !ExecutingCmds && !reloading && ProgramState == Playing &&
LongEventHandler.currentEvent == null` [V]. So the removal fires exactly when the window is
closed from **inside a synced command or inside a tick**, and not when a player closes it by
hand. Two requirements follow, and **both are load-bearing**:

1. **Every lottery `DiaOption` sets `resolveTree = true`.** `PersistentDialog.Click` is a
   `[SyncMethod]`, so it runs as a command with `ExecutingCmds` true, `InInterface` false
   [V]. `resolveTree` makes `Activate()` close the dialog there, `TryRemove` fires with
   `InInterface` false, and the entry leaves `mapDialogs`. **An option without `resolveTree`
   resolves the offer and leaves its `PersistentDialog` behind**, which `ForceShowDialogs`
   then re-opens forever on a choice already made.
2. **The timeout branch must close the dialog from the tick, not merely resolve the state.**
   `Ticking` is true there, so `InInterface` is false and the removal path is available —
   but only if something actually calls `TryRemove`. Resolving `pendingOptions` without
   closing the window leaves a live `PersistentDialog` for an offer that no longer exists.

**The dialog is therefore added exactly once per offer and closed exactly once**, and the
two close paths are the synced click and the tick timeout. There is no third.

**The timeout itself is the shipped idiom, not an invention** — MP registers a **default
letter choice** per choice-letter type and applies it on expiry, including
`CloseDialogsForExpiredLetters.RegisterDefaultLetterChoice(…,
typeof(ChoiceLetter_GrowthMoment))` → `SyncDelegates.PickRandomTraitAndPassions` [V]. While
`pendingOptions != null` and `Find.TickManager.TicksGame >= offerDeadlineTick`, the tick
draws one of the already-drawn options with `Rand`, grants it, closes the dialog and ejects
the recipient. The deadline length is a Balance number and is an open parameter.

#### Two prefixes contend on `DiaOption.Activate`, and only one is the path above

`Multiplayer.dll` patches `DiaOption.Activate` **twice**:

- `NodeTreeDialogSync.Prefix` — gated on `Multiplayer.session != null && **SyncUtil.isDialogNodeTreeOpen**`.
  When both hold and the option's `dialog` is a `Dialog_NodeTree`, it routes the click
  through `[SyncMethod] SyncDialogOptionByIndex(int position)` and returns false. **When the
  flag is false it sets it false and returns true**, falling through [V].
- `DiaOptionActivate.Prefix` — gated on `Multiplayer.InInterface` and
  `PersistentDialog.FindDialog(__instance.dialog) != null`, calling
  `PersistentDialog.Click(ver, opt)` [V]. **This is our path.**

Neither declares a Harmony priority [V], so when both gates hold the winner is patch order
and is not determinable from the decompile. **In the normal case only the second gate holds,
because `isDialogNodeTreeOpen` is normally false** — it is set solely by
`SyncUtil.DialogNodeTreePostfix`, applied only through `Sync.RegisterSyncDialogNodeTree`,
whose call sites are the `[SyncDialogNodeTree]` attribute scan plus two explicit
registrations, `IncidentWorker_CaravanMeeting.TryExecuteWorker` and
`IncidentWorker_CaravanDemand.TryExecuteWorker`
([`docs/engine/determinism.md`](../engine/determinism.md)). The altar is on neither path, so
the sync story above stands **as a conditional, not as an unconditional**.

**The residual hazard, stated plainly.** If the flag is stale-true — a caravan-meeting or
caravan-demand dialogue open, or closed in a way that did not clear it — a click on our
offer can be routed through `SyncDialogOptionByIndex`, which resolves its target with
`Find.WindowStack.WindowOfType<Dialog_NodeTree>()`, a **client-local** lookup, and activates
`options[position]` on whatever that returns. Two clients with different topmost node trees
then activate different options from one index. That is **T-82**'s failure arriving through
a different door, it is silent, and this design cannot read the WindowStack from the tick to
prevent it. It is named in *Verification* as something to watch for rather than engineered
around, because the window is narrow and the mitigation would cost a Harmony patch on
Multiplayer's own prefix.

#### Odds: legible options, opaque distribution — and why

**We build the version the player cannot read the odds of.** The player sees all four drawn
genes in full — `LabelCap` on each option, `DescriptionFull` in the node text — so the
*offer* is perfect information. What is not published is the band curve and the category
weights that produced it.

**The reason, stated once and without hedging: the odds *are* actionable, and that is
exactly why this build leaves them unpublished.** The
roll happens after the charge is spent, but the *distribution* is known before it and is
constant, so a published band curve is a number the player computes against **at the moment
they decide whether to spend the charge at all** — which is the only decision the capsule
offers. Publishing it converts "a gamble you opted into" into arithmetic, and #10 puts the
gamble beyond renegotiation: *"All risk belongs on the lottery, which the player opted
into."*

What the player is owed instead is the **domain**, which #10 names in terms — *"the player
knows the domain of the gamble but not the outcome"* — and the domain is the category. That
**is** printed, on the capsule and on the altar's inspect line, and the four drawn options
are then shown in full. Nothing about the offer is hidden; only the generator is.

**The opposite choice ships in the corpus and is cheap.**
`VanillaQuestsExpandedAncients.Building_ArchogenInjector` computes
`CalculateOutcomeChances()`, normalising every `ArchiteInjectionOutcomeDef.baseWeight` after
facility modifiers, and exposes it per outcome through a public `GetOutcomeChance` for
display [V]. Ported here it is one method over `Draw`'s weight table, ~15 lines. It is
**not** in the estimate below; both versions are buildable.

| Surface | Mechanism | New code |
|---|---|---|
| The capsule states its category and that bad outcomes are in the pool | `description` on the `ThingDef` | XML |
| *"An offer is waiting"* on the altar | one line appended in the existing `GetInspectString` | ~4 lines |
| The four options, each a full gene tile's worth of text | `Dialog_NodeTree` + one `DiaOption` per option; no Close option | ~25 lines |
| The grant, and the timeout grant | `Messages.Message`, reusing `GrantGene` unchanged | ~8 lines |
| The odds | **not shown in this build.** The donor above shows them for ~15 lines | n/a |

### Cost — the lottery

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| `GenePoolDef.Draw` — band, weights, sample without replacement, widen-on-thin | new C# | ~40 | `Archinity.Altar/Source/GenePool.cs` |
| `GeneVectorExtension.category`; the band constants | new C# | ~6 | `Archinity.Altar/Source/AltarData.cs` |
| `OfferLottery` / `ResolveLottery` / timeout on `Tick` / three `Scribe` keys / inspect line | new C# | ~65 | `Archinity.Altar/Source/Building_Altar.cs` |
| `CompAltarLottery : ThingComp` — the allowed declaring type hosting each option's action | new C# | ~25 | `Archinity.Altar/Source/Building_Altar.cs` |
| Lottery-capsule `ThingDef`s (one per category) with `GeneVectorExtension`, `gene` omitted | XML | ~30 | `Archinity.Altar/Defs/ThingDefs/` |
| `CompProperties` for `CompAltarLottery` on the **altar** `ThingDef` | XML | ~5 | `Archinity.Altar/Defs/ThingDefs/` |
| Keyed strings — dialog title, node text, option labels, grant and timeout messages | XML | ~15 | `Archinity.Altar/Languages/English/Keyed/` |

**~136 lines of C# into the assembly we already ship, plus ~50 lines of XML.** No new
assembly, no third-party reference, and **no Harmony patch at all**.

**Not priced here, and not this document's:** the Industrial research and Archon quest that
convert a hoarded Archon capsule into a lottery capsule (#10 §2's hinge) are era and
progression work; the genes inside each category are
[#31](https://github.com/cjd721/Rimworld-Archinity/issues/31)'s.

---

## Persistence and multiplayer

### Save and load

- **The final rite adds no state of its own.** `VRE_Transcendent` is a shipped def, saved in
  the gene tracker like any gene, and `transcendedTick` is `TRANSCENDENCE.md`'s.
- **The lottery's** three keys and null-strip are §8.

### Multiplayer

| Path | How it is safe |
|---|---|
| The rite completing | `Building_Altar.Tick` — the altar's already-synced tick, where `PerformRite` and its `Rand.Value` roll already live [V]. `Rand` reached from a synced tick is deterministic by construction (`CODING_STANDARDS.md` § *Divergence*). |
| Entering the altar | `Building_Enterable.SelectPawn`, registered by Multiplayer in `Multiplayer.Client.SyncDelegates`; `Building_Altar` does not override it [V, via `TRANSCENDENCE.md` §3]. |
| **The lottery draw** | `Building_Altar.Tick` — the same already-synced tick. `Verse.Rand` throughout (`Rand.Value`, `GenCollection.RandomElementByWeight`); `UnityEngine.Random` is touched nowhere in `ArchinityAltar.dll` [V], so [#94](https://github.com/cjd721/Rimworld-Archinity/issues/94)'s boundary — `Rand.PushState`/`PopState` does not reach `UnityEngine.Random` — does not bind this path. |
| **The lottery offer reaching both clients** | `Multiplayer.MapContext` is non-null inside a map tick [V], so `CancelDialogNodeTree` converts our `Dialog_NodeTree` into a map-scoped `PersistentDialog` and `ForceShowDialogs` replays it [V]. §10. |
| **The lottery choice resolving once** | `PersistentDialog.Click(int ver, int opt)`, `[SyncMethod]`, activating `curNode.options[opt]` behind a version guard [V]. Only the index travels — **conditionally on `SyncUtil.isDialogNodeTreeOpen` being false**, which is the normal case; §10 states the contending prefix and the residual hazard. |
| **The offer being cleaned up** | `WindowStackTryRemove` removes the `PersistentDialog` from `mapDialogs` only when `Multiplayer.InInterface` is false [V] — so every option needs `resolveTree = true` and the timeout must close the window from the tick. §10. |
| **The lottery option actions surviving a reload** | Hosted on `CompAltarLottery : ThingComp`; `ThingComp` is on `DelegateSerialization`'s 15-type array [V]. Declared on `Building_Altar` instead they throw `"Delegate deserialization: method not allowed"` on load. §10. |
| **The lottery timeout** | `Building_Altar.Tick`, on a scribed `offerDeadlineTick` compared against `Find.TickManager.TicksGame`. No wall clock, no `Prefs`, no window state. |

**The lottery's divergence gate.** Passes, and the one thing that would break it is named:
the draw must read only the pool def, the pawn's gene list and `AltarModifiers` — all
synced — and the offer dialog must be opened on a fixed tick, **never on a condition read
from `Find.WindowStack`**. Asking whether the dialog is currently open is a client-local
read on a synced path and is the same defect class as viewport-gated RNG
(`CODING_STANDARDS.md` § *Divergence*): one client would add a dialog the other did not, and
the option indexes would then disagree. The design avoids it by adding the dialog exactly
once, from the tick that completes the rite, and resolving anything else through the scribed
deadline.

**The lottery's loudness gate.** A draw from an empty or
over-narrow band widens deterministically and, failing that, has no options to render — a
`Dialog_NodeTree` with zero options is visible immediately rather than silently wrong. The
weak spot is the reverse: an offer that is never resolved would be invisible if the altar
did not hold its occupant, which is why the recipient stays inside until resolution (§9).

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| A transcended founder hauled into the altar as fuel | **Silent** — our `DrainAndKill` calls `Pawn.Kill` directly, which nothing guards | The `CanAcceptPawn` clause in *The final rite*, **inside the `IsFuel` branch**. Without it this is a campaign-ending bug |
| That clause written against the pawn instead of the fuel branch | **Silent** — the altar refuses a transcended founder as a rite recipient too | *The final rite*. Scope it to `IsFuel` / `draining` |
| A `gene: null` vector is used before the lottery is built | **Silent — T-64.** Charge debited, vector destroyed, success posted with `"?"` | §9. The build is the fix; until it lands, refuse the rite loudly |
| The lottery offer dialog is subclassed from `Dialog_NodeTree` | **Silent under Multiplayer** — `PersistentDialog.CreateInstance` misses its bindings dictionary, returns null, and the dialog opens client-locally. Its only log line prints no type name | §10. Use `Dialog_NodeTree` itself. Proposed trap |
| A lottery `DiaOption.action` declared on `Building_Altar` | **Loud, but late** — `"Delegate deserialization: method not allowed"` on *load*, not at click, so it survives any playtest that never reloads | Host it on `CompAltarLottery : ThingComp`. §10, and the same failure `TRANSCENDENCE.md` records for the Administrator |
| The player closes the offer dialog in single-player | Visible: altar still occupied, inspect line still says an offer is waiting | The scribed deadline resolves it on the tick. Under Multiplayer `ForceShowDialogs` re-opens it too — but **only while that map is being drawn**, so the deadline is the guarantee in both modes [V] |
| A lottery `DiaOption` built without `resolveTree = true` | **Silent, and permanent** — the click resolves the offer but the dialog never closes inside the synced command, so `WindowStackTryRemove` never fires and `ForceShowDialogs` re-opens a settled offer forever | §10. `resolveTree = true` on every option, without exception |
| The timeout resolves `pendingOptions` without closing the dialog | **Silent, same shape** — a live `PersistentDialog` for an offer that no longer exists | §10. The tick must close the window, not only clear the state |
| `SyncUtil.isDialogNodeTreeOpen` is stale-true when the offer is clicked | **Silent** — the click routes through `SyncDialogOptionByIndex`, which picks its target with a client-local `WindowStack.WindowOfType<Dialog_NodeTree>()`; one index can activate different options on the two clients | §10. Not engineered around; named as a watch item in *Verification*. **T-82**, different door |
| `<gene>Resurrect</gene>` loads as null (the vanilla def is commented out) | Silent by **T-04** — omitted, not nulled, so the entry survives with no gene | `Available()` already skips `e.gene == null` [V] and `Draw` keeps that guard. The entry is [#112](https://github.com/cjd721/Rimworld-Archinity/issues/112)'s to remove |
| A pool gene is removed with a mod while an offer is pending | **Silent** — a null in a `LookMode.Def` list draws a blank option | The `PostLoadInit` null-strip in §8, copied from `ChoiceLetter_GrowthMoment.ExposeData` |
| A category capsule whose category has too few drawable genes | **Would be silent** — an offer with one option | Category is a **weight, never a filter** (§6). `Social` has exactly one drawable entry today [V] |
| A transcended founder enters the altar while a lottery offer is pending | **Would be silent and worse** — two `PersistentDialog`s on one map, and `ForceShowDialogs` only ever shows `mapDialogs.First()` | `CanAcceptPawn` must refuse entry while `pendingOptions != null`. See *Four clauses in `CanAcceptPawn`, from three documents* below |
| A lottery offer opens while the Administrator dialog is still unresolved | **Silent, and the reverse of the row above** — the offer queues behind it in `mapDialogs`, invisible, while its scribed deadline keeps running | **Unclosed.** A build task in *Outstanding decisions*, with the reason and the remedy |

**No campaign softlock.** Every branch degrades to "the altar refuses and says why", except
the ones marked silent above, each of which is closed by the clause named beside it — save the
Administrator-queue row, which is open and is stated as such.

### Four clauses in `CanAcceptPawn`, from three documents

| # | Clause | Source |
|---|---|---|
| 1 | Refuse a transcended founder (`CompFounderRecord.transcendedTick >= 0`) **inside the `IsFuel` branch only** — never drained, because `DrainAndKill` → `Pawn.Kill` is unguarded. Not keyed on `VRE_Transcendent`, which every `VRE_Archon` carries | *The final rite*, [#59](https://github.com/cjd721/Rimworld-Archinity/issues/59) |
| 2 | The `ext == null` recipient arm is the final rite ([`ENDING.md`](../plot/ENDING.md)), entered only past clause 3 | *The final rite*; [`TRANSCENDENCE.md`](TRANSCENDENCE.md) |
| 3 | Refuse **"X has not claimed a title"** — the `FounderRecord.HasClaimedSelf` gate | [`TRANSCENDENCE.md`](TRANSCENDENCE.md) § 3 |
| 4 | Refuse any entry while `pendingOptions != null` — a second `PersistentDialog` on one map is invisible behind `mapDialogs.First()` | § 10 here, [#110](https://github.com/cjd721/Rimworld-Archinity/issues/110) |

**All four land in one method, and the ordering between them is load-bearing** — clause 1 must be
inside the fuel branch, and clause 2 behind clause 3. Whoever writes the method second is editing
against a version the first has already changed, and the failure modes are a permanently dead
founder, a transcended founder refused as a recipient, and a hidden dialog. Assembling it is a
build task for [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119).

---

## Status

**Evidence class: READ.** Settled from 1.6 defs and decompiled assemblies —
`Assembly-CSharp.dll` (`RimWorldWin64_Data/Managed/`) and our own `ArchinityAltar.dll`. The
lottery half adds `Multiplayer.dll`
(`2606448745/1.6/AssembliesCustom/`), `Multiplayer_Compat.dll`
(`1629973374/1.6/Assemblies/` — the **loaded** copy, not the `Referenced/` stubs) and
`VanillaQuestsExpandedAncients.dll` (`vanillaquestsexpanded.ancients`, `1.6/Assemblies/`).
Corpus verified against `docs/data/MOD-SNAPSHOT.md` (`corpus.py --check`: 155 mods,
matches) at the start and end of both passes.

**The lottery half is READ too, with one named two-client check** — item 4 under
*Verification*. It is a RUN for the multiplayer claim only; everything reading can settle
was settled first, which is why that check is one save-and-reload rather than "test it."

**Verified available mechanisms:**

- The altar's charge, the fuel/recipient split and the kill/survive asymmetry, all already
  built in `ArchinityAltar.dll` [V] — see below.
- `Pawn.Kill` unguarded by Deathless, `preventsDeath` or the coma [V]
  ([`docs/engine/health-and-death.md`](../engine/health-and-death.md)).

**Verified available mechanisms — the lottery half**
([#110](https://github.com/cjd721/Rimworld-Archinity/issues/110); assemblies read:
`Multiplayer.dll` (`2606448745/1.6/AssembliesCustom/`), `VanillaQuestsExpandedAncients.dll`
(`3618306875/1.6/Assemblies/`), `Assembly-CSharp.dll`, our own `ArchinityAltar.dll`):

- `GenePoolDef.Available` / `.EntryFor` and `AltarModifiers.categoryBias` / `.extraOptions`
  exist, are correct for this use, and have **zero readers** [V].
- `Multiplayer.MapContext == AsyncTimeComp.tickingMap ?? executingCmdMap`, so a map tick has
  map context [V].
- `CancelDialogNodeTree` → `PersistentDialog` → `ForceShowDialogs` → `PersistentDialog.Click`
  as a complete, index-based, save-surviving synced choice path for a **plain**
  `Dialog_NodeTree` [V].
- `PersistentDialog.CreateInstance`'s exact-type `bindings` lookup and its null return on a
  miss, with `Bind` / `BindAll` public for a mod that takes the MP API reference [V].
- `WindowStackTryRemove` as the **only** `mapDialogs` cleanup path, gated on
  `!Multiplayer.InInterface` [V] — which is what forces `resolveTree` and a tick-side close.
- The two contending prefixes on `DiaOption.Activate`, and that `SyncUtil.isDialogNodeTreeOpen`
  is armed only by two incident workers, so ours is normally the live path [V].
- MP's default-choice-on-expiry idiom, `CloseDialogsForExpiredLetters.RegisterDefaultLetterChoice` [V].
- MP's seeded-draw idiom, `Rand.PushState(Gen.HashCombineInt(pawn.thingIDNumber,
  letter.arrivalTick))` around `ChoiceLetter_GrowthMoment.TrySetChoices` [V] — not used by
  this build, and the answer if the draw ever has to leave the tick.
- A shipped 1.6 implementation of nearly this whole feature:
  `VanillaQuestsExpandedAncients.Building_ArchogenInjector` + `Window_GeneChoice` +
  `ArchiteInjectionOutcomeDef` [V] — see below.

**Proposed, and [I] until compiled:** that these compose into the behaviour described.
Each mechanism is [V]; the composition is not.

**Selected:** nothing; selection is [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.

---

## Available mechanisms

### The three "asserted and nowhere verified" altar behaviours are built, and they work

The ticket asked for these to be verified. They are not merely expressible — they are
**already implemented in the assembly we ship**, and all three were read at source:

- **Charge that does not spoil.** `Building_Altar.charge` is a `private float`, scribed by
  `Scribe_Values.Look(ref charge, "charge", 0f)`. Nothing in `Tick()` decrements it; the
  only subtraction in the class is `PerformRite` spending it [V]. It does not spoil because
  there is no decay path, which is why the charge lives in the building rather than in
  hemogen packs.
- **The willing/coerced distinction.** `Building_Altar.IsFuel(Pawn)` returns
  `p.IsPrisonerOfColony || p.IsSlaveOfColony`, derived from pawn status with no gizmo [V].
  **But this is coerced-versus-not, not willing-versus-coerced.** A free colonist who
  believes nothing is treated identically to a devout volunteer, and `docs/COSMOLOGY.md`
  § *Devotion* makes that difference load-bearing. The routes are
  [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)'s resolution: a rite can require the giver's
  faith and certainty, coerced Life stays separate, and a faction can send aligned pawns
  (`requirements/ALTAR.md` § *Conversion and certainty*). Who counts as willing, the guards,
  cooldowns and how volunteers arrive are [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119)'s.
- **Donor dies, recipient survives.** `Finish()` branches on `draining`:
  `DrainAndKill(occupant)` → `victim.Kill(null)` and places the corpse, versus
  `PerformRite(recipient)` → `EjectRecipient` [V]. Confirmed, with the caveat in *The final
  rite*.

### The corpus already ships the lottery — once, in one mod, and not multiplayer-safe

**`VanillaQuestsExpandedAncients.Building_ArchogenInjector`** is a live 1.6 implementation
of very nearly this feature, and it is the donor the build copies [V, all of it read at
`3618306875/1.6/Assemblies/VanillaQuestsExpandedAncients.dll`]:

- A `Building_PawnProcessor` a pawn enters, consuming a vanilla `ArchiteCapsule` from its
  own `innerContainer` — the same shape as our `Building_Enterable` altar.
- `CalculateOutcome()` picks an `ArchiteInjectionOutcomeDef` by
  `RandomElementByWeight` over each def's `baseWeight`, **after** `ApplyFacilityModifiers`
  walks `CompAffectedByFacilities` — which is, field for field, what `AltarModifiers.For`
  already does for us.
- The outcome is computed at `StartInjection`, **scribed** (`Scribe_Defs.Look(ref outcome,
  "outcome")`), and consumed at `FinishProcess` — so the roll survives a save taken
  mid-rite. Our `pendingOptions` is the same move one level down.
- `HandleSuccessOutcome` builds a short random list of eligible archite genes plus a
  metabolism-matched list of side-effect genes and opens `Window_GeneChoice(archite,
  sideEffects, onGenesSelected)`.
- `Window_GeneChoice` is a `Window` with `forcePause = true, doCloseX = false,
  closeOnCancel = false, closeOnClickedOutside = false` — **it cannot be declined**, which
  is #10's rule implemented — drawing each option with the public, def-typed
  `GeneUIUtility.DrawGeneDef(GeneDef, Rect, GeneType, …)`.
- `GetFilteredGenes` excludes genes the pawn already has and unmet `prerequisite`s, exactly
  as our `Available()` does.

**What we replace is the window, and only the window.** It is a bespoke `Window`, so under
Multiplayer: `forcePause` does not pause (**T-53**), the dialog is added outside any synced
command, and `onGenesSelected` runs on the clicking client alone. **Multiplayer
Compatibility does not cover this mod** — a sweep of the loaded
`1629973374/1.6/Assemblies/Multiplayer_Compat.dll` returns `vanillaquestsexpanded.generator`
and no other Vanilla Quests Expanded package [V]. So the shipped implementation of our
feature is a desync, and `Dialog_NodeTree` is the piece swapped in. Everything else — the
weighted outcome def, the scribed roll, the facility modifiers, the non-declinable choice of
drawn genes — is confirmation that the shape is right rather than novel.

It also settles the odds question empirically rather than by taste: VQE Ancients
**publishes** its odds (`CalculateOutcomeChances` → `GetOutcomeChance`) [V]; §10 builds the
opposite and prices both.

### What else the corpus does not have

Swept over both roots with `-a -i`, `-g '*.dll'`, `-g '!**/obj/**'`, `-g '!**/Referenced/**'`,
in both the ASCII `#Strings` form and the null-interleaved UTF-16LE `#US` form, each
control-validated against a hit known to exist before any negative was reported:

- `GeneChoice` — **one mod**, VQE Ancients (`Window_GeneChoice`, `architeGeneChoices`).
- `GeneLottery`, `Gene_Lottery`, `ChooseGene`, `Dialog_ChooseGene`, `Dialog_GeneChoice`,
  `RandomGeneChoice` — **zero**, both heaps.
- `lottery` as a word — **zero in the whole corpus**, both heaps.
- **Mechanism-level, not just word-level** — `RandomGene` → five mods, `RandomXenotype` →
  one, `GeneSetMaker` and `RandomizeGenes` → zero. Attributed, the `RandomGene`/
  `RandomXenotype` hits are Xenotype Spawn Control, EdB Prepare Carefully, Biotech for
  Gravship, Medieval Overhaul, World Tech Level and Multiplayer itself [V] — spawn
  weighting, character creation and substring noise. **None offers a player a choice among
  drawn genes.** The mechanism-level sweep is what makes the negative hold: a word-level one
  would miss a mod that shipped this without ever calling it a lottery.
- `ArchiteCapsule` — two mods: VQE Ancients, and More Archotech Garbage, which references
  the item and ships no choice UI, no gene-choice type and nothing named `Window_*` or
  `Dialog_*` in its 1.6 assembly [V].

### `ChoiceLetter` and MP's `Session` — the two routes not taken

- **A `ChoiceLetter` subclass** is the obvious fit and fails on sync twice. Its
  `OpenLetter` already builds a `Dialog_NodeTreeWithFactionInfo` [V], but it is opened from a
  letter-stack click where `MapContext` is null, so no `PersistentDialog` is created; and MP
  syncs vanilla choice-letter options **one lambda at a time, by explicit registration** —
  **13 registration calls covering eight `ChoiceLetter` subclasses** in
  `Multiplayer.Client.SyncDelegates.InitChoiceLetters` — `_ChoosePawn`, `_AcceptJoiner`,
  `_AcceptVisitors`, `_RansomDemand`, `_BabyToChild`, `_BabyBirth`, `_GrowthMoment`,
  `_AcceptCreepJoiner` — e.g.
  `SyncMethod.LambdaInGetter(typeof(ChoiceLetter_AcceptJoiner), "Choices", 0)` [V]. A letter
  of ours is on none of them and its options would activate on one client only. Proposed as
  a trap.
- **`Multiplayer.Client.Persistent.GrowthMomentSession`** is the architecturally perfect
  donor and is read in full [V]: an `ExposableSession` in `map.MpComp().sessionManager`,
  `[SyncMethod] UpdateChoices(int traitIdx, List<int> passionIndexes)` moving the choice as
  indexes, `[SyncMethod] OpenSessionWindow` so the `Rand`-drawing `TrySetChoices` runs inside
  a command on *every* client while only the issuer sees the window, and
  `GetBlockingWindowOptions` to re-open it. It costs a reference to `Multiplayer.API`, which
  this project has never taken, and buys nothing the tick route lacks — our draw is already
  on the tick and needs no seeding. **Recorded as the fallback if the two-client check in
  *Verification* fails.**

---

## Verification

**Already read (no further work needed):**

| Claim | Anchor |
|---|---|
| `Pawn.Kill` is unguarded | `Verse.Pawn.Kill` |
| charge does not decay; fuel/recipient split; donor dies, recipient lives | `Archinity.Building_Altar.Tick`, `.IsFuel`, `.Finish`, `.DrainAndKill`, `.PerformRite` |
| the pool machinery exists, is the right shape, and has zero readers | `Archinity.GenePoolDef.Available`, `.EntryFor`; `Archinity.AltarModifiers.For` |
| T-64 is live exactly as recorded | `Archinity.Building_Altar.PerformRite` |
| a map tick has Multiplayer map context | `Multiplayer.Client.Multiplayer.MapContext` |
| a `Dialog_NodeTree` opened with map context becomes a replayed `PersistentDialog` | `Multiplayer.Client.CancelDialogNodeTree`; `Multiplayer.Client.ForceShowDialogs` |
| the click is synced by index, behind a version guard | `Multiplayer.Client.PersistentDialog.Click` |
| a `Dialog_NodeTree` **subclass** silently loses that path | `Multiplayer.Client.PersistentDialog.CreateInstance`; `Multiplayer.Client.PersistentDialog_NodeTree` |
| a custom `ChoiceLetter`'s options are unsynced | `Multiplayer.Client.SyncDelegates.InitChoiceLetters` |
| MP's seeded-draw and default-choice-on-expiry idioms | `Multiplayer.Client.SyncDelegates.PreLetterChoices`; `Multiplayer.Client.Patches.CloseDialogsForExpiredLetters.RegisterDefaultLetterChoice` |
| MP's session shape for exactly this problem | `Multiplayer.Client.Persistent.GrowthMomentSession`; `.GrowthMomentWindow` |
| the corpus's one shipped implementation, and its window | `VanillaQuestsExpandedAncients.Building_ArchogenInjector.CalculateOutcome` / `.HandleSuccessOutcome` / `.GetFilteredGenes`; `VanillaQuestsExpandedAncients.Window_GeneChoice` |
| MP Compat does not cover that mod | `1629973374/1.6/Assemblies/Multiplayer_Compat.dll` — `vanillaquestsexpanded.generator` only |
| vanilla strips null options from a scribed choice list | `RimWorld.ChoiceLetter_GrowthMoment.ExposeData` |
| the drawable pool's tier and category distribution | `Archinity.Altar/Defs/GenePoolDefs/GenePool_Archite.xml` |

| `mapDialogs` cleanup, and its `InInterface` gate | `Multiplayer.Client.WindowStackTryRemove.Postfix`; `Multiplayer.Client.Multiplayer.InInterface` |
| two contending prefixes on `DiaOption.Activate`, and what arms the flag | `Multiplayer.Client.NodeTreeDialogSync.Prefix`; `Multiplayer.Client.DiaOptionActivate.Prefix`; `Multiplayer.Client.SyncUtil.DialogNodeTreePostfix` |
| `PersistentDialog.Bind` / `.BindAll` are public | `Multiplayer.Client.PersistentDialog` |
| `Resurrect` is commented out in Biotech and defined by no mod | `Data/Biotech/Defs/GeneDefs/GeneDefs_Abilities.xml`; both corpus roots |

**Needs a run, and exactly this much:**

1. **One client — the final rite and its fuel refusal.** Send a founder who has claimed a
   title into the altar with no vector loaded; confirm `VRE_Transcendent` is added and
   `transcendedTick` is set. Then haul that founder in as fuel (prisoner or slave status, so
   `IsFuel` is true) and confirm the refusal, not a death; haul a captured `VRE_Archon`
   prisoner in the same way and confirm it is accepted as fuel. A refusal keyed on the gene,
   or scoped to the pawn instead of the branch, is what this check catches.
2. **One client — the lottery, end to end.** Load a lottery capsule, send an ordinary
   colonist in, and confirm at the rite's end that the charge is debited **once**, the
   capsule is destroyed, four options appear, the dialog has no Close option, and choosing
   one grants that gene as a xenogene with `Archinity_ArchiteSustenance` attached. Then
   repeat on the same pawn and confirm the granted gene is **not** offered again — that is
   `Available()`'s existing exclusion doing the work.
3. **One client — the two silent branches.** (a) Close the offer dialog and let the deadline
   pass; confirm a gene is granted anyway and the pawn is ejected. (b) Save with an offer
   pending, reload, and confirm the four options are the same four.
4. **Two clients — the whole multiplayer claim, and this is the only real risk.** Run the
   rite on one client's altar. Confirm the dialog appears on **both**; that closing it on
   one re-opens it (that is `ForceShowDialogs`); that a click on either client grants the
   same gene on both; and that `Multiplayer > Desync info` is clean afterwards. **Then save
   while the offer dialog is open and reload** — that is the only thing that exercises
   `DelegateSerialization`, and an action accidentally declared on `Building_Altar` throws
   `"Delegate deserialization: method not allowed"` here and nowhere else. If any part of
   this fails, the fallback is MP's own `GrowthMomentSession` shape and a reference to
   `Multiplayer.API` (*Available mechanisms*).
5. **Two clients — the `mapDialogs` leak, which is the check nobody would think to run.**
   After resolving an offer by clicking, and again after letting one lapse to the timeout,
   confirm the dialog **does not come back** when the map is next drawn. That is the only
   observation that distinguishes a correct `resolveTree`/close from a `PersistentDialog`
   left in `mapDialogs`, and the symptom — a settled offer re-opening forever — appears only
   on the client that is looking at that map.

**Watch for, rather than test:** a click on the offer taken while a caravan-meeting or
caravan-demand dialogue is or was recently open. That is the stale-`isDialogNodeTreeOpen`
window in §10, and if the two clients ever grant different genes from one click, this is the
first thing to suspect.

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| **The willing/coerced distinction at the altar** | Today the altar sees prisoner/slave versus not, and `COSMOLOGY.md` § *Devotion* needs believer versus coerced. The routes are [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)'s (*Available mechanisms*) | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) |
| **The tier-band curve** — which `Rand.Value` ranges map to which `[minTier, maxTier]` | Decides what "coherent with the roll" actually feels like, and whether the bad band has teeth. The mechanism works with any curve; without one there is nothing to pass `Available()` | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (balance). `docs/requirements/ALTAR.md` § *Saved state and remaining work*: *"Costs, lottery categories and weights … remain specific design/balance work"* |
| **The lottery capsule's `chargeCost`, and the offer deadline** | Both are single numbers in XML and a constant. Nothing in the build depends on their values | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (balance) |
| **Anti-habituation across repeat draws** — whether a repeat is weighted down, and how | §7 deliberately remembers nothing. Adding a curve later is a weight multiplier inside `Draw`, not a redesign | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) ([#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) closed and left it there) |
| **The symmetric guard — a lottery offer opening while the Administrator dialog is unresolved** | §10's clause 4 stops a founder entering while an offer is pending; **nothing stops the reverse.** `ForceShowDialogs` shows only `mapDialogs.First()`, so the offer queues behind the Administrator dialog, invisible — **while its scribed deadline keeps running**, and the timeout then grants a gene the player never saw offered. It self-heals once the Administrator dialog is answered: T-97 is handled in `TRANSCENDENCE.md` §4 (both options set `resolveTree`), so that dialog does leave `mapDialogs`. The queue delay and the unseen timeout grant remain | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build task). The remedy is one scribed flag recording that the Administrator dialog is *unresolved* — `administratorSeen` records only that it was **shown** [V] — read by `CanAcceptPawn` as a fifth clause. That flag belongs to `CompFounderRecord`, which is [`TRANSCENDENCE.md`](TRANSCENDENCE.md)'s under its rule 1, so this document names it rather than inventing it |
| **Who assembles `CanAcceptPawn`** | Four clauses from three documents, ordering load-bearing — see *Four clauses in `CanAcceptPawn`* above | [#119](https://github.com/cjd721/Rimworld-Archinity/issues/119) (build task) |
| Which genes a pool may offer — core, augment or lottery — and their tiers and categories | Not this document's. Counted: **50 entries, 9 `reserved`, 41 drawable**; by tier `1→1, 2→13, 3→13, 4→10, 5→4`; by category `Survival 11, Work 9, Body 8, Combat 8, Mind 4, Social 1` [V]. **`Social` cannot fill a four-option offer and tier 1 holds one gene** — the first is why §6 weights rather than filters, the second makes the worst band degenerate | [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) — open, **titled *The power grid***; its rows are the vector pools |
| **`VRE_InnatePsylink` in the lottery pool** | The pool offers it (tier 5, `Mind`): a psylink by gene, where `requirements/ALTAR.md` keeps psychic discipleship distinct from genetic augmentation. See `PSYCHIC.md` § *What raises psylink rank besides the altar* (R14) | [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) |
| **Tier 1 needs more drawable genes** before the bad band means anything | A build prerequisite, not a polish item: with one tier-1 gene the lowest band always widens and is indistinguishable from the next. §6 | [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) |
| **`<gene>Resurrect</gene>` is a live dangling reference** | The vanilla `GeneDef` is commented out in `Data/Biotech/Defs/GeneDefs/GeneDefs_Abilities.xml` and no mod in either root defines it [V]. **#10 reported this and was right.** The draw is safe (`Available()` skips a null `gene`) but a pool entry silently does nothing | [#112](https://github.com/cjd721/Rimworld-Archinity/issues/112) |
| `docs/archite-gene-pool.md` does not exist | Cited from `GenePool_Archite.xml` and `GenePool.cs` as the authority for the tier ranking, and absent [V]. Flagged by #10 and still unfixed | [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) |
