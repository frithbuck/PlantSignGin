#!/usr/bin/env python3

from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


    @app.route('/', methods=['GET'])
    def index():
        # Render the form for uploading files
        return render_template_string(open('PlantSignGinWebform.html').read())


    @app.route('/process', methods=['POST'])
    def process_files():
        # Check if files are present
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
        script_path = 'modify-template.py'  # Replace with your script path
        subprocess.run(['python3', script_path, template_path, data_path, output_dir])

        return f"Processing completed. Files saved to {output_dir}."


    if __name__ == '__main__':
        app.run(debug=True)
