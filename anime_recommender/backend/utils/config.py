from dotenv import load_dotenv
import os

# load environment variables from .env
load_dotenv()

# access API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file")
