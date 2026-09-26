"""
LensaData — Mercure Group Data Intelligence Demo
Shared parameter module: every business constant lives here. No magic numbers elsewhere.
Synthetic demonstration. Mercure Group is fictional.
"""
from __future__ import annotations
import numpy as np
from datetime import date, timedelta

# ---------------------------------------------------------------- determinism
# ---------------------------------------------------------------- source systems (synthetic)
# Each branch may run a different POS/ERP system with its own schema and dirty quirks.
SOURCE_SYSTEMS = {
    "PMS-HOTEL-01": {"properties": ["H001", "H003", "H005"], "date_fmt": "%Y-%m-%d", "dec_style": "id"},
    "PMS-HOTEL-02": {"properties": ["H002", "H004"], "date_fmt": "%d/%m/%Y", "dec_style": "en"},
    "PMS-HOTEL-03": {"properties": ["H006", "H007"], "date_fmt": "%d-%b-%Y", "dec_style": "plain"},
    "POS-FNB-01": {"outlets": ["O01", "O03", "O05", "O07", "O08", "O09", "O10"], "date_fmt": "%Y-%m-%d", "dec_style": "id"},
    "POS-FNB-02": {"outlets": ["O02", "O04", "O06", "O11", "O12", "O13", "O14"], "date_fmt": "%d/%m/%Y", "dec_style": "en"},
    "ERP-FIN-01": {"properties": "all", "date_fmt": "%Y-%m-%d", "dec_style": "id"},
    "INV-SYSTEM-01": {"properties": "all", "date_fmt": "%d/%m/%Y", "dec_style": "en"},
    "PROCUREMENT-01": {"properties": "all", "date_fmt": "%Y-%m-%d", "dec_style": "plain"},
    "BUDGET-01": {"properties": "all", "date_fmt": "%Y-%m-%d", "dec_style": "id"},
}

SEED = 20260924

# ---------------------------------------------------------------- calendar
START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 12, 31)
DAYS = (END_DATE - START_DATE).days + 1                     # 731
FORECAST_HORIZON_DAYS = 90
FC_START = date(2027, 1, 1)
FC_END = date(2027, 3, 31)

# Indonesian long-weekend / holiday set — SIMPLIFIED, not a claim about real dates
HOLIDAYS = {
    date(2025, 1, 1): "New Year 2025",
    date(2025, 1, 29): "Chinese New Year 2025",
    date(2025, 3, 31): "Easter Monday 2025",
    date(2025, 3, 29): "Easter Saturday 2025",
    date(2025, 5, 1): "Labour Day 2025",
    date(2025, 6, 1): "Pancasila Day 2025",
    date(2025, 8, 17): "Independence Day 2025",
    date(2025, 12, 25): "Christmas 2025",
    date(2026, 1, 1): "New Year 2026",
    date(2026, 2, 17): "Chinese New Year 2026",
    date(2026, 4, 5): "Easter Sunday 2026",
    date(2026, 5, 1): "Labour Day 2026",
    date(2026, 6, 1): "Pancasila Day 2026",
    date(2026, 8, 17): "Independence Day 2026",
    date(2026, 12, 25): "Christmas 2026",
    date(2026, 12, 26): "Christmas Holiday 2026",
}
# 3-day long-weekend windows centred on the holidays above
LONG_WEEKENDS: list[tuple[date, date]] = []
for d in sorted(HOLIDAYS):
    LONG_WEEKENDS.append((d - timedelta(days=1), d + timedelta(days=1)))

# day-of-week demand multipliers (Mon=0 .. Sun=6)
DOW_FACTOR = {0: 0.92, 1: 0.95, 2: 0.97, 3: 1.02, 4: 1.18, 5: 1.22, 6: 0.88}
MONTH_FACTOR = {1: 1.05, 2: 0.88, 3: 0.90, 4: 0.95, 5: 0.98, 6: 1.08,
                7: 1.12, 8: 1.10, 9: 0.96, 10: 0.97, 11: 1.03, 12: 1.15}
YEAR_UPLIFT = {2025: 1.00, 2026: 1.06}                     # YoY growth
LONG_WEEKEND_BOOST = 1.25

