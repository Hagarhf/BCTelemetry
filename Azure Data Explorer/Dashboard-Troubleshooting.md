# BCTelemetry Dashboard Troubleshooting Guide

**Dashboard**: BCTelemetryDashboard.json
**Date Created**: 2025-10-30
**Status**: Configuration Required

## Overview

The BCTelemetry Dashboard is configured but requires some setup before all queries will work correctly. This guide explains the dashboard architecture and what needs to be configured.

## Dashboard Architecture

### Data Source
- **Name**: AI-Datasource
- **Type**: Azure Data Explorer (Kusto)
- **Cluster**: `https://ade.applicationinsights.io/subscriptions/a8341168-f467-4146-ba71-5e2e523dccb5`
- **Database**: `AI-CustomerNST`

### Base Queries

The dashboard uses "base queries" that act as reusable data sources. These are defined once and referenced by multiple visualizations:

#### 1. `allTraces` (Main Query)
- **Query ID**: `b19a2b7f-6d08-4f7f-b3ed-ce290cb93d82`
- **Purpose**: Central query that filters and enriches all telemetry data
- **Location**: Line 8293-8298 in BCTelemetryDashboard.json

**What it does:**
- Loads signal definitions from external GitHub source
- Unions `traces` and `pageViews` tables
- Filters by time range, eventId, messages, and other parameters
- Enriches data with tenant descriptions and instance mappings
- Calculates elapsed time in milliseconds
- Supports both SaaS (Entra Tenant ID) and On-Premise (Role Instance) deployments

**Dependencies:**
- `entraTenantIdDescriptions` - Tenant ID to customer name mapping
- `onPremiseInstances` - On-premise instance descriptions
- `serviceInstances` - Service instance descriptions
- External data: `https://raw.githubusercontent.com/Hagarhf/BCTelemetry/main/Azure%20Data%20Explorer/ExternalData/Signals.json`

#### 2. `entraTenantIdDescriptions` (Tenant Mapping)
- **Query ID**: `ba39f166-a4d3-48ea-bad0-db65876a054f`
- **Purpose**: Maps Azure AD Tenant IDs to customer-friendly names
- **Location**: Line 8319-8325

**Current Status**: ⚠️ **NEEDS CONFIGURATION**

**Current Value:**
```kql
datatable(entraTenantId :string, tenantDescription:string)
[
        "<GUID>","<CustomerName>"
]
```

#### 3. `onPremiseInstances` (On-Premise Mapping)
- **Query ID**: `cf48c267-b5e4-49fb-be61-ec76987b164e`
- **Purpose**: Maps on-premise role instances to descriptions
- **Location**: Line 8328-8334

**Current Status**: ⚠️ **NEEDS CONFIGURATION**

**Current Value:**
```kql
datatable(roleInstance :string, instanceDescription:string)
[
        "<ServerInstance>","<InstanceDescription>"
]
```

#### 4. `serviceInstances` (Service Mapping)
- **Query ID**: `df59d378-c6f5-5afb-cf72-fd87a98c275f`
- **Purpose**: Maps service instances to their purpose and description
- **Location**: Line 8337-8343

**Current Status**: ⚠️ **NEEDS CONFIGURATION**

**Current Value:**
```kql
datatable(serviceInstance :string, servicePurpose:string, serviceDescription:string)
[
        "<ServiceInstanceName>","<Purpose>","<Description>"
]
```

## Why Queries May Not Be Working

### Issue 1: Placeholder Values in Base Queries

The base queries `entraTenantIdDescriptions`, `onPremiseInstances`, and `serviceInstances` contain placeholder values like `<GUID>`, `<CustomerName>`, etc.

**Impact:**
- Dashboard loads but may show empty results
- Tenant/instance filtering won't work correctly
- `allTraces` base query will join with empty/placeholder data

### Issue 2: Missing Tenant ID Mapping

The `allTraces` query tries to join with `entraTenantIdDescriptions` to provide friendly names for tenants. If this isn't configured, you'll see GUIDs instead of customer names.

## How to Fix

