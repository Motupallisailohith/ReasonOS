Write-Host "`nTesting Gemini AI Integration...`n" -ForegroundColor Cyan

$testQuery = @{
    query = "Show me where processPayment is used"
    repo_path = "C:\Users\sailo\ReasonOS\ReasonOS"
    use_ai = $true
}

$json = $testQuery | ConvertTo-Json
Write-Host "Sending request..." -ForegroundColor Yellow
Write-Host $json -ForegroundColor Gray

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/graph/query" -Method Post -Body $json -ContentType "application/json"

    Write-Host "`n✓ SUCCESS!" -ForegroundColor Green
    Write-Host "`nAI Understanding:" -ForegroundColor Cyan
    Write-Host "Function: $($result.intent.function_name)" -ForegroundColor White
    Write-Host "Action: $($result.intent.action)" -ForegroundColor White
    Write-Host "Confidence: $($result.intent.confidence)" -ForegroundColor White

    if ($result.intent.reasoning) {
        Write-Host "Reasoning: $($result.intent.reasoning)" -ForegroundColor Gray
    }

    Write-Host "`n✓ Gemini AI is working!`n" -ForegroundColor Green

} catch {
    Write-Host "`n✗ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    Write-Host "`nMake sure backend is restarted to load .env file" -ForegroundColor Gray
}