# ---------------------------------------------------------------- properties
PROPERTIES = [
    # id, name, city, region, rooms, class, base_occ, base_adr (Rp '000)
    ("H001", "Mercure Grand Jakarta",   "Jakarta",    "Java", 200, "Upper Midscale", 0.78, 1450),
    ("H002", "Mercure Grand Bandung",   "Bandung",    "Java", 200, "Upper Midscale", 0.74, 1180),
    ("H003", "Mercure Grand Surabaya",  "Surabaya",   "Java", 200, "Upper Midscale", 0.76, 1320),
    ("H004", "Mercure Grand Yogyakarta","Yogyakarta", "Java", 200, "Midscale",       0.70, 1080),
    ("H005", "Mercure Grand Bali",      "Denpasar",   "Bali", 200, "Upper Midscale", 0.82, 1680),
    ("H006", "Mercure Grand Semarang",  "Semarang",   "Java", 200, "Midscale",       0.66,  980),
    ("H007", "Mercure Grand Malang",    "Malang",     "Java", 200, "Midscale",       0.64,  920),
]
FNB_UNITS = [
    ("F001", "Mercure Food Hall",     "Jakarta",  "Java", "F&B"),
    ("F002", "Mercure Dining Group",  "Bandung",  "Java", "F&B"),
]
ROOMS_DEFAULT = 200

# property alias generator — deterministic variants per property
PROPERTY_ALIAS_TEMPLATES = [
    "{name}", "MG {city_short}", "MG {city}", "{name_short}",
    "{upper}", "{dash}",
]
CITY_SHORT = {"Jakarta": "JKT", "Bandung": "BDG", "Surabaya": "SUB", "Yogyakarta": "JOG",
              "Denpasar": "DPS", "Semarang": "SRG", "Malang": "MLG"}
NAME_SHORT = {"Mercure Grand Jakarta": "Mercure Grand JKT", "Mercure Grand Bandung": "Mercure Grand BDG",
              "Mercure Grand Surabaya": "Mercure Grand SUB", "Mercure Grand Yogyakarta": "Mercure Grand JOG",
              "Mercure Grand Bali": "Mercure Grand DPS", "Mercure Grand Semarang": "Mercure Grand SRG",
              "Mercure Grand Malang": "Mercure Grand MLG"}

# ---------------------------------------------------------------- business units
BUSINESS_UNITS = [
    ("BU-HOTEL", "Hotel Operations", "Hotel"),
    ("BU-FNB-1", "Mercure Food Hall", "F&B"),
    ("BU-FNB-2", "Mercure Dining Group", "F&B"),
]
DEPARTMENTS = [
    ("D001", "Rooms"), ("D002", "Food & Beverage"), ("D003", "Kitchen"),
    ("D004", "Engineering"), ("D005", "Sales & Marketing"),
    ("D006", "Administration"), ("D007", "Housekeeping"),
]
SEGMENTS = ["Leisure", "Corporate", "OTA", "Wholesale", "Group", "Wedding & Event"]
SEGMENT_WEIGHT = {"Leisure": 0.34, "Corporate": 0.22, "OTA": 0.20, "Wholesale": 0.10,
                  "Group": 0.08, "Wedding & Event": 0.06}
SEGMENT_CANX = {"Leisure": 0.06, "Corporate": 0.04, "OTA": 0.11, "Wholesale": 0.09,
                "Group": 0.07, "Wedding & Event": 0.08}
SEGMENT_NOSHOW = {"Leisure": 0.015, "Corporate": 0.008, "OTA": 0.025, "Wholesale": 0.02,
                  "Group": 0.01, "Wedding & Event": 0.012}
CHANNELS = ["Direct Website", "OTA", "Corporate", "GDS", "Walk-in", "WhatsApp"]
CHANNEL_WEIGHT = {"Direct Website": 0.28, "OTA": 0.30, "Corporate": 0.18, "GDS": 0.10,
                  "Walk-in": 0.06, "WhatsApp": 0.08}
ROOM_TYPES = [
    # id, name, price multiplier
    ("RT01", "Standard", 1.00), ("RT02", "Deluxe", 1.25), ("RT03", "Executive", 1.55),
    ("RT04", "Suite", 2.10), ("RT05", "Family", 1.40),
]
ROOM_TYPE_WEIGHT = [0.45, 0.25, 0.15, 0.05, 0.10]

