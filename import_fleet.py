import sqlite3
import pandas as pd

def classify_type(type_val, model):
    model = str(model).lower().strip() if not pd.isna(model) else ''
    type_val = str(type_val).lower().strip()

    if "tandem" in model or "double" in model or "2-person" in model:
        return "Double"
    if type_val == "kayak":
        return "Single"
    if type_val == "sup":
        return "SUP"
    return type_val.capitalize()

# Load CSVs (headers start on row 5)
kayaks_df = pd.read_csv('Master - Rental Fleet - Kayaks.csv', header=4)
sups_df = pd.read_csv('Master - Rental Fleet - SUPs.csv', header=4)

# Add and normalize 'type' column
kayaks_df['type'] = kayaks_df['Type']
sups_df['type'] = sups_df['Type']

# Combine
fleet_df = pd.concat([kayaks_df, sups_df], ignore_index=True)

# Rename columns
fleet_df = fleet_df.rename(columns={
    'Boat #': 'boat_id',
    'Serial #': 'serial_number',
    'Brand': 'brand',
    'Model': 'model',
    'Primary Color': 'primary_color',
    'Added to Fleet': 'added_to_fleet'
})

# Select only needed columns
fleet_df = fleet_df[['boat_id', 'serial_number', 'type', 'brand', 'model', 'primary_color', 'added_to_fleet']]
fleet_df['status'] = 'Active'

# Normalize types
fleet_df['type'] = fleet_df.apply(lambda row: classify_type(row['type'], row['model']), axis=1)

# Preview
print("✅ Preview of fleet data to be inserted:")
print(fleet_df.head(10))

# Connect to DB
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create fleet table with composite uniqueness and new ID PK
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fleet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boat_id TEXT,
        serial_number TEXT,
        type TEXT,
        brand TEXT,
        model TEXT,
        primary_color TEXT,
        added_to_fleet TEXT,
        status TEXT DEFAULT 'Active',
        UNIQUE(boat_id, type)
    )
''')

# Create damage_reports table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS damage_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boat_id TEXT,
        description TEXT,
        reported_by TEXT,
        date_reported TEXT
    )
''')

# Optional: Clear and reload fleet table
cursor.execute('DELETE FROM fleet')

# Insert while handling uniqueness
inserted = 0
skipped = 0
for _, row in fleet_df.iterrows():
    try:
        cursor.execute('''
            INSERT INTO fleet (boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['boat_id'], row['serial_number'], row['type'], row['brand'],
            row['model'], row['primary_color'], row['added_to_fleet'], row['status']
        ))
        inserted += 1
    except sqlite3.IntegrityError:
        skipped += 1
        print(f"⚠️ Skipped duplicate: {row['type']} {row['boat_id']}")

conn.commit()
conn.close()

print(f"✅ Database updated. {inserted} boats inserted, {skipped} skipped.")
