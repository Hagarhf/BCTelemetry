<#
.SYNOPSIS
    BC Telemetry MCP Server - PowerShell útgáfa

.DESCRIPTION
    MCP server sem tengist Azure Application Insights og keyrir KQL queries
    fyrir Olis, Storkaup og Bananar.

.NOTES
    Notkun: Þetta script er keyrt af Claude Code MCP
#>

$ErrorActionPreference = "Stop"

# Application Insights configurations
$AppInsights = @{
    "olis" = @{
        Name = "Olis-Application-Insights"
        ResourceGroup = "rg-BC_Teymi"
    }
    "storkaup" = @{
        Name = "Storkaup-Application-Insights"
        ResourceGroup = "rg-BC_Teymi"
    }
    "bananar" = @{
        Name = "Bananar-Application-Insights-Resource"
        ResourceGroup = "rg-BC_Teymi"
    }
}

function Invoke-KqlQuery {
    param(
        [string]$Query,
        [string]$Company = "olis",
        [string]$Timespan = "P7D"
    )

    $config = $AppInsights[$Company.ToLower()]
    if (-not $config) {
        $config = $AppInsights["olis"]
    }

    try {
        $result = az monitor app-insights query `
            --app $config.Name `
            --resource-group $config.ResourceGroup `
            --analytics-query $Query `
            --timespan $Timespan `
            --output json 2>&1

        if ($LASTEXITCODE -eq 0) {
            return @{ success = $true; data = ($result | ConvertFrom-Json) }
        } else {
            return @{ success = $false; error = $result }
        }
    }
    catch {
        return @{ success = $false; error = $_.Exception.Message }
    }
}

function Get-ExtensionUsage {
    param(
        [string]$Company = "olis",
        [int]$Days = 30
    )

    $query = @"
traces
| where timestamp > ago(${Days}d)
| extend extensionName = tostring(customDimensions.extensionName)
| extend extensionPublisher = tostring(customDimensions.extensionPublisher)
| where isnotempty(extensionName)
| summarize ActivityCount = count(), UniqueUsers = dcount(user_Id), LastActivity = max(timestamp) by extensionName, extensionPublisher
| extend UsageLevel = case(ActivityCount < 10, "Low", ActivityCount < 100, "Moderate", ActivityCount < 1000, "Active", "Heavy")
| order by ActivityCount desc
| take 50
"@

    return Invoke-KqlQuery -Query $query -Company $Company -Timespan "P${Days}D"
}

function Get-ErrorSummary {
    param(
        [string]$Company = "olis",
        [int]$Hours = 24
    )

    $query = @"
traces
| where timestamp > ago(${Hours}h)
| where severityLevel >= 3
| extend extensionName = tostring(customDimensions.extensionName)
| summarize ErrorCount = count(), UniqueErrors = dcount(message), LastError = max(timestamp), SampleError = any(message) by extensionName
| order by ErrorCount desc
| take 20
"@

    return Invoke-KqlQuery -Query $query -Company $Company -Timespan "PT${Hours}H"
}

function Get-PageUsage {
    param(
        [string]$Company = "olis",
        [int]$Days = 30
    )

    $query = @"
traces
| where timestamp > ago(${Days}d)
| extend eventId = tostring(customDimensions.eventId)
| where eventId == "RT0005"
| extend pageName = tostring(customDimensions.alObjectName)
| extend pageId = tostring(customDimensions.alObjectId)
| extend extensionName = tostring(customDimensions.extensionName)
| where isnotempty(pageName)
| summarize OpenCount = count(), UniqueUsers = dcount(user_Id), LastOpened = max(timestamp) by pageName, pageId, extensionName
| order by OpenCount desc
| take 50
"@

    return Invoke-KqlQuery -Query $query -Company $Company -Timespan "P${Days}D"
}

function Get-PerformanceAnalysis {
    param(
        [string]$Company = "olis",
        [int]$Days = 7
    )

    $query = @"
traces
| where timestamp > ago(${Days}d)
| extend extensionName = tostring(customDimensions.extensionName)
| extend objectName = tostring(customDimensions.alObjectName)
| extend executionTimeMs = todouble(customDimensions.serverExecutionTime)
| where isnotempty(objectName) and executionTimeMs > 0
| summarize TotalExecutions = count(), AvgMs = round(avg(executionTimeMs), 2), P95Ms = round(percentile(executionTimeMs, 95), 2) by extensionName, objectName
| extend Rating = case(P95Ms < 100, "Excellent", P95Ms < 500, "Good", P95Ms < 2000, "Acceptable", "Slow")
| where P95Ms > 500
| order by P95Ms desc
| take 30
"@

    return Invoke-KqlQuery -Query $query -Company $Company -Timespan "P${Days}D"
}

function Get-ListCompanies {
    return @{
        success = $true
        data = @{
            companies = @("olis", "storkaup", "bananar")
            details = $AppInsights
        }
    }
}

# MCP Protocol Handler
function Handle-Request {
    param([hashtable]$Request)

    $tool = $Request.tool
    $params = $Request.params
    if (-not $params) { $params = @{} }

    switch ($tool) {
        "list_companies" { return Get-ListCompanies }
        "list_tools" {
            return @{
                success = $true
                data = @{
                    extension_usage = @{ description = "Extension notkun"; params = @("company", "days") }
                    error_summary = @{ description = "Villur"; params = @("company", "hours") }
                    page_usage = @{ description = "Síðunotkun"; params = @("company", "days") }
                    performance_analysis = @{ description = "Performance"; params = @("company", "days") }
                    custom_query = @{ description = "Sérsniðin KQL"; params = @("company", "query", "timespan") }
                }
            }
        }
        "extension_usage" {
            $company = if ($params.company) { $params.company } else { "olis" }
            $days = if ($params.days) { [int]$params.days } else { 30 }
            return Get-ExtensionUsage -Company $company -Days $days
        }
        "error_summary" {
            $company = if ($params.company) { $params.company } else { "olis" }
            $hours = if ($params.hours) { [int]$params.hours } else { 24 }
            return Get-ErrorSummary -Company $company -Hours $hours
        }
        "page_usage" {
            $company = if ($params.company) { $params.company } else { "olis" }
            $days = if ($params.days) { [int]$params.days } else { 30 }
            return Get-PageUsage -Company $company -Days $days
        }
        "performance_analysis" {
            $company = if ($params.company) { $params.company } else { "olis" }
            $days = if ($params.days) { [int]$params.days } else { 7 }
            return Get-PerformanceAnalysis -Company $company -Days $days
        }
        "custom_query" {
            $company = if ($params.company) { $params.company } else { "olis" }
            $query = $params.query
            $timespan = if ($params.timespan) { $params.timespan } else { "P7D" }
            if (-not $query) {
                return @{ success = $false; error = "Query is required" }
            }
            return Invoke-KqlQuery -Query $query -Company $company -Timespan $timespan
        }
        default {
            return @{ success = $false; error = "Unknown tool: $tool" }
        }
    }
}

# Main loop - read JSON from stdin, write JSON to stdout
Write-Host "BC Telemetry MCP Server (PowerShell) started" -ForegroundColor Green | Out-Null

while ($true) {
    try {
        $line = [Console]::In.ReadLine()
        if ($null -eq $line) { break }
        if ([string]::IsNullOrWhiteSpace($line)) { continue }

        $request = $line | ConvertFrom-Json -AsHashtable
        $response = Handle-Request -Request $request

        $jsonResponse = $response | ConvertTo-Json -Depth 10 -Compress
        [Console]::Out.WriteLine($jsonResponse)
        [Console]::Out.Flush()
    }
    catch {
        $errorResponse = @{ success = $false; error = $_.Exception.Message } | ConvertTo-Json -Compress
        [Console]::Out.WriteLine($errorResponse)
        [Console]::Out.Flush()
    }
}
