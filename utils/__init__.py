import firebase_admin
from firebase_admin import credentials, storage
import os

# Initialize Firebase once
if not firebase_admin._apps:
    SERVICE_ACC_PATH = 'travel-guide-ai-446403-firebase-adminsdk-fbsvc-33aab49731.json'
    cred = credentials.Certificate(SERVICE_ACC_PATH)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'travel-guide-ai-446403.appspot.com'
    })

def upload_image(image_filename):
    # Ensure the image path is correct
    """
    Uploads an image file to Firebase Storage.

    Args:
        image_filename (str): The name of the image file to upload.

    Returns:
        str: The public URL of the uploaded image.
    """

    image_path = os.path.join(os.getcwd(), image_filename)

    # Get Firebase Storage bucket
    bucket = storage.bucket()
    blob = bucket.blob(f"uploads/{image_filename}")  # Folder 'uploads/' in bucket
    blob.upload_from_filename(image_path)

    # Make it public (optional)
    blob.make_public()

    print("✅ Upload successful!")
    print("🔗 Public URL:", blob.public_url)
    return blob.public_url
