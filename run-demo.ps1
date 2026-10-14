param(
    [ValidateSet('function', 'mcp', 'registry', 'versioning', 'auth-server', 'auth-ok', 'auth-fail')]
    [string]$Demo = 'mcp'
)

$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Chua co .venv. Chay: uv venv .venv; uv pip install --python .venv\Scripts\python.exe -r requirements.txt'
}

$demoFiles = @{
    'function' = @('01-function-calling', 'weather_function_calling.py')
    'mcp' = @('02-mcp-basics', 'weather_client.py')
    'registry' = @('03-production', 'registry_client.py')
    'versioning' = @('03-production', 'versioned_client.py')
    'auth-server' = @('03-production', 'auth_server.py')
    'auth-ok' = @('03-production', 'auth_client.py')
    'auth-fail' = @('03-production', 'auth_client.py')
}

if ($Demo -eq 'function') {
    $envPath = Join-Path $PSScriptRoot '.env'
    if (Test-Path -LiteralPath $envPath) {
        Get-Content -LiteralPath $envPath -Encoding UTF8 | ForEach-Object {
            if ($_ -match '^\s*GEMINI_API_KEY\s*=\s*(.+)$') {
                $env:GEMINI_API_KEY = $matches[1].Trim().Trim('"').Trim("'")
            }
        }
    }
    if (-not $env:GEMINI_API_KEY) { throw 'Dien GEMINI_API_KEY vao .env truoc.' }
}

$previousToken = $env:MCP_AUTH_TOKEN
if ($Demo -in @('auth-server', 'auth-ok')) { $env:MCP_AUTH_TOKEN = 'dev-token-abc123' }
if ($Demo -eq 'auth-fail') { $env:MCP_AUTH_TOKEN = 'wrong-token' }

Push-Location (Join-Path $PSScriptRoot $demoFiles[$Demo][0])
try {
    & $pythonPath -u $demoFiles[$Demo][1]
    $demoExitCode = $LASTEXITCODE
    if ($Demo -eq 'auth-fail') {
        if ($demoExitCode -eq 0) { throw 'Token sai lai duoc chap nhan. Kiem tra server.' }
        Write-Host 'Token sai bi tu choi: day la ket qua mong doi cua demo auth-fail.'
    } elseif ($demoExitCode -ne 0) {
        throw "Demo $Demo that bai (exit code $demoExitCode)."
    }
} finally {
    Pop-Location
    $env:MCP_AUTH_TOKEN = $previousToken
}
