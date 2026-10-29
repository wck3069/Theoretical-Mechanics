$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$envFile = Join-Path $env:USERPROFILE '.config\tm-ai.env'
if (Test-Path $envFile) {
  Get-Content -Encoding UTF8 $envFile | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
      [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
  }
} else {
  Write-Host "未找到 $envFile；请先创建并填入 TM_AI_KEY / TM_AUTH_*。" -ForegroundColor Yellow
}

if (Test-Path (Join-Path $root 'dist\index.html')) {
  $env:TM_STATIC_ROOT = Join-Path $root 'dist'
}

$hostArg = if ($env:TM_HOST) { $env:TM_HOST } else { '127.0.0.1' }
$portArg = if ($env:TM_PORT) { $env:TM_PORT } else { '8765' }
Write-Host "Serving at http://127.0.0.1:$portArg/ (static root: $($env:TM_STATIC_ROOT))"
python (Join-Path $root 'tools\ai_server.py') --host $hostArg --port $portArg