# ---------------------------------------------------------------- F&B menu
MENU = [
    # (category, name, base_price Rp, unit_cost_ratio)
    ("Coffee", "Coffee Latte", 38000, 0.26),
    ("Coffee", "Cappuccino", 36000, 0.26),
    ("Coffee", "Espresso", 28000, 0.22),
    ("Coffee", "Americano", 30000, 0.20),
    ("Coffee", "Caramel Macchiato", 45000, 0.30),
    ("Coffee", "Cold Brew", 42000, 0.24),
    ("Tea", "Earl Grey Tea", 26000, 0.18),
    ("Tea", "Jasmine Tea", 24000, 0.16),
    ("Tea", "Lemon Honey Tea", 32000, 0.20),
    ("Tea", "Iced Thai Tea", 30000, 0.22),
    ("Breakfast", "Continental Breakfast", 85000, 0.32),
    ("Breakfast", "American Breakfast", 95000, 0.34),
    ("Breakfast", "Omelette", 55000, 0.30),
    ("Breakfast", "Pancake Stack", 62000, 0.31),
    ("Breakfast", "Croissant", 28000, 0.28),
    ("Appetizer", "Spring Rolls", 48000, 0.30),
    ("Appetizer", "Calamari", 65000, 0.34),
    ("Appetizer", "Garlic Bread", 38000, 0.25),
    ("Appetizer", "Caesar Salad", 58000, 0.29),
    ("Appetizer", "Soup of the Day", 45000, 0.24),
    ("Main Course", "Nasi Goreng Spesial", 78000, 0.30),
    ("Main Course", "Chicken Steak", 82000, 0.34),
    ("Main Course", "Beef Wellington", 165000, 0.38),
    ("Main Course", "Grilled Salmon", 145000, 0.36),
    ("Main Course", "Margherita Pizza", 88000, 0.31),
    ("Main Course", "Spaghetti Carbonara", 82000, 0.32),
    ("Main Course", "Ayam Bakar", 75000, 0.31),
    ("Main Course", "Sapi Lada Hitam", 115000, 0.36),
    ("Rice & Noodles", "Bakmie Goreng", 55000, 0.28),
    ("Rice & Noodles", "Kwetiau Siram", 58000, 0.29),
    ("Rice & Noodles", "Mie Ayam", 42000, 0.27),
    ("Rice & Noodles", "Nasi Putih", 18000, 0.20),
    ("Rice & Noodles", "Bubur Ayam", 38000, 0.26),
    ("Dessert", "Chocolate Lava Cake", 52000, 0.32),
    ("Rice & Noodles", "Es Campur", 35000, 0.24),
    ("Dessert", "Tiramisu", 58000, 0.33),
    ("Dessert", "Pannacotta", 52000, 0.30),
    ("Dessert", "Fresh Fruit Platter", 48000, 0.28),
    ("Beverage", "Orange Juice", 32000, 0.22),
    ("Beverage", "Mineral Water", 15000, 0.15),
    ("Beverage", "Soft Drink", 22000, 0.18),
    ("Beverage", "Es Teh Manis", 18000, 0.16),
    ("Beverage", "Beer", 45000, 0.30),
    ("Beverage", "Red Wine Glass", 85000, 0.35),
    ("Beverage", "Whisky", 120000, 0.38),
    ("Beverage", "Cocktail", 95000, 0.32),
    ("Beverage", "Mocktail", 68000, 0.26),
    ("Snack", "French Fries", 38000, 0.26),
    ("Snack", "Onion Rings", 42000, 0.28),
    ("Snack", "Chicken Wings", 55000, 0.30),
    ("Snack", "Nachos", 48000, 0.27),
    ("Snack", "Edamame", 35000, 0.22),
    ("Snack", "Pisang Goreng", 30000, 0.24),
    ("Snack", "Kroket", 28000, 0.25),
    ("Snack", "Risol", 25000, 0.24),
    ("Snack", "Dimsum", 42000, 0.28),
    ("Snack", "Roti Bakar", 32000, 0.23),
    ("Snack", "Kacang Rebus", 20000, 0.18),
]
CATEGORIES = ["Coffee", "Tea", "Breakfast", "Appetizer", "Main Course",
              "Rice & Noodles", "Dessert", "Beverage", "Snack"]

