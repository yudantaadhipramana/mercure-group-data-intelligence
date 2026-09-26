var SyntheticDataGenerator = {
  generateAll: function() {
    // Placeholder: real generation is done via Python pipeline and pushed to sheets
    // This module documents the source-system schema for the demo.
    var rawHeaders = {
      'RAW_PMS_BOOKINGS': ['booking_id','property','source_system','booking_date','check_in','check_out','room_type','guest_segment','booking_channel','room_rate','room_revenue','cancellation_status','payment_status'],
      'RAW_POS_TRANSACTIONS': ['transaction_id','transaction_date','outlet','source_system','product_code','product_name','category','quantity','gross_sales','discount','net_sales','payment_method','void_flag','refund_flag'],
      'RAW_FINANCE_GL': ['transaction_id','transaction_date','property','source_system','account_code','account_name','department','amount','transaction_type'],
      'RAW_INVENTORY_MOVEMENTS': ['inventory_date','property','source_system','product_code','product_name','opening_stock','purchase_qty','transfer_qty','consumption_qty','waste_qty','closing_stock','stock_value'],
      'RAW_PROCUREMENT': ['purchase_id','purchase_date','supplier','source_system','property','product_code','product_name','quantity','unit_price','total_amount'],
      'RAW_BUDGET': ['budget_id','period_date','property','source_system','account_code','account_name','department','budget_amount']
    };
    for (var sheet in rawHeaders) {
      Utils.writeSheet(sheet, [rawHeaders[sheet].reduce(function(acc, h) { acc[h] = h; return acc; }, {})]);
    }
    Utils.log('SyntheticDataGenerator.generateAll', 0, 0, 0, 'SUCCESS', 'Schema initialized. Use Python pipeline for actual data.');
  },
  resetAndGenerate: function() { this.generateAll(); }
};
