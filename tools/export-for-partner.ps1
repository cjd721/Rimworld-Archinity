<#
.SYNOPSIS
  Build one handover folder containing every mod and config file your co-op
  partner needs, and nothing else.

.DESCRIPTION
  Reads config\ModsConfig.xml, resolves every active packageId to a folder on
  disk, and copies the lot into a staging directory:

      <out>\Mods\      every workshop mod in the active list, plus the five
                       Archinity mods, one folder each
      <out>\Config\    ModsConfig.xml and every Mod_*.xml settings file
      <out>\READ ME FIRST.txt

  Your partner then pastes Mods\* into RimWorld's Mods folder and Config\*
  into RimWorld's Config folder. Two pastes, no scripts, no Steam.

  WHY BOTHER, WHEN A STEAM COLLECTION IS ONE CLICK:
  Steam auto-updates workshop mods. If a mod updates on one machine and not
  the other, the two def databases stop matching and the session will refuse
  to join or will desync. Local folders cannot be touched by Steam, so both
  installs stay pinned to identical bytes for the life of the save. The whole
  set is well under a gigabyte.

  Your partner must NOT also be subscribed to these mods on Steam, or the
  same packageId exists twice and RimWorld complains.

.EXAMPLE
  .\tools\export-for-partner.ps1
  .\tools\export-for-partner.ps1 -Out D:\ArchinityHandover -Zip
#>

[CmdletBinding()]
param(
    [string] $RimWorldPath = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld",
    [string] $WorkshopPath = "C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
    [string] $Out          = "$env:USERPROFILE\Desktop\Archinity-Handover",
    [switch] $Zip
)

$ErrorActionPreference = 'Stop'
$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ConfigDir = Join-Path $env:USERPROFILE 'AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config'

function Say($m)  { Write-Host "  $m" }
function Ok($m)   { Write-Host "  OK    $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  WARN  $m" -ForegroundColor Yellow }

Write-Host "`nExport the multiplayer set for a co-op partner" -ForegroundColor White
Write-Host ("=" * 60)

[xml] $mc = Get-Content (Join-Path $RepoRoot 'config\ModsConfig.xml')
$active = @($mc.ModsConfigData.activeMods.li | ForEach-Object { $_.Trim().ToLower() })
Say "active mods in config\ModsConfig.xml : $($active.Count)"

# --- Index every mod folder on disk by packageId ---------------------------
$byPackage = @{}
foreach ($root in @($WorkshopPath, (Join-Path $RimWorldPath 'Mods'), $RepoRoot)) {
    if (-not (Test-Path $root)) { continue }
    foreach ($dir in Get-ChildItem $root -Directory) {
        $about = Join-Path $dir.FullName 'About\About.xml'
        if (-not (Test-Path $about)) { continue }
        try   { [xml] $a = Get-Content $about -Raw }
        catch { continue }
        $packageId = $a.ModMetaData.packageId
        if (-not $packageId) { continue }
        $key = $packageId.Trim().ToLower()
        # Prefer the repo copy for our own mods; prefer a real dir over a junction.
        if (-not $byPackage.ContainsKey($key) -or $root -eq $RepoRoot) {
            $byPackage[$key] = $dir.FullName
        }
    }
}

if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
$modsOut   = Join-Path $Out 'Mods'
$configOut = Join-Path $Out 'Config'
New-Item -ItemType Directory -Path $modsOut, $configOut -Force | Out-Null

# --- Copy the mods ----------------------------------------------------------
Write-Host "`nMods" -ForegroundColor White
$copied = 0; $skippedDlc = 0; $missing = @()
foreach ($id in $active) {
    if ($id -like 'ludeon.*') { $skippedDlc++; continue }   # owned, not shipped
    if (-not $byPackage.ContainsKey($id)) { $missing += $id; continue }
    $src = $byPackage[$id]
    Copy-Item $src (Join-Path $modsOut (Split-Path $src -Leaf)) -Recurse -Force
    $copied++
}
Ok "copied $copied mod folder(s)"
Say "skipped $skippedDlc Core/DLC entries - he owns those already"
if ($missing.Count) { Warn "NOT FOUND ON DISK: $($missing -join ', ')" }

