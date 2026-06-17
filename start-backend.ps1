# Backend EPEC — FastAPI
$env:SECRET_KEY = "dev-secret-local-epec-2026"
$env:DATABASE_URL = "sqlite+aiosqlite:///./data/plataforma_clientes.db"
Write-Host "Iniciando backend en http://localhost:8000 ..." -ForegroundColor Cyan
Write-Host "Docs en http://localhost:8000/docs" -ForegroundColor Green
uv run uvicorn main:create_app --factory --app-dir src --port 8000 --reload
