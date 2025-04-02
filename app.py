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
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT boat_id, serial_number, type, brand, model, primary_color, added_to_fleet, status FROM fleet
    ''')
    boats = cursor.fetchall()
    conn.close()
    return render_template('fleet.html', boats=boats)

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
            request.form['type'],
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
        cursor.execute('''
            UPDATE fleet
            SET serial_number = ?, type = ?, brand = ?, model = ?, primary_color = ?, added_to_fleet = ?, status = ?
            WHERE boat_id = ?
        ''', (
            request.form['serial_number'],
            request.form['type'],
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

@app.route('/delete/<boat_id>', methods=['GET'])
def delete_boat(boat_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fleet WHERE boat_id = ?", (boat_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('fleet'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