# --- Copy the config --------------------------------------------------------
Write-Host "`nConfig" -ForegroundColor White
Copy-Item (Join-Path $RepoRoot 'config\ModsConfig.xml') $configOut -Force
Ok "ModsConfig.xml"
$settings = Join-Path $RepoRoot 'config\ModSettings'
$n = 0
if (Test-Path $settings) {
    foreach ($f in Get-ChildItem $settings -Filter 'Mod_*.xml') {
        Copy-Item $f.FullName $configOut -Force; $n++
    }
}
Ok "$n mod settings file(s)"

# --- The note ---------------------------------------------------------------
$readme = @"
ARCHINITY - RIMWORLD CO-OP SETUP
================================

Two pastes. No scripts to run.

BEFORE YOU START
  * Own RimWorld plus Royalty, Ideology, Biotech and Odyssey. All four are used.
  * Close RimWorld.
  * You do NOT have to unsubscribe from anything. If you already subscribe to a
    mod that is also in this pack, RimWorld renames the Steam copy internally
    and loads the local one out of Mods\, which is what we want. Unsubscribing
    is only worth doing to save disk space.
  * Do not INSTALL these through Steam either. The whole point of shipping you
    folders is that Steam cannot auto-update them. If one player's mod updates
    and the other's does not, the save will not join, or it will desync
    mid-game.

STEP 1 - THE MODS
  Copy everything inside this pack's  Mods\  folder into:

      C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\

  (If RimWorld is on another drive, it is the Mods folder sitting next to
  RimWorldWin64.exe.) Whole folders, as they are. Overwrite if asked.

STEP 2 - THE CONFIG
  Copy everything inside this pack's  Config\  folder into:

      %USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\

  Paste that path straight into the Explorer address bar and press Enter - it
  expands on its own. Overwrite what is there.

  NOTE IT SAYS LocalLow, NOT Local. They are two different folders sitting next
  to each other and this is the single most common way this goes wrong.

STEP 3 - LAUNCH
  Start RimWorld. Do NOT touch the mod list and do NOT enable anything by hand.
  ModsConfig.xml already has the exact list AND the exact load order. If the mod
  menu looks right, you are done.

  Do not open any mod's settings menu either. Mod settings are part of what has
  to match between the two of you, and they came in the Config folder.

  Then wait for the host to open the game, and join.

IF SOMETHING IS WRONG
  * "Cannot join" or a version mismatch  ->  the mod list or its order differs.
    Re-do step 2 and make sure you overwrote ModsConfig.xml.
  * A mod appears twice in the list  ->  you are still subscribed to it. Harmless;
    the Steam one is renamed internally and is not loaded. Unsubscribe if the
    clutter bothers you.
  * Red errors on load   ->  screenshot them and send them over.
"@
$readme | Out-File (Join-Path $Out 'READ ME FIRST.txt') -Encoding UTF8

# --- Size, and optional zip -------------------------------------------------
$bytes = (Get-ChildItem $Out -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "`nStaged at  $Out" -ForegroundColor White
Say ("size: {0:N2} GB" -f ($bytes / 1GB))

if ($Zip) {
    $zipPath = "$Out.zip"
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Write-Host "`nCompressing..." -ForegroundColor White

    # NOT Compress-Archive. It is written in PowerShell, adds entries one at a
    # time and is pathologically slow on a set like this - thousands of small
    # texture and def files. Measured at roughly 13 KB of output per minute
    # here, which is hours. ZipFile.CreateFromDirectory is the .NET native
    # implementation and does the same job in a couple of minutes.
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $Out, $zipPath,
        [System.IO.Compression.CompressionLevel]::Fastest,
        $false)

    $zb = (Get-Item $zipPath).Length
    Ok ("{0}  ({1:N2} GB)" -f $zipPath, ($zb / 1GB))
}

Write-Host "`nSend him the folder (or the zip). He reads 'READ ME FIRST.txt'.`n" -ForegroundColor Gray
