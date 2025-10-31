# KQL Extend Statement Fix

**Date**: 2025-10-31
**Issue**: Cannot reference a column in the same `extend` statement where it's created
**Status**: ✅ Fixed

---

## Problem

KQL error in "Extension Health Summary" query:
```
'extend' operator: Failed to resolve column or scalar expression named 'AvgUsagePerObject'
```

### Root Cause

In KQL, you cannot reference a column created in an `extend` statement within the same `extend` statement.

**❌ This doesn't work:**
```kql
| extend
    AvgUsagePerObject = round(toreal(TotalUsage) / toreal(UniqueObjects), 1),
    Health = case(
        AvgUsagePerObject < 5, "🔴 Very Low",  // ERROR: AvgUsagePerObject not yet available
        ...
    )
```

The `Health` calculation tries to use `AvgUsagePerObject` before it's been fully created.

---

## Solution

Split the single `extend` into two separate `extend` statements:

**✅ This works:**
```kql
| extend AvgUsagePerObject = round(toreal(TotalUsage) / toreal(UniqueObjects), 1)
| extend Health = case(
    AvgUsagePerObject < 5, "🔴 Very Low",  // ✅ Now AvgUsagePerObject is available
    AvgUsagePerObject < 20, "⚠️ Low",
    AvgUsagePerObject < 100, "📊 Moderate",
    "✅ High"
)
```

---

## Files Fixed

### 1. BCTelemetryDashboard.json
**Query ID**: `e3f4a5b6-c7d8-4901-3456-7890abcdef12` (Extension Health Summary)
- Split `extend` statement into two
- First creates `AvgUsagePerObject`
- Second creates `Health` using `AvgUsagePerObject`

### 2. UnusedCustomizations-Query.kql
**Query 3**: Extension Health Summary (commented out section)
- Fixed same issue in standalone query file
- Consistent with dashboard query

### 3. UnusedCustomizations-Dashboard-Simple.kql
**Query 3**: Extension Health Summary (commented out section)
- Fixed same issue in simple dashboard version
- Consistent with other files

---

## Key Learning

**KQL Rule**: When you need to create a calculated column and then use it in another calculation, you must use separate `extend` statements:

```kql
// Step 1: Create the column
| extend CalculatedColumn = <expression>

// Step 2: Use the column in another calculation
| extend DerivedColumn = case(
    CalculatedColumn < threshold1, "Value1",
    CalculatedColumn < threshold2, "Value2",
    "DefaultValue"
)
```

**Alternative**: You could also repeat the calculation expression, but that's less maintainable:
```kql
| extend
    AvgUsagePerObject = round(toreal(TotalUsage) / toreal(UniqueObjects), 1),
    Health = case(
        round(toreal(TotalUsage) / toreal(UniqueObjects), 1) < 5, "🔴 Very Low",  // Repeated calculation
        ...
    )
```

---

## Validation

✅ JSON syntax valid
✅ Query executes without errors
✅ All three files updated consistently
✅ Dashboard ready for upload

---

**Status**: ✅ Fixed and Ready for Production
