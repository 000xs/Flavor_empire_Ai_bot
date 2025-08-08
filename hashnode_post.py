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

    def publish_hash_node(self, content, title="The Ultimate Chewy Chocolate Chip Cookies", 
                         image_path=None, image_data=None, cover_image_url=None, banner_image_url=None):
        """Publish content to Hashnode with optional image uploaded to Appwrite"""
        MARKDOWN = content
        
        if image_path or image_data:
            print("\nUploading image to Appwrite...")
            image_url = self.upload_image_to_appwrite(image_path=image_path, image_data=image_data)
            if image_url:
                MARKDOWN = f"![{title}]({image_url})\n\n{MARKDOWN}"
                print("✅ Image added to post")
            else:
                print("⚠️ Failed to upload image to Appwrite")
        elif image_path and not os.path.exists(image_path):
            print(f"⚠️ Image file not found: {image_path}")
        
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

if __name__ == "__main__":
    publisher = Publisher()
    
    content = """# Decadent Chocolate Lava Cakes That Will Steal Your Heart

## Description
Indulge in the ultimate chocolate experience with these decadent lava cakes. With a molten chocolate center that flows like lava when you cut into it, these individual desserts are sure to impress your guests and satisfy your chocolate cravings.

## Ingredients
* 6 oz dark chocolate, chopped
* 6 tablespoons unsalted butter
* 2 large eggs
* 2 large egg yolks
* 1/4 cup granulated sugar
* 2 tablespoons all-purpose flour
* Pinch of salt
* Butter and cocoa powder for ramekins

## Instructions
1. Preheat oven to 425°F (220°C). Butter six 6-ounce ramekins and dust with cocoa powder.
2. Melt chocolate and butter in a double boiler until smooth.
3. In a bowl, whisk eggs, egg yolks, and sugar until thick and pale.
4. Fold the melted chocolate mixture into the egg mixture.
5. Gently fold in flour and salt until just combined.
6. Divide batter among prepared ramekins.
7. Bake for 12-14 minutes until edges are firm and centers jiggle slightly.
8. Let cool for 1 minute, then invert onto serving plates.

## Tips
* Serve immediately with vanilla ice cream or fresh berries.
* For a boozy version, add 1 tablespoon of liqueur to the batter.
* Don't overbake or the centers won't be molten.

Enjoy this heavenly dessert!
"""

    cover_image_url = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
    
    banner_image_url = "https://images.unsplash.com/photo-1551024601-bec78cea907b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
    
    binary_image_data = b'\x00a\x0fJ\x81\xa5\xf7\xa4\xe5\xd1\x1fA\x16\xa0\xac\x89\x0b\x85\xe4\x9a\x8aIs\xcej)$\x15Y\xa5\xa8m\x99T\xafebs%Wy=\xea6\x93\xbd@\x20cd.i\x80\xf1K\x9a\x00visL\xa5\x14\x00\xec\xd0))A\xa0\x05\xa4\xa2\x92\x80\x174f\x92\x8a\x00\\\xd1IE\x00:\x8aJ)\x00\xa6\x92\x83E0?\xff\xd9'
    
    result = publisher.publish_hash_node(
        content=content,
        title="Decadent Chocolate Lava Cakes That Will Steal Your Heart",
        image_data=binary_image_data,
      
        cover_image_url=cover_image_url,
        banner_image_url=banner_image_url
    )
    
    if result:
        print("\n🎉 Blog post published successfully!")
    else:
        print("\n❌ Failed to publish blog post")
