import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 💥 Drop fleet_old if it already exists
cursor.execute("DROP TABLE IF EXISTS fleet_old")

# 🔁 Rename original fleet table
cursor.execute("ALTER TABLE fleet RENAME TO fleet_old")

# 🆕 Create the new fleet table with composite primary key
cursor.execute('''
    CREATE TABLE fleet (
        boat_id TEXT NOT NULL,
        type TEXT NOT NULL,
        serial_number TEXT,
        brand TEXT,
        model TEXT,
        primary_color TEXT,
        added_to_fleet TEXT,
        status TEXT,
        PRIMARY KEY (boat_id, type)
    )
''')

# ⛔ Skip rows with NULL boat_id or type
cursor.execute('''
    INSERT INTO fleet (boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status)
    SELECT boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status 
    FROM fleet_old
    WHERE boat_id IS NOT NULL AND type IS NOT NULL
''')

# 🧹 Drop the backup table (optional if you're done with it)
# cursor.execute("DROP TABLE fleet_old")

conn.commit()
conn.close()

print("✅ Migration complete. Invalid rows were skipped.")
