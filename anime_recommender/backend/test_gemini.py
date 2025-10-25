from backend.core.gemini_client import ask_gemini

if __name__ == "__main__":
    print("🔍 Testing Gemini API connection...")
    try:
        response = ask_gemini("List 3 anime similar to Attack on Titan.")
        print("\n✅ Gemini Response:\n")
        print(response)
    except Exception as e:
        print("\n❌ Error communicating with Gemini API:")
        print(e)
