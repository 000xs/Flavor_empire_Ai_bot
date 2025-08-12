# import requests
# import os
# from datetime import datetime
# from http import HTTPStatus
# import os
# import requests
# from dotenv import load_dotenv
# from prompts import new_blog_post_idea, blog_post_prompt, image_prompt
# import time
# from Notifiy import Publisher
# from http.server import BaseHTTPRequestHandler # New import
# import json # New import

# load_dotenv()

# # def generate_food_image(idea, post):
# #     """
# #     Generate a food image based on `idea` and `post` text.
# #     """
# #     # Check if token is set
# #     try:
# #         HF_TOKEN = os.environ['HF_TOKEN']
# #         if not HF_TOKEN:
# #             raise ValueError("HF_TOKEN is empty")
# #     except KeyError:
# #         print("❌ Error: HF_TOKEN environment variable not set")
# #         print("Please set your Hugging Face token with: export HF_TOKEN=your_token_here")
# #         return None
# #     except ValueError as e:
# #         print(f"❌ Error: {e}")
# #         return None

# #     # Try both router and direct API endpoints
# #     API_URLS = [
# #         "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-3-medium-diffusers",
# #         "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3-medium-diffusers",
# #         "https://router.huggingface.co/fal-ai/fal-ai/fast-sdxl"
# #     ]
    
# #     def query(payload, url):
# #         headers = {
# #             "Authorization": f"Bearer {HF_TOKEN}",
# #             "Content-Type": "application/json"
# #         }
# #         print(f"Trying endpoint: {url}")
# #         response = requests.post(url, headers=headers, json=payload)
        
# #         print(f"Response status: {response.status_code}")
        
# #         if response.status_code == 200:
# #             return response.content
# #         elif response.status_code == 401:
# #             print("❌ Authentication failed. Check your token:")
# #             print("1. Token is valid at https://huggingface.co/settings/tokens")
# #             print("2. Token has 'read' permissions")
# #             print("3. Token is correctly set as HF_TOKEN environment variable")
# #             return None
# #         elif response.status_code == 404:
# #             print("❌ Model not found or temporarily unavailable")
# #             return None
# #         else:
# #             print(f"❌ Error: {response.status_code} - {response.text[:200]}...")
# #             return None

# #     # Generate image prompt
# #     prompt = image_prompt(idea, post)
# #     print(f"Generated image prompt: {prompt}")
    
# #     # Try each endpoint until one works
# #     image_bytes = None
# #     for url in API_URLS:
# #         payload = {
# #             "inputs": prompt,
# #             "options": {"wait_for_model": True}
# #         }
# #         image_bytes = query(payload, url)
        
# #         if image_bytes:
# #             break
# #     # image date as an image and uplode to cloud bucket 
    
    
    
# #     return uplode_image(image_bytes)
  
# def genrate_blog_post_idea():
#     zai_api_key = os.getenv('ZAI_API_KEY')
#     if not zai_api_key:
#         print("❌ Error: ZAI_API_KEY environment variable not set for blog post idea generation.")
#         return None
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {zai_api_key}",
#     }
#     data = {
#         "model": "glm-4.5-flash",
#         "messages": new_blog_post_idea(),
#         "temperature": 0.7,
#         "top_p": 0.8,
#     }
#     try:
#         response = requests.post(
#             "https://api.z.ai/api/paas/v4/chat/completions", headers=headers, json=data
#         )
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Error generating blog post idea: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"❌ Error decoding JSON for blog post idea: {e}")
#         return None

# def generate_blog_post(idea):
#     if not idea: # Check if idea is valid before proceeding
#         print("❌ Cannot generate blog post: idea is missing.")
#         return None
#     zai_api_key = os.getenv('ZAI_API_KEY')
#     if not zai_api_key:
#         print("❌ Error: ZAI_API_KEY environment variable not set for blog post generation.")
#         return None
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {zai_api_key}",
#     }
#     data = {
#         "model": "glm-4.5-flash",
#         "messages": blog_post_prompt(idea),
#         "temperature": 0.7,
#         "top_p": 0.8,
#     }
#     try:
#         response = requests.post(
#             "https://api.z.ai/api/paas/v4/chat/completions", headers=headers, json=data
#         )
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Error generating blog post: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"❌ Error decoding JSON for blog post: {e}")
#         return None

# # Renamed the original handler logic
# def _actual_handler_logic():
#     try:
#         # Get current time in UTC
#         now = datetime.utcnow()
        
#         # Generate idea
#         idea = genrate_blog_post_idea()
#         if not idea:
#             return {
#                 "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
#                 "body": {"message": "Failed to generate blog post idea."}
#             }
#         print(f"Generated blog post idea: {idea}")
        
#         # Generate blog post
#         post = generate_blog_post(idea)
#         if not post:
#             return {
#                 "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
#                 "body": {"message": "Failed to generate blog post content."}
#             }
#         print("Generated blog post:")
#         print(post)
        
#         # Generate food image
#         # link = generate_food_image(idea, post)
#         # print(f"Image uploaded to Firebase: {link}")
        
#         # Publish blog post
#         publisher = Publisher()
#         result = publisher.publish_hash_node(
#             content=post,
#             title=idea,
#             image_url="https://images.unsplash.com/photo-1511690656952-34342bb7c2f2?q=80&w=464&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
#         )
        
#         if not result == None:
#             print("\n🎉 Blog post published successfully!")
#             return {
#                 "statusCode": HTTPStatus.OK,
#                 "body": {"message" : "Blog post published successfully!" , "data" : result},
#             }
#         return {
#             "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
#             "body": {"message": "Failed to publish blog post."}
#         }
#     except Exception as e:
#         print(f"❌ An unexpected error occurred in _actual_handler_logic: {e}")
#         return {
#             "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
#             "body": {"message": f"An unexpected error occurred: {str(e)}"}
#         }

# # New class-based handler
# class handler(BaseHTTPRequestHandler): # Vercel expects 'handler' as the entry point
#     def do_GET(self):
#         response_data = _actual_handler_logic()
        
#         self.send_response(response_data["statusCode"])
#         self.send_header("Content-type", "application/json")
#         self.end_headers()
#         self.wfile.write(json.dumps(response_data["body"]).encode("utf-8"))

#     def do_POST(self):
#         # For cron jobs, usually GET is sufficient, but good to have POST too if needed.
#         # For this specific cron job, it's likely only GET is relevant.
#         self.do_GET() # Re-use GET logic for POST if the functionality is the same.
