import sqlite3
import pandas as pd

# === Load CSVs ===
kayaks = pd.read_csv("Master - Rental Fleet - Kayaks.csv")
sups = pd.read_csv("Master - Rental Fleet - SUPs.csv")

# === Tag each type ===
kayaks["Category"] = "Kayak"
sups["Category"] = "SUP"

# === Combine the two ===
fleet = pd.concat([kayaks, sups])
fleet.reset_index(drop=True, inplace=True)

# === Add a status column ===
fleet["status"] = "Active"

# === Connect to SQLite and create database ===
conn = sqlite3.connect("database.db")

# === Save the fleet table ===
fleet.to_sql("fleet", conn, if_exists="replace", index=False)

# === Create damage_reports table if it doesn't exist ===
conn.execute("""
    CREATE TABLE IF NOT EXISTS damage_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boat_id TEXT,
        description TEXT,
        reported_by TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()

print("✅ Database initialized with fleet and damage_reports tables.")
