# Working a capability research ticket

How the answer gets built and how the evidence gets gathered. Where the answer lands is
`docs/specs/README.md`'s business, and the ticket footer already carries it.

## The question

A capability ticket asks:

> **Does the game already do this? If it does, what carries it, at what cost, and is it
> multiplayer-safe? If it does not, what is the cheapest thing we can build — using which
> levers, which donors and which workarounds — and what does that cost?**

Both halves are the ticket. Naming the provider mod is part of the first — the sourcing
ledger (#14) consumes exactly that verdict, and "XML, a patch, or new C#" is unanswerable
without it. Writing the patch belongs to whoever implements; **saying what to write belongs
here.**

### A negative is half an answer

**"Nothing carries this" does not resolve a ticket.** It is a finding on the way to one.
A resolution whose headline is a confirmed negative is **unfinished** until it also proposes
a build, and the proposal answers all six of these:

| | |
|---|---|
| **Mechanism** | What the thing actually is — a `WorldComponent`, a Def plus a worker, a Harmony postfix on a named method. |
| **State** | Where the number, the flag or the record lives, and what owns it. |
| **Persistence** | How it is scribed, and what happens when it is added to a save that predates it. |
| **Change** | What increments, decrements or writes it, and from which already-existing hook. |
| **Display** | Where the player sees it. A number the player cannot see is not a feature. |
| **Cost** | XML, a patch, or new C# — with a line estimate and the file it lands in. |

If one of the six genuinely belongs to another ticket, say which ticket **by number**, and
check that it exists. #52 wrote *"the UI half is a separate ticket"* about a ticket that had
never been created, and the resulting spec could not answer the question that had been asked.
**A deferral to a ticket that does not exist is a gap, not a hand-off.**

If one of the six is a *requirement* rather than a mechanism, hand it back — see
**Requirements stay where they live**, below. That is a different move from deferring it to
a capability ticket, and it is also written down rather than left implicit.

### Propose the build even when it is ugly

The point is not an elegant design; it is a *priced* one. "Reimplement ~40 lines of the mod
we are not shipping", "one `GoodwillSituationDef` and a `workerClass`", "four Harmony
postfixes in the assembly we already ship" are all complete answers. **"It would need custom
code" is not** — every negative would need custom code, which is why saying so adds nothing.

Where two builds are plausible, name both, recommend one, and say what separates them.
Where the build is genuinely blocked by an engine fact, that fact **is** the answer: state
it, and bring the conflict back rather than inventing a weaker substitute quietly.

## Scoping: a ticket is a behavior, not a seam

**A capability is something the game must be able to do, defined by observable behavior**
(map #2). The corollary is the rule that is easy to get wrong:

> **Split by behavior. Never split by implementation seam.**
> Storage, hooks, persistence and UI are *sections of a spec*. They are not tickets.

One behavior, one ticket, **however many clauses its resolution needs**.

**What actually caused the splitting, stated accurately, because the obvious culprit is not
it.** Map #2 used to carry a sizing rule — *"a ticket whose resolution comment would need more
than one clause is the wrong size"* — and it has been replaced. But it was added on
2026-09-08 at 01:50Z, *after* #52, #54, #55, #57 and #61 already existed, so it cannot have
caused those. The rule that did the work is the anti-bundling one: *"every capability gets its
own ticket… none may be bundled with another capability."* #74's own body cites exactly that —
*"Every capability gets its own ticket, so this is not left inside #52 as a bullet."*

**Read as written it is correct. Read as "anything separable is a separate capability" it
shreds behaviors**, because storage, hooks and UI are always separable. Nothing said they were
not capabilities, so they became tickets. The rule above is the missing half.

**The worked failure.** Reverence — *"faction ABC has 57 Devotion, so their Reverence is
57/100, and I can see it"* — was cut into three: the number (#52), the events that move it
(#74), and a UI ticket that was never created. #52 resolved honestly and its spec still could
not answer the question, because two thirds of the behavior lived elsewhere and one third
lived nowhere. When it was re-run whole as #98, the same method found the apostle hook vanilla
already ships **and corrected two load-bearing claims** the seam-split version had left
standing.

**The worked success, same doc and same method.** #90 was scoped to a behavior — *goodwill
ripples along the faction graph* — and came back with a build: read NPC↔NPC edges, write
player↔X, seed the empty edge set, reuse VEF's delayed-goodwill queue, four Harmony postfixes,
~80–100 lines in the assembly we already ship. **The difference was the scope, not the
research.**

**Before starting, check the ticket's own shape.** If it asks about one seam of a behavior
whose other seams sit on sibling tickets, say so in the resolution and name the siblings.
Re-scoping the map is Conrad's call, not the agent's — but an unreported seam is how the spec
ends up unanswerable.

## Who writes what

**The agent that resolved the ticket writes the spec.** It has the assemblies open and
the evidence in working memory; nobody else will ever be as cheap to write it. One
session produces all three outputs the footer names — the resolution comment, the
`docs/specs/` section, and any `docs/engine/` or `docs/TRAPS.md` entry — and reports a
short summary upward.

**The spec section leads with the build.** `docs/specs/README.md` carries the section order;
follow it. The proposed mechanism comes first and the survey evidence supports it — not the
other way round. A reader must not have to descend past a catalogue of absences to find out
what we are going to do.

**An orchestrator running several of these reviews and merges; it does not re-derive.**
Pulling four full resolutions back through one context to write four specs from them is
the expensive way to get a worse result, and it was tried: the first batch of four cost
roughly 120KB of resolution prose re-read by the orchestrator to reconstruct what the
agents already knew.

Two things stay with the orchestrator, because parallel sessions collide on them:
**shared documents** — `docs/data/`, the map body, `docs/TRAPS.md`'s index table — and
**closing the ticket**. An agent proposes an entry for those; it does not write one.

## The corpus

**155 mods on disk. 93 of them inactive.** `docs/data/MOD-SNAPSHOT.md` is the roster
and the version pin; regenerate or diff it with `python tools/corpus.py` (`--help`
for the modes).

**The corpus spans two roots**, and this catches people:

- `steamapps/workshop/content/294100/` — 145 mods
- `steamapps/common/RimWorld/Mods/` — 83 mods, 77 of which are second copies of a
  workshop mod declaring the same `packageId` (**T-22**)
- plus vanilla and the DLC under `common/RimWorld/Data/`

`corpus.py` hardcodes only the workshop root. **A sweep that searches one root has
searched 145 of 155 mods and will feel complete.** Search both, always.

Every other tool in `tools/` narrows to the active set before it starts — `defdb.py`
reads `config/ModsConfig.xml`, and `patch_check.py`, `audit_research.py` and
`inventory.py` all build on it. That is right for "what will RimWorld build from
today's load order" and wrong for research.

**The active split carries no weight here.** The shipping mod set is an output of the
map, not an input, and mods that conflict today are ones we intend to patch. VFE
Empire and VFE Deserters sit inactive right now, and they are the named donors for
Exaltation, Influence, Intel and Trace. Ask the active database what carries Honor and
it says nothing.

That is the **false negative**, and it is the expensive error: it sends us to write an
assembly we already had. A wrong "yes" costs a second look; a wrong "no" costs months.

**And the split carries no weight in the answer either, not just in the search.** A
resolution names the **carrier** — the mod, the assembly, the method. It does not
report whether that mod is enabled today, does not treat "currently off" as a finding,
and never recommends a load-order change. `config/ModsConfig.xml` is an output of the
map. Writing "the fix ships but is disabled, enable it" turns a capability verdict into
a chore list and re-imports the very distinction this section exists to delete; the
verdict is *"`rwmt.multiplayercompatibility` carries it"*, full stop. Which mods ship is
[the sourcing ledger](https://github.com/cjd721/Rimworld-Archinity/issues/14)'s to decide.

## The wide pass

Search wide, read narrow. Grepping 155 mod folders takes seconds; reading them takes
days. The asymmetry that follows:

> A **positive** answer may stop the moment it is found.
> A **negative** answer is not finished until the wide pass has run — and then it is still
> not finished until it proposes a build.

"Empire Honor carries this" — done, go read Empire. "Nothing carries this" — only
worth something if you looked everywhere first, and only *finished* once you have said what
we build instead.

Four tiers, and most tickets stop at the second:

1. **The repo's own indexes.** `docs/TRAPS.md` and `docs/engine/` for what is already
   verified, `docs/data/PARTS-BIN.md` and `MOD-VERDICTS.md` for what each mod supplies,
   `scratch/` for recon. Free, and already graded [V]. They are indexes into the
   corpus, not substitutes for it: PARTS-BIN surveyed 108 mods and MOD-VERDICTS 130,
   against 145 workshop mods on disk today. **A mod missing from them was not
   assessed and rejected — it postdates the survey.** Its absence is silence, and
   silence is a reason to run the wide pass.
2. **Vanilla, the five DLC, and the mods the ticket names.** Read them properly. This
   is the work.
3. **The wide pass** — grep the whole corpus for the symbol, def type or field name.
   Run it to justify any negative. See **Searching what the mods actually ship**,
   below, because the naive form of this silently misses most of the corpus.
4. **Depth-read whatever tier 3 turned up.**

Ushanka's Hacking Expansion ships full 1.6 C# for exactly the mechanism #58 asks
about. It appears in no repo doc and is inactive, so tiers 1 and 2 both miss it and
tier 3 finds it in one grep.

**A fifth pass, when the answer is negative: read the nearest donor anyway.** Vanilla's
`GoodwillSituationManager` carries no stored per-faction value and is still the architecture
Reverence copies. The mechanism you build is almost always a shipped mechanism with one piece
replaced — find that mechanism and say which piece.

### Searching what the mods actually ship

**Most of the corpus is compiled assemblies with no source.** A plain `rg` over `.cs`
files searches roughly a fifth of it and returns a clean-looking nothing. Four
tickets in a row independently rediscovered this; it is written down now.

- **ripgrep skips binaries by default.** Pass `-a` and glob `-g '*.dll'`, or the
  assemblies are simply not searched.
- **Type and member names** live in the assembly's `#Strings` metadata heap as
  ASCII. A normal `rg -a` finds these.
- **String literals** — including every `Scribe` key, every `defName` looked up by
  string, every `AccessTools.TypeByName` argument — live in the `#US` heap as
  **UTF-16LE**. An ASCII grep misses all of them. Run the pass a second time with
  `--encoding utf-16le`. Ticket #52's only live hit came from that second pass.
- **A namespaced type is stored split.** `System.Random` is a TypeRef whose namespace
  and name are separate strings; grepping the literal `System.Random` finds nothing.
  Grep the bare name (`Random`), then narrow. Ticket #88 filtered 1,057 dlls to 276
  on the null-terminated ASCII name, deduped by SHA-1, collapsed to one 1.6-loading
  copy per mod, and depth-read the surviving 71.
- **Four mods vendor a publicised copy of `Assembly-CSharp.dll`** — six files across
  `2836791007`, `2990596478`, `3241944893` and `3563882422`. A `.dll` wide pass reads
  **vanilla's entire metadata** back as a hit and attributes it to whichever mod ships the
  copy, so the sweep reports a mod carrying the mechanism when what it carries is a build
  artifact. #98's passes were polluted by this until they were fixed.
  **The one reliable filter is `-g '!**/obj/**'`, not the path**: the six sit under
  `Source/obj/Debug/…`, `Source/obj/Release/…` *and* `Source/RimFantasy/obj/Debug/…`, and 18
  mods ship some `.dll` under an `obj/` directory. Exclude `obj/` from every sweep — nothing
  the game loads lives there.
- **Generic instantiations are invisible to text search.** A
  `Dictionary<Faction, float>` field lives in the `#Blob` heap as a type signature,
  not as a readable string. No grep will find it. Bound this class of question by
  enumerating the assemblies that reference a related type at all, then reading
  them — or accept a stated residual gap, as #52 did.

**A metadata-name hit is [I], not [V].** The `#Strings` heap proves an identifier
exists; it says nothing about what the method does. Two of #90's headline finds
evaporated on decompilation — `AffectAlliedFactionGoodwill` writes to one stored
faction, not a graph. **Tier 3 finds candidates; only tier 4 finds answers.**

### Validate the sweep before you trust its negative

**A broken sweep and a clean negative look identical.** #88's sweep returned zero
hits for two full runs because a CRLF in a generated path list made every `ilspycmd`
invocation fail quietly.

> Before reporting "nothing in the corpus does X", run the same sweep against a hit
> you already know exists. If it does not come back, the sweep is broken, not the
> corpus empty.

## Stale source

**18 mods ship C# source that is not for 1.6.** VFE Empire ships 176 `.cs` files under
`1.4/Source/`, none under `1.5/` or `1.6/`, and a *different* `VFEEmpire.dll` for each
of the three. Read that source and you have described 1.4 while the game runs 1.6.
Issue #73 did it, quoting a 1.4 line count as a 1.6 fact.

Source is not merely stale, it is **actively misleading**: #88's source half produced
a false positive (VFE Tribals code absent from the 1.6 assembly), an undercount (6
sites where the assembly has 9), and missed the answer entirely (VEF ships no source
at all).

`MOD-SNAPSHOT.md` marks these **⚠**, and `corpus.py --which` says so per mod. Where
source is stale or absent, decompile the assembly the game actually loads:

```bash
ilspycmd -l c "<mod>/1.6/Assemblies/<Name>.dll"     # list types first
ilspycmd -t <Namespace.Type> "<mod>/1.6/Assemblies/<Name>.dll"   # then one type
```

Decompiling a whole assembly to stdout is slow and floods context. List, then pull
the type you need.

**Assembly layout is not uniform, and the path above is only the common case.**
`Multiplayer.dll` is under `AssembliesCustom/`; World Tech Level's real assembly is
under `1.6/Lunar/Components/`; some mods use a root `Assemblies/` with no version
folder; VEF carries `1.0/` through `1.6/`. Confirm which file the game loads before
citing it — `corpus.py`'s `Dll` column helps but does not always disambiguate, and
**T-22** means there may be a second copy under the other root.

## Marking the evidence

PARTS-BIN's convention, and it governs every claim in a resolution:

- **[V]** — someone read the def, the patch or the decompiled code, and cites the path.
- **[I]** — inferred from a name, a blurb or a folder structure. **A metadata-heap hit
  is [I].**

Mark every claim one or the other. An unmarked claim reads as [V] and gets built on.

**A proposed build is marked too.** The mechanisms it composes are [V] — you read
`WorldComponent.ExposeData`, you read the `workerClass` instantiation. The claim that they
compose into the thing we want is **[I]** until something is built. Say which is which; a
design presented at [V] is the expensive kind of confidence.

**Cite a stable anchor, never a line number.** A trap is `docs/TRAPS.md` T-14; an
engine fact is its file and heading in `docs/engine/`. Line numbers rot — the
citations into the old `technical-findings.md` had already drifted ~53 lines before
that file was split, and every one of them is now dead. Trap IDs never renumber.
#88 checked its own ticket's two line-number citations: one had already drifted eight
lines in weeks.

**For decompiled code, the anchor is `Type.Method`.** A decompile has no stable
headings, and its line numbers are an artifact of your own `ilspycmd` invocation.
Cite the assembly path and the member name.

## Declare the evidence class

Open the resolution with one of:

- **READ** — settled by defs and decompiled assemblies. Most tickets.
- **STUB** — needs a def stub through `tools/patch_check.py` or `tools/xpath.py`.
  Both merge the **active** set, so their verdict is "matches in one configuration."
  State that alongside the number.
- **RUN** — genuinely needs the game launched, or two Multiplayer clients. Hand it
  back rather than reasoning around it; a RUN answer produced by reading is a guess
  wearing a verdict.

**Read everything reading can settle first, so the hand-back is narrow.** #88's RUN
reduced to a one-client log check for a single absent warning string, because the
mechanism had already been read end to end. A RUN that says "needs testing" without
saying exactly what to observe has not done tier 2's work.

**The evidence class grades the survey, not the build.** A READ ticket still owes a
proposed build; the build is [I] by construction and that is fine. Do not downgrade a
resolution to RUN because the *design* is unproven — RUN is for questions reading cannot
answer, not for designs nobody has compiled.

## Conflicts are cargo, not verdicts

A mod that collides with another today stays a candidate — patching collisions is
planned work. When you trip over one, record it in `docs/data/MOD-VERDICTS.md` under
its mod and carry on with the mechanism. Hunting for conflicts belongs to sourcing.

## Inherited claims

Some tickets carry a *"already verified — do not re-derive"* block. Treat it as [V]
only when its cited source is readable and current. Two are neither: #90's block
understates `CanChangeGoodwillFor` by three gates that are specifically NPC↔NPC, and
several cite files under `scratch/`, which is gitignored — readable to a local agent,
invisible to a sandboxed one.

When the source will not open, the claim is **[I]** and yours to verify.

**#90's block was re-derived and the omission was load-bearing**: the missing
`permanentEnemyToEveryoneExcept` gate already hard-blocks Royalty's Empire against
two of Archinity's own factions, forever. The source recon was correct; the ticket's
prose summary of it was not.

**This applies to unmarked background facts too.** A ticket's framing prose is not
evidence, whether or not it sits under a "verified" heading. #87's ticket and
`PARTS-BIN.md` both named `MainTabWindow_Research.GetVisibleResearchProjects`; no such
method exists in 1.6. #52's ticket asserted two donor mechanisms that the 1.6
assemblies contradict. **Re-verify any premise your answer rests on**, and correct it
in the resolution.

**A prior ticket's resolution is an inherited claim like any other.** When a ticket
supersedes or absorbs a closed one, its findings are [I] until re-read — sound work, but
work you are now building on rather than filing beside.

## Requirements stay where they live

What a system must do lives in `docs/requirements/`. Finding a requirement missing is
a result: name it, hand it to the owning requirements ticket, and answer the
capability question that is actually yours.

Three of four tickets in the first batch found a genuine requirements gap this way.
**Naming the gap is a better output than guessing past it** — #87 stopped short of
designing an era filter and found instead that no requirements document owns menu
legibility at all, and that `docs/progression/` (where the filter's key would live)
is empty.

**This is not a licence to hand back the build.** A missing *number* — what the decay rate
is, where the band thresholds sit — is a requirement. A missing *mechanism* — what holds
the number at all — is yours. Propose the build with the requirement stated as an open
parameter, and say which ticket sets it.

## Known tooling hazards

- **`corpus.py --which` attributes a whole wide pass in one call.** It takes a mod
  root, a file, or many of either, reads paths from stdin with `-`, accepts raw
  ripgrep output, and collapses the hits to one row per mod with the inactive and
  stale-source flags already applied:

  ```bash
  rg -a -l "TryAffectGoodwillWith" <both roots> -g '*.dll' -g '!**/obj/**' \
    | python tools/corpus.py --which -
  ```

  It reports paths it could not attribute rather than dropping them — **a path
  owned by no mod usually means the sweep is wrong, not the corpus empty.**
- **`gh` can return exit 0 with empty output under the tool sandbox.** An issue looks
  like it has no body rather than like a blocked network call. If a ticket reads
  empty, re-run with the sandbox disabled before believing it. See
  `docs/agents/issue-tracker.md`.
- **`corpus.py --check` is worth running at the start and the end** of a ticket. A
  mod moved mid-ticket in the first batch, invalidating a pin that had just been
  cited.
