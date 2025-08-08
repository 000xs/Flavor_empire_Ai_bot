import hashlib
import hmac
import datetime
import requests

# --------------------
# 🔐 Credentials
# --------------------
R2_ACCESS_KEY = 'YOUR_ACCESS_KEY'
R2_SECRET_KEY = 'YOUR_SECRET_KEY'
R2_BUCKET = 'your-bucket-name'
R2_ACCOUNT_ID = 'your-account-id'

# R2 endpoint
R2_HOST = f'{R2_BUCKET}.{R2_ACCOUNT_ID}.r2.cloudflarestorage.com'
R2_ENDPOINT = f'https://{R2_HOST}'

# --------------------
# 📤 Upload Function
# --------------------
def upload_image_raw_r2(file_path, object_key):
    with open(file_path, 'rb') as f:
        file_data = f.read()

    method = 'PUT'
    service = 's3'
    region = 'auto'
    content_type = 'application/octet-stream'
    request_datetime = datetime.datetime.utcnow()
    amz_date = request_datetime.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = request_datetime.strftime('%Y%m%d')

    canonical_uri = f'/{object_key}'
    canonical_querystring = ''
    payload_hash = hashlib.sha256(file_data).hexdigest()

    canonical_headers = (
        f'host:{R2_HOST}\n'
        f'x-amz-content-sha256:{payload_hash}\n'
        f'x-amz-date:{amz_date}\n'
    )

    signed_headers = 'host;x-amz-content-sha256;x-amz-date'

    canonical_request = (
        f'{method}\n'
        f'{canonical_uri}\n'
        f'{canonical_querystring}\n'
        f'{canonical_headers}\n'
        f'{signed_headers}\n'
        f'{payload_hash}'
    )

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
    string_to_sign = (
        f'{algorithm}\n'
        f'{amz_date}\n'
        f'{credential_scope}\n'
        f'{hashlib.sha256(canonical_request.encode()).hexdigest()}'
    )

    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    k_date = sign(('AWS4' + R2_SECRET_KEY).encode(), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

    authorization_header = (
        f'{algorithm} '
        f'Credential={R2_ACCESS_KEY}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, '
        f'Signature={signature}'
    )

    headers = {
        'Host': R2_HOST,
        'x-amz-content-sha256': payload_hash,
        'x-amz-date': amz_date,
        'Authorization': authorization_header,
        'Content-Type': content_type
    }

    url = f'{R2_ENDPOINT}/{object_key}'
    response = requests.put(url, data=file_data, headers=headers)

    if response.status_code == 200:
        print("✅ Upload succeeded!")
        print("🔗 Public URL:", url)
    else:
        print("❌ Upload failed:", response.status_code, response.text)
upload_image_raw_r2(
    file_path='Crispy_Honey_Garlic_1754593999.png',
    object_key='uploads/Crispy_Honey_Garlic.png'
)
