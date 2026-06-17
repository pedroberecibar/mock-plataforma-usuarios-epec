# Backend EPEC — FastAPI

# Cargar .env si existe (nunca commitear ese archivo)
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)\s*$') {
            [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
        }
    }
    Write-Host ".env cargado" -ForegroundColor DarkGray
}

# Defaults que .env puede sobreescribir
if (-not $env:SECRET_KEY)    { $env:SECRET_KEY    = "dev-secret-local-epec-2026" }
if (-not $env:DATABASE_URL)  { $env:DATABASE_URL  = "sqlite+aiosqlite:///./data/plataforma_clientes.db" }

# Si OR_INSTANT_CLIENT está definido, agregar al PATH para que las DLL se encuentren
if ($env:OR_INSTANT_CLIENT) {
    $env:PATH = "$($env:OR_INSTANT_CLIENT);$($env:PATH)"
    Write-Host "Oracle Instant Client: $($env:OR_INSTANT_CLIENT)" -ForegroundColor DarkGray
}

# Variables Oracle — definir en .env (nunca commitear).
# Si no están definidas, POST /ingest/consumo responde HTTP 503.
#
# OR_HOST           = <oracle-host>
# OR_PORT           = 1521
# OR_SERVICE_NAME   = <service>
# OR_USER           = <user>
# OR_PASS           = <password>
# OR_INSTANT_CLIENT = C:\Oracle\instantclient_23_6   (vacío = modo thin)

# Scheduler automático — backfill al arrancar + loop periódico.
# INGEST_DESDE_INICIAL  = 2026-01-01   (default: hoy - 90 días)
# INGEST_LOOKBACK_DIAS  = 3
# INGEST_INTERVAL_HORAS = 6

Write-Host "Iniciando backend en http://localhost:8000 ..." -ForegroundColor Cyan
Write-Host "Docs en http://localhost:8000/docs" -ForegroundColor Green
uv run uvicorn main:create_app --factory --app-dir src --port 8000 --reload
