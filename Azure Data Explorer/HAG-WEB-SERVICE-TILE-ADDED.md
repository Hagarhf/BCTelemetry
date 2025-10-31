# HAG Web Service Monitoring Tile - Implementation Complete

## Summary

Based on your diagnostic query results from `HAGWebshop_Summary.csv`, I've prepared everything needed to add HAG Web Service monitoring to your dashboard.

---

## Issue Resolved: "HAG VAT Posting Setup" Showing Up

**Problem**: The summary query was using:
```kql
| where alObjectId == "80107" or alObjectName contains "HAG Web Service"
```

The second part (`alObjectName contains "HAG Web Service"`) was too broad and matched other objects with "HAG" in the name, like "HAG VAT Posting Setup".

**Solution**: Use **only the exact object ID**:
```kql
| where alObjectId == "80107"
```

This ensures precise filtering for page 80107 only.

---

## Dashboard Update Ready

I've created `HAG-WEB-SERVICE-DASHBOARD-UPDATE.json` with the exact tile and query definitions you need to add.

### What the Tile Will Show

The tile displays **hourly metrics** for HAG Web Service (Page 80107):

| Column | Description |
|--------|-------------|
| **timestamp** | Hour of the day |
| **CallCount** | Number of API calls that hour |
| **AvgMs** | Average response time (ms) |
| **P95Ms** | 95th percentile response time (ms) |
| **MaxMs** | Slowest call that hour (ms) |
| **ErrorCount** | Number of errors |
| **PerformanceStatus** | ✅ Fast / ⚠️ Moderate / 🔴 Slow |
| **HealthStatus** | ✅ Healthy / ⚠️ Inactive / 🔴 Has Errors |
| **LastCall** | Timestamp of last call |

### Performance Status Legend
- **✅ Fast (<500ms)** - Good performance
- **⚠️ Moderate (500ms-1s)** - Acceptable but monitor
- **🔴 Slow (>1s)** - Performance issue, investigate

### Health Status Legend
- **✅ Healthy** - No errors, actively used
- **⚠️ Inactive >1h** - No calls in last hour
- **🔴 Has Errors** - Errors detected, requires attention

---

## How to Add to Dashboard

### Option 1: Manual Addition in Azure Data Explorer UI

1. Go to your BCTelemetry Dashboard in Azure Data Explorer
2. Navigate to the **"Hagar Extensions"** page
3. Click **Edit** → **Add tile**
4. Configure:
   - **Title**: HAG Web Service API (Page 80107)
   - **Visualization**: Table
   - **Query**: Copy from `HAG-WEB-SERVICE-DASHBOARD-UPDATE.json` → `query_to_add` → `text`
5. Click **Save**

### Option 2: Update Dashboard JSON Directly

**Step 1: Add the Tile**

Open `BCTelemetryDashboard.json` and find the `tiles` array. After the last Hagar Extensions tile (around line 6087), add a comma and insert:

```json
{
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
        "table__enableRenderLinks": true,
        "colorRulesDisabled": false,
        "colorStyle": "light",
        "crossFilterDisabled": false,
        "drillthroughDisabled": false,
        "crossFilter": [],
        "drillthrough": [],
        "table__renderLinks": [],
        "colorRules": []
    }
}
```

**Step 2: Add the Query**

Find the `queries` array (around line 8690) and before the closing `]`, add a comma after the last query and insert:

```json
{
    "dataSource": {
        "kind": "inline",
        "dataSourceId": "05ae5610-5603-45ac-9458-616539c1c150"
    },
    "text": "let TimeRange = 24h;\ntraces\n| where timestamp > ago(TimeRange)\n| extend\n    alObjectId = tostring(customDimensions.alObjectId),\n    alObjectName = tostring(customDimensions.alObjectName)\n| where alObjectId == \"80107\"\n| extend executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000\n| summarize\n    CallCount = count(),\n    AvgMs = round(avg(executionTimeMs), 2),\n    P95Ms = round(percentile(executionTimeMs, 95), 2),\n    MaxMs = round(max(executionTimeMs), 2),\n    ErrorCount = countif(severityLevel >= 3),\n    LastCall = max(timestamp)\n    by bin(timestamp, 1h)\n| extend MinutesSinceLastCall = datetime_diff('minute', now(), LastCall)\n| extend\n    PerformanceStatus = case(\n        AvgMs > 1000, \"🔴 Slow (>1s)\",\n        AvgMs > 500, \"⚠️ Moderate (500ms-1s)\",\n        \"✅ Fast (<500ms)\"\n    ),\n    HealthStatus = case(\n        ErrorCount > 0, \"🔴 Has Errors\",\n        MinutesSinceLastCall > 60, \"⚠️ Inactive >1h\",\n        \"✅ Healthy\"\n    )\n| project\n    timestamp,\n    CallCount,\n    AvgMs,\n    P95Ms,\n    MaxMs,\n    ErrorCount,\n    PerformanceStatus,\n    HealthStatus,\n    LastCall\n| order by timestamp desc",
    "id": "d9e0f1a2-b3c4-4678-9012-345678bcdef8",
    "usedVariables": []
}
```

