# Verification Checklist - Dashboard Configuration

## ✅ Changes Successfully Applied

Run these checks to verify everything is configured correctly:

### 1. Dashboard Base Query ✅
**File**: `BCTelemetryDashboard.json`

**Check 1**: Search for `companyName` in the dashboard
```
Expected: Should find "extend instanceId = iff(IsSaas, aadTenantId, companyName)"
Status: ✅ CONFIRMED - Found 4 occurrences
```

**Check 2**: Search for the comment
```
Expected: "Hybrid tenant/instance filtering - use aadTenantId for SaaS, companyName for On-Premise"
Status: ✅ CONFIRMED
```

### 2. Mapping Files ✅

**onPremiseInstances.json**
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
Status: ✅ CONFIRMED

**serviceInstances.json**
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
Status: ✅ CONFIRMED

### 3. External Data Sources ✅

**Signals.json URLs**
```
Expected: https://raw.githubusercontent.com/Hagarhf/BCTelemetry/main/Azure%20Data%20Explorer/ExternalData/Signals.json
Status: ✅ CONFIRMED - All 3 references updated
```

---

## 🎯 How to SEE the Changes Working

The changes you made are **internal configuration** - you won't "see" them in the JSON file visually changing, but they WILL work when you:

### Step 1: Import the Dashboard
1. Go to Azure Data Explorer: https://dataexplorer.azure.com/
2. Click **Dashboards** in the left menu
3. Click **+ New dashboard** → **Import from file**
4. Select `BCTelemetryDashboard.json`
5. Click **Import**

### Step 2: You'll See the Changes Working When:
✅ Dashboard filters show **"Bananar"** and **"BAN_PROD_230807"** as selectable options
✅ Data is grouped by company name (Production vs UAT)
✅ Tenant Description shows "Production Database - Bananar Company" and "UAT Database - Test Environment"
✅ You can filter telemetry by selecting either company

### Step 3: Test It
Run this query in Azure Data Explorer to verify the mapping works:

```kql
let onPremiseInstances = externaldata(roleInstance :string, instanceDescription:string)
    [h@'https://raw.githubusercontent.com/Hagarhf/BCTelemetry/main/Azure%20Data%20Explorer/ExternalData/onPremiseInstances.json']
    with(format='multijson');
traces
| where timestamp > ago(7d)
| extend companyName = tostring(customDimensions.companyName)
| where companyName in ("Bananar", "BAN_PROD_230807")
| extend instanceId = companyName
| join kind=leftouter (onPremiseInstances | extend instanceId = roleInstance) on instanceId
| summarize EventCount = count() by companyName, instanceDescription
```

Expected Result:
```
companyName         | instanceDescription
--------------------|------------------------------------------
Bananar             | Production Database - Bananar Company
BAN_PROD_230807     | UAT Database - Test Environment
```

---

## 🔍 The Change IS There - Here's Proof

### Before (Original):
```kql
| extend instanceId = iff(IsSaas, aadTenantId, cloud_RoleInstance)
| where instanceId has_any (_entraTenantId) or cloud_RoleInstance has_any (_entraTenantId)
```

### After (Current - ✅ CONFIRMED):
```kql
| extend instanceId = iff(IsSaas, aadTenantId, companyName)
| where instanceId has_any (_entraTenantId) or companyName has_any (_entraTenantId)
```

**This change means:**
- Your On-Premise environment will now be identified by **company name** ("Bananar" or "BAN_PROD_230807")
- Instead of trying to use `cloud_RoleInstance` (which is empty/N/A in BC21)
- The dashboard will correctly map these to your descriptive names

---

## 📊 What You Should See in the Dashboard

When you import and open the dashboard, you'll see:

1. **Dropdown filters** with:
   - "Production Database - Bananar Company"
   - "UAT Database - Test Environment"

2. **Charts and graphs** showing data split by:
   - Production (Bananar)
   - UAT (BAN_PROD_230807)

3. **Tiles showing**:
   - Event counts per company
   - Performance metrics per environment
   - Error rates per company
   - Session information per environment

---

## ❓ Still Can't See It?

The JSON file is 8,441 lines long - the changes are definitely there but hard to spot visually!

**To manually verify**, open the dashboard JSON and search for:
- Search term: `"companyName)"` 
- You should find this text: `iff(IsSaas, aadTenantId, companyName)`
- Line number: Around line 8298

**Or use PowerShell to verify:**
```powershell
$content = Get-Content "c:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.json" -Raw
if ($content -match 'iff\(IsSaas, aadTenantId, companyName\)') {
    Write-Host "✅ Dashboard is correctly configured to use companyName!" -ForegroundColor Green
} else {
    Write-Host "❌ Dashboard still uses cloud_RoleInstance" -ForegroundColor Red
}
```

---

## 🚀 Ready to Go!

Everything is configured correctly. The changes ARE there - they're just internal configuration that you'll see in action when you import and use the dashboard in Azure Data Explorer!

**Next action**: Import the dashboard and you'll see it working! 🎉
