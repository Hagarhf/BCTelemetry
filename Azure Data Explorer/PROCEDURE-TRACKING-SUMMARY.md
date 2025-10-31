# HAG Web Service - Procedure Tracking Summary

**Issue**: Need to track individual procedures (GetTransactions, GetInvoice, etc.) within HAG Web Service (Page 80107)
**Solution**: Add custom telemetry to each procedure

---

## Question 1: Why "HAG VAT Posting Setup" Shows Up?

Your original query used:
```kql
| where alObjectId == "80107" or alObjectName contains "HAG Web Service"
```

The `alObjectName contains "HAG Web Service"` part is too broad and might match other objects with "HAG" in the name.

**Fix**: Use **only the object ID** for precise filtering:
```kql
| where alObjectId == "80107"
```

---

## Question 2: Can I Track Individual Procedures?

**Short Answer**: Not by default, but YES with custom telemetry!

### Current State
BC telemetry logs:
- ✅ Page was accessed (80107)
- ✅ How long it took
- ✅ Who called it
- ❌ Which procedure was called (GetTransactions, GetInvoice, etc.)

### Solution
Add custom telemetry to each procedure in your AL code.

---

## Quick Start - 3 Steps

### Step 1: Add Helper Procedure (Copy Once)
Add this to your page 80107:

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
        '0000HAG',  // Use your own telemetry ID
        StrSubstNo('HAG Web Service: %1 - %2 (%3ms)', ProcedureName, Status, ExecutionTimeMs),
        Verbosity::Normal,
        DataClassification::SystemMetadata,
        TelemetryScope::All,
        TelemetryDimensions
    );
end;
```

### Step 2: Add Telemetry to GetTransactions
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

### Step 3: Query the Results
After deploying the code, run this query:

```kql
traces
| where timestamp > ago(24h)
| extend
    pageId = tostring(customDimensions.PageID),
    procedure = tostring(customDimensions.Procedure),
    status = tostring(customDimensions.Status)
| where pageId == "80107"
| summarize
    CallCount = count(),
    SuccessCount = countif(status == "Success"),
    ErrorCount = countif(status startswith "Error"),
    LastCall = max(timestamp)
    by procedure
| project procedure, CallCount, SuccessCount, ErrorCount, LastCall
| order by CallCount desc
```

**Expected Result**:
```
procedure          CallCount  SuccessCount  ErrorCount  LastCall
GetTransactions    150        148           2           2025-10-31 10:45:00
GetInvoice         89         89            0           2025-10-31 10:44:30
GetCustomer        45         44            1           2025-10-31 10:43:00
```

---

## What You Can Track

### Per Procedure:
- **Call count** - How many times called
- **Success/Error rate** - Reliability
- **Performance** - Average, P95, Max execution time
- **Parameters** - Which customers, dates, etc.
- **Error messages** - What went wrong

### Dashboard Metrics:
```
Procedure: GetTransactions
- Calls: 150/day (6.25/hour)
- Success Rate: 98.7%
- Avg Time: 245ms
- P95 Time: 890ms
- Status: ✅ Fast & Healthy
```

---

## Files Created

### 1. **HAGWebService-ProcedureTracking.kql**
**8 Diagnostic Queries**:
1. Find exact HAG Web Service by object ID
2. Find procedure/function names (Method 1)
3. Find procedures in message text
4. Extract procedure names from custom dimensions
5. Raw data inspection
6. Search for specific procedure names
7. Session-based procedure tracking
8. Dashboard query (after adding telemetry)

**Plus**: Quick diagnostic query at the end

### 2. **HAGWebService-AddProcedureTelemetry.al**
**Complete AL Code Examples**:
- Helper procedure (LogProcedureCall)
- 6 example procedures with telemetry:
  - GetTransactions
  - GetInvoice
  - GetCustomer
  - PostTransaction
  - GetItemList
  - UpdateCustomerData
- Error handling patterns
- Try-catch integration
- 4 ready-to-use KQL queries for monitoring

---

## Before You Add Custom Telemetry

Run these diagnostic queries first to see if procedure names are already being logged:

### Query 1: Check for Procedure Names in Current Telemetry
```kql
traces
| where timestamp > ago(7d)
| extend alObjectId = tostring(customDimensions.alObjectId)
| where alObjectId == "80107"
| take 5
| project timestamp, message, customDimensions
```

Look for:
- `alObjectMethod` in customDimensions
- `alMethodName` in customDimensions
- Procedure names in message text

**If you find them**: Use Query 2 from HAGWebService-ProcedureTracking.kql
**If you don't**: Add custom telemetry using the AL code examples

---

## Next Steps

### Immediate (Before Adding Code)
1. ✅ Run **Query 1** from HAGWebService-ProcedureTracking.kql (exact ID filter)
2. ✅ Run **QUICK DIAGNOSTIC** at bottom of same file
3. ✅ Look at raw `customDimensions` to see what's available

### If Procedures NOT Currently Logged
1. ✅ Copy helper procedure to your page 80107
2. ✅ Add telemetry to GetTransactions (most important one first)
3. ✅ Deploy and test
4. ✅ Run Query 1 to verify it appears
5. ✅ Add telemetry to remaining procedures

### After Adding Telemetry
1. ✅ Create dashboard tile with procedure-level metrics
2. ✅ Set up alerts for high error rates
3. ✅ Track performance trends
4. ✅ Analyze which procedures are most used

---

## Recommended Priority

Add telemetry in this order (most important first):

1. **GetTransactions** - Probably your most-called procedure
2. **GetInvoice** - Critical for invoice data
3. **Any POST/UPDATE procedures** - Track data changes
4. **GetCustomer** - Customer data access
5. **Remaining GET procedures** - Nice to have

---

## Performance Impact

Adding telemetry has **minimal impact**:
- ~1-5ms overhead per procedure call
- No impact on business logic
- Logs to Application Insights asynchronously
- No user-visible slowdown

---

**Status**: Ready to implement
**Files**: 3 files created (KQL queries + AL code + this summary)
**Location**: `C:\AL\BCTelemetry\Azure Data Explorer\`
