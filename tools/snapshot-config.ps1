<#
.SYNOPSIS
  Freeze the live game's mod list and mod settings into the repo, ready to commit.

.DESCRIPTION
  Run this AFTER you have launched RimWorld, enabled the mods you want, opened
  every settings menu and set everything the way you want it.

  It copies, from RimWorld's live Config folder into this repo:

    ModsConfig.xml   ->  config\ModsConfig.xml        (the mod list AND its order)
    Mod_*.xml        ->  config\ModSettings\          (one per mod that has settings)

  Settings files for mods that are NOT in the active list are skipped, and any
  stale ones already in the repo are deleted, so the snapshot always describes
  exactly the build you are playing.

  Then commit and push. Your co-op partner pulls, and pastes those same files
  into his own Config folder. That is the whole sync protocol.

  WHY THIS MATTERS: both players need identical mods, identical load order AND
  identical mod settings. The third is the one people miss. In this build the
  settings that reach synced simulation are Starjack, Hussar, Sanguophage and
  Ushanka's Glittertech Expansion - if those differ, you desync.

.EXAMPLE
  .\tools\snapshot-config.ps1
  .\tools\snapshot-config.ps1 -All          # keep settings for disabled mods too
#>

[CmdletBinding()]
param(
    [string] $RimWorldPath = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld",
    [string] $WorkshopPath = "C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
    [switch] $All
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot

# RimWorld writes to AppData\LocalLow, a SIBLING of AppData\Local, not a child.
# There is no environment variable for LocalLow.
$ConfigDir   = Join-Path $env:USERPROFILE 'AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config'
$DestConfig  = Join-Path $RepoRoot 'config'
$DestSettings= Join-Path $DestConfig 'ModSettings'

function Write-Ok($m)   { Write-Host "  OK    $m" -ForegroundColor Green }
function Write-Skip($m) { Write-Host "  skip  $m" -ForegroundColor DarkGray }
function Write-Del($m)  { Write-Host "  drop  $m" -ForegroundColor Yellow }

Write-Host "`nSnapshot live config into the repo" -ForegroundColor White
Write-Host ("=" * 60)

if (-not (Test-Path $ConfigDir)) {
    Write-Host "`nRimWorld's Config folder is not where I expected:`n  $ConfigDir" -ForegroundColor Red
    Write-Host "Launch the game once, then re-run.`n" -ForegroundColor Red
    exit 1
}
Write-Host "  from  $ConfigDir"
Write-Host "  into  $DestConfig`n"

New-Item -ItemType Directory -Path $DestSettings -Force | Out-Null

# --- The mod list -----------------------------------------------------------
$liveModsConfig = Join-Path $ConfigDir 'ModsConfig.xml'
if (-not (Test-Path $liveModsConfig)) {
    Write-Host "No ModsConfig.xml in the live Config folder. Launch the game once." -ForegroundColor Red
    exit 1
}
Copy-Item $liveModsConfig (Join-Path $DestConfig 'ModsConfig.xml') -Force

[xml] $mc = Get-Content $liveModsConfig
$active = @($mc.ModsConfigData.activeMods.li | ForEach-Object { $_.Trim().ToLower() })
Write-Ok "ModsConfig.xml  ($($active.Count) active mods)"

# --- Map workshop folder id -> packageId, so settings can be filtered --------
$idToPackage = @{}
foreach ($root in @($WorkshopPath, (Join-Path $RimWorldPath 'Mods'))) {
    if (-not (Test-Path $root)) { continue }
    foreach ($dir in Get-ChildItem $root -Directory) {
        $about = Join-Path $dir.FullName 'About\About.xml'
        if (-not (Test-Path $about)) { continue }
        try   { [xml] $a = Get-Content $about -Raw }
        catch { continue }
        $packageId = $a.ModMetaData.packageId
        if ($packageId) { $idToPackage[$dir.Name] = $packageId.Trim().ToLower() }
    }
}

# --- Mod settings -----------------------------------------------------------
Write-Host ""
$kept = 0
foreach ($f in Get-ChildItem $ConfigDir -Filter 'Mod_*.xml') {
    $id  = if ($f.Name -match '^Mod_(\d+)_') { $Matches[1] } else { $null }
    $pkg = if ($id -and $idToPackage.ContainsKey($id)) { $idToPackage[$id] } else { $null }

    if ($All -or ($pkg -and $active -contains $pkg)) {
        Copy-Item $f.FullName (Join-Path $DestSettings $f.Name) -Force
        Write-Ok "$($f.Name)  <- $(if ($pkg) { $pkg } else { 'unknown mod' })"
        $kept++
    } else {
        Write-Skip "$($f.Name)  [$(if ($pkg) { $pkg } else { "unknown id $id" })] not in the active list"
    }
}

# --- Drop stale snapshots ---------------------------------------------------
if (-not $All) {
    foreach ($f in Get-ChildItem $DestSettings -Filter 'Mod_*.xml') {
        if (-not (Test-Path (Join-Path $ConfigDir $f.Name))) {
            Remove-Item $f.FullName -Force
            Write-Del "$($f.Name)  no longer present in the live config"
            continue
        }
        $id  = if ($f.Name -match '^Mod_(\d+)_') { $Matches[1] } else { $null }
        $pkg = if ($id -and $idToPackage.ContainsKey($id)) { $idToPackage[$id] } else { $null }
        if (-not ($pkg -and $active -contains $pkg)) {
            Remove-Item $f.FullName -Force
            Write-Del "$($f.Name)  mod is not in the active list"
        }
    }
}

Write-Host "`nSnapshotted $($active.Count) mods and $kept settings file(s)." -ForegroundColor White
Write-Host @"

Next:
  1. git add config
  2. git commit -m "config: freeze mod list and settings"
  3. git push
  4. Tell your co-op partner to pull and paste config\ModsConfig.xml and
     everything in config\ModSettings\ into his own:
       %USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\

"@ -ForegroundColor Gray
