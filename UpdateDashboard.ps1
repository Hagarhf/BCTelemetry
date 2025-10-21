# Update BCTelemetryDashboard.json to use companyName instead of cloud_RoleInstance

$dashboardPath = "c:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.json"

Write-Host "Reading dashboard file..." -ForegroundColor Cyan
$content = Get-Content $dashboardPath -Raw

Write-Host "Making replacements..." -ForegroundColor Cyan

# Replace comment
$content = $content -replace 'Hybrid tenant/instance filtering - use aadTenantId for SaaS, cloud_RoleInstance for On-Premise', 'Hybrid tenant/instance filtering - use aadTenantId for SaaS, companyName for On-Premise'

# Replace the instanceId calculations
$content = $content -replace 'extend instanceId = iff\(IsSaas, aadTenantId, cloud_RoleInstance\)', 'extend instanceId = iff(IsSaas, aadTenantId, companyName)'

# Replace the where clause
$content = $content -replace 'where instanceId has_any \(_entraTenantId\) or cloud_RoleInstance has_any \(_entraTenantId\)', 'where instanceId has_any (_entraTenantId) or companyName has_any (_entraTenantId)'

Write-Host "Saving updated dashboard..." -ForegroundColor Cyan
$content | Set-Content $dashboardPath -NoNewline

Write-Host "Done!" -ForegroundColor Green
