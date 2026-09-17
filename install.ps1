#requires -version 5
param([Parameter(Mandatory=$true)][string]$Target)

if (-not (Test-Path -PathType Container $Target)) { Write-Error "Target '$Target' is not a directory."; exit 1 }
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path

$need = @(".claude\agents", ".claude\commands", ".claude\hooks", ".claude\factory")
$missing = @()
foreach ($d in $need) { if (-not (Test-Path -PathType Container (Join-Path $Src $d))) { $missing += $d } }
if (-not (Test-Path (Join-Path $Src ".claude\settings.json"))) { $missing += ".claude\settings.json" }
# The contract points at these by relative path; a missing one is a silent dead pointer.
$contract = @("CONVENTIONS.md","terminology-zh-tw.md","CLAUDE-rationale.md","EXPLORE-MODE.md","PHASE-BOUNDARIES.md")
foreach ($f in $contract) {
  if (-not (Test-Path (Join-Path $Src ".claude\factory\$f"))) { $missing += ".claude\factory\$f" }
}
if ($missing.Count -gt 0) {
  Write-Error ("This template copy is incomplete - missing: " + ($missing -join ", ") + ". Re-extract the ZIP with hidden files included.")
  exit 1
}

New-Item -ItemType Directory -Force -Path (Join-Path $Target ".claude") | Out-Null
Copy-Item -Recurse -Force (Join-Path $Src ".claude\*") (Join-Path $Target ".claude")
Write-Host "* Copied .claude/ into $Target"

$claudeMd = Join-Path $Target "CLAUDE.md"
$snippet  = Join-Path $Src "CLAUDE.factory-snippet.md"
if (Test-Path $claudeMd) {
  Copy-Item -Force $snippet (Join-Path $Target "CLAUDE.factory-snippet.md")
  Write-Host "* Existing CLAUDE.md left untouched - merge the two <<< FEATURE FACTORY >>> blocks into it."
} else {
  Copy-Item -Force $snippet $claudeMd
  Write-Host "* No CLAUDE.md found - installed the snippet as a starter CLAUDE.md."
}

$a = (Get-ChildItem (Join-Path $Target ".claude\agents") -Filter *.md -EA SilentlyContinue).Count
$c = (Get-ChildItem (Join-Path $Target ".claude\commands") -Filter *.md -EA SilentlyContinue).Count
$h = (Get-ChildItem (Join-Path $Target ".claude\hooks") -Filter *.sh -EA SilentlyContinue).Count
Write-Host ""
Write-Host "Installed (counts):"
Write-Host "  agents:   $a  (expect 8)"
Write-Host "  commands: $c  (expect 17)"
Write-Host "  hooks:    $h  (expect 3)"
Write-Host ""
Write-Host "Contract files in .claude/factory/ (imported by CLAUDE.md, or reached by pointer):"
foreach ($f in $contract) {
  if (Test-Path (Join-Path $Target ".claude\factory\$f")) { Write-Host "  ok  $f" } else { Write-Host "  MISSING  $f" }
}
Write-Host "Done. Next: cd `"$Target`", open Claude Code, run /feat-init"
