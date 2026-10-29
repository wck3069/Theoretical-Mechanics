$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root 'dist'
if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Path $out | Out-Null
Copy-Item (Join-Path $root 'index.html') $out
Copy-Item (Join-Path $root 'catalog.html') $out
Copy-Item (Join-Path $root 'modules') $out -Recurse
Get-ChildItem (Join-Path $out 'modules') -Directory | ForEach-Object {
  $qa = Join-Path $_.FullName 'qa'
  if (Test-Path $qa) { Remove-Item $qa -Recurse -Force }
}
New-Item -ItemType File -Path (Join-Path $out '.nojekyll') | Out-Null
Write-Host "Exported to $out ($((Get-ChildItem $out -Recurse -File).Count) files)"
