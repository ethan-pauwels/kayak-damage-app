from flask import Flask, render_template, request
import os
import sqlite3

app = Flask(__name__)

# --- Auto-create DB table if not exists ---
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

# Initialize the DB when the app starts
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

    # Save report to database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO damage_reports (boat_id, description, reported_by)
        VALUES (?, ?, ?)
    ''', (boat_id, description, reported_by))
    conn.commit()
    conn.close()

    return "✅ Damage report submitted successfully!"

# Run app on Render's assigned port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
