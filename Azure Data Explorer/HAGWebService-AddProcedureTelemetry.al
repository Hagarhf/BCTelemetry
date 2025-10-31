// ================================================================
// HAG Web Service - Add Procedure-Level Telemetry
// ================================================================
// Purpose: Track individual procedures (GetTransactions, GetInvoice, etc.)
// File: This is example AL code to add to your page 80107
// ================================================================

page 80107 "HAG Web Service"
{
    PageType = API;
    APIPublisher = 'hagar';
    APIGroup = 'webshop';
    APIVersion = 'v1.0';
    EntityName = 'hagWebService';
    EntitySetName = 'hagWebServices';

    // ============================================================
    // Helper Procedure - Add this to your page
    // ============================================================
    local procedure LogProcedureCall(ProcedureName: Text; Status: Text; ExecutionTimeMs: Integer; AdditionalInfo: Dictionary of [Text, Text])
    var
        TelemetryDimensions: Dictionary of [Text, Text];
        Key: Text;
    begin
        // Core telemetry data
        TelemetryDimensions.Add('PageID', '80107');
        TelemetryDimensions.Add('PageName', 'HAG Web Service');
        TelemetryDimensions.Add('Procedure', ProcedureName);
        TelemetryDimensions.Add('Status', Status);
        TelemetryDimensions.Add('ExecutionTimeMs', Format(ExecutionTimeMs));
        TelemetryDimensions.Add('Timestamp', Format(CurrentDateTime, 0, 9));

        // Add any additional custom dimensions
        foreach Key in AdditionalInfo.Keys do
            TelemetryDimensions.Add(Key, AdditionalInfo.Get(Key));

        // Log to Application Insights
        Session.LogMessage(
            '0000HAG',  // Unique telemetry ID - use your own range
            StrSubstNo('HAG Web Service: %1 - %2 (%3ms)', ProcedureName, Status, ExecutionTimeMs),
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::All,
            TelemetryDimensions
        );
    end;

    // ============================================================
    // Example 1: GetTransactions with Telemetry
    // ============================================================
    procedure GetTransactions(CustomerNo: Code[20]; FromDate: Date; ToDate: Date): Text
    var
        StartTime: DateTime;
        ExecutionTime: Duration;
        AdditionalInfo: Dictionary of [Text, Text];
        ResultText: Text;
    begin
        StartTime := CurrentDateTime;

        // Add parameters to telemetry
        AdditionalInfo.Add('CustomerNo', CustomerNo);
        AdditionalInfo.Add('FromDate', Format(FromDate));
        AdditionalInfo.Add('ToDate', Format(ToDate));

        // Your actual procedure logic here
        ResultText := GetTransactionsInternal(CustomerNo, FromDate, ToDate);

        // Log success
        ExecutionTime := CurrentDateTime - StartTime;
        AdditionalInfo.Add('RecordsReturned', Format(CountRecords(ResultText)));
        LogProcedureCall('GetTransactions', 'Success', ExecutionTime, AdditionalInfo);

        exit(ResultText);
    end;

    // ============================================================
    // Example 2: GetInvoice with Error Handling
    // ============================================================
    procedure GetInvoice(InvoiceNo: Code[20]): Text
    var
        StartTime: DateTime;
        ExecutionTime: Duration;
        AdditionalInfo: Dictionary of [Text, Text];
        SalesInvoiceHeader: Record "Sales Invoice Header";
        ResultText: Text;
    begin
        StartTime := CurrentDateTime;
        AdditionalInfo.Add('InvoiceNo', InvoiceNo);

        // Check if invoice exists
        if not SalesInvoiceHeader.Get(InvoiceNo) then begin
            ExecutionTime := CurrentDateTime - StartTime;
            AdditionalInfo.Add('ErrorMessage', 'Invoice not found');
            LogProcedureCall('GetInvoice', 'Error: Not Found', ExecutionTime, AdditionalInfo);
            exit('');
        end;

        // Get invoice data
        ResultText := FormatInvoiceData(SalesInvoiceHeader);

        // Log success
        ExecutionTime := CurrentDateTime - StartTime;
        AdditionalInfo.Add('CustomerNo', SalesInvoiceHeader."Sell-to Customer No.");
        AdditionalInfo.Add('Amount', Format(SalesInvoiceHeader."Amount Including VAT"));
        LogProcedureCall('GetInvoice', 'Success', ExecutionTime, AdditionalInfo);

        exit(ResultText);
    end;

    // ============================================================
    // Example 3: GetCustomer (Simple Version)
    // ============================================================
    procedure GetCustomer(CustomerNo: Code[20]): Text
    var
        StartTime: DateTime;
        ExecutionTime: Duration;
        AdditionalInfo: Dictionary of [Text, Text];
    begin
        StartTime := CurrentDateTime;
        AdditionalInfo.Add('CustomerNo', CustomerNo);

        // Your logic here
        // ...

        ExecutionTime := CurrentDateTime - StartTime;
        LogProcedureCall('GetCustomer', 'Success', ExecutionTime, AdditionalInfo);

        exit(''); // Your result
    end;

    // ============================================================
    // Example 4: PostTransaction with Validation Tracking
    // ============================================================
    procedure PostTransaction(TransactionData: Text): Text
    var
        StartTime: DateTime;
        ExecutionTime: Duration;
        AdditionalInfo: Dictionary of [Text, Text];
        ValidationErrors: Integer;
    begin
        StartTime := CurrentDateTime;
        AdditionalInfo.Add('DataSize', Format(StrLen(TransactionData)));

        // Validate
        ValidationErrors := ValidateTransaction(TransactionData);
        if ValidationErrors > 0 then begin
            ExecutionTime := CurrentDateTime - StartTime;
            AdditionalInfo.Add('ValidationErrors', Format(ValidationErrors));
            LogProcedureCall('PostTransaction', 'Error: Validation Failed', ExecutionTime, AdditionalInfo);
            exit('Error');
        end;

        // Post transaction
        // ... your posting logic ...

        ExecutionTime := CurrentDateTime - StartTime;
        AdditionalInfo.Add('Posted', 'true');
        LogProcedureCall('PostTransaction', 'Success', ExecutionTime, AdditionalInfo);

        exit('Success');
    end;

    // ============================================================
    // Example 5: Batch Operation with Item Count
    // ============================================================
    procedure GetItemList(CategoryCode: Code[20]): Text
    var
        StartTime: DateTime;
        ExecutionTime: Duration;
        AdditionalInfo: Dictionary of [Text, Text];
        Item: Record Item;
        ItemCount: Integer;
    begin
        StartTime := CurrentDateTime;
        AdditionalInfo.Add('CategoryCode', CategoryCode);

        // Get items
        Item.SetRange("Item Category Code", CategoryCode);
        ItemCount := Item.Count();

        // Your logic to format items
        // ...

        ExecutionTime := CurrentDateTime - StartTime;
        AdditionalInfo.Add('ItemsReturned', Format(ItemCount));
        AdditionalInfo.Add('FilterApplied', 'Category');
        LogProcedureCall('GetItemList', 'Success', ExecutionTime, AdditionalInfo);

        exit(''); // Your result
    end;

    // ============================================================
    // Example 6: With Try-Catch Error Handling
    // ============================================================
    procedure UpdateCustomerData(CustomerNo: Code[20]; JsonData: Text): Boolean
    var
        StartTime: DateTime;
        ExecutionTime: Duration;
        AdditionalInfo: Dictionary of [Text, Text];
    begin
        StartTime := CurrentDateTime;
        AdditionalInfo.Add('CustomerNo', CustomerNo);

        if not TryUpdateCustomer(CustomerNo, JsonData) then begin
            ExecutionTime := CurrentDateTime - StartTime;
            AdditionalInfo.Add('ErrorText', GetLastErrorText());
            LogProcedureCall('UpdateCustomerData', 'Error: Update Failed', ExecutionTime, AdditionalInfo);
            ClearLastError();
            exit(false);
        end;

        ExecutionTime := CurrentDateTime - StartTime;
        LogProcedureCall('UpdateCustomerData', 'Success', ExecutionTime, AdditionalInfo);
        exit(true);
    end;

    [TryFunction]
    local procedure TryUpdateCustomer(CustomerNo: Code[20]; JsonData: Text)
    begin
        // Your update logic that might fail
    end;
}

