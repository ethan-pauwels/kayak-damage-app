from flask import Flask, render_template, request, redirect
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Route: health check
@app.route('/test')
def test():
    return "✅ Flask is working"

# Route: redirect root to /run
@app.route('/')
def index():
    return redirect('/run')

# Route: show the damage report form
@app.route('/run')
def run_page():
    return render_template('report.html')

# Route: handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form.get('boat_id')
    description = request.form.get('description')
    reported_by = request.form.get('reported_by')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save to SQLite database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boat_id TEXT,
                    description TEXT,
                    reported_by TEXT,
                    timestamp TEXT
                )''')
    c.execute('INSERT INTO reports (boat_id, description, reported_by, timestamp) VALUES (?, ?, ?, ?)',
              (boat_id, description, reported_by, timestamp))
    conn.commit()
    conn.close()

    return "🛶 Damage report submitted! Thank you."

# Run the app on Render (port must come from environment)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
