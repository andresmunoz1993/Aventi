import google.generativeai as genai
import os

CONFIG = {
    "api_key": "AIzaSyCanTgTZp9l6diSaU1uLcKtlqrXIDBv5Vk",
    "model_name": "models/gemini-2.0-flash"
}

genai.configure(api_key=CONFIG["api_key"])

def test_model():
    try:
        model = genai.GenerativeModel(CONFIG["model_name"])
        response = model.generate_content("Hola.")
        print(f"SUCCESS: {response.text}")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_model()
