var ReconciliationService = {
  run: function() {
    var rawPms = Utils.readSheetAsObjects('RAW_PMS_BOOKINGS').length;
    var cleanPms = Utils.readSheetAsObjects('CLEAN_PMS_BOOKINGS').length;
    return { source: 'RAW_PMS_BOOKINGS', raw: rawPms, clean: cleanPms, difference: rawPms - cleanPms };
  }
};