# outlets: (id, name, property_id, business_unit_id, type, daily covers base)
OUTLETS = [
    ("O01", "The Grand Table",      "H001", "BU-HOTEL", "All-Day Dining",   180),
    ("O02", "The Grand Table",      "H002", "BU-HOTEL", "All-Day Dining",   140),
    ("O03", "The Grand Table",      "H003", "BU-HOTEL", "All-Day Dining",   160),
    ("O04", "The Grand Table",      "H004", "BU-HOTEL", "All-Day Dining",   120),
    ("O05", "The Grand Table",      "H005", "BU-HOTEL", "All-Day Dining",   170),
    ("O06", "The Grand Table",      "H006", "BU-HOTEL", "All-Day Dining",    90),
    ("O07", "The Grand Table",      "H007", "BU-HOTEL", "All-Day Dining",    85),
    ("O08", "Senja Rooftop Bar",    "H001", "BU-HOTEL", "Rooftop Bar",       70),
    ("O09", "Lobby Lounge",         "H001", "BU-HOTEL", "Lobby Lounge",      95),
    ("O10", "Lobby Lounge",         "H003", "BU-HOTEL", "Lobby Lounge",      60),
    ("O11", "Dewi Dining",          "F001", "BU-FNB-1", "Specialty",        130),
    ("O12", "Food Hall Court",      "F001", "BU-FNB-1", "Food Hall",        220),
    ("O13", "Saffron Kitchen",      "F002", "BU-FNB-2", "Specialty",        110),
    ("O14", "City Bowl",            "F002", "BU-FNB-2", "Casual Dining",    150),
]
OUTLET_TYPE_MIX = {
    "All-Day Dining": {"Main Course": .28, "Rice & Noodles": .20, "Beverage": .16, "Coffee": .10,
                       "Breakfast": .08, "Appetizer": .06, "Dessert": .06, "Snack": .04, "Tea": .02},
    "Rooftop Bar":    {"Beverage": .42, "Snack": .22, "Main Course": .14, "Dessert": .08,
                       "Appetizer": .06, "Coffee": .04, "Tea": .02, "Breakfast": .01, "Rice & Noodles": .01},
    "Lobby Lounge":   {"Coffee": .32, "Tea": .16, "Dessert": .18, "Beverage": .14, "Snack": .10,
                       "Main Course": .05, "Appetizer": .02, "Breakfast": .02, "Rice & Noodles": .01},
    "Specialty":      {"Main Course": .40, "Appetizer": .16, "Dessert": .14, "Rice & Noodles": .10,
                       "Beverage": .10, "Coffee": .04, "Tea": .02, "Breakfast": .02, "Snack": .02},
    "Food Hall":      {"Rice & Noodles": .26, "Snack": .20, "Beverage": .16, "Main Course": .14,
                       "Coffee": .08, "Tea": .04, "Dessert": .06, "Breakfast": .04, "Appetizer": .02},
    "Casual Dining":  {"Main Course": .34, "Rice & Noodles": .18, "Beverage": .14, "Coffee": .10,
                       "Snack": .08, "Dessert": .08, "Appetizer": .04, "Tea": .02, "Breakfast": .02},
}
PAYMENT_METHODS = ["Cash", "Debit Card", "Credit Card", "QRIS", "GoPay", "OVO", "Bank Transfer"]
PAYMENT_WEIGHT = [0.18, 0.12, 0.20, 0.22, 0.10, 0.10, 0.08]
DISCOUNT_RATE = 0.045        # ~4.5% of gross as discount value
VOID_RATE = 0.012
REFUND_RATE = 0.008

