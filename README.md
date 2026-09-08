# Archinity

A suite of RimWorld 1.6 mods for a single long co-op playthrough: neolithic start,
slow climb through every tech era, endgame in orbit, and a late-game antagonist
worth beating.

## References

- [Campaign overview](docs/PLOT.md) — the complete arc and links to era chapters.
- [Cosmology](docs/COSMOLOGY.md) — how anima, devotion and selfhood work.
- [System specifications](docs/specs/) — Charting, religion, the altar and Glittertech.
- [Wayfinder](https://github.com/cjd721/Rimworld-Archinity/issues/2) — remaining design and specification work.
- [Glossary](CONTEXT.md), [coding standards](CODING_STANDARDS.md) and [technical findings](docs/technical-findings.md).

## Mods

The existing modules are `Archinity.Origins`, `Archinity.Pacing`,
`Archinity.Drifters`, `Archinity.Glitterites` and `Archinity.Altar`. They contain
defs, assets, patches and altar source code. Their presence does not mean the
campaign described in the design references is implemented. Quest authoring and
integration remain work tracked by the wayfinder.

## Setup

Clone this repo anywhere, then:

```powershell
.\setup.ps1 -SyncConfig
```

This creates a **directory junction** for every `Archinity.*` folder into
RimWorld's `Mods\` directory. Junctions don't need administrator rights, and
edits in the repo are live in the game with no copy step.

`-SyncConfig` also installs the repository's current `ModsConfig.xml` (load order) and any
per-mod settings from `config/`. Your previous config is backed up first.

Other flags:

```powershell
.\setup.ps1 -RimWorldPath "D:\Steam\steamapps\common\RimWorld"   # non-default install
.\setup.ps1 -Unlink                                              # remove the junctions
```

## Multiplayer

Both players need:

1. **The same Steam Workshop subscriptions** (this repo does not vendor them).
2. **The same load order** — handled by `config/ModsConfig.xml`.
3. **The same mod settings** — handled by `config/ModSettings/`.

Point 3 is the one people miss. Ignorance Is Bliss and TechBlock are entirely
settings-driven with no defs of their own, so mismatched sliders between clients
produce divergent behavior that reads as a desync.

Use the **Multiplayer** mod (`rwmt.multiplayer`). Do not run RimWorld Together
at the same time.

## Tooling

- `ilspycmd` (pin `8.2.0.7535`; latest is broken on .NET 8) — decompiling
  `Assembly-CSharp.dll` and mod assemblies to confirm field names.
- RimSort — load order solving.
- VS Code + Red Hat XML extension.
