# Adding HAG Web Service Tile to Dashboard

**Great News**: Your diagnostic queries found HAG Web Service (Page 80107) telemetry!
**Next Step**: Add a monitoring tile to your Hagar Extensions page

---

## Option 1: Quick Manual Addition (Recommended)

### Step 1: Run the Summary Query

In Azure Data Explorer, run this query to see your API stats:

```kql
traces
| where timestamp > ago(24h)
| extend
    alObjectId = tostring(customDimensions.alObjectId),
    alObjectName = tostring(customDimensions.alObjectName),
    extensionName = tostring(customDimensions.extensionName)
| where alObjectId == "80107" or alObjectName contains "HAG Web Service"
| summarize
    TotalCalls = count(),
    UniqueUsers = dcount(user_Id),
    UniqueSessions = dcount(tostring(customDimensions.sessionId)),
    FirstCall = min(timestamp),
    LastCall = max(timestamp),
    ErrorCount = countif(severityLevel >= 3)
    by extensionName, alObjectName
| extend
    CallsPerHour = round(toreal(TotalCalls) / 24.0, 1),
    MinutesSinceLastCall = datetime_diff('minute', now(), LastCall),
    HealthStatus = case(
        ErrorCount > 10, "🔴 High Errors",
        ErrorCount > 0, "⚠️ Some Errors",
        MinutesSinceLastCall > 120, "⚠️ Inactive >2h",
        MinutesSinceLastCall > 60, "📊 Inactive >1h",
        "✅ Healthy"
    )
| project
    extensionName,
    alObjectName,
    TotalCalls,
    CallsPerHour,
    UniqueUsers,
    UniqueSessions,
    ErrorCount,
    MinutesSinceLastCall,
    LastCall,
    HealthStatus
```

**Expected Results**:
- Extension Name: Hagar Webshop
- Object Name: HAG Web Service (or page 80107)
- Total Calls: X (from last 24h)
- Calls Per Hour: X
- Unique Users: X
- Health Status: ✅ Healthy (hopefully!)

### Step 2: Add Tile to Dashboard (Manual Method)

1. In Azure Data Explorer, go to your BCTelemetry Dashboard
2. Click **Edit** on the "Hagar Extensions" page
3. Click **Add tile**
4. Configure:
   - **Title**: "HAG Web Service API (Page 80107)"
   - **Visualization**: Table
   - **Query**: Paste QUERY 10 from `HAGWebService-Analysis.kql`
5. Position it below the existing tiles
6. **Save**

---

## Option 2: Add to Dashboard JSON (For Advanced Users)

If you want to update the dashboard JSON directly, add this tile and query:

### New Tile Definition

Add to the `tiles` array (before the closing `]` of tiles):

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

### New Query Definition

Add to the `queries` array (before the closing `]` of queries):

```json
{
    "dataSource": {
        "kind": "inline",
        "dataSourceId": "05ae5610-5603-45ac-9458-616539c1c150"
    },
    "text": "let TimeRange = 24h;\ntraces\n| where timestamp > ago(TimeRange)\n| extend\n    alObjectId = tostring(customDimensions.alObjectId),\n    alObjectName = tostring(customDimensions.alObjectName)\n| where alObjectId == \"80107\" or alObjectName contains \"HAG Web Service\"\n| extend executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000\n| summarize\n    CallCount = count(),\n    AvgMs = round(avg(executionTimeMs), 2),\n    P95Ms = round(percentile(executionTimeMs, 95), 2),\n    MaxMs = round(max(executionTimeMs), 2),\n    ErrorCount = countif(severityLevel >= 3),\n    LastCall = max(timestamp)\n    by bin(timestamp, 1h)\n| extend\n    MinutesSinceLastCall = datetime_diff('minute', now(), LastCall),\n    PerformanceStatus = case(\n        AvgMs > 1000, \"🔴 Slow (>1s)\",\n        AvgMs > 500, \"⚠️ Moderate (500ms-1s)\",\n        \"✅ Fast (<500ms)\"\n    ),\n    HealthStatus = case(\n        ErrorCount > 0, \"🔴 Has Errors\",\n        MinutesSinceLastCall > 60, \"⚠️ Inactive >1h\",\n        \"✅ Healthy\"\n    )\n| project\n    timestamp,\n    CallCount,\n    AvgMs,\n    P95Ms,\n    MaxMs,\n    ErrorCount,\n    PerformanceStatus,\n    HealthStatus,\n    LastCall\n| order by timestamp desc",
    "id": "d9e0f1a2-b3c4-4678-9012-345678bcdef8",
    "usedVariables": []
}
```

