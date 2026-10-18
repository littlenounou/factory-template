#requires -version 5
param([Parameter(Mandatory=$true)][string]$Target)

if (-not (Test-Path -PathType Container $Target)) { Write-Error "Target '$Target' is not a directory."; exit 1 }
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path

$need = @(".claude\agents", ".claude\commands", ".claude\hooks", ".claude\factory")
$missing = @()
foreach ($d in $need) { if (-not (Test-Path -PathType Container (Join-Path $Src $d))) { $missing += $d } }
if (-not (Test-Path (Join-Path $Src ".claude\settings.json"))) { $missing += ".claude\settings.json" }
# The contract points at these by relative path; a missing one is a silent dead pointer.
$contract = @("CONVENTIONS.md","terminology-zh-tw.md","CLAUDE-rationale.md","EXPLORE-MODE.md","PHASE-BOUNDARIES.md","WRITING-FOR-AGENTS.md")
foreach ($f in $contract) {
  if (-not (Test-Path (Join-Path $Src ".claude\factory\$f"))) { $missing += ".claude\factory\$f" }
}
if ($missing.Count -gt 0) {
  Write-Error ("This template copy is incomplete - missing: " + ($missing -join ", ") + ". Re-extract the ZIP with hidden files included.")
  exit 1
}

# Template-owned files are overwritten on every install. Two files are the repo's own and
# are handled below instead: .claude/factory/MEMORY.md and .claude/settings.json.
$dst  = Join-Path $Target ".claude"
$fdst = Join-Path $dst "factory"
New-Item -ItemType Directory -Force -Path $fdst | Out-Null
Get-ChildItem -Force (Join-Path $Src ".claude") | Where-Object { $_.Name -notin @("settings.json", "factory") } |
  ForEach-Object { Copy-Item -Recurse -Force $_.FullName $dst }
Get-ChildItem -Force (Join-Path $Src ".claude\factory") | Where-Object { $_.Name -ne "MEMORY.md" } |
  ForEach-Object { Copy-Item -Recurse -Force $_.FullName $fdst }
Write-Host "* Copied .claude/ into $Target"

# MEMORY.md is written by /feat-distill, so the repo's copy is never overwritten. It lives in
# <artifactsDir>; read that from project.json the same way the hooks do.
$artDir = ".claude/factory"
$proj = Join-Path $fdst "project.json"
if (Test-Path $proj) {
  try {
    $p = Get-Content -Raw $proj | ConvertFrom-Json
    if ($p.artifactsDir) { $artDir = ([string]$p.artifactsDir -replace '\\', '/').TrimEnd('/') -replace '^\./', '' }
  } catch { }
  if (-not $artDir) { $artDir = ".claude/factory" }
}
$mem = Join-Path $fdst "MEMORY.md"
if ($artDir -ne ".claude/factory") {
  Write-Host "* MEMORY.md not installed: artifactsDir is '$artDir', so the memory layer is"
  Write-Host "  $artDir/MEMORY.md. To start one, copy the template's .claude/factory/MEMORY.md there."
} elseif (Test-Path $mem) {
  Write-Host "* Kept the repo's .claude/factory/MEMORY.md (never overwritten)."
} else {
  Copy-Item -Force (Join-Path $Src ".claude\factory\MEMORY.md") $mem
  Write-Host "* Installed a starter .claude/factory/MEMORY.md."
}

