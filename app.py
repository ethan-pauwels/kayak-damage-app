from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB = 'database.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Create fleet table if needed
    c.execute('''
        CREATE TABLE IF NOT EXISTS fleet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_number TEXT,
            serial_number TEXT,
            type TEXT,
            brand TEXT,
            model TEXT,
            primary_color TEXT,
            added_to_fleet TEXT,
            in_current_fleet TEXT,
            date_removed TEXT,
            notes TEXT
        )
    ''')

    # Create damage reports table
    c.execute('''
        CREATE TABLE IF NOT EXISTS broken_boats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boat_id TEXT NOT NULL,
            description TEXT,
            reported_by TEXT,
            report_time TEXT,
            status TEXT DEFAULT 'Broken'
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect('/run')


# ✅ Main route — renders report.html
@app.route('/run')
def index():
    print("💡 Flask is serving the index route")  # Debug print
    return render_template('report.html')

# ✅ POST route to handle submissions
@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    description = request.form['description']
    reported_by = request.form['reported_by']
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO broken_boats (boat_id, description, reported_by, report_time) VALUES (?, ?, ?, ?)",
              (boat_id, description, reported_by, report_time))
    conn.commit()
    conn.close()

    return redirect('/')

# ✅ Test route to confirm Flask is working
@app.route('/test')
def test():
    return "Flask is working 🎉"

# ✅ Start the Flask server on 0.0.0.0 with Render's PORT
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
