import csv
import pandas as pd
import os
import re
import json
import mimetypes
import base64
import requests
import qrcode
from io import BytesIO
from urllib.parse import urlparse

CUSTOM_TARGETS = {
    'qr': '[QR_TARGET]'
}


def qr_code_to_base64(url):
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )

    # Add the URL data to the QR code
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image of the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Save the image to a BytesIO buffer
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    # Encode image to base64
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Create the Data URI scheme
    data_uri = f"data:image/png;base64,{img_base64}"

    return data_uri


def is_image_url(url: str) -> bool:
    # Parse the URL and check if it's a valid URL
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return False

    # Guess the MIME type based on the file extension
    mime_type, _ = mimetypes.guess_type(url)
    if mime_type and mime_type.startswith('image/'):
        return True
    return False

def url_to_data_uri(url: str) -> str:
    if not is_image_url(url):
        raise ValueError("The provided string is not a valid image URL.")

    # Custom headers including User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # Fetch the image from the URL with the custom User-Agent
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Get the MIME type and encode the image data to base64
    mime_type = response.headers['Content-Type']
    image_data = base64.b64encode(response.content).decode('utf-8')

    # Return the data URI
    return f"data:{mime_type};base64,{image_data}"

def findAndReplace(file_path, replacements):
    with open(file_path, 'r') as file:
        content = file.read()

    for key, value in replacements.items():
        content = content.replace(key, value)

    with open(file_path, 'w') as file:
        file.write(content)

def main(template_path, data_path, batch_dir):
    # Read data from CSV file into a nested list
    # with open(data_path, newline='') as csvfile:
    #     reader = csv.reader(csvfile)
    #     data = list(reader)
    count = 0

    # Use pandas to read the CSV file as a list of dicts
    df = pd.read_csv(data_path)
    all_data = df.to_dict(orient='records')

    #data[0] = ['[' + item for item in data[0] + ']']
    # Starting from the second row, for each row i in row
    for sign_data in all_data:
        # Create the directory if it doesn't exist
        filename_base = re.sub(r'[^\w\-_.]', '_', sign_data['Latin']) # This regex makes sure the string is safe to use as a filename

        if not os.path.exists(batch_dir):
            os.makedirs(batch_dir)

        # Path for the HTML file inside the new directory
        html_file = os.path.join(batch_dir, f"{filename_base}.html")

        # Copy "template.html" content to the new HTML file
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        with open(html_file, 'w') as working_file:
            working_file.write(template_content)
            count += 1

        # Prepare the replacements dictionary
        replacements = {}

        for key, value in sign_data.items():
            if key == CUSTOM_TARGETS['qr']:
                try:
                    target = f"{value}{filename_base}.html"
                    qr = qr_code_to_base64(target)
                    value = qr
                except Exception as e:
                    print(f"Error: QRCode: {e}")

            if is_image_url(value):
                try:
                    value = url_to_data_uri(value)
                except Exception as e:
                    print(f"Error: Image: {e}")

            replacements[f"[{key}]"] = value

        #print(json.dumps(replacements, indent=4))

        # Replace the placeholders in the HTML file
        findAndReplace(html_file, replacements)
        z = f"{count}/{len(all_data)}"

    print(f"Processed {count} files.")
    return z

if __name__ == "__main__":
    template_path = "template.html"
    data_path = "workingdata.csv"
    output_dir = "signs"
    main(template_path, data_path, output_dir)