### Step 1: Identify Your Tenant IDs

Run this query in Azure Data Explorer to find all tenant IDs in your telemetry:

```kql
traces
| where timestamp > ago(30d)
| extend aadTenantId = tostring(customDimensions.aadTenantId)
| where isnotempty(aadTenantId)
| summarize
    EventCount = count(),
    FirstSeen = min(timestamp),
    LastSeen = max(timestamp)
    by aadTenantId
| order by EventCount desc
```

**Expected Result:**
- List of Tenant ID GUIDs
- How many events each tenant has logged
- When you first/last saw each tenant

### Step 2: Update entraTenantIdDescriptions

In the dashboard JSON, find query ID `ba39f166-a4d3-48ea-bad0-db65876a054f` (around line 8324) and replace with:

```kql
datatable(entraTenantId :string, tenantDescription:string)
[
    "YOUR-ACTUAL-TENANT-GUID-1", "Storkaup Production",
    "YOUR-ACTUAL-TENANT-GUID-2", "Storkaup Test",
    "YOUR-ACTUAL-TENANT-GUID-3", "Customer X Production"
]
```

**Example with real format:**
```kql
datatable(entraTenantId :string, tenantDescription:string)
[
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "Storkaup Production",
    "11223344-5566-7788-99aa-bbccddeeff00", "Storkaup Test"
]
```

### Step 3: Check If You Have On-Premise Instances

Run this query to see if you have on-premise installations:

```kql
traces
| where timestamp > ago(30d)
| extend environmentName = tostring(customDimensions.environmentName)
| extend IsSaas = iff(isempty(environmentName) or environmentName in ('common','null','default','undefined'), false, true)
| summarize EventCount = count() by IsSaas
```

**If you see `IsSaas = false`**, you need to configure on-premise mappings.

Run this to find instance names:

```kql
traces
| where timestamp > ago(30d)
| extend environmentName = tostring(customDimensions.environmentName)
| extend IsSaas = iff(isempty(environmentName) or environmentName in ('common','null','default','undefined'), false, true)
| where IsSaas == false
| extend roleInstance = tostring(cloud_RoleInstance)
| summarize EventCount = count() by roleInstance
| order by EventCount desc
```

### Step 4: Update onPremiseInstances (If Needed)

If you have on-premise instances, update query ID `cf48c267-b5e4-49fb-be61-ec76987b164e` (around line 8333):

```kql
datatable(roleInstance :string, instanceDescription:string)
[
    "BC-SERVER-01", "Storkaup Production Server",
    "BC-SERVER-02", "Storkaup Test Server"
]
```

**If you only have SaaS**, you can leave the placeholder or use empty datatable:

```kql
datatable(roleInstance :string, instanceDescription:string)
[
    // No on-premise instances
]
```

### Step 5: Update serviceInstances (Optional)

This is typically used for microservices or background services. If you don't have these, leave it empty:

```kql
datatable(serviceInstance :string, servicePurpose:string, serviceDescription:string)
[
    // No service instances
]
```

Or configure if you have services:

```kql
datatable(serviceInstance :string, servicePurpose:string, serviceDescription:string)
[
    "OrderSyncService", "Integration", "Syncs orders from web store",
    "DatadwellSync", "Integration", "Digital asset synchronization"
]
```

## Verification Steps

After making changes:

### 1. Test allTraces Base Query

In Azure Data Explorer, run the exact query from line 8298 with your parameters set:

```kql
// Set parameters (copy from dashboard or adjust)
let _startTime = ago(1h);
let _endTime = now();
let _eventId = dynamic(["LC0045", "RT0030", "AL0000JRG"]);  // or your events
let _MessageFilter = "";
let _customDimensionsContains = "";
let _IsSaaS = dynamic([true, false]);
let _entraTenantId = dynamic(["ALL"]);  // or specific tenant IDs
let _environmentName = dynamic(["ALL"]);
let _CompanyFilter = "";
let _extensionName = dynamic(["ALL"]);
let _extensionPublisher = dynamic(["ALL"]);
let _componentVersionFilter = "";
let _TenantDescription = dynamic(["ALL"]);

// Your tenant mapping (from step 2)
let entraTenantIdDescriptions = datatable(entraTenantId :string, tenantDescription:string)
[
    "YOUR-TENANT-GUID", "Your Customer Name"
];

// Your on-premise mapping (from step 4)
let onPremiseInstances = datatable(roleInstance :string, instanceDescription:string)
[
    // Empty or your instances
];

// Service instances (from step 5)
let serviceInstances = datatable(serviceInstance :string, servicePurpose:string, serviceDescription:string)
[
    // Empty or your services
];

// Now paste the allTraces query from line 8298...
```