// ================================================================
// After Adding Telemetry - Use These Queries
// ================================================================

// Query 1: Procedure Call Summary
/*
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
| extend SuccessRate = round(toreal(SuccessCount) * 100.0 / toreal(CallCount), 1)
| project procedure, CallCount, SuccessCount, ErrorCount, SuccessRate, LastCall
| order by CallCount desc
*/

// Query 2: Procedure Performance
/*
traces
| where timestamp > ago(24h)
| extend
    pageId = tostring(customDimensions.PageID),
    procedure = tostring(customDimensions.Procedure),
    executionTimeMs = toint(customDimensions.ExecutionTimeMs)
| where pageId == "80107"
| summarize
    CallCount = count(),
    AvgMs = round(avg(executionTimeMs), 2),
    P50Ms = round(percentile(executionTimeMs, 50), 2),
    P95Ms = round(percentile(executionTimeMs, 95), 2),
    MaxMs = max(executionTimeMs)
    by procedure
| extend PerformanceStatus = case(
    AvgMs > 1000, "🔴 Slow (>1s)",
    AvgMs > 500, "⚠️ Moderate (500ms-1s)",
    "✅ Fast (<500ms)"
)
| project procedure, CallCount, AvgMs, P50Ms, P95Ms, MaxMs, PerformanceStatus
| order by CallCount desc
*/

