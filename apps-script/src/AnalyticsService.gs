var AnalyticsService = {
  refresh: function() {
    // Refresh dashboard JSON by reading MART_KPI_DAILY
    var rows = Utils.readSheetAsObjects('MART_KPI_DAILY');
    Logger.log('Analytics refreshed: ' + rows.length + ' rows');
  }
};
