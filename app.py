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

init_db()

# Route: Health check
@app.route('/test')
def test():
    return "✅ Flask is working"

# Route: Show damage report form
@app.route('/')
def index():
    return render_template('report.html')

# Route: Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    description = request.form['description']
    reported_by = request.form['reported_by']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert damage report into table
    cursor.execute('''
        INSERT INTO damage_reports (boat_id, description, reported_by)
        VALUES (?, ?, ?)
    ''', (boat_id, description, reported_by))

    # Mark the boat as Broken in the fleet table
    cursor.execute('''
        UPDATE fleet
        SET status = 'Broken'
        WHERE "Boat ID" = ?
    ''', (boat_id,))

    conn.commit()
    conn.close()

    return "✅ Damage report submitted and boat marked as Broken!"

# Route: View all damage reports
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

# Route: View the full fleet with status
@app.route('/fleet')
def fleet():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "Boat ID", "Serial Number", Category, status
        FROM fleet
        ORDER BY Category, "Boat ID"
    ''')
    boats = cursor.fetchall()
    conn.close()
    return render_template('fleet.html', boats=boats)

# Run app (Render uses PORT env var)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
