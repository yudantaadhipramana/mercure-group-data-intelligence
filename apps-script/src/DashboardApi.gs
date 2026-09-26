function doGet(e) {
  var action = e.parameter.action || 'kpi';
  var data = {};
  if (action === 'kpi') {
    data.kpi = Utils.readSheetAsObjects('KPI');
  } else if (action === 'revenue') {
    data.revenue = Utils.readSheetAsObjects('REVENUE_TREND');
  } else if (action === 'property') {
    data.property = Utils.readSheetAsObjects('PROPERTY_PERFORMANCE');
  } else if (action === 'fnb') {
    data.fnb = Utils.readSheetAsObjects('FNB_PERFORMANCE');
  } else if (action === 'quality') {
    data.quality = Utils.readSheetAsObjects('DATA_QUALITY');
  } else if (action === 'forecast') {
    data.forecast = Utils.readSheetAsObjects('FORECAST');
  } else if (action === 'anomaly') {
    data.anomaly = Utils.readSheetAsObjects('ANOMALY');
  }
  return jsonResponse(data);
}

function jsonResponse(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload)).setMimeType(ContentService.MimeType.JSON);
}
