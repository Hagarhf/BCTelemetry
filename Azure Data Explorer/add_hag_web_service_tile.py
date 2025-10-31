#!/usr/bin/env python3
"""
Script to add HAG Web Service monitoring tile and query to BCTelemetryDashboard.json
"""

import json
import sys
from pathlib import Path

def add_hag_web_service_tile(dashboard_file):
    """Add HAG Web Service tile and query to the dashboard JSON"""

    # Read the dashboard JSON
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        dashboard = json.load(f)

    # Define the new tile
    new_tile = {
        "id": "e9f0a1b2-c3d4-4567-8901-234567bcdef7",
        "title": "HAG Web Service API (Page 80107)",
        "visualType": "table",
        "pageId": "f4a5b6c7-d8e9-4012-3456-789012abcdef",
        "layout": {
            "x": 0,
            "y": 22,
            "width": 24,
            "height": 8
        },
        "queryRef": {
            "kind": "query",
            "queryId": "d9e0f1a2-b3c4-4678-9012-345678bcdef8"
        },
        "visualOptions": {
            "table__enableRenderLinks": True,
            "colorRulesDisabled": False,
            "colorStyle": "light",
            "crossFilterDisabled": False,
            "drillthroughDisabled": False,
            "crossFilter": [],
            "drillthrough": [],
            "table__renderLinks": [],
            "colorRules": []
        }
    }

    # Define the new query
    query_text = """let TimeRange = 24h;
traces
| where timestamp > ago(TimeRange)
| extend
    alObjectId = tostring(customDimensions.alObjectId),
    alObjectName = tostring(customDimensions.alObjectName)
| where alObjectId == "80107"
| extend executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000
| summarize
    CallCount = count(),
    AvgMs = round(avg(executionTimeMs), 2),
    P95Ms = round(percentile(executionTimeMs, 95), 2),
    MaxMs = round(max(executionTimeMs), 2),
    ErrorCount = countif(severityLevel >= 3),
    LastCall = max(timestamp)
    by bin(timestamp, 1h)
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
    CallCount,
    AvgMs,
    P95Ms,
    MaxMs,
    ErrorCount,
    PerformanceStatus,
    HealthStatus,
    LastCall
| order by timestamp desc"""

    new_query = {
        "dataSource": {
            "kind": "inline",
            "dataSourceId": "05ae5610-5603-45ac-9458-616539c1c150"
        },
        "text": query_text,
        "id": "d9e0f1a2-b3c4-4678-9012-345678bcdef8",
        "usedVariables": []
    }

    # Check if tile already exists
    tile_exists = any(tile.get('id') == new_tile['id'] for tile in dashboard.get('tiles', []))
    if tile_exists:
        print("✓ Tile already exists (ID: e9f0a1b2-c3d4-4567-8901-234567bcdef7)")
    else:
        # Add the tile
        if 'tiles' not in dashboard:
            dashboard['tiles'] = []
        dashboard['tiles'].append(new_tile)
        print("✓ Added HAG Web Service tile")

    # Check if query already exists
    query_exists = any(query.get('id') == new_query['id'] for query in dashboard.get('queries', []))
    if query_exists:
        print("✓ Query already exists (ID: d9e0f1a2-b3c4-4678-9012-345678bcdef8)")
    else:
        # Add the query
        if 'queries' not in dashboard:
            dashboard['queries'] = []
        dashboard['queries'].append(new_query)
        print("✓ Added HAG Web Service query")

    # Write back to file
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Dashboard updated successfully: {dashboard_file}")
    print("\nNext steps:")
    print("1. Upload BCTelemetryDashboard.json to Azure Data Explorer")
    print("2. Navigate to the 'Hagar Extensions' page")
    print("3. Verify the 'HAG Web Service API (Page 80107)' tile appears")

if __name__ == "__main__":
    dashboard_path = Path("C:/AL/BCTelemetry/Azure Data Explorer/BCTelemetryDashboard.json")

    if not dashboard_path.exists():
        print(f"Error: Dashboard file not found: {dashboard_path}")
        sys.exit(1)

    print("Adding HAG Web Service monitoring tile to dashboard...")
    print(f"File: {dashboard_path}\n")

    try:
        add_hag_web_service_tile(dashboard_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
