import os
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_r2_client():
    """
    Initializes and returns a boto3 client for Cloudflare R2.
    """
    try:
        account_id = os.environ['R2_ACCOUNT_ID']
        access_key_id = os.environ['R2_ACCESS_KEY_ID']
        access_key_secret = os.environ['R2_SECRET_ACCESS_KEY']
        bucket_name = os.environ['R2_BUCKET_NAME']
    except KeyError as e:
        raise ValueError(f"Missing required environment variable: {e}")

    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key_secret,
        config=Config(signature_version='s3v4')
    )
    return s3_client, bucket_name

def upload_image_to_r2(image_bytes, file_name):
    """
    Uploads an image to a Cloudflare R2 bucket and returns the public URL.

    Args:
        image_bytes (bytes): The image data.
        file_name (str): The desired file name for the image in the bucket.

    Returns:
        str: The public URL of the uploaded image, or None if the upload fails.
    """
    try:
        s3_client, bucket_name = get_r2_client()
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=image_bytes,
            ContentType='image/jpeg'  # Assuming JPEG, adjust if necessary
        )
        
        # Construct the public URL
        account_id = os.environ['R2_ACCOUNT_ID']
        public_url = f"https://pub-{account_id}.r2.dev/{file_name}"
        
        print(f"Successfully uploaded {file_name} to R2.")
        return public_url

    except (NoCredentialsError, PartialCredentialsError):
        print("❌ Error: AWS credentials not found. Please check your environment variables.")
        return None
    except Exception as e:
        print(f"❌ An error occurred during R2 upload: {e}")
        return None
