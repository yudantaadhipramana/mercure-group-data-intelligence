# Mercure Group — Apps Script Backend

Modular Google Apps Script project for the Hospitality & F&B Data Intelligence demo.

## Modules

- `Config.gs` — project constants and sheet lists.
- `Menu.gs` — custom spreadsheet menu.
- `Utils.gs` — shared helpers (read/write sheets, logging).
- `SyntheticDataGenerator.gs` — schema initializer for raw sheets.
- `ETLOrchestrator.gs` — pipeline orchestration.
- `DataQualityService.gs` — quality checks.
- `ReconciliationService.gs` — source/target reconciliation.
- `AnalyticsService.gs` — analytical refresh.
- `DashboardApi.gs` — web app API (`doGet`).
- `TestService.gs` — smoke tests.
- `LoggingService.gs` — execution log viewer.

## Deploy

```bash
clasp push
```

## Note

Actual synthetic data generation is performed by the Python pipeline in `05_etl/` and then synced to Google Sheets via the existing push scripts. The Apps Script project provides the operational layer, API, and menu actions for the spreadsheet demo.
