# Working a capability research ticket

How the evidence gets gathered. Where the answer lands is `docs/specs/README.md`'s
business, and the ticket footer already carries it.

A capability ticket asks: **does the game already do this, what carries it, at what
cost, and is it multiplayer-safe?** It answers with a mechanism and its constraints.
Naming the provider mod is part of that — the sourcing ledger (#14) consumes exactly
that verdict, and "XML, a patch, or new C#" is unanswerable without it. Writing the
patch belongs to whoever implements.

## The corpus

**155 mods on disk. 93 of them inactive.** `docs/data/MOD-SNAPSHOT.md` is the roster
and the version pin; regenerate or diff it with `python tools/corpus.py` (`--help`
for the modes).

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
   Run it to justify any negative. `tools/corpus.py --which <path>` attributes a hit
   to its mod and says whether the tools can see it.
4. **Depth-read whatever tier 3 turned up.**

Ushanka's Hacking Expansion ships full 1.6 C# for exactly the mechanism #58 asks
about. It appears in no repo doc and is inactive, so tiers 1 and 2 both miss it and
tier 3 finds it in one grep.

## Stale source

**18 mods ship C# source that is not for 1.6.** VFE Empire ships 176 `.cs` files under
`1.4/Source/`, none under `1.5/` or `1.6/`, and a *different* `VFEEmpire.dll` for each
of the three. Read that source and you have described 1.4 while the game runs 1.6.
Issue #73 did it, quoting a 1.4 line count as a 1.6 fact.

`MOD-SNAPSHOT.md` marks these **⚠**, and `corpus.py --which` says so per mod. Where
source is stale or absent, decompile the assembly the game actually loads:

```bash
ilspycmd "<mod>/1.6/Assemblies/<Name>.dll" > /tmp/name.cs
```

## Marking the evidence

PARTS-BIN's convention, and it governs every claim in a resolution:

- **[V]** — someone read the def, the patch or the decompiled code, and cites the path.
- **[I]** — inferred from a name, a blurb or a folder structure.

Mark every claim one or the other. An unmarked claim reads as [V] and gets built on.

**Cite a stable anchor, never a line number.** A trap is `docs/TRAPS.md` T-14; an
engine fact is its file and heading in `docs/engine/`. Line numbers rot — the
citations into the old `technical-findings.md` had already drifted ~53 lines before
that file was split, and every one of them is now dead. Trap IDs never renumber.

## Declare the evidence class

Open the resolution with one of:

- **READ** — settled by defs and decompiled assemblies. Most tickets.
- **STUB** — needs a def stub through `tools/patch_check.py` or `tools/xpath.py`.
  Both merge the **active** set, so their verdict is "matches in one configuration."
  State that alongside the number.
- **RUN** — genuinely needs the game launched, or two Multiplayer clients. Hand it
  back rather than reasoning around it; a RUN answer produced by reading is a guess
  wearing a verdict.

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

## Requirements stay where they live

What a system must do lives in `docs/requirements/`. Finding a requirement missing is
a result: name it, hand it to the owning requirements ticket, and answer the
capability question that is actually yours.
