import sqlite3
import pandas as pd

# Load CSVs (headers are on row 5, which is index 4)
kayaks_df = pd.read_csv('Master - Rental Fleet - Kayaks.csv', header=4)
sups_df = pd.read_csv('Master - Rental Fleet - SUPs.csv', header=4)

# Add 'type' column
def classify_kayak_type(model):
    if isinstance(model, str) and "Double" in model:
        return "Double Kayak"
    return "Single Kayak"

kayaks_df['type'] = kayaks_df['Model'].apply(classify_kayak_type)
sups_df['type'] = 'SUP'  # All SUPs are just SUPs

# Combine the two DataFrames
fleet_df = pd.concat([kayaks_df, sups_df], ignore_index=True)

# Rename columns to match database schema
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

# Print the DataFrame to verify it's loaded correctly
print("✅ Preview of fleet data to be inserted:")
print(fleet_df.head())

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

# Optional: clear existing fleet data to avoid duplicates
cursor.execute('DELETE FROM fleet')

# Insert fleet data
cursor.executemany('''
    INSERT OR REPLACE INTO fleet 
    (boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', fleet_df.values.tolist())

# Finalize
conn.commit()
conn.close()

print("✅ Database initialized with correct columns and fresh fleet data.")
