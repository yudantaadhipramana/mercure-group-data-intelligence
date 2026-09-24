function doGet(e) {
  const spreadsheetId = '1x7RyquXcQ3eFcsGh4R3B7wmCg2XWneHddhtY_nql4mw';
  const action = e.parameter.action || 'kpi';
  const sheet = SpreadsheetApp.openById(spreadsheetId);
  if (action === 'kpi') {
    return jsonResponse({ kpi: getSheetData(sheet, 'KPI') });
  }
  if (action === 'revenue') {
    return jsonResponse({ revenue: getSheetData(sheet, 'REVENUE_TREND') });
  }
  if (action === 'property') {
    return jsonResponse({ property: getSheetData(sheet, 'PROPERTY_PERFORMANCE') });
  }
  if (action === 'fnb') {
    return jsonResponse({ fnb: getSheetData(sheet, 'FNB_PERFORMANCE') });
  }
  if (action === 'quality') {
    return jsonResponse({ quality: getSheetData(sheet, 'DATA_QUALITY') });
  }
  if (action === 'forecast') {
    return jsonResponse({ forecast: getSheetData(sheet, 'FORECAST') });
  }
  if (action === 'anomaly') {
    return jsonResponse({ anomaly: getSheetData(sheet, 'ANOMALY') });
  }
  return jsonResponse({ sheets: sheet.getSheets().map(s => s.getName()) });
}

function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  const spreadsheetId = '1x7RyquXcQ3eFcsGh4R3B7wmCg2XWneHddhtY_nql4mw';
  const ss = SpreadsheetApp.openById(spreadsheetId);
  writeSheet(ss, data.sheetName, data.rows);
  return jsonResponse({ status: 'ok', sheetName: data.sheetName, rows: data.rows.length });
}

function getSheetData(sheet, name) {
  const s = sheet.getSheetByName(name);
  if (!s) return [];
  const values = s.getDataRange().getValues();
  const headers = values[0];
  return values.slice(1).map(row => {
    const obj = {};
    for (let i = 0; i < headers.length; i++) obj[headers[i]] = row[i];
    return obj;
  });
}

function writeSheet(ss, name, rows) {
  let s = ss.getSheetByName(name);
  if (s) {
    s.clear();
  } else {
    s = ss.insertSheet(name);
  }
  if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const data = [headers];
  rows.forEach(row => data.push(headers.map(h => row[h] !== undefined ? row[h] : '')));
  s.getRange(1, 1, data.length, data[0].length).setValues(data);
}

function jsonResponse(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
