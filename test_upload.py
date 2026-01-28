import google.generativeai as genai
import os
import time

CONFIG = {
    "api_key": "AIzaSyCanTgTZp9l6diSaU1uLcKtlqrXIDBv5Vk",
    "model_name": "models/gemini-2.0-flash",
    "test_pdf": r"C:\Proyectos\Aventi\Fichas Tecnicas\22158-FT.pdf"
}

genai.configure(api_key=CONFIG["api_key"])

def test_upload():
    try:
        if not os.path.exists(CONFIG["test_pdf"]):
            print(f"File not found: {CONFIG['test_pdf']}")
            return
            
        print(f"Uploading {CONFIG['test_pdf']}...")
        file = genai.upload_file(CONFIG["test_pdf"], mime_type="application/pdf")
        print(f"Upload SUCCESS: {file.name}")
        
        print("Testing content generation with file...")
        model = genai.GenerativeModel(CONFIG["model_name"])
        response = model.generate_content([file, "Resume este PDF."])
        print(f"Generation SUCCESS: {response.text[:100]}...")
        
        file.delete()
        print("File deleted.")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_upload()
