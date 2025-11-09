# Test script to verify both backend and frontend are working

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Testing ReasonOS Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Backend
Write-Host "Testing Backend (http://localhost:8000)..." -ForegroundColor Yellow
try {
    $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health"
    Write-Host "[OK] Backend is running: $($backendHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Backend is not responding" -ForegroundColor Red
    Write-Host "Start with: cd backend && uvicorn app.main:app --reload" -ForegroundColor Yellow
}

Write-Host ""

# Test Frontend
Write-Host "Testing Frontend (http://localhost:3000)..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "[OK] Frontend is running" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Frontend is not responding" -ForegroundColor Red
    Write-Host "Start with: cd frontend && npm run dev" -ForegroundColor Yellow
}

Write-Host ""

# Test API Endpoints
Write-Host "Testing Semantic Graph API..." -ForegroundColor Yellow
try {
    $apiDocs = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5
    if ($apiDocs.StatusCode -eq 200) {
        Write-Host "[OK] API documentation available at http://localhost:8000/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] API docs not accessible" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application:" -ForegroundColor White
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Graph Demo: http://localhost:3000/graph-demo" -ForegroundColor Cyan
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
