"""v3 parameters — Mercure Group Data Intelligence Demo."""
import os
from pathlib import Path
from datetime import date, timedelta

BASE = Path(__file__).resolve().parent.parent

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)
FC_START = date(2026, 1, 1)
FC_END = date(2026, 3, 31)

RAW_DIR = str(BASE / "01_raw")
MST_DIR = str(BASE / "03_master")
STG_DIR = str(BASE / "02_staging")
DWH_DIR = str(BASE / "05_warehouse")
SQL_DIR = str(BASE / "06_sql")
FC_DIR = str(BASE / "08_forecast")
AD_DIR = str(BASE / "09_anomaly")
DASH_DIR = str(BASE / "07_dashboard_data")
DB_PATH = str(BASE / "05_warehouse" / "mercure_v3.duckdb")

PROPERTIES = [
    ("P001", "Mercure Jakarta Gatot Subroto", "Jakarta", "Java", 245, "4-star"),
    ("P002", "Mercure Bandung City Centre", "Bandung", "Java", 180, "4-star"),
    ("P003", "Mercure Surabaya", "Surabaya", "Java", 210, "4-star"),
    ("P004", "Mercure Bali Legian", "Legian", "Bali", 150, "4-star"),
    ("P005", "Mercure Makassar", "Makassar", "Sulawesi", 120, "4-star"),
]

FNB_UNITS = [
    ("F001", "The Gato - Jakarta", "Jakarta", "Java"),
    ("F002", "Gacoan Bandung", "Bandung", "Java"),
    ("F003", "Gacoan Surabaya", "Surabaya", "Java"),
    ("F004", "Gacoan Bali", "Legian", "Bali"),
]

OUTLETS = [
    ("O001", "The Gato - Jakarta", "P001", "restaurant", "F&B"),
    ("O002", "Gacoan Bandung", "P002", "restaurant", "F&B"),
    ("O003", "Gacoan Surabaya", "P003", "restaurant", "F&B"),
    ("O004", "Gacoan Bali", "P004", "restaurant", "F&B"),
    ("O005", "Pool Bar Bali", "P004", "bar", "F&B"),
    ("O006", "Sky Lounge Jakarta", "P001", "bar", "F&B"),
]

ROOM_TYPES = [
    ("RT01", "Standard"),
    ("RT02", "Superior"),
    ("RT03", "Deluxe"),
    ("RT04", "Suite"),
    ("RT05", "Executive"),
]

SEGMENTS = ["Corporate", "Leisure", "Wedding & Event", "Group", "OTA", "Wholesale", "Government"]
CHANNELS = ["Direct Website", "Traveloka", "Booking.com", "Agoda", "OTA Other", "Corporate Direct", "Walk-in", "Phone", "Agent"]

CATEGORIES = ["Food", "Beverage", "Dessert", "Snack", "Alcohol", "Merchandise"]

MENU = [
    ("Food", "Mie Ayam", "bowl", 1.0, 32000),
    ("Food", "Mie Yamin", "bowl", 1.0, 34000),
    ("Food", "Pangsit Goreng", "portion", 0.8, 18000),
    ("Food", "Siomay", "portion", 0.8, 16000),
    ("Beverage", "Ice Tea", "glass", 1.0, 12000),
    ("Beverage", "Lemon Tea", "glass", 1.0, 15000),
    ("Dessert", "Sundae", "cup", 1.0, 25000),
    ("Snack", "Keripik", "pack", 1.0, 10000),
]

DEPARTMENTS = [
    ("D01", "Rooms"),
    ("D02", "F&B"),
    ("D03", "Sales & Marketing"),
    ("D04", "Engineering"),
    ("D05", "HR & Training"),
    ("D06", "Finance & Accounting"),
    ("D07", "Procurement"),
]

ACCOUNTS = [
    ("4100", "Room Revenue", "Revenue", "D01"),
    ("4200", "F&B Revenue", "Revenue", "D02"),
    ("5000", "Food Cost", "COGS", "D02"),
    ("5100", "Beverage Cost", "COGS", "D02"),
    ("6100", "Payroll", "Operating Expense", "D05"),
    ("6200", "Utilities", "Operating Expense", "D04"),
    ("6300", "Marketing", "Operating Expense", "D03"),
    ("6400", "Maintenance", "Operating Expense", "D04"),
    ("6500", "Administrative", "Operating Expense", "D06"),
    ("6600", "Rent & Leasing", "Operating Expense", "D06"),
]

DOW_FACTOR = {0: 0.92, 1: 0.93, 2: 0.95, 3: 1.00, 4: 1.05, 5: 1.12, 6: 1.10}
MONTH_FACTOR = {1: 1.0, 2: 1.0, 3: 1.02, 4: 1.02, 5: 1.05, 6: 1.0, 7: 0.98, 8: 1.0, 9: 1.03, 10: 1.05, 11: 1.08, 12: 1.15}
YEAR_UPLIFT = {2024: 1.0, 2025: 1.08, 2026: 1.12}
HOLIDAYS = {date(2025, 1, 1), date(2025, 4, 18), date(2025, 5, 1), date(2025, 6, 6), date(2025, 12, 25), date(2026, 1, 1), date(2026, 3, 11), date(2026, 3, 29)}
HEALTHY_FOOD_COST = 28
