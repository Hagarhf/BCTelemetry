# Dashboard Changes - Unused Customizations Page Added

**Date**: 2025-10-31
**Status**: ✅ Complete and Validated

---

## Summary

Successfully added a new "Custom: Unused Objects" page to the BCTelemetry Dashboard with 3 tiles showing:
1. All custom objects with usage statistics (sorted by least used first)
2. Critical low usage objects (< 5 uses in 30 days)
3. Extension health summary by publisher

---

## What Was Added

### 1. New Page Definition

**Page Name**: "Custom: Unused Objects"
**Page ID**: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

Added to the `pages` array after the BCPT page.

### 2. Three Dashboard Tiles

#### Tile 1: Unused/Low Usage Objects (All)
- **Location**: Top of page (x:0, y:0, width:24, height:10)
- **Type**: Table
- **Query ID**: `uc-query-001-main`
- **Purpose**: Shows all custom objects from Storkaup, Hagar, and NVL extensions with usage statistics
- **Key Columns**:
  - Status (🔴 Remove?, ⚠️ Review, 📊 Monitor, ✅ Keep)
  - Extension name
  - Object type (Page, Codeunit, Table, etc.)
  - Object ID and name
  - Usage count (total in 30 days)
  - Usage per day (average)
  - Days since last use
  - Unique users
  - Last used timestamp

**Sorting**: Least used first (ascending by usage count, then descending by days since last use)

#### Tile 2: Critical Low Usage (< 5 uses in 30 days)
- **Location**: Middle of page (x:0, y:10, width:24, height:8)
- **Type**: Table
- **Query ID**: `uc-query-002-critical`
- **Purpose**: Highlights objects with very low usage that are strong removal candidates
- **Key Columns**:
  - Extension name
  - Object type
  - Object ID and name
  - Usage count
  - Days since last use
  - Last used timestamp
  - Recommendation (🗑️ Strong removal candidate, 🗑️ Consider removing, ⚠️ Review with stakeholders, ℹ️ Monitor for another month)

**Filtering**: Only shows objects with < 5 uses in 30 days

#### Tile 3: Extension Health Summary
- **Location**: Bottom of page (x:0, y:18, width:24, height:6)
- **Type**: Table
- **Query ID**: `uc-query-003-summary`
- **Purpose**: High-level health overview of each custom extension
- **Key Columns**:
  - Extension name
  - Unique objects (count)
  - Total usage (all events in 30 days)
  - Average usage per object
  - Health (🔴 Very Low, ⚠️ Low, 📊 Moderate, ✅ High)

**Sorting**: Least healthy extensions first (ascending by average usage per object)

### 3. Three KQL Queries

All queries filter for **your custom extensions only**:
- `extensionPublisher in ("Storkaup", "Hagar", "NVL")`
- Excludes Microsoft, LS Retail, Wise, and all other 3rd party extensions

**Time Range**: 30 days (`let TimeRange = 30d;`)

---

## How to Use the New Page

### 1. Access the Page

1. Open your BCTelemetry Dashboard in Azure Data Explorer
2. Look for the new page "**Custom: Unused Objects**" in the left navigation
3. Click to view the page

### 2. Interpreting the Results

**Status Indicators (Tile 1)**:
- 🔴 **Remove?** - Less than 5 uses in 30 days - Top removal candidates
- ⚠️ **Review** - 5-10 uses - Discuss with stakeholders before removing
- 📊 **Monitor** - 10-50 uses - Keep monitoring trends
- ✅ **Keep** - 50+ uses - Actively used, definitely keep

**Recommendations (Tile 2)**:
- 🗑️ **Strong removal candidate** - 1 use, not used in 60+ days
- 🗑️ **Consider removing** - < 3 uses, not used in 30+ days
- ⚠️ **Review with stakeholders** - < 5 uses, not used in 14+ days
- ℹ️ **Monitor for another month** - Low usage but recently used

**Health Status (Tile 3)**:
- 🔴 **Very Low** - < 5 average uses per object
- ⚠️ **Low** - 5-20 average uses per object
- 📊 **Moderate** - 20-100 average uses per object
- ✅ **High** - 100+ average uses per object

### 3. Taking Action

**Before Removing Any Objects**:

1. ✅ **Export the results** to Excel for stakeholder review
2. ✅ **Verify with business users** - Some objects may be used only during specific periods (month-end, quarter-end, annually)
3. ✅ **Check dependencies** - Some objects (event subscribers, error handlers) may not generate direct telemetry
4. ✅ **Consider increasing time range** - Change `TimeRange` to 90d or 180d for seasonal functionality
5. ✅ **Get approval** - Always get stakeholder sign-off before removing any objects
6. ✅ **Test in non-production first** - Remove from test environment and verify no impact
7. ✅ **Document removals** - Keep track of what was removed and when
8. ✅ **Create rollback plan** - Be prepared to restore if needed