// Query 3: Error Details
/*
traces
| where timestamp > ago(24h)
| extend
    pageId = tostring(customDimensions.PageID),
    procedure = tostring(customDimensions.Procedure),
    status = tostring(customDimensions.Status),
    errorMessage = tostring(customDimensions.ErrorMessage)
| where pageId == "80107"
| where status startswith "Error"
| summarize
    ErrorCount = count(),
    FirstError = min(timestamp),
    LastError = max(timestamp),
    SampleErrors = make_set(errorMessage, 5)
    by procedure, status
| order by ErrorCount desc
*/

// Query 4: Parameter Analysis (Example: CustomerNo)
/*
traces
| where timestamp > ago(7d)
| extend
    pageId = tostring(customDimensions.PageID),
    procedure = tostring(customDimensions.Procedure),
    customerNo = tostring(customDimensions.CustomerNo)
| where pageId == "80107"
| where isnotempty(customerNo)
| summarize
    CallCount = count(),
    LastCall = max(timestamp)
    by procedure, customerNo
| order by CallCount desc
| take 20
*/

// ================================================================
// Dashboard Tile Query - Procedure-Level Monitoring
// ================================================================
/*
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
    LastCall = max(timestamp)
    by procedure
| extend
    SuccessRate = round(toreal(SuccessCount) * 100.0 / toreal(CallCount), 1),
    PerformanceStatus = case(
        AvgMs > 1000, "🔴 Slow",
        AvgMs > 500, "⚠️ Moderate",
        "✅ Fast"
    ),
    HealthStatus = case(
        ErrorCount > 10, "🔴 High Errors",
        ErrorCount > 0, "⚠️ Has Errors",
        "✅ Healthy"
    )
| project
    procedure,
    CallCount,
    SuccessRate,
    AvgMs,
    P95Ms,
    ErrorCount,
    PerformanceStatus,
    HealthStatus,
    LastCall
| order by CallCount desc
*/
