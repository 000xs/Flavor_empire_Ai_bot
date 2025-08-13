from flask import Flask, jsonify, request, render_template
import os
import requests
import json
from datetime import datetime
from http import HTTPStatus
from dotenv import load_dotenv
from prompts import new_blog_post_idea, blog_post_prompt, image_prompt
from Notifiy import Publisher
from utils.image_uploader import upload_image_to_r2
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)

# Supabase setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def generate_food_image(idea, post):
    """
    Generate a food image based on `idea` and `post` text.
    """
    # Check if token is set
    try:
        HF_TOKEN = os.environ['HF_TOKEN']
        if not HF_TOKEN:
            raise ValueError("HF_TOKEN is empty")
    except KeyError:
        print("❌ Error: HF_TOKEN environment variable not set")
        print("Please set your Hugging Face token with: export HF_TOKEN=your_token_here")
        return None
    except ValueError as e:
        print(f"❌ Error: {e}")
        return None

    # Try both router and direct API endpoints
    API_URLS = [
        "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-3-medium-diffusers",
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3-medium-diffusers",
        "https://router.huggingface.co/fal-ai/fal-ai/fast-sdxl"
    ]
    
    def query(payload, url):
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        print(f"Trying endpoint: {url}")
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 401:
            print("❌ Authentication failed. Check your token:")
            print("1. Token is valid at https://huggingface.co/settings/tokens")
            print("2. Token has 'read' permissions")
            print("3. Token is correctly set as HF_TOKEN environment variable")
            return None
        elif response.status_code == 404:
            print("❌ Model not found or temporarily unavailable")
            return None
        else:
            print(f"❌ Error: {response.status_code} - {response.text[:200]}...")
            return None

    # Generate image prompt
    prompt = image_prompt(idea, post)
    print(f"Generated image prompt: {prompt}")
    
    # Try each endpoint until one works
    image_bytes = None
    for url in API_URLS:
        payload = {
            "inputs": prompt,
            "options": {"wait_for_model": True}
        }
        image_bytes = query(payload, url)
        
        if image_bytes:
            break
    
    if image_bytes:
        file_name = f"{idea.replace(' ', '-').lower()}-{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        image_url = upload_image_to_r2(image_bytes, file_name)
        return image_url
    return None

def generate_blog_post_idea():
    zai_api_key = os.getenv("ZAI_API_KEY")
    if not zai_api_key:
        print("❌ Error: ZAI_API_KEY environment variable not set")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {zai_api_key}",
    }
    data = {
        "model": "glm-4.5-flash",
        "messages": new_blog_post_idea(),
        "temperature": 0.7,
        "top_p": 0.8,
    }

    try:
        response = requests.post(
            "https://api.z.ai/api/paas/v4/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generating blog post idea: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return None

def generate_blog_post(idea):
    if not idea:
        print("❌ Cannot generate blog post: idea is missing")
        return None

    zai_api_key = os.getenv("ZAI_API_KEY")
    if not zai_api_key:
        print("❌ Error: ZAI_API_KEY environment variable not set")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {zai_api_key}",
    }
    data = {
        "model": "glm-4.5-flash",
        "messages": blog_post_prompt(idea),
        "temperature": 0.7,
        "top_p": 0.8,
    }

    try:
        response = requests.post(
            "https://api.z.ai/api/paas/v4/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generating blog post: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/posts", methods=["GET"])
def get_posts():
    try:
        data, count = supabase.table('tasks').select('*').execute()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route("/api/scheduled-call", methods=["GET"])
def scheduled_call():
    try:
        # Generate idea
        idea = generate_blog_post_idea()
        if not idea:
            return jsonify({
                "error": "Failed to generate blog post idea"
            }), HTTPStatus.INTERNAL_SERVER_ERROR

        print(f"Generated blog post idea: {idea}")

        # Generate blog post
        post_content = generate_blog_post(idea)
        if not post_content:
            return jsonify({
                "error": "Failed to generate blog post content"
            }), HTTPStatus.INTERNAL_SERVER_ERROR

        print("Generated blog post:")
        print(post_content)

        # Generate and upload image
        image_url = generate_food_image(idea, post_content)
        if not image_url:
            print("⚠️ Could not generate image. Using a default.")
            image_url = "https://cdn.image.sniplyx.xyz/uploaded-image-20250813104033.jpg"

        # Save to Supabase
        try:
            data, count = supabase.table('tasks').insert({
                "title": idea,
                "image_url": image_url
            }).execute()
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")
            return jsonify({"error": f"Failed to save to Supabase: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR

        # Publish blog post
        publisher = Publisher()
        result = publisher.publish_hash_node(
            content=post_content,
            title=idea,
            image_url=image_url,
        )

        if result:
            print("\n🎉 Blog post published successfully!")
            # Update post_url in Supabase
            try:
                post_url = result.get('url') # Assuming the result from publish_hash_node contains the URL
                if post_url:
                    supabase.table('tasks').update({"post_url": post_url}).eq("title", idea).execute()
            except Exception as e:
                print(f"❌ Error updating post_url in Supabase: {e}")

            return jsonify({
                "message": "Blog post published successfully!",
                "data": result
            }), HTTPStatus.OK

        return jsonify({
            "error": "Failed to publish blog post"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    try:
        image_bytes = request.get_data() # Get raw bytes from the request body

        if not image_bytes:
            return jsonify({"error": "No image bytes provided in the request body"}), HTTPStatus.BAD_REQUEST
        
        # Generate a unique filename. Assuming the uploaded image is a JPG.
        file_name = f"uploaded-image-{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        
        image_url = upload_image_to_r2(image_bytes, file_name)

        if image_url:
            return jsonify({
                "message": "Image uploaded successfully!",
                "image_url": image_url
            }), HTTPStatus.OK
        else:
            return jsonify({
                "error": "Failed to upload image to R2"
            }), HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception as e:
        print(f"❌ Unexpected error during image upload: {e}")
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(debug=True)
