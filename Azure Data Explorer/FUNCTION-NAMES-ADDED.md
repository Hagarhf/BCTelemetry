# HAG Web Service Query Updated - Function Names Added! ✅

## Summary

Successfully updated the HAG Web Service dashboard query to **extract and display function names** from the telemetry data!

---

## What Changed

### Before:
The query showed **aggregated data per hour** without function names:
```
timestamp             CallCount  AvgMs  ErrorCount  Status
2025-10-31 10:00:00   68         198    0           ✅ Fast
2025-10-31 09:00:00   73         245    1           🔴 Has Errors
```
- Could see total API activity
- **Could NOT see which functions** were called

### After:
The query now shows **data per function per hour**:
```
timestamp             FunctionName       CallCount  AvgMs  ErrorCount  Status
2025-10-31 10:00:00   getInvoices        45         234    0           ✅ Fast
2025-10-31 10:00:00   getTransactions    23         156    0           ✅ Fast
2025-10-31 09:00:00   getInvoices        52         289    1           🔴 Has Errors
2025-10-31 09:00:00   getTransactions    21         189    0           ✅ Fast
```
- Can see each function's activity separately
- Can identify which function has performance issues or errors
- Can track usage patterns per function

---

## Technical Changes Made

### 1. Extract Endpoint from Custom Dimensions
```kql
| extend endpoint = tostring(customDimensions.endpoint)
```

### 2. Extract Function Name Using Regex
```kql
| extend FunctionName = extract(@"Microsoft\.NAV\.(\w+)", 1, endpoint)
```
Extracts function name from pattern like:
```
"stkweb/api/hagar/hagws/v2.0/companies()/hagWSFunction()/Microsoft.NAV.getInvoices"
                                                                        ^^^^^^^^^^^
```

### 3. Filter Out Empty Function Names
```kql
| where isnotempty(FunctionName)
```

### 4. Group By Function Name
```kql
by bin(timestamp, 1h), FunctionName
```
Now aggregates by both hour AND function name

### 5. Add Function Name to Output
```kql
| project
    timestamp,
    FunctionName,    ← NEW COLUMN
    CallCount,
    ...
```

---

## Query ID
- **Query ID**: `d9e0f1a2-b3c4-4678-9012-345678bcdef8`
- **Tile ID**: `e9f0a1b2-c3d4-4567-8901-234567bcdef7`
- **Page**: Hagar Extensions (`f4a5b6c7-d8e9-4012-3456-789012abcdef`)

---

## What You'll See

### Dashboard Tile Columns:
1. **timestamp** - Hour of the day
2. **FunctionName** - The API function called (getInvoices, getTransactions, etc.) ✨ NEW!
3. **CallCount** - Number of calls for this function in this hour
4. **AvgMs** - Average response time
5. **P95Ms** - 95th percentile response time
6. **MaxMs** - Slowest call
7. **ErrorCount** - Number of errors
8. **PerformanceStatus** - ✅ Fast / ⚠️ Moderate / 🔴 Slow
9. **HealthStatus** - ✅ Healthy / ⚠️ Inactive / 🔴 Has Errors
10. **LastCall** - Timestamp of last call

### Function Names You'll See:
Based on your telemetry, you'll see functions like:
- `getInvoices`
- `getTransactions`
- `getCustomer`
- Any other functions in your HAG Web Service API

---

## Benefits

### 1. Identify Problem Functions
Quickly see which specific function has errors:
```
FunctionName       ErrorCount  Status
getInvoices        5           🔴 Has Errors
getTransactions    0           ✅ Healthy
```

### 2. Find Slow Functions
Identify performance bottlenecks:
```
FunctionName       AvgMs  PerformanceStatus
getInvoices        1,250  🔴 Slow (>1s)
getTransactions    350    ✅ Fast (<500ms)
```

### 3. Track Usage Patterns
See which functions are most used:
```
FunctionName       CallCount
getInvoices        450
getTransactions    230
getCustomer        89
```

### 4. Monitor Function Health Over Time
Track trends for each function:
- Is getInvoices getting slower?
- Has getTransactions started failing?
- When is getCustomer most active?

---

## Next Steps

### 1. Upload to Azure Data Explorer
1. Save/commit the updated `BCTelemetryDashboard.json`
2. Open Azure Data Explorer
3. Navigate to your dashboard
4. Click **Edit** → **Upload** or **Import**
5. Select `BCTelemetryDashboard.json`
6. Confirm upload

### 2. Verify the Update
1. Navigate to **"Hagar Extensions"** page
2. Find **"HAG Web Service API (Page 80107)"** tile
3. Check that the **FunctionName** column appears
4. Verify function names are showing (getInvoices, getTransactions, etc.)

### 3. Set Up Monitoring
Now that you can see per-function metrics, consider:
- **Alerts** for specific functions with high error rates
- **Performance baselines** per function
- **Usage trends** to understand API patterns

---

## No Custom Telemetry Needed!

**Great news**: We discovered the function names are already in the standard BC telemetry in the `endpoint` field, so you **don't need to add any AL code**!

The custom telemetry approach in these files is **not required**:
- ~~HAGWebService-AddProcedureTelemetry.al~~ (not needed)
- ~~PROCEDURE-TRACKING-SUMMARY.md~~ (not needed)

Keep these files for reference, but the standard telemetry already provides what you need.

---

## Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `BCTelemetryDashboard.json` | **Updated** - Ready to upload | ✅ Updated |
| `HAG-Web-Service-Final-Query.kql` | Reference query with function extraction | ✅ Created |
| `TEST-Endpoint-Extraction.kql` | Test query to verify function names | ✅ Created |
| `FUNCTION-NAMES-GUIDE.md` | Complete guide and decision tree | ✅ Created |
| `THOROUGH-HAG-DIAGNOSTIC.kql` | Diagnostic queries (used to find the data) | ✅ Created |

---

## Example: What You Might See

```
timestamp             FunctionName       CallCount  AvgMs   P95Ms   ErrorCount  Status
2025-10-31 11:00:00   getInvoices        45         234     450     0           ✅ Fast
2025-10-31 11:00:00   getTransactions    23         156     280     0           ✅ Fast
2025-10-31 11:00:00   getCustomer        12         98      150     0           ✅ Fast
2025-10-31 10:00:00   getInvoices        52         289     520     2           🔴 Has Errors
2025-10-31 10:00:00   getTransactions    28         189     310     0           ✅ Fast
2025-10-31 10:00:00   getCustomer        9          105     175     0           ✅ Fast
```

From this, you can see:
- ✅ `getInvoices` had 2 errors at 10:00 but recovered by 11:00
- ✅ `getTransactions` is consistently fast and reliable
- ✅ `getCustomer` has lower usage but good performance
- ✅ All functions are currently healthy (11:00 hour)

---

**Status**: ✅ Complete - Dashboard updated with function name extraction
**Date**: 2025-10-31
**Location**: `C:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.json`

**Ready to upload to Azure Data Explorer!** 🎉
