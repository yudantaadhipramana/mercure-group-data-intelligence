var Utils = {
  getOrCreateSheet: function(name) {
    var ss = SpreadsheetApp.openById(CONFIG.spreadsheetId);
    var sheet = ss.getSheetByName(name);
    if (!sheet) { sheet = ss.insertSheet(name); }
    return sheet;
  },
  clearSheet: function(name) {
    var sheet = this.getOrCreateSheet(name);
    sheet.clear();
    return sheet;
  },
  writeSheet: function(name, rows) {
    var sheet = this.clearSheet(name);
    if (!rows || rows.length === 0) return sheet;
    var headers = Object.keys(rows[0]);
    var data = [headers];
    rows.forEach(function(row) {
      data.push(headers.map(function(h) { return row[h] !== undefined ? row[h] : ''; }));
    });
    sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
    return sheet;
  },
  readSheetAsObjects: function(name) {
    var ss = SpreadsheetApp.openById(CONFIG.spreadsheetId);
    var sheet = ss.getSheetByName(name);
    if (!sheet) return [];
    var values = sheet.getDataRange().getValues();
    var headers = values[0];
    return values.slice(1).map(function(row) {
      var obj = {};
      headers.forEach(function(h, i) { obj[h] = row[i]; });
      return obj;
    });
  },
  log: function(process, inputRows, outputRows, failedRows, status, error) {
    var sheet = this.getOrCreateSheet(CONFIG.logSheet);
    var runId = 'RUN-' + new Date().getTime();
    sheet.appendRow([runId, new Date(), process, inputRows, outputRows, failedRows, status, error || '']);
  }
};