# ---------------------------------------------------------------- finance
# (code, name, type, department_id)
ACCOUNTS = [
    ("4000", "Room Revenue",            "Revenue", "D001"),
    ("4001", "F&B Revenue",             "Revenue", "D002"),
    ("4002", "Other Income",            "Revenue", "D006"),
    ("4003", "Service Charge Income",   "Revenue", "D001"),
    ("4004", "Banquet & Event Revenue", "Revenue", "D002"),
    ("4005", "Minibar Revenue",         "Revenue", "D001"),
    ("4006", "Laundry Revenue",         "Revenue", "D007"),
    ("4007", "Spa & Wellness Revenue",  "Revenu",  "D001"),   # intentional invalid type
    ("5000", "Food Cost",               "COGS",    "D003"),
    ("5001", "Beverage Cost",           "COGS",    "D003"),
    ("5002", "Cleaning Supply Cost",    "COGS",    "D007"),
    ("5003", "Guest Amenities Cost",    "COGS",    "D001"),
    ("5004", "Laundry Operating Cost",  "COGS",    "D007"),
    ("5005", "Telecommunication Cost",  "COGS",    "D006"),
    ("6000", "Staff Salary",            "OPEX",    "D006"),
    ("6001", "Utility Expense",         "OPEX",    "D004"),
    ("6002", "Marketing Expense",       "OPEX",    "D005"),
    ("6003", "Maintenance Expense",     "OPEX",    "D004"),
    ("6004", "Insurance Expense",       "OPEX",    "D006"),
    ("6005", "Depreciation",            "OPEX",    "D006"),
    ("6006", "Office Supplies",         "OPEX",    "D006"),
    ("6007", "Professional Fees",       "OPES",    "D006"),   # intentional invalid type
    ("6008", "Travel Expense",          "OPEX",    "D005"),
    ("6009", "Training Expense",        "OPEX",    "D006"),
    ("6010", "Fuel Expense",            "OPEX",    "D004"),
    ("6011", "Security Expense",        "OPEX",    "D006"),
    ("6012", "Software & IT",           "OPEX",    "D006"),
    ("6013", "Bank Charges",            "OPEX",    "D006"),
    ("6014", "Permits & Licenses",      "OPEX",    "D006"),
    ("6015", "Waste Disposal",          "OPEX",    "D003"),
    ("6016", "Uniform Expense",         "OPEX",    "D007"),
    ("6017", "Distribution Expense",    "OPEX",    "D005"),
    ("6018", "Vehicle Expense",         "OPEX",    "D004"),
    ("6019", "Miscellaneous Expense",   "OPEX",    "D006"),
    ("6020", "Property Tax",            "OPEX",    "D006"),
    ("6021", "Repairs Expense",         "OPEX",    "D004"),
    ("6022", "Kitchen Fuel",            "OPEX",    "D003"),
]
ACCOUNT_TYPES = ["Revenue", "COGS", "OPEX"]
SUPPLIERS = [
    ("S001", "Sentosa Food Supply", "Jakarta", 2, 30),
    ("S002", "Maju Bersama Catering", "Jakarta", 3, 30),
    ("S003", "Segar Fresh Market", "Bandung", 2, 30),
    ("S004", "Nusantara Beverage", "Surabaya", 4, 30),
    ("S005", "Sumber Pangan Jaya", "Yogyakarta", 3, 30),
    ("S006", "Bali Fresh Seafood", "Denpasar", 2, 30),
    ("S007", "Karya Mandiri Supply", "Semarang", 4, 30),
    ("S008", "Sari Roti Bakery", "Malang", 2, 30),
    ("S00", "Inconsistent Supplier Code", "Jakarta", 3, 30),  # intentional malformed code
    ("S010", "Global Coffee Trader", "Jakarta", 5, 30),
    ("S011", "Petro Energy Fuel", "Jakarta", 7, 30),
    ("S012", "Clean Pro Supplies", "Bandung", 3, 30),
    ("S013", "Fresh Dairy Farm", "Surabaya", 2, 30),
    ("S014", "Asian Spice House", "Jakarta", 4, 30),
]
OPEX_TO_REVENUE = 0.34          # OPEX ~34% of revenue (excl. COGS) — management allocation model
OTHER_INCOME_TO_REV = 0.018
NET_PROFIT_FACTOR = 0.72        # EBITDA → Net Profit simplified (D&A, interest, tax)

