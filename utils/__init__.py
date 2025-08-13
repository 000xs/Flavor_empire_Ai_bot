import requests
import os

def upload_image(image_byte):
    url = "https://the-flavor-emperor-ai.vercel.app/api/upload-image"

    # Check if the image file exists
    if image_byte is None:
        print(f"Error: Image data file not found  ")
    else:
         

        # Set the headers
        headers = {
            "Content-Type": "application/octet-stream"
        }

        try:
            # Send the POST request with the image bytes as the body
            response = requests.post(url, data=image_byte, headers=headers)

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
