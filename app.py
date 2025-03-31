from flask import Flask, render_template, request, redirect
import os
import sqlite3

app = Flask(__name__)

# Route: Health check
@app.route('/test')
def test():
    return "✅ Flask is working"

# Route: Damage report form
@app.route('/')
def index():
    return render_template('report.html')

# Route: Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form['boat_id']
    description = request.form['description']
    reported_by = request.form['reported_by']

    # Insert the damage report into the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO damage_reports (boat_id, description, reported_by)
        VALUES (?, ?, ?)
    ''', (boat_id, description, reported_by))
    conn.commit()
    conn.close()

    return "✅ Damage report submitted successfully!"

# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
