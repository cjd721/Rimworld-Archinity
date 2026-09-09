# Working a capability research ticket

How the evidence gets gathered. Where the answer lands is `docs/specs/README.md`'s
business, and the ticket footer already carries it.

A capability ticket asks: **does the game already do this, what carries it, at what
cost, and is it multiplayer-safe?** It answers with a mechanism and its constraints.
Naming the provider mod is part of that — the sourcing ledger (#14) consumes exactly
that verdict, and "XML, a patch, or new C#" is unanswerable without it. Writing the
patch belongs to whoever implements.

## Who writes what

**The agent that resolved the ticket writes the spec.** It has the assemblies open and
the evidence in working memory; nobody else will ever be as cheap to write it. One
session produces all three outputs the footer names — the resolution comment, the
`docs/specs/` section, and any `docs/engine/` or `docs/TRAPS.md` entry — and reports a
short summary upward.

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
> A **negative** answer is not finished until the wide pass has run.

"Empire Honor carries this" — done, go read Empire. "Nothing carries this" — only
worth something if you looked everywhere first.

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

## Requirements stay where they live

What a system must do lives in `docs/requirements/`. Finding a requirement missing is
a result: name it, hand it to the owning requirements ticket, and answer the
capability question that is actually yours.

Three of four tickets in the first batch found a genuine requirements gap this way.
**Naming the gap is a better output than guessing past it** — #87 stopped short of
designing an era filter and found instead that no requirements document owns menu
legibility at all, and that `docs/progression/` (where the filter's key would live)
is empty.

## Known tooling hazards

- **`corpus.py --which` attributes a whole wide pass in one call.** It takes a mod
  root, a file, or many of either, reads paths from stdin with `-`, accepts raw
  ripgrep output, and collapses the hits to one row per mod with the inactive and
  stale-source flags already applied:

  ```bash
  rg -a -l "TryAffectGoodwillWith" <both roots> -g '*.dll' \
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
