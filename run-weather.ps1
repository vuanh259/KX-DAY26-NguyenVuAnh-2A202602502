param([ValidateSet('server', 'verify', 'web')][string]$Mode = 'web')
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Get-Content -LiteralPath (Join-Path $PSScriptRoot '.env') -Encoding UTF8 | ForEach-Object {
    if ($_ -match '^\s*(GEMINI_API_KEY|WEATHERAPI_KEY|MCP_SERVER_URL)\s*=\s*(.+)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim().Trim('"').Trim("'"), 'Process')
    }
}
$env:GOOGLE_API_KEY = $env:GEMINI_API_KEY
if ($Mode -eq 'server') {
    if (-not $env:WEATHERAPI_KEY) { throw 'Dien WEATHERAPI_KEY vao .env.' }
    $env:PORT = '8085'
    Push-Location (Join-Path $PSScriptRoot '04-lab\mcp-server')
    try { & .\.venv\Scripts\python.exe -u weather.py } finally { Pop-Location }
} else {
    if (-not $env:GOOGLE_API_KEY) { throw 'Dien GEMINI_API_KEY vao .env.' }
    Push-Location (Join-Path $PSScriptRoot '04-lab\mcp-client')
    try {
        if ($Mode -eq 'verify') { & .\.venv\Scripts\python.exe -u verify_setup.py }
        else { & .\.venv\Scripts\adk.exe web --host 127.0.0.1 --port 8000 }
    } finally { Pop-Location }
}
if ($LASTEXITCODE -ne 0) { throw "Weather lab failed: $LASTEXITCODE" }
