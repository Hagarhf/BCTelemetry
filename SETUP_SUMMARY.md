# BC Telemetry Dashboard - Setup Summary

## Overview
Your BC Telemetry Dashboard has been successfully configured for **On-Premise Business Central 21** using **company names** to distinguish between environments.

## Configuration Details

### Environment Setup
- **Business Central Version**: 21.0.56004.0
- **Deployment Type**: On-Premise (BC21 doesn't support CloudRoleInstance configuration)
- **Identification Method**: Company Name (`customDimensions.companyName`)

### Company Mappings

#### Production Database
- **Company Name**: `Bananar`
- **Description**: Production Database - Bananar Company
- **Service Instances**: 3 instances (Standard purpose)

#### UAT Database  
- **Company Name**: `BAN_PROD_230807`
- **Description**: UAT Database - Test Environment
- **Service Instances**: 1 instance (Standard purpose)

## Dashboard Changes Made

### 1. Base Query Updates
- **Changed**: `cloud_RoleInstance` → `companyName` for instance identification
- **Reason**: BC21 doesn't populate cloud_RoleInstance field, company name is more reliable
- **Impact**: Dashboard now uses company names to filter and group telemetry data

### 2. Mapping Files Created/Updated

#### `onPremiseInstances.json`
```json
[
    {
        "roleInstance": "Bananar",
        "instanceDescription": "Production Database - Bananar Company"
    },
    {
        "roleInstance": "BAN_PROD_230807",
        "instanceDescription": "UAT Database - Test Environment"
    }
]
```

#### `serviceInstances.json`
```json
[
    {
        "serviceInstance": "Bananar",
        "servicePurpose": "Standard",
        "serviceDescription": "Production - Standard Business Central Service (3 instances)"
    },
    {
        "serviceInstance": "BAN_PROD_230807",
        "servicePurpose": "Standard",
        "serviceDescription": "UAT - Test Environment Service (1 instance)"
    }
]
```

#### `entraTenantId.json`
```json
[
    {
        "entraTenantId": "a3aee5b-dce4-456c-8449-c513ca453f3",
        "tenantDescription": "Placeholder - No SaaS environments configured"
    }
]
```

### 3. External Data Sources
All external data files are served from your public GitHub repository:
- **Repository**: `Hagarhf/BCTelemetry`
- **Branch**: `main`
- **Signals.json**: Updated to reference your repository instead of Waldo's

## How to Use the Dashboard

### 1. Import to Azure Data Explorer
1. Open Azure Data Explorer Web UI
2. Navigate to your cluster and database
3. Click "+ Add" → "Dashboard from file"
4. Select `BCTelemetryDashboard.json`
5. Configure data connection to your Application Insights resource

### 2. Filter by Environment
The dashboard will automatically distinguish between:
- **Production** (Bananar company)
- **UAT** (BAN_PROD_230807 company)

Use the tenant/instance filters in the dashboard to view specific environments.

### 3. Monitoring Multiple Service Instances
**Current Limitation**: Since BC21 doesn't support `cloud_RoleInstance` configuration, you cannot distinguish between the 3 production service instances individually. The dashboard will show:
- Aggregated data for all Production instances (under "Bananar")
- Separate data for UAT instance (under "BAN_PROD_230807")

## Future Enhancements

### Option 1: Upgrade to BC22+ (if available)
Newer versions may support proper `cloud_RoleInstance` configuration, allowing instance-level granularity.

### Option 2: Use Custom Dimensions
You could add custom dimensions in your AL code to identify different service instances:
```al
Session.LogMessage('0000ABC', 'Custom event', Verbosity::Normal, DataClassification::SystemMetadata, 
    TelemetryScope::All, 'ServiceInstance', 'PROD-Standard-01');
```

### Option 3: Separate Application Insights Resources
Configure each service instance to send telemetry to different App Insights resources.

## Files in This Workspace

```
BCTelemetry/
├── Azure Data Explorer/
│   ├── BCTelemetryDashboard.json          # Main dashboard (updated for companyName)
│   ├── DiscoveryQueries.kql               # Queries to discover tenant/instance info
│   ├── CompanyNameDiscovery.kql           # Queries to discover company names
│   ├── AlternativeDiscovery.kql           # Alternative field discovery
│   └── ExternalData/
│       ├── entraTenantId.json             # SaaS tenant mappings (empty)
│       ├── onPremiseInstances.json        # On-Premise instance mappings (configured)
│       ├── serviceInstances.json          # Service instance mappings (configured)
│       └── Signals.json                   # Event definitions (1347 events)
└── UpdateDashboard.ps1                    # Script used to update dashboard

```

## Key Technical Details

### Hybrid Detection Logic
```kql
// Determines if environment is SaaS or On-Premise
| extend IsSaas = iff(
    isempty(environmentName) or 
    environmentName in ('common','null','default','undefined'),
    false,  // On-Premise
    true    // SaaS
)
```

### Instance Identification
```kql
// Uses aadTenantId for SaaS, companyName for On-Premise
| extend instanceId = iff(IsSaas, aadTenantId, companyName)
```

### Filtering
```kql
// Allows filtering by either tenant ID or company name
| where instanceId has_any (_entraTenantId) or companyName has_any (_entraTenantId)
```

## Support & Troubleshooting

### Dashboard Not Loading Data
1. Verify Application Insights connection string is correct
2. Check that telemetry is flowing (run simple query in App Insights)
3. Verify company names match exactly (case-sensitive)

### Company Names Not Appearing
1. Run `CompanyNameDiscovery.kql` queries to verify company names
2. Check `customDimensions.companyName` field exists in your telemetry
3. Ensure data is within the selected time range

### External Data Not Loading
1. Verify repository is public: https://github.com/Hagarhf/BCTelemetry
2. Check file URLs are accessible
3. Validate JSON syntax in mapping files

## Next Steps

✅ **Dashboard is ready to use!**
1. Import `BCTelemetryDashboard.json` to Azure Data Explorer
2. Connect to your Application Insights data source
3. Start monitoring your BC telemetry with Production/UAT separation

---

**Dashboard Version**: Configured for BC21 On-Premise with Company Name identification  
**Last Updated**: October 21, 2025  
**Configuration**: Production (Bananar) + UAT (BAN_PROD_230807)
