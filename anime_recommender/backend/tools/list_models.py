import google.generativeai as genai
from backend.utils.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

print("🔍 Listing available Gemini models that support text generation:\n")

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"✅ {m.name}")