**Safe Removal Workflow**:
1. Identify objects with 🔴 status and 60+ days since last use
2. Validate with business stakeholders
3. Remove from test environment
4. Monitor for 2 weeks
5. If no issues, remove from production
6. Monitor production for another 2 weeks

---

## Based on Your 24-Hour Data

From the full system analysis, here's what you can expect to see:

### Extensions with Telemetry (Will Show in Dashboard)

1. **Hagar Connect**: 1,115 events (0.71%)
   - HAG ASB Queue: 858 calls
   - HAG Datadog Utils: 251 calls
   - HAG Export Processing: 6 operations
   - **Expected Health**: ✅ High to 📊 Moderate

2. **Hagar Webshop**: 64 events (0.04%)
   - HAG Delete Export Tools: 27 slow queries
   - HAG Web Inventory Functions: 1 operation
   - HAG Customer API: 1 operation
   - **Expected Health**: ⚠️ Low

3. **WebStore (NVL)**: 72 events (0.05%)
   - NVL CO Status Mgmt: 36 operations
   - NVL Omni BO Utils: 36 operations
   - **Expected Health**: ⚠️ Low

4. **Storkaup**: 38 events (0.02%)
   - PTE AX Int. Update Inventory: 36 operations
   - PTEEventSubscriber: 1 operation
   - PTEUpdateUnitPrFromSalesPr: 1 operation
   - **Expected Health**: 🔴 Very Low

### Extensions with ZERO Telemetry (Investigation Needed)

These extensions had **0 events in 24 hours** - they may be:
- Not installed
- Used less frequently (weekly/monthly)
- Event subscribers with no direct telemetry
- Deprecated but still deployed

**Missing Extensions**:
- OrderProcess
- CustomerPricing
- CustPriceDisc
- Datadwell
- NationalRegistry
- SalesReleaseCheck
- CustomerCreditCheck
- ... and 12+ more extensions

**Action**: Review these extensions to determine if they should be removed or if they're just low-frequency usage.

---

## Adjusting the Time Range

If you want to analyze a longer period (to catch monthly/quarterly usage):

1. In Azure Data Explorer, open the dashboard for editing
2. Find the queries with ID: `uc-query-001-main`, `uc-query-002-critical`, `uc-query-003-summary`
3. Change `let TimeRange = 30d;` to:
   - `let TimeRange = 90d;` (3 months)
   - `let TimeRange = 180d;` (6 months)
   - `let TimeRange = 365d;` (1 year)

**Recommendation**: Start with 30 days, then increase to 90 days if you see too many low-usage objects that might be seasonal.

---

## Backup Information

**Original Dashboard Backup**: `BCTelemetryDashboard.backup.[timestamp].json`

To restore the backup if needed:
1. Rename the backup file to `BCTelemetryDashboard.json`
2. Upload to Azure Data Explorer
3. Refresh the dashboard

---

## Technical Details

### Files Modified

**File**: `C:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.json`

**Changes**:
1. Added page definition (line ~6445)
2. Added 3 tile definitions (lines ~5899-5979)
3. Added 3 query definitions (lines ~8525-8551)

**Validation**: ✅ JSON syntax validated successfully

### Query IDs

- **Main View**: `uc-query-001-main`
- **Critical Low Usage**: `uc-query-002-critical`
- **Extension Summary**: `uc-query-003-summary`

### Tile IDs

- **Main Tile**: `uc-tile-001-main-view`
- **Critical Tile**: `uc-tile-002-critical`
- **Summary Tile**: `uc-tile-003-summary`

### Page ID

- **Page**: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

---

## Related Files

These standalone query files were created earlier and can be run independently:

1. **UnusedCustomizations-Query.kql** - Comprehensive version with multiple views
2. **UnusedCustomizations-Dashboard-Simple.kql** - Simplified dashboard version

**Note**: The queries in the dashboard JSON are based on these files.

---

## Next Steps

1. ✅ **Upload the modified dashboard** to Azure Data Explorer
2. ✅ **Verify the new page appears** in the navigation
3. ✅ **Run the queries** and verify they return data
4. ✅ **Export results** to Excel for stakeholder review
5. ✅ **Schedule monthly reviews** to track usage trends over time
6. ✅ **Consider adjusting time range** to 90 days if you see many low-usage objects

---

## Support

If you encounter any issues:

1. **JSON validation errors**: Restore the backup and check for syntax issues
2. **Empty results**: Verify you have telemetry data for Storkaup, Hagar, or NVL extensions
3. **Performance issues**: Consider reducing the time range or adding indexes

---

**Created**: 2025-10-31
**Status**: ✅ Complete and Ready for Use
**Validation**: ✅ JSON syntax valid
**Backup**: ✅ Created before modifications
