import sqlite3
import pandas as pd

# Load CSVs (headers are on row 5)
kayaks_df = pd.read_csv('Master - Rental Fleet - Kayaks.csv', header=4)
sups_df = pd.read_csv('Master - Rental Fleet - SUPs.csv', header=4)

# Add 'type' column
kayaks_df['type'] = 'Kayak'
sups_df['type'] = 'SUP'

# Combine
fleet_df = pd.concat([kayaks_df, sups_df], ignore_index=True)

# Rename columns to match your DB schema
fleet_df = fleet_df.rename(columns={
    'Boat #': 'boat_id',
    'Serial #': 'serial_number',
    'Brand': 'brand',
    'Model': 'model',
    'Primary Color': 'primary_color',
    'Added to Fleet': 'added_to_fleet'
})

# Select only the needed columns
fleet_df = fleet_df[['boat_id', 'serial_number', 'type', 'brand', 'model', 'primary_color', 'added_to_fleet']]
fleet_df['status'] = 'Active'  # Default status for all boats

# Connect to SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fleet (
        boat_id TEXT PRIMARY KEY,
        serial_number TEXT,
        type TEXT,
        brand TEXT,
        model TEXT,
        primary_color TEXT,
        added_to_fleet TEXT,
        status TEXT DEFAULT 'Active'
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS damage_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boat_id TEXT,
        description TEXT,
        reported_by TEXT,
        date_reported TEXT
    )
''')

# Insert data
cursor.executemany('''
    INSERT OR REPLACE INTO fleet 
    (boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', fleet_df.values.tolist())

conn.commit()
conn.close()

print("✅ Database initialized with correct columns.")
