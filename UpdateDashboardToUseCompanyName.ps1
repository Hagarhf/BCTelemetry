# PowerShell script to update BCTelemetryDashboard.json to use companyName instead of cloud_RoleInstance

$dashboardPath = "c:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.json"

Write-Host "Reading dashboard file..." -ForegroundColor Cyan
$content = Get-Content $dashboardPath -Raw

Write-Host "Making replacements..." -ForegroundColor Cyan

# Replace comment
$content = $content -replace 'Hybrid tenant/instance filtering - use aadTenantId for SaaS, cloud_RoleInstance for On-Premise', 'Hybrid tenant/instance filtering - use aadTenantId for SaaS, companyName for On-Premise (BC21 uses companyName)'

# Replace the instanceId calculations (there are 2 occurrences)
$content = $content -replace 'extend instanceId = iff\(IsSaas, aadTenantId, cloud_RoleInstance\)', 'extend instanceId = iff(IsSaas, aadTenantId, companyName)'

# Replace the where clause
$content = $content -replace 'where instanceId has_any \(_entraTenantId\) or cloud_RoleInstance has_any \(_entraTenantId\)', 'where instanceId has_any (_entraTenantId) or companyName has_any (_entraTenantId)'

Write-Host "Saving updated dashboard..." -ForegroundColor Cyan
$content | Set-Content $dashboardPath -NoNewline

Write-Host "✓ Dashboard updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Yellow
Write-Host "  - Updated instanceId to use companyName instead of cloud_RoleInstance for On-Premise" -ForegroundColor White
Write-Host "  - Updated 2 extend statements" -ForegroundColor White
Write-Host "  - Updated where clause" -ForegroundColor White
Write-Host "  - Updated comment to reflect BC21 compatibility" -ForegroundColor White
Write-Host ""
Write-Host "Your dashboard is now ready to use with company names:" -ForegroundColor Cyan
Write-Host "  Production: Bananar" -ForegroundColor Green
Write-Host "  UAT: BAN underscore PROD underscore 230807" -ForegroundColor Green
