from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def report_form():
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    description = request.form['description']
    reported_by = request.form['reported_by']
    date_reported = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert damage report
    cursor.execute('''
        INSERT INTO damage_reports (boat_id, description, reported_by, date_reported)
        VALUES (?, ?, ?, ?)
    ''', (boat_id, description, reported_by, date_reported))

    # Update fleet status to Damaged
    cursor.execute('''
        UPDATE fleet SET status = 'Damaged' WHERE boat_id = ?
    ''', (boat_id,))
    conn.commit()
    conn.close()
    return "✅ Damage report submitted successfully!"

@app.route('/fleet')
def fleet():
    boat_type_filter = request.args.get('type')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if boat_type_filter:
        cursor.execute('''
            SELECT boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status 
            FROM fleet
            WHERE type = ?
        ''', (boat_type_filter,))
    else:
        cursor.execute('''
            SELECT boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status 
            FROM fleet
        ''')

    fleet_data = cursor.fetchall()

    # Get distinct types for dropdown filter
    cursor.execute('SELECT DISTINCT type FROM fleet')
    types = [row[0] for row in cursor.fetchall()]

    conn.close()
    return render_template('fleet.html', fleet=fleet_data, types=types)

@app.route('/delete-mode')
def delete_mode():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status 
        FROM fleet
    ''')
    fleet_data = cursor.fetchall()
    conn.close()
    return render_template('delete_mode.html', fleet=fleet_data)


@app.route('/fix/<boat_id>', methods=['POST', 'GET'])
def mark_fixed(boat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE fleet SET status = 'Active' WHERE boat_id = ?", (boat_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('fleet'))

@app.route('/add', methods=['GET', 'POST'])
def add_boat():
    if request.method == 'POST':
        boat_data = (
            request.form['boat_id'],
            request.form['serial_number'],
            classify_type(request.form['type'], request.form['model']),
            request.form['brand'],
            request.form['model'],
            request.form['primary_color'],
            request.form['added_to_fleet'],
            request.form['status']
        )
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fleet (boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', boat_data)
        conn.commit()
        conn.close()
        return redirect(url_for('fleet'))
    return render_template('add_boat.html')

@app.route('/update/<boat_id>', methods=['GET', 'POST'])
def update_boat(boat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        updated_type = classify_type(request.form['type'], request.form['model'])
        cursor.execute('''
            UPDATE fleet
            SET serial_number = ?, type = ?, brand = ?, model = ?, primary_color = ?, added_to_fleet = ?, status = ?
            WHERE boat_id = ?
        ''', (
            request.form['serial_number'],
            updated_type,
            request.form['brand'],
            request.form['model'],
            request.form['primary_color'],
            request.form['added_to_fleet'],
            request.form['status'],
            boat_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('fleet'))

    cursor.execute("SELECT * FROM fleet WHERE boat_id = ?", (boat_id,))
    boat = cursor.fetchone()
    conn.close()
    return render_template('update_boat.html', boat=boat)

@app.route('/delete/<boat_id>', methods=['POST'])
def delete_boat(boat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fleet WHERE boat_id = ?", (boat_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('fleet'))

def classify_type(type_val, model):
    model_lower = model.lower()
    if "tandem" in model_lower or "double" in model_lower or "2-person" in model_lower:
        return "Double Kayak" if type_val.lower() == "kayak" else type_val
    if type_val.lower() == "kayak":
        return "Single Kayak"
    return type_val  # For SUPs or other types

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
