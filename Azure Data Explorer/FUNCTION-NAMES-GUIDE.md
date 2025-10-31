# How to See Function Names in HAG Web Service Query

## Quick Answer

**Standard BC telemetry does NOT log function/procedure names by default for API pages.**

However, there are two ways to get function names:

1. ✅ **Check if they're already logged** (some BC versions/configurations do this)
2. ✅ **Add custom telemetry** to your AL code (guaranteed to work)

---

## Step 1: Check If Function Names Are Already Available

Run the diagnostic queries in `Check-HAG-Function-Names.kql` to see what's in your telemetry.

### Run This First:

```kql
traces
| where timestamp > ago(24h)
| extend
    alObjectId = tostring(customDimensions.alObjectId),
    alObjectMethod = tostring(customDimensions.alObjectMethod),
    alMethodName = tostring(customDimensions.alMethodName)
| where alObjectId == "80107"
| summarize Count = count() by alObjectMethod, alMethodName
| where isnotempty(alObjectMethod) or isnotempty(alMethodName);
```

### Results:

**If you see data** (function names in `alObjectMethod` or `alMethodName`):
- ✅ Function names ARE logged!
- Proceed to **Solution A** below

**If you see NO data** (empty results):
- ❌ Function names NOT logged
- Proceed to **Solution B** below

---

## Solution A: Function Names Are Already Logged

If the diagnostic query shows function names, update the dashboard query to include them.

### Updated Dashboard Query

Replace the current query with this version (includes `FunctionName` column):

```kql
let TimeRange = 24h;
traces
| where timestamp > ago(TimeRange)
| extend
    alObjectId = tostring(customDimensions.alObjectId),
    alObjectMethod = tostring(customDimensions.alObjectMethod),
    alMethodName = tostring(customDimensions.alMethodName)
| where alObjectId == "80107"
| extend FunctionName = coalesce(alObjectMethod, alMethodName, "Unknown")
| extend executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000
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
| order by timestamp desc, CallCount desc;
```

### What Changes:
1. Added `FunctionName` extraction from `alObjectMethod` or `alMethodName`
2. Added `FunctionName` to `summarize` grouping (`by bin(timestamp, 1h), FunctionName`)
3. Added `FunctionName` column to output

### Result:
Your dashboard tile will now show:
```
timestamp             FunctionName       CallCount  AvgMs  ...
2025-10-31 10:00:00   GetTransactions    45         234    ...
2025-10-31 10:00:00   GetInvoice         23         156    ...
2025-10-31 09:00:00   GetTransactions    52         289    ...
```

---

## Solution B: Function Names Are NOT Logged (Add Custom Telemetry)

If function names are not in the telemetry, you need to add custom telemetry to your AL code.

### Quick Implementation

**1. Add Helper Procedure to Page 80107:**

```al
local procedure LogProcedureCall(ProcedureName: Text; Status: Text; ExecutionTimeMs: Integer; AdditionalInfo: Dictionary of [Text, Text])
var
    TelemetryDimensions: Dictionary of [Text, Text];
    Key: Text;
begin
    TelemetryDimensions.Add('PageID', '80107');
    TelemetryDimensions.Add('Procedure', ProcedureName);
    TelemetryDimensions.Add('Status', Status);
    TelemetryDimensions.Add('ExecutionTimeMs', Format(ExecutionTimeMs));

    foreach Key in AdditionalInfo.Keys do
        TelemetryDimensions.Add(Key, AdditionalInfo.Get(Key));

    Session.LogMessage(
        '0000HAG',
        StrSubstNo('HAG Web Service: %1 - %2 (%3ms)', ProcedureName, Status, ExecutionTimeMs),
        Verbosity::Normal,
        DataClassification::SystemMetadata,
        TelemetryScope::All,
        TelemetryDimensions
    );
end;
```

**2. Add Telemetry to Each Procedure:**

```al
procedure GetTransactions(CustomerNo: Code[20]; FromDate: Date; ToDate: Date): Text
var
    StartTime: DateTime;
    ExecutionTime: Duration;
    AdditionalInfo: Dictionary of [Text, Text];
    ResultText: Text;
begin
    StartTime := CurrentDateTime;
    AdditionalInfo.Add('CustomerNo', CustomerNo);
    AdditionalInfo.Add('FromDate', Format(FromDate));
    AdditionalInfo.Add('ToDate', Format(ToDate));

    // Your existing logic
    ResultText := GetTransactionsInternal(CustomerNo, FromDate, ToDate);

    // Log success
    ExecutionTime := CurrentDateTime - StartTime;
    AdditionalInfo.Add('RecordsReturned', Format(CountRecords(ResultText)));
    LogProcedureCall('GetTransactions', 'Success', ExecutionTime, AdditionalInfo);

    exit(ResultText);
end;
```

