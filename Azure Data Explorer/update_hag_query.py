#!/usr/bin/env python3
"""
Update HAG Web Service query in BCTelemetryDashboard.json to include function names
"""

import json
import sys
from pathlib import Path

# The new query text with function name extraction
NEW_QUERY = """let TimeRange = 24h;
traces
| where timestamp > ago(TimeRange)
| extend alObjectId = tostring(customDimensions.alObjectId)
| where alObjectId == "80107"
| extend
    endpoint = tostring(customDimensions.endpoint),
    executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000
| extend FunctionName = extract(@"Microsoft\\.NAV\\.(\\w+)", 1, endpoint)
| where isnotempty(FunctionName)
| summarize
    CallCount = count(),
    AvgMs = round(avg(executionTimeMs), 2),
    P95Ms = round(percentile(executionTimeMs, 95), 2),
    MaxMs = round(max(executionTimeMs), 2),
    ErrorCount = countif(severityLevel >= 3),
    LastCall = max(timestamp)
    by bin(timestamp, 1h), FunctionName
| extend MinutesSinceLastCall = datetime_diff('minute', now(), LastCall)
| extend
    PerformanceStatus = case(
        AvgMs > 1000, "🔴 Slow (>1s)",
        AvgMs > 500, "⚠️ Moderate (500ms-1s)",
        "✅ Fast (<500ms)"
    ),
    HealthStatus = case(
        ErrorCount > 0, "🔴 Has Errors",
        MinutesSinceLastCall > 60, "⚠️ Inactive >1h",
        "✅ Healthy"
    )
| project
    timestamp,
    FunctionName,
    CallCount,
    AvgMs,
    P95Ms,
    MaxMs,
    ErrorCount,
    PerformanceStatus,
    HealthStatus,
    LastCall
| order by timestamp desc, CallCount desc"""

def update_dashboard():
    dashboard_path = Path("C:/AL/BCTelemetry/Azure Data Explorer/BCTelemetryDashboard.json")

    # Read dashboard
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        dashboard = json.load(f)

    # Find and update the HAG Web Service query (ID: d9e0f1a2-b3c4-4678-9012-345678bcdef8)
    query_id = "d9e0f1a2-b3c4-4678-9012-345678bcdef8"
    updated = False

    for query in dashboard.get('queries', []):
        if query.get('id') == query_id:
            print(f"Found query with ID: {query_id}")
            print(f"Old query length: {len(query.get('text', ''))}")
            query['text'] = NEW_QUERY
            print(f"New query length: {len(NEW_QUERY)}")
            updated = True
            break

    if not updated:
        print(f"ERROR: Query with ID {query_id} not found!")
        return False

    # Write back
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)

    print("\n✅ Successfully updated HAG Web Service query!")
    print("\nChanges:")
    print("- Added 'endpoint' extraction from customDimensions")
    print("- Added 'FunctionName' extraction using regex")
    print("- Added 'FunctionName' to grouping (by bin(timestamp, 1h), FunctionName)")
    print("- Added 'FunctionName' column to output")
    print("\nThe dashboard tile will now show function names like:")
    print("  getInvoices, getTransactions, getCustomer, etc.")

    return True

if __name__ == "__main__":
    try:
        success = update_dashboard()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