# ---------------------------------------------------------------- inventory
REORDER_COVERAGE = 5            # days of demand held as reorder point
WASTE_RATE = 0.030
INFLATION_DRIFT_YEARLY = 0.055   # procurement cost inflation — drives food-cost trend

# ---------------------------------------------------------------- dirty data rates
P_NULL = 0.02                   # nulls on optional fields
P_DUP_TXN = 0.011               # duplicate transaction ids
P_NEG_QTY = 0.006               # negative quantity artifacts
P_INVALID_CODE = 0.004          # malformed codes
P_ORPHAN = 0.006                # orphan product/property references
P_BAD_DATE = 0.004              # impossible dates
P_UNKNOWN_PROPERTY = 0.004      # unknown property string
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y", "%Y%m%d"]
DECIMAL_STYLES = ["id", "en", "plain"]     # 1.234,56 / 1,234.56 / 1234.56

# ---------------------------------------------------------------- PoC scale
# Production design point: PMS 100k-250k, POS 500k-1.5M, Inventory 300k+, Proc 100k+, Fin 50k+.
POC_BOOKING_RATE = 0.55         # share of eligible arrivals materialised as bookings
POC_COVER_RATE = 0.42           # share of outlet covers materialised as POS lines
POC_INV_PROPERTY_RATE = 1.0     # inventory tracked at all hotel+F&B properties
POC_INV_PRODUCT_RATE = 0.30     # subset of menu SKUs tracked in inventory

# ---------------------------------------------------------------- KPI targets / tiers
DQ_TIER_BOUNDS = [(98.0, "A"), (95.0, "B"), (90.0, "C"), (0.0, "D")]
HEALTHY_FOOD_COST = 32.0
ANOMALY_Z = 3.0
ANOMALY_IQR = 1.5
ANOMALY_ROLLING_WINDOW = 28
BR_FOOD_COST = 40.0
BR_OCC_MAX = 100.0
BR_OCC_MIN = 20.0
BR_DISCOUNT = 20.0
BR_VOID = 5.0

# ---------------------------------------------------------------- palette (modern luxury hospitality)
NAVY = "#0B1F3A"; NAVY_2 = "#102A4C"; GOLD = "#C9A227"; GOLD_SOFT = "#E3C878"
WARM_WHITE = "#F7F4EE"; CHARCOAL = "#2A2A2A"; SOFT_GRAY = "#8A8F98"
GOOD = "#2E7D5B"; WARN = "#B98218"; BAD = "#B3402F"
FONT = "Inter, 'Segoe UI', Arial, sans-serif"

# ---------------------------------------------------------------- io helpers
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW_DIRS = {k: _os.path.join(_ROOT, "01_raw_data", k) for k in
            ["pms", "pos", "finance", "inventory", "procurement", "budget"]}
STG_DIR = _os.path.join(_ROOT, "02_staging")
CLN_DIR = _os.path.join(_ROOT, "03_cleaned_data")
MST_DIR = _os.path.join(_ROOT, "04_master_data")
DWH_DIR = _os.path.join(_ROOT, "06_data_warehouse")
EDA_DIR = _os.path.join(_ROOT, "08_eda")
FC_DIR = _os.path.join(_ROOT, "10_forecasting")
AD_DIR = _os.path.join(_ROOT, "11_anomaly_detection")
DASH_DIR = _os.path.join(_ROOT, "09_dashboard")
DOC_DIR = _os.path.join(_ROOT, "12_documentation")
DB_PATH = _os.path.join(DWH_DIR, "mercure.duckdb")


def daterange():
    d = START_DATE
    while d <= END_DATE:
        yield d
        d += timedelta(days=1)


def date_factors(d: date) -> float:
    """Demand multiplier for a date: DOW × month × long-weekend × year uplift."""
    f = DOW_FACTOR[d.weekday()] * MONTH_FACTOR[d.month] * YEAR_UPLIFT[d.year]
    for a, b in LONG_WEEKENDS:
        if a <= d <= b:
            f *= LONG_WEEKEND_BOOST
            break
    return f


def is_long_weekend(d: date) -> bool:
    for a, b in LONG_WEEKENDS:
        if a <= d <= b:
            return True
    return False


def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(SEED * 100003 + seed)
