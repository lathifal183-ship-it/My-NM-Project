import json, re
from google import genai
from google.genai import types
from app.config import settings

def extract_json(text):
    text = re.sub(r"^```(?:json)?\\s*|\\s*```$", "", (text or "").strip(), flags=re.I)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\\{.*\\}", text, re.S)
        if match:
            return json.loads(match.group(0))
        raise ValueError("AI response was not valid JSON.")

def build_prompt(planner, payload, image_attached=False):
    schema = {
        "total_budget": 0,
        "budget_breakdown": [{"category": "category", "allocation": 0,
          "items": [{"name": "item", "description": "details", "estimated_price": 0,
                     "quantity": 1, "search_terms": "search phrase",
                     "platforms": ["Amazon"]}]}],
        "remaining_budget": 0, "additional_suggestions": ["tip"]
    }
    return (
        "You are PocketSmart AI, a practical Indian budget planning assistant.\\n"
        f"Planner: {planner}\\nInputs: {json.dumps(payload, ensure_ascii=False)}\\n"
        f"Outfit image attached: {image_attached}\\n"
        f"Return ONLY valid JSON with this structure: {json.dumps(schema)}\\n"
        "All prices must be estimated INR, not claimed live prices. Keep all allocations within total budget. "
        "Do not claim stock or verified current offers. Give 2-5 categories and 1-3 items per category. "
        "Home platforms: Amazon, Flipkart, IKEA. Party: Swiggy, Zomato, OYO, BookMyShow. "
        "Jewelry: Amazon, Flipkart, Bluestone, Tanishq, CaratLane. "
        "If an image is attached, describe visible outfit colors/style only and use as coordination hints."
    )

def generate_with_gemini(prompt, image_bytes=None, mime_type="image/jpeg"):
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    client = genai.Client(api_key=settings.gemini_api_key)
    contents = [prompt]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    response = client.models.generate_content(model=settings.gemini_model, contents=contents)
    return extract_json(response.text or "")
