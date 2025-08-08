import os
import requests
from dotenv import load_dotenv
import json
import base64
from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from urllib.parse import urljoin
import time

load_dotenv()

class Publisher:
    def __init__(self) -> None:
        # Hashnode credentials
        self.HASHNODE_PAT = os.getenv("HASHNODE_PAT")  # Personal Access Token
        self.PUBLICATION_ID = os.getenv("HASHNODE_PUB_ID")
        
        # Appwrite credentials
        self.APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
        self.APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
        self.APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
        self.APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID")
        
        # Initialize Appwrite client
        self.client = Client()
        self.client.set_endpoint(self.APPWRITE_ENDPOINT)
        self.client.set_project(self.APPWRITE_PROJECT_ID)
        self.client.set_key(self.APPWRITE_API_KEY)
        
        # Initialize storage service
        self.storage = Storage(self.client)
        
        # GraphQL queries
        self.create_draft_query = """
        mutation createDraft($input: CreateDraftInput!) {
            createDraft(input: $input) {
                draft {
                    id
                    title
                    slug
                }
            }
        }
        """
        
        self.publish_draft_query = """
        mutation publishDraft($input: PublishDraftInput!) {
            publishDraft(input: $input) {
                post {
                    id
                    title
                    slug
                    url
                }
            }
        }
        """

    def get_available_tags(self):
        """Fetch available tags from Hashnode"""
        query = """
        query {
            tag(first: 20) {
                edges {
                    node {
                        id
                        name
                        slug
                    }
                }
            }
        }
        """
        response = requests.post(
            "https://gql.hashnode.com/",
            headers={
                "Authorization": self.HASHNODE_PAT,
                "Content-Type": "application/json",
            },
            json={"query": query},
        )
        data = response.json()
        if "errors" not in data:
            tags = []
            for edge in data.get("data", {}).get("tag", {}).get("edges", []):
                tags.append(edge["node"])
            return tags
        else:
            print("Error fetching tags:", data["errors"])
            return []

    def get_appwrite_file_url(self, file_id):
        """Construct the public URL for an Appwrite file"""
        endpoint = self.APPWRITE_ENDPOINT.rstrip('/v1').rstrip('/')
        return f"{endpoint}/v1/storage/buckets/{self.APPWRITE_BUCKET_ID}/files/{file_id}/view?project={self.APPWRITE_PROJECT_ID}"

    def upload_image_to_appwrite(self, image_path=None, image_data=None, mime_type="image/png"):
        """Upload an image to Appwrite storage and return the URL"""
        try:
            if not all([self.APPWRITE_ENDPOINT, self.APPWRITE_PROJECT_ID, 
                       self.APPWRITE_API_KEY, self.APPWRITE_BUCKET_ID]):
                print("❌ Appwrite credentials not properly configured")
                return None
                
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    file_data = image_file.read()
                
                if mime_type == "image/png":
                    file_extension = os.path.splitext(image_path)[1].lower()
                    if file_extension == '.jpg' or file_extension == '.jpeg':
                        mime_type = "image/jpeg"
                    elif file_extension == '.gif':
                        mime_type = "image/gif"
                
                filename = os.path.basename(image_path)
            elif image_data:
                file_data = image_data
                filename = f"image_{int(time.time())}.{'png' if mime_type == 'image/png' else 'jpg'}"
            else:
                print("❌ No image path or image data provided")
                return None
            
            input_file = InputFile.from_bytes(
                file_data,
                filename=filename,
                mime_type=mime_type
            )
            
            response = self.storage.create_file(
                bucket_id=self.APPWRITE_BUCKET_ID,
                file_id='unique()',
                file=input_file,
                permissions=['read("any")']
            )
            
            if not response:
                print("❌ Appwrite upload failed: No response")
                return None
                
            file_id = response.get('$id')
            if not file_id:
                print("❌ Failed to get file ID from Appwrite response")
                return None
                
            image_url = self.get_appwrite_file_url(file_id)
            
            print(f"✅ Image uploaded to Appwrite: {image_url}")
            return image_url
                
        except Exception as e:
            print(f"❌ Error uploading image to Appwrite: {str(e)}")
            return None

    def publish_hash_node(self, content, title="The Ultimate Chewy Chocolate Chip Cookies", image_url=None):
        """Publish content to Hashnode with optional image uploaded to Appwrite"""
        MARKDOWN = content
        
         
            
        cover_image_url = image_url
        banner_image_url = image_url 
        
        print("\nFetching available tags...")
        available_tags = self.get_available_tags()
        if available_tags:
            print("Available tags:")
            for tag in available_tags:
                print(f"  {tag['name']}: {tag['id']}")
            
            relevant_tags = []
            tag_names = ["desserts", "baking", "cookies", "recipes"]
            for tag in available_tags:
                if tag["name"].lower() in tag_names:
                    relevant_tags.append({"id": tag["id"]})
            
            relevant_tags = relevant_tags[:3]
            print(f"\nUsing tags: {[tag['id'] for tag in relevant_tags]}")
        else:
            relevant_tags = []
            print("No tags available or error fetching tags")
        
        create_draft_variables = {
            "input": {
                "title": title,
                "contentMarkdown": MARKDOWN,
                "tags": relevant_tags,   
                "publicationId": self.PUBLICATION_ID,
                "settings": {
                    "delist": False,
                    "enableTableOfContent": True
                }
            }
        }
        
        
        if cover_image_url:
            create_draft_variables["input"]["coverImageOptions"] = {
                "coverImageURL": cover_image_url
            }
            print(f"✅ Cover image set: {cover_image_url}")
        
        if banner_image_url:
            create_draft_variables["input"]["bannerImageOptions"] = {
                "bannerImageURL": banner_image_url
            }
            print(f"✅ Banner image set: {banner_image_url}")
      
        if not self.HASHNODE_PAT:
            print("❌ Error: HASHNODE_PAT environment variable not set")
            return None
            
        if not self.PUBLICATION_ID:
            print("❌ Error: HASHNODE_PUB_ID environment variable not set")
            return None
            
        print(f"\nUsing Publication ID: {self.PUBLICATION_ID}")
        
        print("\nCreating draft...")
        response = requests.post(
            "https://gql.hashnode.com/",
            headers={"Authorization": self.HASHNODE_PAT, "Content-Type": "application/json"},
            json={"query": self.create_draft_query, "variables": create_draft_variables},
        )
        
        data = response.json()
        
        if "errors" in data:
            print("❌ Error creating draft:", json.dumps(data["errors"], indent=2))
            return None
            
        draft_data = data.get("data", {}).get("createDraft", {}).get("draft")
        if not draft_data:
            print("❌ Unexpected response structure:", json.dumps(data, indent=2))
            return None
            
        print("\n✅ Draft created successfully!")
        print(f"Draft ID: {draft_data['id']}")
        print(f"Title: {draft_data['title']}")
        print(f"Slug: {draft_data['slug']}")
        
        print("\nPublishing draft...")
        publish_variables = {
            "input": {
                "draftId": draft_data["id"]
            }
        }
        
        response = requests.post(
            "https://gql.hashnode.com/",
            headers={"Authorization": self.HASHNODE_PAT, "Content-Type": "application/json"},
            json={"query": self.publish_draft_query, "variables": publish_variables},
        )
        
        data = response.json()
        
        if "errors" in data:
            print("❌ Error publishing draft:", json.dumps(data["errors"], indent=2))
            return None
            
        post_data = data.get("data", {}).get("publishDraft", {}).get("post")
        if not post_data:
            print("❌ Unexpected response structure:", json.dumps(data, indent=2))
            return None
            
        print("\n✅ Post published successfully!")
        print(f"Post ID: {post_data['id']}")
        print(f"Title: {post_data['title']}")
        print(f"Slug: {post_data['slug']}")
        print(f"URL: {post_data['url']}")
        
        return post_data

 