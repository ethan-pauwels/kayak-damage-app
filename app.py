from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    description = request.form['description']
    reported_by = request.form['reported_by']
    date_reported = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert damage report
    cursor.execute('''
        INSERT INTO damage_reports (boat_id, description, reported_by, date_reported)
        VALUES (?, ?, ?, ?)
    ''', (boat_id, description, reported_by, date_reported))

    # Update status of the boat in the fleet
    cursor.execute('''
        UPDATE fleet
        SET status = 'Damaged'
        WHERE boat_id = ?
    ''', (boat_id,))

    conn.commit()
    conn.close()

    return "✅ Damage report submitted successfully!"

@app.route('/fleet')
def fleet():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            boat_id, 
            serial_number, 
            type, 
            brand, 
            model, 
            primary_color, 
            added_to_fleet, 
            status 
        FROM fleet
    ''')
    rows = cursor.fetchall()
    conn.close()

    fleet_data = [{
        'boat_id': row[0],
        'serial_number': row[1],
        'type': row[2],
        'brand': row[3],
        'model': row[4],
        'primary_color': row[5],
        'added_to_fleet': row[6],
        'status': row[7]
    } for row in rows]

    return render_template('fleet.html', fleet=fleet_data)

if __name__ == '__main__':
    app.run(debug=True)
