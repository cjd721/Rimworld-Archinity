# Engine and mod reference

**Verified facts about how RimWorld 1.6 and our loaded mods actually behave.**
Recorded so they are never re-litigated.

Everything here was confirmed against game defs or decompiled source — not
documentation, not the wiki, not assumption. A fact recorded here is a **verified
available mechanism**, not a commitment to use it: selection happens in
`docs/specs/`.

Base game version 1.6.4871 unless a file or entry says otherwise. Re-verify after
any major RimWorld update.

## The files

| File | Owns |
|---|---|
| `def-loading.md` | How the def database is assembled, and what that means for a patch |
| `determinism.md` | Ticks, `Rand`, threads, and what Multiplayer actually syncs |
| `factions-and-worldgen.md` | The roster, settlement allocation, and climbing a faction mid-campaign |
| `research-and-tech-tiers.md` | Research pacing and the tech-gating mod stack |
| `quests.md` | Quest rewards, presentation, and the quest system as event scheduler |
| `facilities-and-recipes.md` | Bench augments, linkable facilities, recipe gating |
| `items-and-materials.md` | Deterioration, armour maths and the stuff ladder |
| `world-time-and-layers.md` | The 60-day year, and the Odyssey orbit layer |
| `gravship-and-substructure.md` | Affordances, what flies, and the cell budget |
| `mods/medieval-overhaul.md` | MO's settings surface, resource chains and licensing |
| `mods/kcsg.md` | Settlement and structure layout authoring |
| `mods/vqe-ancients.md` | Archite injection and its gates |

Two neighbours own things this directory deliberately does not:

- **`docs/TRAPS.md`** owns every behaviour that fails **silently**. A finding that
  produces no error message goes there, not here, and these files cross-reference it
  by ID.
- **`docs/specs/`** owns what we will actually build. A mechanism verified here
  becomes a commitment only when a spec selects it.

## Filing rule

**Organize by subject, never by session.** This directory replaced a single
1300-line file that had been appended to in research batches — `Session 4 findings`,
`Session 5 findings` — until the same subject lived in three places and a later
batch had to open by saying it "extends the section above rather than replacing it".
That is the failure mode this structure exists to prevent.

So:

- A new fact goes in the file for its **subject**, merged into the existing section.
  If no file fits and the subject is substantial, add one and list it above.
- **Corrections edit the fact in place.** Do not append "an earlier draft said…"
  under superseded text. The exception is a correction that warns against a claim
  still live in another document — say what is wrong and where.
- **Stamp provenance.** Every fact carries the build it was verified against, either
  from the file header or on the entry. A file whose header says 1.6.4871 must mark
  any entry verified against something else.
- **Link, do not copy.** The investigation stays on its issue; the system design
  stays in its spec. This directory takes only the fact worth knowing *outside* the
  system that turned it up.
- **If it fails silently, it belongs in `docs/TRAPS.md` instead.** Loudness is the
  whole selection criterion. Keep the positive mechanism here and cross-reference the
  trap for the warning.
