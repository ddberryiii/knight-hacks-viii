import google.generativeai as genai
from backend.utils.config import GEMINI_API_KEY


# Configure the Gemini client using your key
genai.configure(api_key=GEMINI_API_KEY)

def ask_gemini(prompt: str):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text
