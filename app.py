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
