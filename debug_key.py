import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

print(f"Clave detectada: {api_key[:8]}... (Longitud: {len(api_key)})")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

try:
    response = model.generate_content("Hola")
    print(f"PRUEBA TEXTO: Exitosa - {response.text[:20]}...")
except Exception as e:
    print(f"PRUEBA TEXTO: Fallida - {e}")
