# Frontend EPEC — Vite dev server
Write-Host "Iniciando frontend en http://localhost:5173 ..." -ForegroundColor Cyan
$env:NODE_OPTIONS = "--tls-max-v1.2"
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
cmd /c "npm run dev --prefix frontend"
