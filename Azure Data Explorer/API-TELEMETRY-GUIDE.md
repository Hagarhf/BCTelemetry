# API Telemetry Guide - HAG Web Service (Page 80107)

**Issue**: API endpoints in HAG Web Service (Page 80107) are not visible in dashboard or queries
**Date**: 2025-10-31

---

## Why API Pages Don't Show in Telemetry

### Problem 1: API Pages Don't Generate Standard Events

**API pages (PageType = API)** in Business Central do not generate the same telemetry events as normal pages:

❌ **Not Logged**:
- Page open events (AL0000E3L)
- Page view events
- User interaction events
- Button click events

✅ **May Be Logged** (depending on implementation):
- Web service calls (RT0008) - **Only if called via SOAP/OData**
- Custom telemetry (if you add it manually)
- Errors/exceptions (if they occur)

### Problem 2: Direct HTTP Calls vs Web Service Calls

If your API is called via:
- **RESTful HTTP** (GET/POST to `/api/...`) → May not log as RT0008
- **Direct page invocation** → No page open telemetry
- **Background job/automation** → May not generate user telemetry

If called via:
- **SOAP web service** → Logs as RT0008
- **OData** → Logs as RT0008
- **Published as web service** → Logs as RT0008

---

## Diagnostic Steps

### Step 1: Run the Diagnostic Queries

I've created `DiagnosticQuery-HAGWebService.kql` with 8 queries to find your API telemetry.

Run them in order:
1. **Query 1**: Direct search for page 80107
2. **Query 2**: Search for "HAG Web" objects
3. **Query 3**: Web service calls (RT0008)
4. **Query 4**: All API/Service pages from Hagar
5. **Query 5**: Unbound API pages
6. **Query 6**: All 80xxx objects from Hagar
7. **Query 7**: All Hagar Webshop events
8. **Query 8**: Custom telemetry tags

### Step 2: Check What IS Being Logged

Run this simple query to see what's coming from Hagar Webshop:

```kql
traces
| where timestamp > ago(24h)
| extend extensionName = tostring(customDimensions.extensionName)
| where extensionName == "Hagar Webshop"
| summarize Count = count() by
    eventId = tostring(customDimensions.eventId),
    alObjectType = tostring(customDimensions.alObjectType),
    alObjectName = tostring(customDimensions.alObjectName)
| order by Count desc
```

**Expected Result**: Should show 64 events from your 24h analysis
- HAG Delete Export Tools: 27 events
- HAG Web Inventory Functions: 1 event
- HAG Customer API: 1 event

### Step 3: Check if Page is Published as Web Service

In Business Central:
1. Search for "Web Services"
2. Check if "HAG Web Service" or page 80107 is published
3. Note the **Service Name** (this is what appears in telemetry)

---

## Solution Options

### Option 1: Add Custom Telemetry (Recommended)

Add custom telemetry to your API page procedures:

```al
page 80107 "HAG Web Service"
{
    PageType = API;

    procedure GetCustomerData(CustomerNo: Code[20])
    var
        TelemetryCustomDimensions: Dictionary of [Text, Text];
    begin
        // Add custom telemetry at start of procedure
        TelemetryCustomDimensions.Add('CustomerNo', CustomerNo);
        TelemetryCustomDimensions.Add('Endpoint', 'GetCustomerData');
        TelemetryCustomDimensions.Add('APIPage', '80107');

        Session.LogMessage(
            '0000ABC',  // Use your own tag
            'HAG Web Service: GetCustomerData called',
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::All,
            TelemetryCustomDimensions
        );

        // Your API logic here

        // Log success/failure at end
        TelemetryCustomDimensions.Add('Status', 'Success');
        Session.LogMessage(
            '0000ABD',
            'HAG Web Service: GetCustomerData completed',
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::All,
            TelemetryCustomDimensions
        );
    end;
}
```

### Option 2: Use Telemetry Helper Codeunit

Create a reusable telemetry helper:

```al
codeunit 80100 "HAG Telemetry Helper"
{
    procedure LogAPICall(APIName: Text; ProcedureName: Text; Parameters: Dictionary of [Text, Text])
    var
        TelemetryCustomDimensions: Dictionary of [Text, Text];
    begin
        TelemetryCustomDimensions.Add('APIName', APIName);
        TelemetryCustomDimensions.Add('Procedure', ProcedureName);
        TelemetryCustomDimensions.Add('Timestamp', Format(CurrentDateTime, 0, 9));

        // Add all parameters
        foreach Key in Parameters.Keys do
            TelemetryCustomDimensions.Add(Key, Parameters.Get(Key));

        Session.LogMessage(
            '0000HAG',
            StrSubstNo('API Call: %1.%2', APIName, ProcedureName),
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::All,
            TelemetryCustomDimensions
        );
    end;
}
```

Then use it in your API:

```al
procedure GetCustomerData(CustomerNo: Code[20])
var
    TelemetryHelper: Codeunit "HAG Telemetry Helper";
    Params: Dictionary of [Text, Text];
begin
    Params.Add('CustomerNo', CustomerNo);
    TelemetryHelper.LogAPICall('HAG Web Service', 'GetCustomerData', Params);

    // Your API logic
end;
```

### Option 3: Add Performance Tracking

Track API performance with start/end telemetry:

```al
procedure GetCustomerData(CustomerNo: Code[20])
var
    StartTime: DateTime;
    EndTime: DateTime;
    ExecutionTime: Duration;
    TelemetryCustomDimensions: Dictionary of [Text, Text];
begin
    StartTime := CurrentDateTime;

    // Your API logic here

    EndTime := CurrentDateTime;
    ExecutionTime := EndTime - StartTime;

    // Log performance
    TelemetryCustomDimensions.Add('Endpoint', 'GetCustomerData');
    TelemetryCustomDimensions.Add('CustomerNo', CustomerNo);
    TelemetryCustomDimensions.Add('ExecutionTimeMs', Format(ExecutionTime));

    Session.LogMessage(
        '0000HAG',
        StrSubstNo('API call completed in %1ms', ExecutionTime),
        Verbosity::Normal,
        DataClassification::SystemMetadata,
        TelemetryScope::All,
        TelemetryCustomDimensions
    );
end;
```

---

## Dashboard Query to Monitor Custom Telemetry

Once you've added custom telemetry, add this query to your Hagar Extensions page:

```kql
// HAG Web Service API Calls
let TimeRange = 24h;
traces
| where timestamp > ago(TimeRange)
| extend
    extensionName = tostring(customDimensions.extensionName),
    apiName = tostring(customDimensions.APIName),
    procedure = tostring(customDimensions.Procedure),
    endpoint = tostring(customDimensions.Endpoint),
    executionTimeMs = toint(customDimensions.ExecutionTimeMs)
| where extensionName == "Hagar Webshop"
| where isnotempty(apiName) or isnotempty(endpoint)
| summarize
    CallCount = count(),
    AvgExecutionMs = round(avg(executionTimeMs), 2),
    P95ExecutionMs = round(percentile(executionTimeMs, 95), 2),
    MaxExecutionMs = max(executionTimeMs),
    LastCall = max(timestamp)
    by apiName, procedure, endpoint
| extend Status = case(
    AvgExecutionMs > 1000, "🔴 Slow (>1s)",
    AvgExecutionMs > 500, "⚠️ Moderate (500ms-1s)",
    "✅ Fast (<500ms)"
)
| project apiName, procedure, endpoint, CallCount, AvgExecutionMs, P95ExecutionMs, MaxExecutionMs, Status, LastCall
| order by CallCount desc
```

---

## Alternative: Check if Procedures are Called via Codeunits

Your API page might trigger codeunits that ARE being logged. Check if you see these:

```kql
traces
| where timestamp > ago(7d)
| extend
    alObjectType = tostring(customDimensions.alObjectType),
    alObjectName = tostring(customDimensions.alObjectName),
    extensionName = tostring(customDimensions.extensionName)
| where extensionName == "Hagar Webshop"
| where alObjectType == "CodeUnit"
| where alObjectName contains "Web" or alObjectName contains "API" or alObjectName contains "Service"
| summarize Count = count() by alObjectName
| order by Count desc
```

---

## Common Patterns in Your System

Based on your 24h analysis, here's what IS being logged from Hagar Webshop:

| Object | Events | Type |
|--------|--------|------|
| HAG Delete Export Tools | 27 | Slow queries |
| HAG Web Inventory Functions | 1 | Operation |
| HAG Customer API | 1 | Operation |

Notice:
- "HAG Web Inventory Functions" - 1 event
- "HAG Customer API" - 1 event

These might be codeunits called BY your web service page!

---

## Quick Test

To verify if your API is working but just not logging:

1. **Call your API** from an external tool (Postman, curl, etc.)
2. **Immediately run** this query:

```kql
traces
| where timestamp > ago(5m)
| extend extensionName = tostring(customDimensions.extensionName)
| where extensionName == "Hagar Webshop"
| project timestamp, message, customDimensions
| order by timestamp desc
| take 50
```

3. **Look for any activity** around the time you made the call
4. **Check the customDimensions** to see what's being logged

---

## Recommendations

### Immediate Action
1. ✅ Run diagnostic queries to see what's currently logged
2. ✅ Check if page is published as web service
3. ✅ Review what objects ARE showing from Hagar Webshop

### Short Term (This Week)
1. ✅ Add custom telemetry to top 3-5 most-used API procedures
2. ✅ Create dashboard tile for HAG Web Service monitoring
3. ✅ Test that telemetry appears in dashboard

### Long Term (This Month)
1. ✅ Add telemetry to all API endpoints
2. ✅ Create performance baselines
3. ✅ Set up alerts for slow API calls
4. ✅ Add error tracking with detailed diagnostics

---

## Example: Complete Telemetry Implementation

```al
page 80107 "HAG Web Service"
{
    PageType = API;
    APIPublisher = 'hagar';
    APIGroup = 'webshop';
    APIVersion = 'v1.0';

    // Helper procedure for all telemetry
    local procedure LogAPICall(ProcedureName: Text; Status: Text; ExecutionTimeMs: Integer; AdditionalInfo: Dictionary of [Text, Text])
    var
        TelemetryCustomDimensions: Dictionary of [Text, Text];
        Key: Text;
    begin
        TelemetryCustomDimensions.Add('APIPage', 'HAG Web Service');
        TelemetryCustomDimensions.Add('PageID', '80107');
        TelemetryCustomDimensions.Add('Procedure', ProcedureName);
        TelemetryCustomDimensions.Add('Status', Status);
        TelemetryCustomDimensions.Add('ExecutionTimeMs', Format(ExecutionTimeMs));

        // Add all additional info
        foreach Key in AdditionalInfo.Keys do
            TelemetryCustomDimensions.Add(Key, AdditionalInfo.Get(Key));

        Session.LogMessage(
            '0000HAG',
            StrSubstNo('HAG Web Service: %1 - %2 (%3ms)', ProcedureName, Status, ExecutionTimeMs),
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::All,
            TelemetryCustomDimensions
        );
    end;

    procedure GetCustomerData(CustomerNo: Code[20]): Text
    var
        StartTime: DateTime;
        ExecutionTime: Duration;
        AdditionalInfo: Dictionary of [Text, Text];
        Customer: Record Customer;
    begin
        StartTime := CurrentDateTime;
        AdditionalInfo.Add('CustomerNo', CustomerNo);

        // Your API logic
        if not Customer.Get(CustomerNo) then begin
            ExecutionTime := CurrentDateTime - StartTime;
            LogAPICall('GetCustomerData', 'Error: Customer not found', ExecutionTime, AdditionalInfo);
            exit('');
        end;

        // Process and return data
        ExecutionTime := CurrentDateTime - StartTime;
        AdditionalInfo.Add('RecordsReturned', '1');
        LogAPICall('GetCustomerData', 'Success', ExecutionTime, AdditionalInfo);

        exit(FormatCustomerData(Customer));
    end;
}
```

---

## Support

If you still can't see your API telemetry after:
1. Running diagnostic queries
2. Adding custom telemetry
3. Verifying the API is being called

Then check:
- **Application Insights connection** - Is telemetry flowing?
- **Extension configuration** - Is telemetry enabled for Hagar Webshop?
- **BC version** - API telemetry support varies by version
- **Permissions** - Does the calling user have telemetry rights?

---

**Created**: 2025-10-31
**Purpose**: Help diagnose and add telemetry for HAG Web Service API endpoints
**Status**: Ready for implementation
