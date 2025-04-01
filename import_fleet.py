import sqlite3
import pandas as pd

# Load data starting from row 5 (zero-indexed, so skip first 4)
kayaks_df = pd.read_csv("Master - Rental Fleet - Kayaks.csv", skiprows=4)
sups_df = pd.read_csv("Master - Rental Fleet - SUPs.csv", skiprows=4)

# Add status column to both and set to Active
kayaks_df["status"] = "Active"
sups_df["status"] = "Active"

# Add a column to indicate the type
kayaks_df["type"] = "Kayak"
sups_df["type"] = "SUP"

# Rename columns to match what we expect in the app
kayaks_df.rename(columns={
    "Boat #": "boat_id",
    "Serial #": "serial_number"
}, inplace=True)

sups_df.rename(columns={
    "Boat #": "boat_id",
    "Serial #": "serial_number"
}, inplace=True)

# Keep only the relevant columns
kayaks_df = kayaks_df[["boat_id", "serial_number", "type", "status"]]
sups_df = sups_df[["boat_id", "serial_number", "type", "status"]]

# Combine both fleets
fleet_df = pd.concat([kayaks_df, sups_df])

# Save to SQLite database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Reset the fleet table
cursor.execute("DROP TABLE IF EXISTS fleet")
cursor.execute("""
    CREATE TABLE fleet (
        boat_id TEXT,
        serial_number TEXT,
        type TEXT,
        status TEXT
    )
""")

# Save data
fleet_df.to_sql("fleet", conn, if_exists="append", index=False)

# Create the damage_reports table if not exists
cursor.execute("""
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