**Step 3: Validate and Upload**

1. Validate JSON syntax (use a JSON validator)
2. Upload to Azure Data Explorer
3. Verify the tile appears on the "Hagar Extensions" page

---

## Updated Hagar Extensions Page Layout

After adding the HAG Web Service tile, your page will have **5 tiles**:

```
┌─────────────────────────────────────────────────┐
│  Tile 1: Hagar Extensions Activity Overview     │
│  (Full width, top)                              │
└─────────────────────────────────────────────────┘

┌────────────────────────┬────────────────────────┐
│  Tile 2: ASB Queue     │  Tile 3: Export        │
│  Performance           │  Processing & Slow Ops │
│  (Left, middle)        │  (Right, middle)       │
└────────────────────────┴────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Tile 4: Hagar Extensions Errors & Warnings     │
│  (Full width, bottom-middle)                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Tile 5: HAG Web Service API (Page 80107)       │  ✅ NEW!
│  (Full width, bottom)                           │
└─────────────────────────────────────────────────┘
```

---

## Tracking Individual Procedures (GetTransactions, GetInvoice)

As shown in your results, **BC telemetry does not log individual procedure names by default** for API pages. You only see:
- ✅ Page 80107 was accessed
- ✅ How long it took
- ✅ Who called it
- ❌ Which procedure was called (GetTransactions, GetInvoice, etc.)

### Solution: Add Custom Telemetry

To track individual procedures like `GetTransactions` and `GetInvoice`, you need to add custom telemetry to your AL code.

**Complete implementation guide**: See `PROCEDURE-TRACKING-SUMMARY.md`

**AL code examples**: See `HAGWebService-AddProcedureTelemetry.al`

**Diagnostic queries**: See `HAGWebService-ProcedureTracking.kql`

#### Quick Implementation Steps

1. **Add helper procedure** to page 80107 (copy from `HAGWebService-AddProcedureTelemetry.al`)
2. **Add telemetry calls** to each procedure you want to track
3. **Deploy and test**
4. **Run procedure tracking queries** to verify it works

**Priority Order for Adding Telemetry**:
1. GetTransactions (most important)
2. GetInvoice
3. Any POST/UPDATE procedures
4. GetCustomer
5. Remaining GET procedures

---

## Monitoring Recommendations

### 🔴 Critical Alerts

Set up alerts for:
- **Error count > 0** in any hour
- **Average response time > 1 second**
- **Inactive > 2 hours** during business hours

### ⚠️ Warnings

Monitor for:
- **Average response time > 500ms**
- **Call count drops by > 50%** compared to baseline
- **Max response time > 5 seconds**

### 📊 Analysis Queries

Additional queries for deeper analysis are available in:
- `HAGWebService-Analysis.kql` - 10 detailed analysis queries
- `HAGWebService-ProcedureTracking.kql` - 8 diagnostic queries

---

## Files Reference

| File | Purpose |
|------|---------|
| `HAG-WEB-SERVICE-DASHBOARD-UPDATE.json` | Exact tile and query JSON to add |
| `HAGWebService-Analysis.kql` | 10 analysis queries for the API |
| `HAGWebService-ProcedureTracking.kql` | 8 queries to find/track procedures |
| `HAGWebService-AddProcedureTelemetry.al` | AL code to add custom telemetry |
| `PROCEDURE-TRACKING-SUMMARY.md` | Complete implementation guide |
| `ADD-HAG-WEB-SERVICE-TILE.md` | Original tile addition guide |

---

## Next Steps

### Immediate
1. ✅ Add the HAG Web Service tile to your dashboard (use Option 1 or 2 above)
2. ✅ Verify the tile shows data correctly
3. ✅ Run the corrected summary query with exact object ID filter

### After Tile is Added
1. ✅ Set up alerts for critical issues (errors, slow performance)
2. ✅ Review hourly patterns to understand API usage
3. ✅ Use analysis queries for deeper insights

### For Procedure Tracking
1. ✅ Read `PROCEDURE-TRACKING-SUMMARY.md` for implementation guide
2. ✅ Copy helper procedure to page 80107
3. ✅ Add telemetry to GetTransactions (start with most important)
4. ✅ Deploy, test, and verify procedure tracking works
5. ✅ Add telemetry to remaining procedures

---

**Status**: Ready to implement!
**Dashboard JSON Update**: Available in `HAG-WEB-SERVICE-DASHBOARD-UPDATE.json`
**Location**: `C:\AL\BCTelemetry\Azure Data Explorer\`
