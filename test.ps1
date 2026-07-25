# Test script cho bot
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST BOT TELEGRAM - PRIVACY UPDATE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$content = Get-Content 'f:\workspace12\task_bot.py' -Raw

# Test 1: Data structures
Write-Host "`nTEST 1: Data structures" -ForegroundColor Yellow
$t1 = ($content -match 'user_tasks = \{\}') -and ($content -match 'user_chat_mapping = \{\}')
if ($t1) { Write-Host "  PASS" -ForegroundColor Green } else { Write-Host "  FAIL" -ForegroundColor Red }

# Test 2: Helper functions  
Write-Host "`nTEST 2: Helper functions" -ForegroundColor Yellow
$t2 = ($content -match 'def get_user_id\(') -and ($content -match 'def update_user_chat_mapping\(')
if ($t2) { Write-Host "  PASS" -ForegroundColor Green } else { Write-Host "  FAIL" -ForegroundColor Red }

# Test 3: No forbidden chat_id patterns
Write-Host "`nTEST 3: No chat_id in data ops" -ForegroundColor Yellow
$t3 = -not ($content -match 'user_tasks\[chat_id\]')
if ($t3) { Write-Host "  PASS" -ForegroundColor Green } else { Write-Host "  FAIL" -ForegroundColor Red }

# Test 4: Callback handler
Write-Host "`nTEST 4: Callback handler" -ForegroundColor Yellow
$t4 = ($content -match 'user_id = call\.from_user\.id') -and ($content -match 'chat_id = call\.message\.chat\.id')
if ($t4) { Write-Host "  PASS" -ForegroundColor Green } else { Write-Host "  FAIL" -ForegroundColor Red }

# Test 5: Reminder system
Write-Host "`nTEST 5: Reminder system" -ForegroundColor Yellow
$t5 = ($content -match 'for user_id, tasks') -and ($content -match 'user_chat_mapping\.get')
if ($t5) { Write-Host "  PASS" -ForegroundColor Green } else { Write-Host "  FAIL" -ForegroundColor Red }

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
$passed = @($t1, $t2, $t3, $t4, $t5) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "KET QUA: $passed/5 tests passed" -ForegroundColor $(if ($passed -eq 5) { 'Green' } else { 'Yellow' })

if ($passed -eq 5) {
    Write-Host "`nBOT SAN SANG DEPLOY!" -ForegroundColor Green
    Write-Host "`nCac buoc tiep theo:" -ForegroundColor Cyan
    Write-Host "1. pip install pyTelegramBotAPI python-dotenv requests"
    Write-Host "2. Tao file .env voi TELEGRAM_BOT_TOKEN"
    Write-Host "3. python task_bot.py"
} else {
    Write-Host "`nCAN KIEM TRA LAI!" -ForegroundColor Red
}
