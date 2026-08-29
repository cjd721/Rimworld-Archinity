<#
.SYNOPSIS
  Copy every active Steam Workshop mod into RimWorld's local Mods folder, so
  Steam can never auto-update them out from under a co-op save.

.DESCRIPTION
  Steam updates workshop items whenever it feels like it. In a two-player save
  running for months, one machine getting an update the other has not is enough
  to stop the session joining, or to desync it mid-game. There is no per-item
  "do not update" setting in Steam, and the game-level "only update on launch"
  option does not cover workshop content.

  So take a local copy. RimWorld loads a mod out of its local Mods folder the
  same way it loads a workshop one: folder names are irrelevant, the packageId
  inside About.xml is what ModsConfig.xml matches on.

  YOU DO NOT HAVE TO UNSUBSCRIBE. RimWorld handles the collision natively and
  in our favour. Verified in the decompiled Verse.ModLister.TryAddMod:

      if (mod.OnSteamWorkshop != modWithIdentifier.OnSteamWorkshop)
      {
          ModMetaData modMetaData = (mod.OnSteamWorkshop ? mod : modWithIdentifier);
          if (!modMetaData.appendPackageIdSteamPostfix)
          {
              modMetaData.appendPackageIdSteamPostfix = true;
              return TryAddMod(mod);
          }
      }

  When the same packageId appears once locally and once on the workshop, the
  STEAM copy is the one that gets flagged, and ModMetaData.PackageId then
  returns packageIdLowerCase + ModMetaData.SteamModPostfix, which is "_steam".
  The local copy keeps the clean id. ModsConfig.xml lists clean ids and
  ModLister.GetModWithIdentifier looks them up in modsByPackageId, which is
  keyed on that postfixed PackageId - so every entry resolves to the LOCAL
  copy, and the Steam copy is simply not in the active list.

  The "Tried loading mod with the same packageId multiple times" error only
  fires when both copies are on the same side (both local, or both workshop),
  which is not what this produces.

  So Steam may keep the subscriptions and keep updating its own copies. The
  game will not load them. The only costs are disk (the set is duplicated,
  under a gigabyte) and a mod list that shows both entries.

.EXAMPLE
  .\tools\freeze-workshop-mods.ps1          # copy
  .\tools\freeze-workshop-mods.ps1 -Check   # verify, copy nothing
#>

[CmdletBinding()]
param(
    [string] $RimWorldPath = "C:\Program Files (x86)\Steam\steamapps\common\RimWorld",
    [string] $WorkshopPath = "C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
    [switch] $Check
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ModsDir  = Join-Path $RimWorldPath 'Mods'

function Ok($m)   { Write-Host "  OK    $m" -ForegroundColor Green }
function Info($m) { Write-Host "  $m" }
function Warn($m) { Write-Host "  WARN  $m" -ForegroundColor Yellow }

Write-Host "`nFreeze workshop mods into the local Mods folder" -ForegroundColor White
Write-Host ("=" * 62)

[xml] $mc = Get-Content (Join-Path $RepoRoot 'config\ModsConfig.xml')
$active = @($mc.ModsConfigData.activeMods.li | ForEach-Object { $_.Trim().ToLower() })

function Index($root) {
    $map = @{}
    if (-not (Test-Path $root)) { return $map }
    foreach ($dir in Get-ChildItem $root -Directory) {
        $about = Join-Path $dir.FullName 'About\About.xml'
        if (-not (Test-Path $about)) { continue }
        try   { [xml] $a = Get-Content $about -Raw }
        catch { continue }
        $packageId = $a.ModMetaData.packageId
        if ($packageId) { $map[$packageId.Trim().ToLower()] = $dir.FullName }
    }
    return $map
}

$inWorkshop = Index $WorkshopPath
$inLocal    = Index $ModsDir

$needed = @($active | Where-Object { $_ -notlike 'ludeon.*' })
Info "active mods                : $($active.Count)"
Info "  Core and DLC (in Data\)  : $($active.Count - $needed.Count)"
Info "  must exist as a folder   : $($needed.Count)"
Info "present in local Mods\     : $(@($needed | Where-Object { $inLocal.ContainsKey($_) }).Count)"
Info "present in the workshop    : $(@($needed | Where-Object { $inWorkshop.ContainsKey($_) }).Count)"

# --- Check ------------------------------------------------------------------
if ($Check) {
    Write-Host "`nCheck" -ForegroundColor White
    $notLocal = @($needed | Where-Object { -not $inLocal.ContainsKey($_) })
    $bothPlaces = @($needed | Where-Object { $inLocal.ContainsKey($_) -and $inWorkshop.ContainsKey($_) })

    if ($notLocal.Count) {
        Warn "$($notLocal.Count) active mod(s) are NOT in Mods\ - Steam can still update these:"
        foreach ($m in $notLocal) { Info "    $m" }
        Info "Run without -Check to copy them."
    } else {
        Ok "all $($needed.Count) active mods exist locally in Mods\"
        Ok "every ModsConfig.xml entry will resolve to the local copy"
        Ok "Steam cannot change what the game loads"
    }

    if ($bothPlaces.Count) {
        Info ""
        Info "$($bothPlaces.Count) also still exist in the workshop folder. That is FINE and"
        Info "expected: RimWorld renames the Steam copy to <packageId>_steam and loads"
        Info "the local one. No need to unsubscribe. See the notes at the top of this"
        Info "script for the decompiled ModLister.TryAddMod branch that does it."
    }
    Write-Host ""
    return
}

# --- Copy -------------------------------------------------------------------
Write-Host "`nCopying" -ForegroundColor White
$copied = 0; $already = 0
foreach ($id in $needed) {
    if ($inLocal.ContainsKey($id))          { $already++; continue }
    if (-not $inWorkshop.ContainsKey($id))  { continue }
    $src  = $inWorkshop[$id]
    Copy-Item $src (Join-Path $ModsDir (Split-Path $src -Leaf)) -Recurse -Force
    $copied++
}
Ok "copied $copied"
Info "already local : $already   (our mods, plus anything frozen previously)"

Write-Host @"

DONE. You can launch.
=====================
  Do NOT unsubscribe. You do not need to, and this is the whole point:

    * RimWorld sees each mod twice, once local and once from Steam.
    * It renames the STEAM one to <packageId>_steam and leaves the local one
      holding the clean id.
    * ModsConfig.xml lists clean ids, so all 87 entries resolve to the LOCAL
      copies, in the load order you froze.
    * Steam may keep updating its own copies forever. The game will not load
      them.

  Confirm any time with:

      .\tools\freeze-workshop-mods.ps1 -Check

  The mod list in-game will show duplicate entries. That is expected, and the
  Steam-side ones are inert.

  WHEN YOU ACTUALLY WANT AN UPDATE, it becomes a deliberate act rather than
  something Steam decides:
      1. delete that mod's folder from RimWorld\Mods\
      2. let Steam's copy update
      3. re-run this script
      4. re-run .\tools\export-for-partner.ps1 and send the pack again

"@ -ForegroundColor Gray
