import requests
import os

# The image to upload
image_path = "test.png"

# The API endpoint URL
url = "https://the-flavor-emperor-ai.vercel.app/api/upload-image"

# Check if the image file exists
if not os.path.exists(image_path):
    print(f"Error: Image file not found at '{image_path}'")
else:
    # Read the image file in binary mode
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    # Set the headers
    headers = {
        "Content-Type": "application/octet-stream"
    }

    try:
        # Send the POST request with the image bytes as the body
        response = requests.post(url, data=image_bytes, headers=headers)

        # Check the response
        if response.status_code == 200:
            print("Image uploaded successfully!")
            print("Response JSON:", response.json())
        else:
            print(f"Error uploading image. Status code: {response.status_code}")
            try:
                print("Error response:", response.json())
            except requests.exceptions.JSONDecodeError:
                print("Error response:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
