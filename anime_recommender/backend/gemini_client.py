import os
from google import genai

def chat_with_gemini(message: str) -> str:
    """
    Sends a message to the Gemini API and returns a concise, formatted response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment")

    client = genai.Client(api_key=api_key)

    system_prompt = (
        "You are a concise, friendly anime recommendation assistant. "
        "Respond in short, clear paragraphs or bullet points. "
        "Limit your response to roughly 4–6 sentences. "
        "Do NOT ramble or provide overly detailed explanations."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            {"role": "user", "parts": [{"text": f"{system_prompt}\n\nUser: {message}"}]}
        ]
    )

    return response.text.strip() if hasattr(response, "text") else str(response)
