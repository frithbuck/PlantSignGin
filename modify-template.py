from flask import Flask, request, jsonify, render_template, send_file
import csv
import os
import re
import mimetypes
import base64
import requests
import qrcode
from io import BytesIO
from urllib.parse import urlparse

app = Flask(__name__)

def qr_code_to_base64(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    data_uri = f"data:image/png;base64,{img_base64}"
    return data_uri

def is_image_url(url: str) -> bool:
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return False
    mime_type, _ = mimetypes.guess_type(url)
    return mime_type and mime_type.startswith('image/')

def url_to_data_uri(url: str) -> str:
    if not is_image_url(url):
        raise ValueError("The provided string is not a valid image URL.")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    mime_type = response.headers['Content-Type']
    image_data = base64.b64encode(response.content).decode('utf-8')
    return f"data:{mime_type};base64,{image_data}"

def findAndReplace(file_path, replacements):
    with open(file_path, 'r') as file:
        content = file.read()
    for key, value in replacements.items():
        content = content.replace(key, value)
    with open(file_path, 'w') as file:
        file.write(content)

def process_data(template_path, data, batch_dir):
    count = 0
    data[0] = ['~' + item for item in data[0]]
    for i in range(1, len(data)):
        i_name = re.sub(r'[^\w\-_.]', '_', data[i][0])
        i_dir = batch_dir
        if not os.path.exists(i_dir):
            os.makedirs(i_dir)
        html_file = os.path.join(i_dir, f"{i_name}.html")
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()
        with open(html_file, 'w') as working_file:
            working_file.write(template_content)
            count += 1
        replacements = {}
        for j in range(len(data[i])):
            if data[0][j] == "~QR_TARGET":
                try:
                    target = f"{data[i][j]}{i_name}.html"
                    qr = qr_code_to_base64(target)
                    data[i][j] = qr
                except Exception as e:
                    print(f"Error: QRCode: {e}")
            if is_image_url(data[i][j]):
                try:
                    data[i][j] = url_to_data_uri(data[i][j])
                except Exception as e:
                    print(f"Error: Image: {e}")
            replacements[data[0][j]] = data[i][j]
        findAndReplace(html_file, replacements)
    return f"Processed {count} files."

@app.route('/process', methods=['POST'])
def process_template():
    if 'template' not in request.files or 'data' not in request.files:
        return jsonify({"error": "Template or data file missing"}), 400

    template_file = request.files['template']
    data_file = request.files['data']

    template_path = os.path.join("templates", template_file.filename)
    template_file.save(template_path)

    data = []
    csv_file = csv.reader(data_file.stream)
    for row in csv_file:
        data.append(row)

    batch_dir = "output"
    os.makedirs(batch_dir, exist_ok=True)

    result = process_data(template_path, data, batch_dir)
    return jsonify({"message": result})

if __name__ == "__main__":
    app.run(debug=True)
