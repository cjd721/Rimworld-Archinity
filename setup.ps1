<#
.SYNOPSIS
  Links the Archinity mods into RimWorld and optionally syncs shared config.

.DESCRIPTION
  Creates a directory junction for every Archinity.* folder in this repo into
  RimWorld's Mods directory. Junctions do NOT require administrator rights.
  Edits made in the repo are live in the game immediately - no copying.

  With -SyncConfig, also installs the canonical ModsConfig.xml and mod settings
  from config/. Both multiplayer clients must run this so their load order and
  mod settings match exactly.

.EXAMPLE
  .\setup.ps1
  .\setup.ps1 -SyncConfig
  .\setup.ps1 -RimWorldPath "D:\Steam\steamapps\common\RimWorld" -SyncConfig
#>

[CmdletBinding()]
param(
    [string] $RimWorldPath = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld",
    [switch] $SyncConfig,
    [switch] $Unlink
)

$ErrorActionPreference = 'Stop'
$RepoRoot = $PSScriptRoot
$ModsDir  = Join-Path $RimWorldPath 'Mods'
# RimWorld writes to AppData\LocalLow, which is a sibling of AppData\Local and
# NOT a child of it. Joining 'Low\...' onto $env:LOCALAPPDATA produces
# AppData\Local\Low\... which does not exist, and -SyncConfig then silently
# warned and did nothing. There is no environment variable for LocalLow.
$ConfigDir = Join-Path $env:USERPROFILE 'AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config'

function Write-Step($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  OK   $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "  WARN $msg" -ForegroundColor Yellow }

Write-Host "`nArchinity setup" -ForegroundColor White
Write-Host ("=" * 60)

# --- Validate RimWorld location -------------------------------------------
if (-not (Test-Path $ModsDir)) {
    Write-Host "`nCould not find RimWorld's Mods folder at:`n  $ModsDir" -ForegroundColor Red
    Write-Host "Re-run with -RimWorldPath pointing at your RimWorld install.`n" -ForegroundColor Red
    exit 1
}
Write-Ok "RimWorld found: $RimWorldPath"

# --- Discover mods in this repo -------------------------------------------
$mods = Get-ChildItem -Path $RepoRoot -Directory |
        Where-Object { $_.Name -like 'Archinity.*' } |
        Sort-Object Name

if (-not $mods) {
    Write-Warn2 "No Archinity.* mod folders found in $RepoRoot"
    exit 1
}

# --- Link (or unlink) ------------------------------------------------------
Write-Host "`nMods" -ForegroundColor White
foreach ($mod in $mods) {
    $link = Join-Path $ModsDir $mod.Name
    $existing = Get-Item $link -ErrorAction SilentlyContinue

    if ($Unlink) {
        if ($existing -and $existing.LinkType -eq 'Junction') {
            [System.IO.Directory]::Delete($link, $false)
            Write-Ok "unlinked $($mod.Name)"
        } else {
            Write-Step "$($mod.Name) not linked, skipping"
        }
        continue
    }

    if ($existing) {
        if ($existing.LinkType -eq 'Junction') {
            # Re-point in case the repo moved.
            [System.IO.Directory]::Delete($link, $false)
        } else {
            Write-Warn2 "$($mod.Name) exists in Mods and is a REAL folder, not a junction."
            Write-Warn2 "Move or delete it yourself, then re-run. Skipping to avoid data loss."
            continue
        }
    }

    New-Item -ItemType Junction -Path $link -Target $mod.FullName | Out-Null
    Write-Ok "linked $($mod.Name)"
}

# --- Config sync -----------------------------------------------------------
if ($SyncConfig -and -not $Unlink) {
    Write-Host "`nConfig" -ForegroundColor White

    if (-not (Test-Path $ConfigDir)) {
        Write-Warn2 "RimWorld config folder not found at $ConfigDir - launch the game once first."
    } else {
        $stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
        $backup = Join-Path $ConfigDir "_backup-$stamp"
        New-Item -ItemType Directory -Path $backup -Force | Out-Null

        # ModsConfig.xml - the canonical load order
        $srcModsConfig = Join-Path $RepoRoot 'config\ModsConfig.xml'
        if (Test-Path $srcModsConfig) {
            $dstModsConfig = Join-Path $ConfigDir 'ModsConfig.xml'
            if (Test-Path $dstModsConfig) { Copy-Item $dstModsConfig $backup }
            Copy-Item $srcModsConfig $dstModsConfig -Force
            Write-Ok "installed ModsConfig.xml (previous backed up)"
        }

        # Per-mod settings - these MUST match between multiplayer clients.
        $srcSettings = Join-Path $RepoRoot 'config\ModSettings'
        if (Test-Path $srcSettings) {
            Get-ChildItem $srcSettings -Filter 'Mod_*.xml' | ForEach-Object {
                $dst = Join-Path $ConfigDir $_.Name
                if (Test-Path $dst) { Copy-Item $dst $backup }
                Copy-Item $_.FullName $dst -Force
                Write-Ok "installed $($_.Name)"
            }
        }

        Write-Step "backups in $backup"
    }
}

Write-Host "`nDone.`n" -ForegroundColor White
if (-not $Unlink) {
    Write-Host "Launch RimWorld and enable the Archinity mods in the mod list." -ForegroundColor Gray
    Write-Host "Turn on Dev Mode (Options > Gameplay) to see def errors.`n" -ForegroundColor Gray
}
