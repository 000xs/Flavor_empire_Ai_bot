"""
prompt templates
"""


def new_blog_post_idea():
    """
    prompt template for new blog idea
    add this
        "messages": new_blog_idea()
    """
    return [
        {
            "role": "system",
            "content": """
You are a helpful and creative chef assistant. You specialize in brainstorming engaging recipe titles that are always based on existing recipes already found on the internet. You also have a strong background in writing for social media and food blogs, so your recipe titles must be catchy and blog-worthy.
Only output one recipe **title** per request, in plain text, without any additional explanation or formatting. Keep the title concise and appealing. Do not invent completely new dishes — use known recipe ideas, just rephrase or remix the titles creatively.
            """,
        },
        {
            "role": "user",
            "content": """
Give me a single catchy recipe title based on an existing recipe from the internet. Only output the title as plain text.

            """,
        },
    ]


def blog_post_prompt(idea):
    """
    prompt template for new blog idea
    add this
        "messages": new_blog_idea()
    """
    return [
        {
            "role": "system",
            "content": """
You are a professional food writer and recipe creator. You specialize in writing full recipe articles in Markdown format, based on existing recipes that are already available on the internet. Your writing should be clear, engaging, and suitable for blogs or food websites.

Each article you generate must include the following Markdown structure:

# Title  
A catchy recipe name (based on an existing internet recipe).

## Description  
A short and engaging paragraph describing the dish and its appeal.

## Ingredients  
A bullet-point list of ingredients with quantities.

## Instructions  
A step-by-step numbered list explaining how to prepare the recipe.

## Tips  
(Optional) 1–3 helpful cooking tips or serving suggestions.

add CTA as lin [DOWNLOAD](https://enrageperplexparable.com/f3i1jxxx?key=0ec94d1ae3c0b6c8921f343d4f86ee0c) , dowlode reipe like some , recipe post incleu minmum 2 cta buttons
Only use well-known recipe types and avoid inventing new dishes.
Do an seo Reaserch and use key words prases add this Post. 
Use Emojis.
 
 
            """,
        },
        {
            "role": "user",
            "content": f"""
Write a complete recipe article in Markdown format about the dish titled: {idea}.

            """,
        },
    ]


def image_prompt(idea, post):
    """
    Generates a dynamic food photography prompt using variables.

    Args:
        idea (str): Main dish name (e.g., "gourmet cheeseburger")
        post(str): Detailed description of the dish (e.g., "with aged cheddar, caramelized onions, and truffle aioli on brioche bun")

    Returns:
        str: Complete image generation prompt with dynamic variables
    """
    prompt = f"""Professional food photography of {idea}, {post}.

CAMERA & LENS:
- Camera: Canon EOS R5 or Sony A7R IV
- Lens: 85mm f/1.2 or 100mm f/2.8 macro
- Settings: f/2.8 aperture, 1/200s shutter speed, ISO 100

LIGHTING:
- Primary: Soft natural window light from 45° angle
- Secondary: Subtle fill light from opposite side
- Reflector: Silver reflector to fill shadows
- Atmosphere: Morning or late afternoon golden hour light

COMPOSITION:
- Angle: Overhead or 45° perspective
- Focus: Sharp focus on main subject with shallow depth of field
- Framing: Rule of thirds placement, negative space for text overlay
- Props: Minimal, complementary items (e.g., utensils, ingredients)

STYLING:
- Plating: Restaurant-quality presentation on ceramic or slate
- Garnishes: Fresh herbs, microgreens, edible flowers, spice dust
- Texture: Visible steam (if warm), glistening sauces, fresh ingredients
- Authenticity: Natural food appearance, no artificial enhancements

BACKGROUND:
- Surface: Rustic wood, marble, or linen tablecloth
- Setting: Blurred kitchen or dining environment
- Depth: Layered background with warm, inviting atmosphere
- Color Palette: Complementary colors to the dish

MOOD & STYLE:
- Mood: Appetizing, vibrant, fresh, inviting
- Style: Commercial food photography, editorial quality
- Color: Natural, true-to-life colors with rich saturation
- Atmosphere: Warm, homey, professional yet approachable

TECHNICAL SPECIFICATIONS:
- Resolution: 8K ultra-high definition
- Detail: Intricate textures, realistic food surfaces
- Realism: Photorealistic, no illustration or cartoon elements
- Quality: Professional food photography standards
- Exclusions: No artificial filters, no digital enhancements, no props that distract from food

NEGATIVE PROMPT:
- cartoon, illustration, drawing, painting, blurry, deformed, low quality
- artificial, plastic-looking, overprocessed, unrealistic colors
- digital art, 3D render, CGI, fake food, inedible appearance
- harsh lighting, deep shadows, cluttered background, distracting props
- unrealistic garnishes, messy plating, unappetizing presentation"""
    return prompt.strip()