---

## What You'll See in the Tile

### Columns:
1. **timestamp** - Hour of the day
2. **CallCount** - Number of API calls that hour
3. **AvgMs** - Average response time
4. **P95Ms** - 95th percentile response time
5. **MaxMs** - Slowest call that hour
6. **ErrorCount** - Number of errors
7. **PerformanceStatus** - ✅ Fast / ⚠️ Moderate / 🔴 Slow
8. **HealthStatus** - ✅ Healthy / ⚠️ Inactive / 🔴 Has Errors
9. **LastCall** - Timestamp of last call

### Status Indicators:
- **✅ Fast** - Average response < 500ms
- **⚠️ Moderate** - Average response 500ms-1s
- **🔴 Slow** - Average response > 1s
- **✅ Healthy** - No errors, active
- **⚠️ Inactive >1h** - No calls in last hour
- **🔴 Has Errors** - Errors detected

---

## Hagar Extensions Page - Updated Layout

After adding the HAG Web Service tile, your page will have **5 tiles**:

```
┌─────────────────────────────────────────────────┐
│  Tile 1: Hagar Extensions Activity Overview    │
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
│  Tile 5: HAG Web Service API (Page 80107)       │  ← NEW!
│  (Full width, bottom)                           │
└─────────────────────────────────────────────────┘
```

---

## Monitoring Recommendations

### 🔴 Critical Alerts
- **Error count > 0** in any hour
- **Average response time > 1 second**
- **Inactive > 2 hours** during business hours

### ⚠️ Warnings
- **Average response time > 500ms**
- **Call count drops by > 50%** compared to baseline
- **Max response time > 5 seconds**

### 📊 Information
- **Call patterns** - When is API busiest?
- **Performance trends** - Is it getting slower?
- **Usage patterns** - Which hours have most traffic?

---

## Additional Analysis Queries

Once the tile is added, use these queries for deeper analysis:

### 1. Most Active API Procedures
```kql
traces
| where timestamp > ago(7d)
| extend alObjectId = tostring(customDimensions.alObjectId)
| where alObjectId == "80107"
| extend operation = tostring(customDimensions.alObjectMethod)
| summarize Count = count() by operation
| order by Count desc
```

### 2. API Calls by User
```kql
traces
| where timestamp > ago(7d)
| extend alObjectId = tostring(customDimensions.alObjectId)
| where alObjectId == "80107"
| summarize
    CallCount = count(),
    LastCall = max(timestamp)
    by user_Id
| order by CallCount desc
```

### 3. API Performance by Hour of Day
```kql
traces
| where timestamp > ago(7d)
| extend alObjectId = tostring(customDimensions.alObjectId)
| where alObjectId == "80107"
| extend
    hour = datetime_part("hour", timestamp),
    executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000
| summarize
    AvgMs = round(avg(executionTimeMs), 2),
    CallCount = count()
    by hour
| order by hour asc
```

---

## Troubleshooting

### If Tile Shows No Data

**Check 1**: Verify object ID is correct
```kql
traces
| where timestamp > ago(24h)
| extend
    alObjectId = tostring(customDimensions.alObjectId),
    alObjectName = tostring(customDimensions.alObjectName)
| where alObjectName contains "Web Service" or alObjectId == "80107"
| summarize by alObjectId, alObjectName
```

**Check 2**: Verify extension name
```kql
traces
| where timestamp > ago(24h)
| extend
    extensionName = tostring(customDimensions.extensionName),
    alObjectId = tostring(customDimensions.alObjectId)
| where alObjectId == "80107"
| summarize by extensionName
```

**Check 3**: Check time range
```kql
traces
| where timestamp > ago(24h)
| extend alObjectId = tostring(customDimensions.alObjectId)
| where alObjectId == "80107"
| summarize
    FirstCall = min(timestamp),
    LastCall = max(timestamp),
    TotalCalls = count()
```

---

## Files Reference

- **HAGWebService-Analysis.kql** - 10 detailed analysis queries
- **DiagnosticQuery-HAGWebService.kql** - 8 diagnostic queries
- **API-TELEMETRY-GUIDE.md** - Complete implementation guide

---

**Next Steps**:
1. ✅ Run the Summary Query to see your current API stats
2. ✅ Add the tile using Option 1 (manual) or Option 2 (JSON)
3. ✅ Verify the tile shows data
4. ✅ Set up alerts for critical issues
5. ✅ Use analysis queries for deeper insights

**Status**: Ready to implement!
