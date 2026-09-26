var TestService = {
  runAll: function() {
    // Minimal smoke tests
    var results = [];
    var kpi = Utils.readSheetAsObjects('MART_KPI_DAILY');
    results.push({ test: 'MART_KPI_DAILY exists', pass: kpi.length > 0 });
    results.push({ test: 'First KPI has total_revenue', pass: kpi.length > 0 && 'total_revenue' in kpi[0] });
    Logger.log(JSON.stringify(results));
    return results;
  }
};
