const fs = require('fs');

// Read dashboard
const data = JSON.parse(fs.readFileSync('BCTelemetryDashboard.json', 'utf8'));

// Fixed query prefix with proper join syntax
const queryPrefix = `// 🔧 CONFIGURATION: Update this datatable for different companies
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    // Format: Publisher, Extension Name (or "" for all), Include All?
    // Include ALL extensions from these publishers:
    "Storkaup", "", true,
    "NVL", "", true,
    "Stórkaup", "", true,
    // Include ONLY specific extensions:
    "Hagar", "Liquor License", false,
    "Wise", "OrderProcess", false
];
let TimeRange = 30d;
traces
| where timestamp > ago(TimeRange)
| extend
    extensionName = tostring(customDimensions.extensionName),
    extensionPublisher = tostring(customDimensions.extensionPublisher),
    alObjectType = tostring(customDimensions.alObjectType),
    alObjectId = tostring(customDimensions.alObjectId),
    alObjectName = tostring(customDimensions.alObjectName)
| join kind=inner (
    CustomExtensionsToMonitor
) on extensionPublisher
| where IncludeAll == true or extensionName == extensionName1`;

// Query 1: Main view
const query1 = `${queryPrefix}
| where isnotempty(alObjectId) and alObjectId != "-1"
| where isnotempty(alObjectType)
| summarize
    UsageCount = count(),
    UniqueUsers = dcount(user_Id),
    LastUsed = max(timestamp),
    FirstUsed = min(timestamp)
    by extensionName, extensionPublisher, alObjectType, alObjectId, alObjectName
| extend
    DaysSinceLastUse = datetime_diff('day', now(), LastUsed),
    UsagePerDay = round(toreal(UsageCount) / 30.0, 2)
| extend Status = case(
    UsageCount < 5, "🔴 Remove?",
    UsageCount < 10, "⚠️ Review",
    UsageCount < 50, "📊 Monitor",
    "✅ Keep"
)
| project
    Status,
    extensionName,
    alObjectType,
    alObjectId,
    alObjectName,
    UsageCount,
    UsagePerDay,
    DaysSinceLastUse,
    UniqueUsers,
    LastUsed
| order by UsageCount asc, DaysSinceLastUse desc`;

// Query 2: Critical low usage
const query2 = `${queryPrefix}
| where isnotempty(alObjectId) and alObjectId != "-1"
| summarize
    UsageCount = count(),
    LastUsed = max(timestamp)
    by extensionName, alObjectType, alObjectId, alObjectName
| where UsageCount < 5
| extend DaysSinceLastUse = datetime_diff('day', now(), LastUsed)
| extend Recommendation = case(
    UsageCount == 1 and DaysSinceLastUse > 60, "🗑️ Strong removal candidate",
    UsageCount < 3 and DaysSinceLastUse > 30, "🗑️ Consider removing",
    UsageCount < 5 and DaysSinceLastUse > 14, "⚠️ Review with stakeholders",
    "ℹ️ Monitor for another month"
)
| project
    extensionName,
    alObjectType,
    alObjectId,
    alObjectName,
    UsageCount,
    DaysSinceLastUse,
    LastUsed,
    Recommendation
| order by UsageCount asc, DaysSinceLastUse desc`;

// Query 3: Extension summary
const query3 = `${queryPrefix}
| where isnotempty(alObjectId) and alObjectId != "-1"
| summarize
    UniqueObjects = dcount(alObjectId),
    TotalUsage = count()
    by extensionName
| extend AvgUsagePerObject = round(toreal(TotalUsage) / toreal(UniqueObjects), 1)
| extend Health = case(
    AvgUsagePerObject < 5, "🔴 Very Low",
    AvgUsagePerObject < 20, "⚠️ Low",
    AvgUsagePerObject < 100, "📊 Moderate",
    "✅ High"
)
| project extensionName, UniqueObjects, TotalUsage, AvgUsagePerObject, Health
| order by AvgUsagePerObject asc`;

// Update queries
const queryUpdates = {
  'c1a2b3d4-e5f6-7890-1234-567890abcdef': query1,
  'd2e3f4a5-b6c7-4890-2345-678901bcdef0': query2,
  'e3f4a5b6-c7d8-4901-3456-7890abcdef12': query3
};

let updatedCount = 0;
for (let query of data.queries) {
  if (queryUpdates[query.id]) {
    query.text = queryUpdates[query.id];
    console.log(`✅ Updated query ${query.id}`);
    updatedCount++;
  }
}

// Write back
fs.writeFileSync('BCTelemetryDashboard.json', JSON.stringify(data, null, 2), 'utf8');
console.log(`\n✅ Fixed join with proper column references`);
console.log(`   Updated ${updatedCount} queries`);
console.log(`\n📝 Join uses:`);
console.log(`   - extensionPublisher (matches both sides)`);
console.log(`   - extensionName vs extensionName1 (KQL auto-renames duplicates)`);
