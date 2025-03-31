from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('report.html')

@app.route('/submit', methods=['POST'])
def submit():
    boat_id = request.form.get('boat_id')
    description = request.form.get('description')
    reported_by = request.form.get('reported_by')

    return f"Received report for boat {boat_id} from {reported_by}: {description}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
