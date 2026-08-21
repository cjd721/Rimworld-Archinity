# Archinity

A suite of RimWorld 1.6 mods for a single long co-op playthrough: neolithic start,
slow climb through every tech era, endgame in orbit, and a late-game antagonist
worth beating.

Everything here is **XML defs only** — no C#, no Harmony patches. Def-only mods
carry no simulation code, which makes them inherently multiplayer-safe.

## Mods

| Mod | Status | Contents |
|---|---|---|
| `Archinity.Origins` | **built** | Archonian Sanguophage xenotype + "Seed of Archinity" scenario |
| `Archinity.Pacing` | **partial** | Orbit size, Archon raid lockout, Transcendent reserved, MRR fix |
| `Archinity.Drifters` | **built** | Starjack Free Companies — neutral, hostile-capable orbital faction |
| `Archinity.Glitterites` | planned | Ultra-tech antagonist, orbital fortresses, mech deployment |
| `Archinity.Chronicle` | planned | Quest chain spine tying the arc together |

## Setup

Clone this repo anywhere, then:

```powershell
.\setup.ps1 -SyncConfig
```

This creates a **directory junction** for every `Archinity.*` folder into
RimWorld's `Mods\` directory. Junctions don't need administrator rights, and
edits in the repo are live in the game with no copy step.

`-SyncConfig` also installs the canonical `ModsConfig.xml` (load order) and any
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

## Design notes

The pacing spine is `requiredResearch` on VEF's `QuestChainExtension`, keyed to
TechBlock's tier-lock research projects:

| Research def | Means |
|---|---|
| `TB_NeolithicTheory` | entered Neolithic |
| `TB_MedievalTheory` | entered Medieval |
| `TB_IndustrialTheory` | entered Industrial |
| `TB_SpacerTheory` | entered Spacer |
| `TB_UltraTheory` | entered Ultra |
| `TB_ArchoTheory` | entered Archotech |

This gates story beats on actual progression rather than elapsed days.
`rootMinProgressScore` is **not** usable for this — it computes as
`freeColonists + (wealth * 0.0001)` and ignores research entirely.

## Tooling

- `ilspycmd` (pin `8.2.0.7535`; latest is broken on .NET 8) — decompiling
  `Assembly-CSharp.dll` and mod assemblies to confirm field names.
- RimSort — load order solving.
- VS Code + Red Hat XML extension.
