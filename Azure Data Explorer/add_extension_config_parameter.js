const fs = require('fs');

// Read dashboard
const data = JSON.parse(fs.readFileSync('BCTelemetryDashboard.json', 'utf8'));

// Add a new parameter for custom extension configuration
const newParameter = {
  "kind": "string",
  "selectionType": "freetext",
  "id": "ext-config-12345678-1234-1234-1234-123456789abc",
  "displayName": "Custom Extensions Config",
  "variableName": "_CustomExtensionsConfig",
  "description": "Format: Publisher1:*,Publisher2:App1,Publisher3:App2|App3 (use * for all extensions, | to separate multiple apps)",
  "defaultValue": {
    "kind": "value",
    "value": "Storkaup:*,NVL:*,Stórkaup:*,Hagar:Liquor License,Wise:OrderProcess"
  },
  "showOnPages": {
    "kind": "selection",
    "pageIds": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]  // Custom: Unused Objects page
  }
};

// Add parameter if it doesn't exist
const parameterExists = data.parameters.some(p => p.id === newParameter.id);
if (!parameterExists) {
  data.parameters.push(newParameter);
  console.log('✅ Added Custom Extensions Config parameter');
} else {
  console.log('ℹ️  Parameter already exists');
}

// Now update the queries to use this parameter
// Parse the configuration string and build the filter dynamically
const queryPrefix = `// Parse custom extension configuration
let ConfigString = _CustomExtensionsConfig;
let CustomExtensionsToMonitor =
    ConfigString
    | extend Parts = split(ConfigString, ",")
    | mv-expand Part = Parts to typeof(string)
    | extend PublisherAndApps = split(Part, ":")
    | extend
        Publisher = tostring(PublisherAndApps[0]),
        Apps = tostring(PublisherAndApps[1])
    | extend AppList = split(Apps, "|")
    | mv-expand App = AppList to typeof(string)
    | project Publisher, App = tostring(App), IncludeAll = (App == "*")
    | distinct Publisher, App, IncludeAll;
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
) on $left.extensionPublisher == $right.Publisher
| where IncludeAll == true or extensionName == App`;

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
    console.log(`✅ Updated query ${query.id} to use parameter`);
    updatedCount++;
  }
}

// Write back
fs.writeFileSync('BCTelemetryDashboard.json', JSON.stringify(data, null, 2), 'utf8');
console.log(`\n✅ Dashboard updated successfully`);
console.log(`   Added parameter and updated ${updatedCount} queries`);
console.log(`\nConfiguration format:`);
console.log(`   Publisher1:*,Publisher2:AppName,Publisher3:App1|App2`);
console.log(`\nExample for another company:`);
console.log(`   CompanyA:*,Vendor1:CriticalApp,Vendor2:App1|App2|App3`);
