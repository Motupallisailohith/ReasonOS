# ReasonOS Semantic Graph - Start Both Servers
# Run this after setup.ps1 has been completed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting ReasonOS Semantic Graph Demo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend in a new PowerShell window
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host 'Backend Server' -ForegroundColor Cyan; Write-Host 'Starting on http://localhost:8000' -ForegroundColor Green; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# Start Frontend in a new PowerShell window
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Frontend Server' -ForegroundColor Cyan; Write-Host 'Starting on http://localhost:5173' -ForegroundColor Green; npm run dev"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[OK] Servers Starting!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "   Demo Page:      http://localhost:5173/graph-demo" -ForegroundColor White
Write-Host "   Home Page:      http://localhost:5173/" -ForegroundColor White
Write-Host "   API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Wait 5-10 seconds for servers to fully start" -ForegroundColor Yellow
Write-Host ""
Write-Host "Demo Flow:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:5173/graph-demo" -ForegroundColor White
Write-Host "2. Enter repo path (e.g., ./backend)" -ForegroundColor White
Write-Host "3. Enter function name (e.g., analyze_repository)" -ForegroundColor White
Write-Host "4. Click 'Analyze Repository'" -ForegroundColor White
Write-Host "5. Explore: Graph View, All Usages, Impact Assessment" -ForegroundColor White
Write-Host ""
Write-Host "Ready to demo! Good luck at the hackathon!" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop this script (servers will keep running)" -ForegroundColor Gray
Write-Host "To stop servers: Close the PowerShell windows or press Ctrl+C in them" -ForegroundColor Gray

# Keep this window open
Read-Host "Press Enter to exit this script"
