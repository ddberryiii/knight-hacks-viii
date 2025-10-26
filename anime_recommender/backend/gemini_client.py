import os
from google import genai

def chat_with_gemini(message: str) -> str:

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[{"role": "user", "parts": [{"text": message}]}]
    )

    return response.text.strip() if hasattr(response, "text") else str(response)
