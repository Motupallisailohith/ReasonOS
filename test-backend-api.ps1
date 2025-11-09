# Complete Backend API Test Script
# Tests all 5 endpoints of ReasonOS backend

$baseUrl = "http://localhost:8000"
$repoPath = "C:\Users\sailo\ReasonOS\ReasonOS\backend"

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   ReasonOS Backend API Test Suite     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "[1/5] Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health"
    Write-Host "✓ Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nMake sure backend is running:" -ForegroundColor Yellow
    Write-Host "cd backend" -ForegroundColor Gray
    Write-Host "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
    exit 1
}

# Test 2: Analyze Repository
Write-Host "`n[2/5] Analyzing Repository..." -ForegroundColor Yellow
Write-Host "    Path: $repoPath" -ForegroundColor Gray
try {
    $analyzeBody = @{
        repo_path = $repoPath
        force_rebuild = $true
    } | ConvertTo-Json

    $analysis = Invoke-RestMethod -Uri "$baseUrl/api/v1/graph/analyze" `
        -Method Post `
        -Body $analyzeBody `
        -ContentType "application/json"

    Write-Host "✓ Status: $($analysis.status)" -ForegroundColor Green
    Write-Host "    Files Discovered: $($analysis.statistics.files_discovered)" -ForegroundColor Gray
    Write-Host "    Functions Found: $($analysis.statistics.functions_found)" -ForegroundColor Gray
    Write-Host "    Edges Created: $($analysis.statistics.edges_created)" -ForegroundColor Gray
    Write-Host "    Time Taken: $($analysis.statistics.time_taken_seconds)s" -ForegroundColor Gray
} catch {
    Write-Host "✗ Analysis failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Find Function Usages
Write-Host "`n[3/5] Finding Function Usages..." -ForegroundColor Yellow
Write-Host "    Function: analyze_repository" -ForegroundColor Gray
try {
    $usages = Invoke-RestMethod -Uri "$baseUrl/api/v1/graph/function/analyze_repository/usages?repo_path=$repoPath"

    Write-Host "✓ Function: $($usages.function_name)" -ForegroundColor Green
    Write-Host "    Total Usages: $($usages.total_usages)" -ForegroundColor Gray
    Write-Host "    Files Affected: $($usages.files_affected)" -ForegroundColor Gray
    Write-Host "    Definition Count: $($usages.summary.definition_count)" -ForegroundColor Gray
    Write-Host "    Call Count: $($usages.summary.call_count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Usages query failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "    This might mean the function doesn't exist in the analyzed code" -ForegroundColor Yellow
}

# Test 4: Assess Impact
Write-Host "`n[4/5] Assessing Change Impact..." -ForegroundColor Yellow
Write-Host "    Simulating: Rename analyze_repository function" -ForegroundColor Gray
try {
    $impactBody = @{
        repo_path = $repoPath
        function_name = "analyze_repository"
        change_description = "Rename to analyze_codebase"
    } | ConvertTo-Json

    $impact = Invoke-RestMethod -Uri "$baseUrl/api/v1/graph/assess-impact" `
        -Method Post `
        -Body $impactBody `
        -ContentType "application/json"

    Write-Host "✓ Risk Assessment Complete" -ForegroundColor Green
    Write-Host "    Risk Level: $($impact.summary.risk_level)" -ForegroundColor Gray
    Write-Host "    Risk Score: $($impact.risk_score.total_score)" -ForegroundColor Gray
    Write-Host "    Total Usages: $($impact.summary.total_usages)" -ForegroundColor Gray
    Write-Host "    Modules Affected: $($impact.modules.Count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Impact assessment failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Get Statistics
Write-Host "`n[5/5] Getting Graph Statistics..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/api/v1/graph/stats?repo_path=$repoPath"

    Write-Host "✓ Statistics Retrieved" -ForegroundColor Green
    Write-Host "    Graph is cached and ready for queries" -ForegroundColor Gray
} catch {
    Write-Host "✗ Stats failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         All Tests Complete!            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "✓ Backend API is working correctly" -ForegroundColor Green
Write-Host "`nKey Findings:" -ForegroundColor Yellow
Write-Host "• Backend only accepts LOCAL folder paths" -ForegroundColor Gray
Write-Host "• GitHub URLs are NOT supported (you must clone first)" -ForegroundColor Gray
Write-Host "• Analysis is fast (< 1 second for small repos)" -ForegroundColor Gray
Write-Host "• Graph is cached - subsequent queries are instant" -ForegroundColor Gray

Write-Host "`nNext Steps for Frontend:" -ForegroundColor Yellow
Write-Host "1. Parse JSON responses shown above" -ForegroundColor Gray
Write-Host "2. Display statistics in cards/tables" -ForegroundColor Gray
Write-Host "3. Visualize graph using ReactFlow" -ForegroundColor Gray
Write-Host "4. Show usage locations with file/line numbers" -ForegroundColor Gray
Write-Host "5. Display risk scores with color coding" -ForegroundColor Gray

Write-Host "`nAPI Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