### 2. Check for Errors

Common errors:
- ❌ "Column 'X' not found" → Check customDimensions field names
- ❌ "External data source failed" → Check GitHub URL is accessible
- ❌ "Parse error" → Check datatable syntax (commas, quotes)

### 3. Verify Results

The query should return rows with:
- `tenantDescription` showing your friendly names (not GUIDs)
- `eventId`, `timestamp`, `message` populated
- `extensionName`, `extensionPublisher` for custom extensions

## Quick Fix for Testing

If you want to test the dashboard immediately without full configuration:

**Option 1: Use Auto-Generated Names**

Replace line 8324 with:
```kql
traces
| where timestamp between (_startTime .. _endTime)
| extend entraTenantId = tostring(customDimensions.aadTenantId)
| where isnotempty(entraTenantId)
| summarize by entraTenantId
| extend tenantDescription = strcat("Tenant-", substring(entraTenantId, 0, 8))
| project entraTenantId, tenantDescription
```

This generates names like "Tenant-a1b2c3d4" from the GUID.

**Option 2: Use Empty Mappings**

Replace lines 8324, 8333, 8342 with empty datatables:

```kql
// entraTenantIdDescriptions
datatable(entraTenantId :string, tenantDescription:string) []

// onPremiseInstances
datatable(roleInstance :string, instanceDescription:string) []

// serviceInstances
datatable(serviceInstance :string, servicePurpose:string, serviceDescription:string) []
```

The dashboard will work but show GUIDs/technical names instead of friendly names.

## Best Practices

1. **Document Your Mappings**: Keep a separate file with your tenant/instance mappings
2. **Version Control**: Track changes to BCTelemetryDashboard.json in git
3. **Regular Updates**: When adding new tenants/instances, update the mappings
4. **Security**: Don't commit actual tenant GUIDs to public repositories
5. **Testing**: Test queries in Azure Data Explorer before updating dashboard

## Related Files

- **BCTelemetryDashboard.json** - Main dashboard configuration
- **StorkaupExtensionUsage.kql** - Storkaup-specific analysis queries
- **StorkaupExtensionUsage_README.md** - Query documentation
- **DiscoveryQueries.kql** - Discovery and exploration queries

## Common Dashboard Queries

The dashboard includes queries for:

1. **Event Summary** (Count per company, Count per eventId)
2. **Extension Analysis** (Usage by extension name/publisher)
3. **Performance** (Slow operations, execution times)
4. **Missing Indexes** (Database optimization opportunities)
5. **Many Joins** (Query complexity analysis)
6. **Job Queues** (Background task monitoring)
7. **Errors** (Error tracking and trending)

All of these depend on the `allTraces` base query working correctly.

## Support

For issues:
1. Verify datasource connection in Azure Data Explorer
2. Test base queries individually
3. Check Application Insights has data flowing
4. Verify time range parameters are reasonable (not too far in past)

## Next Steps

1. ✅ Identify your tenant IDs (Step 1)
2. ✅ Update `entraTenantIdDescriptions` (Step 2)
3. ✅ Check for on-premise instances (Step 3)
4. ✅ Update `onPremiseInstances` if needed (Step 4)
5. ✅ Test `allTraces` base query (Verification)
6. ✅ Reload dashboard and verify visualizations work

---

**Remember**: The dashboard queries are not broken - they just need configuration with your specific tenant IDs and instance names. Once configured, all queries should work correctly.
