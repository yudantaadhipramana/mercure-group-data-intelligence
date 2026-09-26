var DataQualityService = {
  runChecks: function() {
    // Read KPI and report basic counts
    var kpi = Utils.readSheetAsObjects('MART_KPI_DAILY');
    var issues = [];
    kpi.forEach(function(row) {
      if (!row.property_id) issues.push({ issue: 'missing property_id', row: row });
    });
    Logger.log('DQ issues: ' + issues.length);
    return issues;
  }
};