**3. Dashboard Query After Adding Telemetry:**

```kql
let TimeRange = 24h;
traces
| where timestamp > ago(TimeRange)
| extend
    pageId = tostring(customDimensions.PageID),
    procedure = tostring(customDimensions.Procedure),
    status = tostring(customDimensions.Status),
    executionTimeMs = toint(customDimensions.ExecutionTimeMs)
| where pageId == "80107"
| summarize
    CallCount = count(),
    SuccessCount = countif(status == "Success"),
    ErrorCount = countif(status startswith "Error"),
    AvgMs = round(avg(executionTimeMs), 2),
    P95Ms = round(percentile(executionTimeMs, 95), 2),
    MaxMs = max(executionTimeMs),
    LastCall = max(timestamp)
    by bin(timestamp, 1h), procedure
| extend
    SuccessRate = round(toreal(SuccessCount) * 100.0 / toreal(CallCount), 1),
    PerformanceStatus = case(
        AvgMs > 1000, "🔴 Slow (>1s)",
        AvgMs > 500, "⚠️ Moderate (500ms-1s)",
        "✅ Fast (<500ms)"
    ),
    HealthStatus = case(
        ErrorCount > 0, "🔴 Has Errors",
        "✅ Healthy"
    )
| project
    timestamp,
    procedure,
    CallCount,
    SuccessRate,
    AvgMs,
    P95Ms,
    MaxMs,
    ErrorCount,
    PerformanceStatus,
    HealthStatus,
    LastCall
| order by timestamp desc, CallCount desc;
```

### Result After Implementation:
```
timestamp             procedure          CallCount  SuccessRate  AvgMs  ...
2025-10-31 10:00:00   GetTransactions    45         100.0        234    ...
2025-10-31 10:00:00   GetInvoice         23         100.0        156    ...
2025-10-31 09:00:00   GetTransactions    52         98.1         289    ...
```

---

## Comparison: With vs Without Function Names

### Current Query (No Function Names):
```
timestamp             CallCount  AvgMs  ErrorCount  Status
2025-10-31 10:00:00   68         198    0           ✅ Fast
2025-10-31 09:00:00   73         245    1           🔴 Has Errors
```
- Shows **overall** page activity per hour
- Cannot tell which function was called

### With Function Names:
```
timestamp             FunctionName       CallCount  AvgMs  ErrorCount  Status
2025-10-31 10:00:00   GetTransactions    45         234    0           ✅ Fast
2025-10-31 10:00:00   GetInvoice         23         156    0           ✅ Fast
2025-10-31 09:00:00   GetTransactions    52         289    1           🔴 Has Errors
2025-10-31 09:00:00   GetInvoice         21         189    0           ✅ Fast
```
- Shows activity **per function** per hour
- Can identify which function has errors or performance issues

---

## Decision Tree

```
Start: Can I see function names in HAG Web Service query?
│
├─ YES → Run Check-HAG-Function-Names.kql diagnostic queries
│   │
│   ├─ Results show function names?
│   │   ├─ YES → Use Solution A (update dashboard query)
│   │   └─ NO → Use Solution B (add custom telemetry)
│   │
│   └─ How important is function-level detail?
│       ├─ Critical → Use Solution B (custom telemetry)
│       └─ Nice to have → Try Solution A first
│
└─ NO → I want to see which procedures are called
    │
    └─ Use Solution B (add custom telemetry)
        - Start with most important procedures
        - Priority: GetTransactions, GetInvoice, PostTransaction
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `Check-HAG-Function-Names.kql` | Diagnostic queries to check current telemetry |
| `HAG-Web-Service-Query-With-Functions.kql` | Updated query for Solution A |
| `HAGWebService-AddProcedureTelemetry.al` | Complete AL code for Solution B |
| `PROCEDURE-TRACKING-SUMMARY.md` | Full implementation guide for Solution B |
| `HAGWebService-ProcedureTracking.kql` | Additional diagnostic queries |

---

## Next Steps

### Immediate:
1. ✅ Run `Check-HAG-Function-Names.kql` queries in Azure Data Explorer
2. ✅ Check the results to see if function names are available
3. ✅ Choose Solution A or B based on results

### If Solution A (Already Logged):
1. ✅ Update dashboard query with function name extraction
2. ✅ Upload updated dashboard to ADE
3. ✅ Verify function names appear in the tile

### If Solution B (Custom Telemetry):
1. ✅ Add `LogProcedureCall` helper to page 80107
2. ✅ Add telemetry to GetTransactions (start with most important)
3. ✅ Deploy and test
4. ✅ Verify telemetry appears with Query 1 from Check file
5. ✅ Add telemetry to remaining procedures
6. ✅ Update dashboard query to use custom dimensions

---

**Status**: Ready to check and implement
**Location**: `C:\AL\BCTelemetry\Azure Data Explorer\`
