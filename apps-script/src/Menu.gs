function onOpen(e) {
  SpreadsheetApp.getUi().createMenu('LensaData Intelligence')
    .addItem('Generate Synthetic Raw Data', 'SyntheticDataGenerator.generateAll')
    .addItem('Reset and Regenerate Demo Dataset', 'SyntheticDataGenerator.resetAndGenerate')
    .addItem('Profile Raw Data', 'DataProfilingService.profileRaw')
    .addItem('Run EDA', 'DataProfilingService.runEda')
    .addItem('Run ETL', 'ETLOrchestrator.runFullPipeline')
    .addItem('Run Data Quality Checks', 'DataQualityService.runChecks')
    .addItem('Run Reconciliation', 'ReconciliationService.run')
    .addItem('Refresh Analytical Data', 'AnalyticsService.refresh')
    .addItem('Run Full Pipeline', 'ETLOrchestrator.runFullPipeline')
    .addItem('View Latest Execution Log', 'LoggingService.showLog')
    .addItem('Run Automated Tests', 'TestService.runAll')
    .addToUi();
}
