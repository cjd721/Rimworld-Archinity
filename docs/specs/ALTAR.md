# The altar

## Purpose and scope

How the altar authors the Transcendent Archogene from the founder standing in it, and
what "death is temporary absence" is made of.

Requirements this implements:

- [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *One apparatus and separate
  rewards* — "Stored charge does not spoil. The sacrificial donor dies; the ordinary gene
  recipient is not killed by the operation." Both are already built and are verified below.
- [`docs/requirements/ALTAR.md`](../requirements/ALTAR.md) § *Saved state and remaining
  work* — founder survival before transcendence, "up until the altar authors the
  Transcendent Archogene".
- [`docs/plot/ENDING.md`](../plot/ENDING.md) § *The Transcendent Archogene* — the only
  Archogene that cannot preexist its owner, and immortality as removal-from-this-reality
  rather than invulnerability.

Established by [#59](https://github.com/cjd721/Rimworld-Archinity/issues/59).

**This document owns the gene and the death rule.** It does not own the per-founder state
store — that is [`TRANSCENDENCE.md`](TRANSCENDENCE.md)'s `CompFounderRecord`, which this
design **reads and extends by one field** rather than duplicating, under that document's
rule 1. It does not own the victory, the Administrator or the crossing (also
`TRANSCENDENCE.md`), the volunteer/Devotion rule
([#49](https://github.com/cjd721/Rimworld-Archinity/issues/49)), which genes sit in which
pool ([#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) — open, and titled
*The power grid* rather than anything about pools; its rows are the vector pools), or the
lottery draw,
which has **no owner today** — see *Outstanding decisions*.

---

## The build

**The Transcendent Archogene is authored per pawn by a `Gene` instance: one static
`GeneDef` in XML whose `geneClass` writes its own contents from the founder at the moment
of the rite and scribes them on that pawn.** Vanilla ships every piece of this, and two
mods in the corpus already ship the shape. (A `GeneDef` itself cannot be minted at
runtime — §1 — which is why the instance, not the def, is the authored artifact.)

| | |
|---|---|
| **Mechanism** | `GeneDef Archinity_Transcendent` (XML) whose `geneClass` is `Archinity.Gene_Transcendent : Gene`. Authoring happens in the virtual `Gene.PostAdd`, where `pawn` is already set. Return-after-death is **one Harmony postfix** on `SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead`, plus part-regrowth on the gene's `TickInterval`. |
| **State** | Fields on the `Gene_Transcendent` instance — what it authored, from whom, and when. Plus **one new field on `CompFounderRecord`** (`TRANSCENDENCE.md`), `archinity_transcendentGeneLoadID`, so the founder record can find its gene without walking the gene list. That field is **sanctioned, not assumed**: `TRANSCENDENCE.md` rule 1 requires founder state to be added to `CompFounderRecord` rather than to a second store, and rule 2's `archinity_` Scribe-key prefix is satisfied verbatim. |
| **Persistence** | `Pawn_GeneTracker.ExposeData` scribes both gene lists with `LookMode.Deep` [V], so the subclass is saved with a `Class=` attribute and `Gene.ExposeData` — which is **virtual** [V] — carries our fields. A save that predates the feature has no such gene. **No migration code.** |
| **Change** | `Building_Altar.PerformRite`, on the altar's already-synced `Tick`, when no vector is loaded and the transcendence preconditions hold. |
| **Display** | The tooltip header over the gene tile, free, via the virtual `Gene.LabelCap`. The Health-tab hediff row and the inspect-pane header are `TRANSCENDENCE.md`'s and already costed there. **The gene tile itself and the info card cannot show it without a patch** — **T-63**, and see *Available mechanisms*. |
| **Cost** | ~135 lines of new C# in the assembly we already ship (`ArchinityAltar.dll`) and ~45 lines of XML. No new assembly, no third-party reference. |

### 1. Why the def cannot be minted, stated once

Four facts, each read at source, and together they close the question:

1. **All def generation happens before any save is read.**
   `DefGenerator.GenerateImpliedDefs_PreResolve` runs inside def loading, and
   `RimWorld.GeneDefGenerator.ImpliedGeneDefs` is the `GeneDef` entry in it [V]. There is
   no later window. The def database is rebuilt from XML on **every** load.
2. **A def added after that never gets a short hash.**
   `Verse.ShortHashGiver.GiveAllShortHashes` runs once, and `Log.Error`s on any def that
   already has one; `DefDatabase<T>.Add` assigns `index` and no hash [V].
3. **A gene stores its def as a defName and re-resolves it.**
   `Gene.ExposeData` is `Scribe_Defs.Look(ref def, "def")`, which saves `def.defName` and on
   load calls `ScribeExtractor.DefFromNode<T>`, which logs *"Could not load reference to
   Verse.GeneDef named X"* and returns **null** [V].
4. **The consequence is already observed in our own corpus.** `docs/data/PARTS-BIN.md`
   records VRE Starjack's runtime-generated astrogenes orphaning genes already saved on
   living pawns when the modlist changes [V]. That is exactly failure 3, in the wild.

So a per-pawn def would have to be re-minted, with a byte-identical defName, before the
save is read — from information that only the save contains. It is not a cost question.

**What this costs in meaning: nothing, if the instance does the authoring.** The cheap
substitute the ticket feared — a pre-authored gene the player simply cannot otherwise
obtain — is *not* what is proposed here and is rejected in *Available mechanisms*. The
def is a **form**; the instance is the **content**, and the content is written from the
founder at the moment of the rite and belongs to nobody else. Founder A's Transcendent
Archogene and founder B's are different objects with different stored contents and
different labels. The cosmology's claim — *"the only Archogene that cannot preexist its
owner"* — survives intact, because the *thing that cannot preexist* is the instance.

### 2. `Gene_Transcendent` — the authored instance

```csharp
public class Gene_Transcendent : Gene
{
    private string  authoredFrom;       // the epithet as claimed, snapshotted at the rite
    private int     authoredTick = -1;
    private List<HediffDef> granted = new List<HediffDef>();   // what it wrote into them

    public override string Label =>
        "Archinity_TranscendentGeneLabel".Translate(authoredFrom ?? pawn.LabelShortCap);

    public override void PostAdd()
    {
        base.PostAdd();
        if (authoredTick < 0) Author();   // first creation only; see the load note below
        Apply();
    }

    public override void ExposeData()
    {
        base.ExposeData();
        Scribe_Values.Look(ref authoredFrom, "archinity_authoredFrom");
        Scribe_Values.Look(ref authoredTick, "archinity_authoredTick", -1);
        Scribe_Collections.Look(ref granted, "archinity_granted", LookMode.Def);
    }
}
```

**`PostAdd` is the authoring hook and `pawn` is live in it.** `GeneMaker.MakeGene` does
`Activator.CreateInstance(def.geneClass)`, sets `def`, `pawn` and `loadID`, then calls
`PostMake()`; `Pawn_GeneTracker.AddGene(Gene, bool)` calls `gene.PostAdd()` as its last act,
after the gene is already in the list [V]. So `PostAdd` can read the whole founder.

**`PostAdd` does not run on load.** Only `ExposeData` does. Anything the gene *did* to the
pawn must therefore be recorded in `granted` and re-applied from it, not re-derived — which
is why `granted` exists rather than being recomputed. VRE Hussars hits this and works around
it by calling its apply routine from `ExposeData`; recording what was granted is the honest
version of the same fix.

**What the gene authors *from* is a requirement, not a mechanism, and it is unwritten.**
No document states which founder facts feed the payload. The mechanism above is
input-agnostic: it can read the claimed epithet (`CompFounderRecord.claimedTitle`), psylink
level, the core vectors carried, the Church title, or any combination, and it writes the
result into `granted`. See *Outstanding decisions*.

### 3. Return after death — vanilla already ships it, minus one clause

This is the largest saving in the design and it was not expected.

`RimWorld.SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead(Pawn)` is a
`public static bool` that returns true when, in order: Biotech is active, the pawn's
`health.ShouldBeDead()` is already true, the pawn has an active `GeneDefOf.Deathless`, and
**the brain is present, not missing, and `GetPartHealth(brain) > 0f`** [V]. When it is true,
`Pawn_HealthTracker.CheckForStateChange` calls `ForceDeathrestOrComa` instead of
`pawn.Kill`, which — for a pawn that cannot deathrest — calls
`SanguophageUtility.TryStartRegenComa` and adds `HediffDefOf.RegenerationComa` [V].

`RegenerationComa` is 420000 ticks with Consciousness capped at `0.1`, and its
`HediffComp_DisappearsPausable_LethalInjuries` **pauses its own countdown for exactly as
long as the pawn would still be dead** [V]. That is, verbatim, *"death here means temporary
absence while they recover the strength to return."* Vanilla wrote it for sanguophages.

**So the gene's whole job is to delete the brain clause.**

```csharp
[HarmonyPatch(typeof(SanguophageUtility),
    nameof(SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead))]
public static class TranscendentAbsencePatch
{
    public static void Postfix(ref bool __result, Pawn pawn)
    {
        if (__result || pawn?.genes == null) return;
        if (!pawn.genes.HasActiveGene(ArchinityDefOf.Archinity_Transcendent)) return;
        if (!pawn.health.ShouldBeDead()) return;
        __result = true;
    }
}
```

Twelve lines. The founders take the `TryStartRegenComa` branch rather than the deathrest
one, because `ForceDeathrestOrComa` tests `pawn.CanDeathrest()` first and the founders
deliberately do not carry Deathrest — `GenePool_Archite.xml`'s `conversionAddsGenes` gives
it to converts precisely so *"every vampire the colony makes must go into the ground
periodically, and the two originals never do."*

**One thing the patch alone does not finish.** If the brain is destroyed, the coma's
countdown is paused forever by `HediffComp_DisappearsPausable_LethalInjuries` and the
founder is permanently comatose rather than temporarily absent. `Gene_Transcendent` must
therefore regrow missing parts while the coma is present — walk `hediffSet` for
`Hediff_MissingPart` and remove them on a slow interval from `Gene.TickInterval`, which is
virtual [V]. ~25 lines. That regrowth **is** the fiction: the body is being rebuilt from
beyond, and the pause is what makes the absence last exactly as long as the damage does.

**Reuse `RegenerationComa` rather than authoring our own.** Our own def would need its own
duration, text and pausable comp, and buys only flavour; the duration is a Balance number
either way. If the flavour is wanted later it is a copied def and a changed argument to
`TryStartRegenComa`, not a redesign.

### 4. The defect this exposes in code we already ship

`Building_Altar.DrainAndKill` calls `victim.Kill(null)` directly [V]. **No vanilla path
guards `Pawn.Kill`** — not Deathless, not `preventsDeath`, not the coma (§*Available
mechanisms*). A transcended founder hauled into the altar as fuel would be permanently
killed by our own code, past every protection this document builds.

**The refusal is scoped to the fuel branch, never to the pawn**, and this is load-bearing.
`TRANSCENDENCE.md` § *The Administrator, the choice, and coming back* requires that a
transcended founder (`transcendedTick >= 0`) **is** an acceptable occupant of the altar
with no vector loaded, because entering in that state is leaving the universe — it is the
standing re-offer of the ending. A clause refusing *a transcended pawn* would delete that
ending silently. What is refused is **being drained**: the new test sits inside
`CanAcceptPawn`'s existing `if (IsFuel(p))` branch — the same branch whose result is
latched into `draining` by `TryAcceptPawn` and read by `Finish()` [V] — and returns
`Archinity_AltarTranscendentNotFuel` when the occupant carries the Transcendent Archogene.
~5 lines.

**Both clauses land in the same method and must be authored together.** The fuel branch
gains this refusal; the recipient branch's `ext == null` arm, which today returns
`Archinity_AltarNoVector` unconditionally [V], is where `TRANSCENDENCE.md`'s departure
entry is accepted instead for a transcended founder. Authored separately, whichever lands
second is written against a method the other has already changed, and the failure mode of
getting it wrong is either a permanently dead founder or an unreachable ending. The
departure arm itself is `TRANSCENDENCE.md`'s and is costed there.

### 5. Where the player sees it

| Surface | Mechanism | New code |
|---|---|---|
| Tooltip header over the gene tile: *"the Transcendent Archogene of Aria, She Who Does Not Ask"* | virtual `Gene.LabelCap`, used by `GeneUIUtility.DrawGene` for the tooltip title [V] | none |
| The gene tile label, and the info card | **Not available — T-63.** `DrawGeneBasics` is typed on `GeneDef` and `Dialog_InfoCard` is constructed from `gene.def` [V], so a per-instance label reaches neither. See *Available mechanisms* | n/a without a patch |
| The Health tab row, the inspect-pane header | `TRANSCENDENCE.md`'s `Archinity_FounderRecord` hediff and `Pawn_StoryTracker.title` | none here |
| The rite completing, and each return from absence | letters | ~15 lines |
| *"X cannot be given to the altar"* when a transcended founder is hauled **as fuel** — the altar still accepts them with no vector loaded, which is the departure | `CanAcceptPawn` refusal string, inside the `IsFuel` branch only (§4) | ~5 lines |

### Cost

| Piece | Kind | Estimate | Lands in |
|---|---|---|---|
| `GeneDef Archinity_Transcendent` (incl. `geneClass`) | XML | ~25 lines | `Archinity.Altar/Defs/GeneDefs/` (new) |
| Keyed strings (gene label, letters, refusal) | XML | ~20 lines | `Archinity.Altar/Languages/English/Keyed/` |
| `Gene_Transcendent : Gene` — author, apply, scribe | new C# | ~60 | `Archinity.Altar/Source/GeneTranscendent.cs` (new) |
| Missing-part regrowth on `TickInterval` | new C# | ~25 | same file |
| `TranscendentAbsencePatch` | new C# | ~12 | `Archinity.Altar/Source/Patches.cs` |
| `PerformRite` no-vector branch; `CanAcceptPawn` fuel refusal | new C# | ~20 | `Archinity.Altar/Source/Building_Altar.cs` |
| Letters — the rite completing, and each return from absence (§5) | new C# | ~15 | `Archinity.Altar/Source/Building_Altar.cs`, `GeneTranscendent.cs` |
| One field on `CompFounderRecord` | new C# | ~3 | `TRANSCENDENCE.md`'s file |

**~135 lines of C# into the assembly we already ship, plus ~45 lines of XML.** The rows
sum to that; an earlier headline of ~120 omitted the letters row, which §5 prices and the
table did not carry.

---

## Persistence and multiplayer

### Save and load

- **The gene instance.** `Pawn_GeneTracker.ExposeData` scribes `xenogenes` and `endogenes`
  with `LookMode.Deep` [V], so the concrete subclass is written with a `Class=` attribute
  and rehydrated as itself. `Gene.ExposeData` is virtual, so our fields ride along.
- **A pre-feature save** carries no `Archinity_Transcendent` gene at all. Nothing to
  migrate, nothing to version.
- **`PostAdd` does not run on load** — only `ExposeData` [V]. Side effects must be replayed
  from `granted`, never re-derived, or two loads of the same save produce two different
  founders.
- **Never rename or remove `Archinity_Transcendent`.** By fact 3 in §1, a saved gene whose
  defName no longer resolves becomes a null-def entry in the tracker list. This is the same
  hazard `TRANSCENDENCE.md` records as **T-34** for comps, arriving through a different door.

### Multiplayer

| Path | How it is safe |
|---|---|
| The rite completing | `Building_Altar.Tick` — the altar's already-synced tick, where `PerformRite` and its `Rand.Value` roll already live [V]. `Rand` reached from a synced tick is deterministic by construction (`CODING_STANDARDS.md` § *Divergence*). |
| Entering the altar | `Building_Enterable.SelectPawn`, registered by Multiplayer in `Multiplayer.Client.SyncDelegates`; `Building_Altar` does not override it [V, via `TRANSCENDENCE.md` §3]. |
| The death interception | `SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead` is a pure read over pawn state, called from `Pawn_HealthTracker.CheckForStateChange` on both clients from the same damage event. Our postfix reads only the gene list and `ShouldBeDead()`. No new synchronisation. |
| Part regrowth | `Gene.TickInterval`, driven by the pawn's tick. |
| Our gene instance being MP-serializable | **[I] — not verified.** `TRANSCENDENCE.md` verified the equivalent for `HediffComp`; the `Gene` case has not been read. Named as a check in *Verification*. |

**Divergence gate.** The authoring step must read **only** pawn state and the founder
record. No `ModSettings`, no `Prefs`, no `Find.CurrentMap`, no wall clock. This is not
hypothetical caution: `docs/data/PARTS-BIN.md` blocks VRE Starjack precisely because
`Gene_Randomizer.PostAdd` reads a client-local settings value and consumes a different
number of `Rand` draws per client [V]. **The nearest existing implementation of this
mechanism is a desync**, and avoiding it is a one-line rule. **Passes, as specified.**

**Loudness gate.** Weak, and stated rather than hidden. A gene that authors the wrong
payload produces a wrong founder, not an error. The mitigating design choice is `granted`:
what was written is recorded, inspectable in the save, and replayed rather than recomputed.

---

## Failure and recovery

| Failure | Detection | Recovery |
|---|---|---|
| `Archinity_Transcendent` renamed or removed from the defs | **Loud but late** — `"Could not load reference to Verse.GeneDef named …"` on the next load, and a null-def entry in the tracker | Prevention only. Never rename it. §1 |
| A transcended founder hauled into the altar as fuel | **Silent** — our `DrainAndKill` calls `Pawn.Kill` directly, which nothing guards | The `CanAcceptPawn` clause in §4, **inside the `IsFuel` branch**. Without it this is a campaign-ending bug |
| That clause written against the pawn instead of the fuel branch | **Silent, and worse** — the altar refuses a transcended founder outright and the ending stops being reachable | §4. Scope it to `IsFuel` / `draining`; `TRANSCENDENCE.md` needs the no-vector entry to keep working |
| Brain destroyed, coma entered, never leaves it | Visible: a permanently comatose founder with a paused countdown | The `TickInterval` regrowth in §3. Without it, absence is permanent |
| The authored label appears nowhere the player looks | **Silent — T-63.** The tile draws the def label and no error occurs | Expected, by design. The identity is carried by the hediff and the inspect pane (`TRANSCENDENCE.md`), not the gene tile |
| `PostAdd` re-authors on load and overwrites the original | Would be silent | `authoredTick < 0` guards it. §2 |
| Two founders transcend in the same tick | Two independent gene instances on two pawns | No interaction |

**No campaign softlock.** Every branch degrades to "the altar refuses and says why", except
the two marked above, both of which are closed by the clauses in §3 and §4.

---

## Status

**Evidence class: READ.** Settled from 1.6 defs and decompiled assemblies —
`Assembly-CSharp.dll` (`RimWorldWin64_Data/Managed/`), `VREHussars.dll`
(`vanillaracesexpanded.hussar`, `1.6/Assemblies/`),
`VanillaRacesExpandedStarjack.dll` (`vanillaracesexpanded.starjack`, `1.6/Assemblies/`),
and our own `ArchinityAltar.dll`. Corpus verified against `docs/data/MOD-SNAPSHOT.md`
(`corpus.py --check`: 155 mods, matches) at the start and end.

**Verified available mechanisms:**

- `GeneDef.geneClass` as a `Type` validated by `ConfigErrors`, instantiated by
  `GeneMaker.MakeGene` via `Activator.CreateInstance` [V].
- `Gene.PostAdd`, `Gene.ExposeData`, `Gene.Label`/`LabelCap` and `Gene.TickInterval` as
  **virtual** members, with `pawn` set before `PostAdd` runs [V].
- `Pawn_GeneTracker.ExposeData` scribing both gene lists `LookMode.Deep` [V].
- `SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead` and
  `HediffDefOf.RegenerationComa` as a shipped, pausable "temporary absence" [V].
- `HediffDef.preventsDeath` short-circuiting `Pawn_HealthTracker.ShouldBeDead()` ahead of
  every other check **except the `if (Dead) return true;` that precedes it** — and **set by
  no def in vanilla, the DLC, or the corpus** [V].
- The altar's charge, the fuel/recipient split and the kill/survive asymmetry, all already
  built in `ArchinityAltar.dll` [V] — see below.

**Proposed, and [I] until compiled:** that these compose into the behaviour described.
Each mechanism is [V]; the composition is not.

**Selected:** nothing. This is the design #59 returned; the commitment is Conrad's.

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
  believes nothing is treated identically to a devout volunteer. `docs/COSMOLOGY.md`
  § *Devotion* makes that difference load-bearing, and the altar does not express it at all
  today. That is a requirements gap, handed to #49.
- **Donor dies, recipient survives.** `Finish()` branches on `draining`:
  `DrainAndKill(occupant)` → `victim.Kill(null)` and places the corpse, versus
  `PerformRite(recipient)` → `EjectRecipient` [V]. Confirmed, with the caveat in §4.

### Vanilla mints `GeneDef`s in code — at load, and only at load

`RimWorld.GeneTemplateDef` plus `GeneDefGenerator.GetFromTemplate` generate one `GeneDef`
per `SkillDef` and per addictive `ChemicalDef`, yielded from `ImpliedGeneDefs` into
`DefGenerator.GenerateImpliedDefs_PreResolve` → `AddImpliedDef` → `DefDatabase<GeneDef>.Add` [V].

**The corpus does the same, in 1.6, today.** VRE Hussars ships
`VREHussars_GeneDefGenerator_ImpliedGeneDefs_Patch`, a Harmony **postfix on
`GeneDefGenerator.ImpliedGeneDefs`** that mints one gene per qualifying weapon `ThingDef`
from its own `WeaponGeneTemplateDef` [V]. VRE Starjack and VRE Android carry the same
patch [V]. `docs/data/PARTS-BIN.md` already records the Hussar postfix.

So *"a GeneDef can be created in code"* is a firm **yes** — and it is the wrong yes. Every
one of these runs during def loading, before a save exists, from static data. None of them
can see a pawn. That is the whole finding of §1.

### The corpus donors for the per-instance substitute

Both are live 1.6 assemblies and both ship the exact shape proposed:

- **`VREHussars.Gene_Weapon`** — a `Gene` subclass overriding `PostAdd`, `PostRemove` and
  `ExposeData`, registering per-pawn state on add and unregistering on remove, and calling
  its apply routine from `ExposeData` because `PostAdd` does not run on load [V].
- **`VanillaRacesExpandedStarjack.Gene_Randomizer`** — a `Gene` subclass whose `PostAdd`
  writes genes onto its own pawn and then removes itself [V]. Also the desync example cited
  under the divergence gate.

### The nearest vanilla donor for "the player authors a genetic artifact that persists"

`RimWorld.CustomXenogerm` — a player-typed `name`, a `List<GeneSet>`, an icon, deep-scribed
into `CustomXenogermDatabase` on the `Game` [V]. It is the proof that runtime-authored,
player-named, persistent genetic content is ordinary in this engine. It is **not** a donor
for our case, because it composes existing `GeneDef`s and mints none — which is exactly the
line this design also respects, one level down.

### `HediffDef.preventsDeath` — stronger than Deathless, and used by nobody

`Pawn_HealthTracker.ShouldBeDead()` opens with `if (Dead) return true;` and **only then**
returns **false immediately** on `hediffSet.HasPreventsDeath`, ahead of the
required-capacity, core-part and lethal-damage checks [V]. It is first among the *living*
checks, not first in the method — an already-dead pawn is unaffected by it.
`HediffSet.HasPreventsDeath` is `hediffs.Any(h => h.def.preventsDeath)` [V].
The field has exactly two occurrences in the whole 1.6 assembly — its declaration and that
one read — and a sweep of both corpus roots plus `common/RimWorld/Data` for the XML field
name returns **zero** [V]. It is an unused vanilla switch that no def anywhere sets.

**Not selected, for a reason worth stating.** It grants "cannot die", not "temporary
absence": no corpse, no letter, no mourning, no return — the fiction's entire second half
disappears. It is recorded here as the one-field XML fallback if §3's coma route proves
unworkable, and as an engine fact regardless.

### What `Deathless` actually does, correcting the ambient assumption

`Pawn_HealthTracker.ShouldBeDead()` contains **no Deathless check at all** [V].
`GeneDefOf.Deathless` is special-cased at ten discrete call sites — executions,
bloodfeeding, surgery outcomes, childbirth, MTB death, the death-on-downed roll, and two
UI strings — and the load-bearing one is the coma interception in §3 [V].
`Verse.Gene_Deathless` itself holds only `lastSkillReductionTick` and a `PostRemove` [V],
confirming what `TRANSCENDENCE.md` says about it.

**[#11](https://github.com/cjd721/Rimworld-Archinity/issues/11)'s claim is confirmed
against 1.6, and now has an anchor.** "Deathless and fast-healing, brain destruction kills
permanently" is precisely the brain clause inside
`ShouldBeDeathrestingOrInComaInsteadOfDead` — brain present, not missing,
`GetPartHealth(brain) > 0f` [V]. `docs/plot/NEOLITHIC.md`'s note that the behaviour "still
needs reading against 1.6" is discharged.

**And one thing nothing guards: `Pawn.Kill`.** Neither Deathless, nor `preventsDeath`, nor
the coma intercepts a direct call [V]. Every protection in this document is a property of
the *damage* path. §4 is the consequence.

### What was ruled out, and why

- **A pre-authored gene the player cannot otherwise obtain**, with no per-pawn content.
  This is the cheap answer the ticket named, and it does cost what the ticket feared: the
  Transcendent Archogene becomes a reward with a locked door, identical on both founders,
  and `COSMOLOGY.md`'s *"cannot preexist its owner"* becomes false in a way the campaign
  itself would notice. The instance-authoring design costs ~60 lines more and keeps the
  claim true, which is why it is recommended instead.
- **Minting the def and re-minting it on every load from a `GameComponent`.** Requires the
  defName to be derivable before the save is read, which for per-pawn content it is not,
  and leaves every such gene one modlist change away from orphaning. §1.
- **Patching the gene tile to show the instance label.** This is **T-63**: overriding
  `Gene.Label` reaches the tooltip header and nothing else, because the tile is drawn by
  `DrawGeneBasics(GeneDef, …)` and the info card is `new Dialog_InfoCard(gene.def)` [V] —
  both def-typed, so a per-instance label is silently invisible on both. It is achievable —
  VRE Starjack prefixes `GeneUIUtility.DrawSection` to pull its own genes out of the list
  and redraw them in a postfix [V], and that prefix exists **because of** T-63 — and it
  costs ~50 lines plus a patch on a private method, for a label. The
  identity already displays on the inspect pane and the Health tab through
  `TRANSCENDENCE.md`'s work. Rejected on price.
- **`GeneDef.statOffsets` for the authored payload.** Def-level, therefore identical on both
  founders, therefore not authored. The payload is granted per instance at `PostAdd` and
  recorded in `granted` instead.

---

## Verification

**Already read (no further work needed):**

| Claim | Anchor |
|---|---|
| `geneClass` is a `Type` on `GeneDef`, validated at load | `Verse.GeneDef.ConfigErrors` |
| the instance is constructed from it, with `pawn` set | `RimWorld.GeneMaker.MakeGene` |
| `PostAdd` runs last, after the gene is in the list | `RimWorld.Pawn_GeneTracker.AddGene(Gene, bool)` |
| `Label`, `LabelCap`, `ExposeData`, `TickInterval`, `PostAdd` are virtual | `Verse.Gene` |
| gene lists are scribed `LookMode.Deep` | `RimWorld.Pawn_GeneTracker.ExposeData` |
| a gene's def is stored as a defName and re-resolved | `Verse.Gene.ExposeData`; `Verse.Scribe_Defs.Look`; `Verse.ScribeExtractor.DefFromNode` |
| def generation happens only during def load | `RimWorld.DefGenerator.GenerateImpliedDefs_PreResolve`, `AddImpliedDef` |
| a later-added def gets no short hash | `Verse.ShortHashGiver.GiveAllShortHashes`; `Verse.DefDatabase\`1.Add` |
| vanilla mints GeneDefs from templates | `RimWorld.GeneTemplateDef`; `RimWorld.GeneDefGenerator.GetFromTemplate` |
| the corpus mints them by postfix | `VREHussars.VREHussars_GeneDefGenerator_ImpliedGeneDefs_Patch` |
| the per-instance substitute ships in 1.6 | `VREHussars.Gene_Weapon`; `VanillaRacesExpandedStarjack.Gene_Randomizer` |
| coma-instead-of-death, and its brain clause | `RimWorld.SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead` |
| the coma is entered, and by which branch | `Verse.Pawn_HealthTracker.ForceDeathrestOrComa`; `RimWorld.SanguophageUtility.TryStartRegenComa` |
| the countdown pauses while the pawn would still be dead | `Verse.HediffComp_DisappearsPausable_LethalInjuries.Paused`; `Biotech/Defs/HediffDefs/Hediffs_Various.xml` `RegenerationComa` |
| `preventsDeath` short-circuits `ShouldBeDead` after its opening `if (Dead) return true;`, and nothing sets it | `Verse.HediffDef.preventsDeath`; `Verse.HediffSet.HasPreventsDeath`; `Verse.Pawn_HealthTracker.ShouldBeDead` |
| `Pawn.Kill` is unguarded | `Verse.Pawn.Kill` |
| the tile and info card are def-typed | `RimWorld.GeneUIUtility.DrawGeneBasics`; `RimWorld.GeneUIUtility.DrawGene` |
| charge does not decay; fuel/recipient split; donor dies, recipient lives | `Archinity.Building_Altar.Tick`, `.IsFuel`, `.Finish`, `.DrainAndKill`, `.PerformRite` |

**Needs a run, and exactly this much:**

1. **One client, dev mode.** Add `Archinity_Transcendent` to a pawn; confirm the instance is
   a `Gene_Transcendent` and the tooltip header shows the authored label. Save, reload,
   confirm the fields survive and `PostAdd` did not re-author.
2. **One client.** Destroy a transcended founder's brain. Confirm `RegenerationComa` is added
   rather than death, that the countdown is paused while parts are missing, that regrowth
   clears them, and that the founder then wakes. This is the entire §3 risk.
3. **Two clients.** Perform the rite on each player's founder, confirm both see the same
   authored label on both founders, and that `Multiplayer > Desync info` reports no desync.
   **This is also the check for the one [I] above** — whether MP serialises a `Gene`
   reference is unread, and this exercises it.
4. **One client, both halves of §4's method.** Haul a transcended founder to the altar as
   fuel (prisoner or slave status, so `IsFuel` is true) and confirm the refusal, not a
   death. Then load no vector and send the same founder in as an occupant, and confirm the
   altar still **accepts** them — that is `TRANSCENDENCE.md`'s departure, and a refusal
   scoped to the pawn instead of the branch is what this check catches.

---

## Outstanding decisions

| Question | Consequence | Owner |
|---|---|---|
| **What the gene is authored *from*** — which founder facts become the payload | Decides what `PostAdd` reads and what goes in `granted`. The mechanism works with any answer; without one there is nothing to write | **gap — no owner.** Not in `docs/requirements/ALTAR.md`, not in `ENDING.md`, and #49's scope does not reach it |
| **The willing/coerced distinction at the altar** | Today the altar sees prisoner/slave versus not, and `COSMOLOGY.md` § *Devotion* needs believer versus coerced | [#49](https://github.com/cjd721/Rimworld-Archinity/issues/49) |
| How long absence lasts, and whether it scales | `RegenerationComa` ships 420000 ticks; any other number is a def edit | Balance |
| **The lottery draw** — what selects the four options, where the offer lives across a save, and how two players resolve one dialog | `GenePoolDef.Available()` and `EntryFor()` have **zero call sites**; `categoryBias` and `extraOptions` are computed and never read; and **T-64** — ours — a `GeneVectorExtension` with `gene: null`, documented as "the lottery", spends the charge, destroys the vector, grants nothing **and prints a success message** [V] | **no ticket exists.** #10 settled the rules and said "Mechanism is open". The nearest standing ticket is [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31), **titled *The power grid*** and open with no comments; its rows are vector pools, so it is a defensible home for *which genes the draw may offer* but not for the draw mechanism, and its title will not tell a reader that. See the resolution comment on #59 |
| Which genes a pool may offer — core, augment or lottery | Not this document's | [#31](https://github.com/cjd721/Rimworld-Archinity/issues/31) — open, **titled *The power grid***; its rows are the vector pools |