# settings.json: the template owns "hooks"; every other key (permissions, env, ...) is the repo's.
# Merge: keep the repo's keys, add keys only the template has, replace "hooks" with the template's.
$set = Join-Path $dst "settings.json"
$tplPath = Join-Path $Src ".claude\settings.json"
if (-not (Test-Path $set)) {
  Copy-Item -Force $tplPath $set
  Write-Host "* Installed .claude/settings.json."
} else {
  $cur = $null
  try { $cur = Get-Content -Raw $set | ConvertFrom-Json } catch { }
  if (-not ($cur -is [System.Management.Automation.PSCustomObject])) {
    Copy-Item -Force $set "$set.bak"
    Copy-Item -Force $tplPath $set
    Write-Warning "Could not merge .claude/settings.json (the file is not a JSON object). Replaced it with the template's; your old file is .claude/settings.json.bak. Copy back any permissions or other settings you need."
  } else {
    $tpl = Get-Content -Raw $tplPath | ConvertFrom-Json
    $tplHooks = $tpl.hooks | ConvertTo-Json -Depth 50 -Compress
    $changed = $false
    if ($null -eq $cur.hooks) {
      $note = "* Merged .claude/settings.json: added the factory hooks, kept your other settings."
      $changed = $true
    } elseif (($cur.hooks | ConvertTo-Json -Depth 50 -Compress) -eq $tplHooks) {
      $note = "* Merged .claude/settings.json: hooks already current, kept your other settings."
    } else {
      Copy-Item -Force $set "$set.bak"
      $note = "* Merged .claude/settings.json: replaced `"hooks`" with the template's, kept your other`n  settings. The old file is .claude/settings.json.bak; re-add any hooks of your own from it."
      $changed = $true
    }
    foreach ($prop in $tpl.PSObject.Properties) {
      if ($prop.Name -eq "hooks") { continue }
      if ($null -eq $cur.PSObject.Properties[$prop.Name]) {
        $cur | Add-Member -NotePropertyName $prop.Name -NotePropertyValue $prop.Value
        $changed = $true
      }
    }
    # Rewrite only when something changes, so an up-to-date file keeps its formatting.
    if ($changed) {
      $cur | Add-Member -Force -NotePropertyName "hooks" -NotePropertyValue $tpl.hooks
      $setFull = (Resolve-Path $set).Path
      # UTF-8 without BOM: Windows PowerShell's -Encoding UTF8 would add one.
      [System.IO.File]::WriteAllText($setFull, ($cur | ConvertTo-Json -Depth 50), (New-Object System.Text.UTF8Encoding $false))
    }
    Write-Host $note
  }
}

$claudeMd = Join-Path $Target "CLAUDE.md"
$snippet  = Join-Path $Src "CLAUDE.factory-snippet.md"
if (Test-Path $claudeMd) {
  Copy-Item -Force $snippet (Join-Path $Target "CLAUDE.factory-snippet.md")
  Write-Host "* Existing CLAUDE.md left untouched - add the two @import lines from the <<< FEATURE FACTORY >>> block."
  Write-Host "  Upgrading? Delete the old '### Feature Factory' block - it now lives in CONVENTIONS.md."
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
Write-Host "  commands: $c  (expect 20)"
Write-Host "  hooks:    $h  (expect 3)"
Write-Host ""
Write-Host "Contract files in .claude/factory/ (imported by CLAUDE.md, or reached by pointer):"
foreach ($f in $contract) {
  if (Test-Path (Join-Path $Target ".claude\factory\$f")) { Write-Host "  ok  $f" } else { Write-Host "  MISSING  $f" }
}

# The hooks in settings.json use onFailure: "block", which needs Claude Code 2.1.295+.
# Warn only: the installer may run in a shell where `claude` is not on PATH.
$needVer = [version]"2.1.295"
Write-Host ""
$cmd = Get-Command claude -EA SilentlyContinue
if ($cmd) {
  $raw = (& claude --version 2>$null | Out-String)
  if ($raw -match '(\d+(\.\d+){1,3})') {
    $haveVer = [version]$Matches[1]
    if ($haveVer -lt $needVer) {
      Write-Warning "Claude Code $haveVer is older than $needVer. The hooks rely on onFailure: `"block`" (a hook that cannot run blocks the tool call). Upgrade Claude Code before using this repo."
    } else {
      Write-Host "Claude Code $haveVer - ok (needs $needVer+)."
    }
  } else {
    Write-Host "NOTE: could not read the Claude Code version; check that it is $needVer or later."
  }
} else {
  Write-Host "NOTE: 'claude' not found on PATH here; check that Claude Code is $needVer or later."
}
Write-Host "Done. Next: cd `"$Target`", open Claude Code, run /feat-init"
