#!/usr/bin/env python3

from flask import Flask, request, render_template_string
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define the home route
@app.route('/', methods=['GET'])
def index():
    # Simple HTML form as a string
    webform_html = open('PlantSignGinWebform.html').read()
    return render_template_string(webform_html)

# Define the processing route
@app.route('/process', methods=['POST'])
def process_files():
    if 'template' not in request.files or 'data' not in request.files:
        return 'No files uploaded.'

    template_file = request.files['template']
    data_file = request.files['data']
    output_dir = request.form['output']

    # Save the files to the upload folder
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_file.filename)
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], data_file.filename)

    template_file.save(template_path)
    data_file.save(data_path)

    # Run the provided Python script with arguments
    script_path = 'modify-template.py'  # Replace with the path to your script
    subprocess.run(['python3', script_path, template_path, data_path, output_dir])

    return f"Processing completed. Files saved to {output_dir}."

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
