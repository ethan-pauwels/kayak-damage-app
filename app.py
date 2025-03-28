from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
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
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    description = request.form['description']
    reported_by = request.form['reported_by']
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO broken_boats (boat_id, description, reported_by, report_time) VALUES (?, ?, ?, ?)",
              (boat_id, description, reported_by, report_time))
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
