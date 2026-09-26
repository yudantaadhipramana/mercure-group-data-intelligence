# EDA — Mercure Group Data Intelligence (Powered by LensaData)

Every figure below is computed from the warehouse marts.
Synthetic demonstration — all values fictional.

## 1. Dataset Overview

| Table | Rows |
|---|---|
| `dim_date` | 820 |
| `dim_property` | 9 |
| `dim_product` | 58 |
| `dim_account` | 37 |
| `fact_room_sales` | 136,931 |
| `fact_fnb_sales` | 1,404,931 |
| `fact_inventory` | 151,110 |
| `fact_purchase` | 16,202 |
| `fact_expense` | 7,415 |
| `fact_budget` | 7,413 |

## 2. Distributions

**room_revenue**: count=125,345, mean=1,697,252.90, std=525,478.62, min=960,000.00, p01=984,000.00, p05=1,037,000.00

**adr**: count=125,345, mean=1,697,252.90, std=525,478.62, min=960,000.00, p01=984,000.00, p05=1,037,000.00

**fnb_net_sales**: count=1,388,010, mean=116,042.92, std=95,808.63, min=-528,002.32, p01=-88,000.00, p05=24,197.48

**fnb_check_size**: count=556,859, mean=289,245.10, std=204,000.84, min=-948,134.43, p01=-40,437.17, p05=39,260.55

**food_cost_pct**: count=1,362,910, mean=28.70, std=5.81, min=15.00, p01=15.00, p05=18.00

![distributions](dist_distributions.png)

## 3. Time Series

![daily](ts_daily.png)

![monthly](ts_monthly.png)

## 4. Segmentation

**By property**: Mercure Grand Malang=122.91bn, Mercure Grand Bali=87.93bn, Mercure Grand Jakarta=75.07bn, Mercure Grand Surabaya=74.49bn, Mercure Grand Bandung=49.92bn, Mercure Grand Yogyakarta=49.66bn, Mercure Grand Semarang=42.48bn

![seg property](seg_property.png)

**By channel**: OTA=62.75bn, Direct Website=58.78bn, Corporate=37.31bn, GDS=20.91bn, WhatsApp=16.39bn, Walk-in=12.38bn

![seg channel](seg_channel.png)

**By segment**: Leisure=71.62bn, Corporate=47.58bn, OTA=39.47bn, Wholesale=20.29bn, Group=16.98bn, Wedding & Event=12.54bn

![seg segment](seg_segment.png)

**By category**: Main Course=71.79bn, Beverage=23.56bn, Rice & Noodles=18.33bn, Dessert=11.72bn, Coffee=10.23bn, Breakfast=9.21bn, Appetizer=8.62bn, Snack=7.01bn

![seg category](seg_category.png)

## 5. Outliers (statistical)

**daily_revenue**: 24 high outliers (z>3), 0 low (z<-3)

**occupancy**: 0 high outliers (z>3), 0 low (z<-3)

**food_cost**: 4 high outliers (z>3), 0 low (z<-3)

**fnb_transactions**: 0 high outliers (z>3), 0 low (z<-3)