var ETLOrchestrator = {
  runFullPipeline: function() {
    SyntheticDataGenerator.generateAll();
    DataQualityService.runChecks();
    AnalyticsService.refresh();
    ReconciliationService.run();
    Utils.log('ETLOrchestrator.runFullPipeline', 0, 0, 0, 'SUCCESS', 'Pipeline executed (demo).');
  }
};
