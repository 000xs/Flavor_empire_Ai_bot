# import requests
# import os
# from datetime import datetime
# from http import HTTPStatus

# def handler(request):
#     # Get current time in UTC
#     now = datetime.utcnow()
    
#     # Define your API endpoint and headers
#     API_URL = os.environ.get("API_URL")
#     API_TOKEN = os.environ.get("API_TOKEN")
    
#     if not API_URL or not API_TOKEN:
#         return {
#             "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
#             "body": "Missing API configuration"
#         }
    
#     headers = {
#         "Authorization": f"Bearer {API_TOKEN}",
#         "Content-Type": "application/json"
#     }
    
#     try:
#         # Make API call
#         response = requests.get(
#             API_URL,
#             headers=headers,
#             timeout=10
#         )
        
#         # Log response details
#         print(f"API Call at {now}: Status {response.status_code}")
        
#         if response.status_code == 200:
#             return {
#                 "statusCode": HTTPStatus.OK,
#                 "body": f"API call successful at {now}"
#             }
#         else:
#             return {
#                 "statusCode": response.status_code,
#                 "body": f"API returned status {response.status_code}"
#             }
            
#     except requests.exceptions.RequestException as e:
#         print(f"API Call failed at {now}: {str(e)}")
#         return {
#             "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
#             "body": f"API call failed: {str(e)}"
#         }