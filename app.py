from flask import Flask, render_template, request
import os
import sqlite3

app = Flask(__name__)

# --- Auto-create damage_reports table if not exists ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS damage_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT,
            description TEXT,
            reported_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# --- Ensure fleet table has a 'status' column ---
def ensure_status_column():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE fleet ADD COLUMN status TEXT DEFAULT "Active"')
        print("✅ 'status' column added to fleet table")
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

# Run setup on startup
init_db()
ensure_status_column()

# --- Routes ---
@app.route('/test')
def test():
    return "✅ Flask is working"

@app.route('/')
def index():
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    description = request.form['description']
    reported_by = request.form['reported_by']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert into damage_reports
    cursor.execute('''
        INSERT INTO damage_reports (boat_id, description, reported_by)
        VALUES (?, ?, ?)
    ''', (boat_id, description, reported_by))

    # Update fleet status
    cursor.execute('''
        UPDATE fleet
        SET status = 'Broken'
        WHERE "Boat ID" = ?
    ''', (boat_id,))

    conn.commit()
    conn.close()

    return "✅ Damage report submitted and boat marked as Broken!"

@app.route('/reports')
def reports():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT boat_id, description, reported_by, timestamp
        FROM damage_reports
        ORDER BY timestamp DESC
    ''')
    reports = cursor.fetchall()
    conn.close()
    return render_template('reports.html', reports=reports)

@app.route('/fleet')
def fleet():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "Boat ID", "Serial Number", status
        FROM fleet
        ORDER BY "Boat ID"
    ''')
    boats = cursor.fetchall()
    conn.close()
    return render_template('fleet.html', boats=boats)

# --- App runner ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
