var LoggingService = {
  showLog: function() {
    var ss = SpreadsheetApp.openById(CONFIG.spreadsheetId);
    var sheet = ss.getSheetByName(CONFIG.logSheet);
    if (sheet) { ss.setActiveSheet(sheet); }
  }
};
