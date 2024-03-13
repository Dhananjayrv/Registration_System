import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import csv
import random

app = Flask(__name__, template_folder='templates')

# Set the path for the uploaded profile pictures
UPLOAD_FOLDER = 'profile_pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Load CSV database
def load_database():
    with open('Sample data.csv', 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Save OTP to CSV
def save_otp_to_csv(phone_number, otp):
    database = load_database()
    entry_updated = False

    for entry in database:
        if entry['Member Mobile Number'] == phone_number:
            entry['otp'] = otp
            entry_updated = True
            break

    with open('Sample data.csv', 'w', newline='') as file:
        fieldnames = ['Sr.No.', 'District Number', 'Member Name', 'Member Mobile Number', 'Email ID', 'Remark if any', 'otp']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(database)

        if not entry_updated:
            entry = {
                'Sr.No.': '',  # You might need to adjust this based on your actual data structure
                'District Number': '',
                'Member Name': '',
                'Member Mobile Number': phone_number,
                'Email ID': '',
                'Remark if any': '',
                'otp': otp
            }
            writer.writerow(entry)

# Save profile picture to the specified folder
def save_profile_picture(file, name):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{name}_{filename}"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['Member Name']
        phone_number = request.form['Member Mobile Number']
        otp = generate_otp()

        # Save OTP to CSV
        save_otp_to_csv(phone_number, otp)

        # Save profile picture
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                save_profile_picture(file, name)

        # Pass both phone_number and name to otp.html for reference
        return render_template('otp.html', phone_number=phone_number, name_from_form=name)

@app.route('/verify', methods=['POST'])
def verify():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        entered_otp = request.form['otp']

        # Verify OTP
        database = load_database()
        for entry in database:
            if entry['Member Mobile Number'] == phone_number and entry['otp'] == entered_otp:
                return render_template('success.html')
        return render_template('failure.html')

# Add an endpoint to fetch name details
@app.route('/get_details', methods=['GET'])
def get_details():
    name = request.args.get('name', '').lower()
    database = load_database()
    details = next((entry for entry in database if entry['Member Name'].lower() == name), None)
    return jsonify(details)

# Add an endpoint to fetch name suggestions
@app.route('/get_names', methods=['GET'])
def get_names():
    prefix = request.args.get('prefix', '').lower()
    database = load_database()
    suggestions = [entry['Member Name'] for entry in database if entry['Member Name'].lower().startswith(prefix)]
    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    app.run(debug=True)
