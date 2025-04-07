from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import pandas as pd
import zipfile
import io

app = Flask(__name__)

def normalize_type(full_type):
    if full_type == "Single Kayak":
        return "Single"
    elif full_type == "Double Kayak":
        return "Double"
    return full_type

@app.route('/')
def report_form():
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    boat_type_raw = request.form['boat_type']
    boat_type = normalize_type(boat_type_raw)
    description = request.form['description']
    reported_by = request.form['reported_by']
    date_reported = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO damage_reports (boat_id, description, reported_by, date_reported)
        VALUES (?, ?, ?, ?)
    ''', (f"{boat_type_raw} {boat_id}", description, reported_by, date_reported))

    cursor.execute('''
        UPDATE fleet SET status = 'Damaged' WHERE boat_id = ? AND type = ?
    ''', (boat_id, boat_type))

    conn.commit()
    conn.close()
    return "✅ Damage report submitted successfully!"

@app.route('/fleet')
def fleet():
    boat_type_filter = request.args.get('type')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if boat_type_filter:
        normalized_type = normalize_type(boat_type_filter)
        cursor.execute('''
            SELECT boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status 
            FROM fleet
            WHERE type = ?
        ''', (normalized_type,))
    else:
        cursor.execute('''
            SELECT boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status 
            FROM fleet
        ''')

    fleet_data = cursor.fetchall()
    cursor.execute('SELECT DISTINCT type FROM fleet')
    types = [row[0] for row in cursor.fetchall()]
    conn.close()

    return render_template('fleet.html', fleet=fleet_data, types=types)

@app.route('/reports')
def view_reports():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, boat_id, description, reported_by, date_reported
        FROM damage_reports
        ORDER BY date_reported DESC
    ''')
    reports = cursor.fetchall()
    conn.close()
    return render_template('reports.html', reports=reports)

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
        raw_type = request.form['type']
        model = request.form['model']
        boat_data = (
            request.form['boat_id'],
            request.form['serial_number'],
            classify_type(raw_type, model),
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
        raw_type = request.form['type']
        model = request.form['model']
        updated_type = classify_type(raw_type, model)
        cursor.execute('''
            UPDATE fleet
            SET serial_number = ?, type = ?, brand = ?, model = ?, primary_color = ?, added_to_fleet = ?, status = ?
            WHERE boat_id = ?
        ''', (
            request.form['serial_number'],
            updated_type,
            request.form['brand'],
            model,
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

@app.route('/export')
def export_data():
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        conn = sqlite3.connect('database.db')
        
        # Export fleet
        fleet_df = pd.read_sql_query("SELECT * FROM fleet", conn)
        fleet_csv = fleet_df.to_csv(index=False)
        zip_file.writestr(f"fleet_export_{now}.csv", fleet_csv)
        
        # Export damage reports
        report_df = pd.read_sql_query("SELECT * FROM damage_reports", conn)
        report_csv = report_df.to_csv(index=False)
        zip_file.writestr(f"damage_reports_export_{now}.csv", report_csv)

        conn.close()

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip',
                     download_name=f"fleet_exports_{now}.zip", as_attachment=True)

def classify_type(type_val, model):
    model_lower = model.lower()
    if "tandem" in model_lower or "double" in model_lower or "2-person" in model_lower:
        return "Double"
    if type_val.lower() == "kayak":
        return "Single"
    return type_val

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
