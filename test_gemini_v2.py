import google.generativeai as genai
import os

def test_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        # Try both flash and pro to be sure
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro']
        for model_name in models_to_try:
            print(f"Probando modelo: {model_name}...")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hola, esto es una prueba de conexión.")
                print(f"SUCCESS with {model_name}: {response.text}")
                return True
            except Exception as inner_e:
                print(f"Error con {model_name}: {inner_e}")
        return False
    except Exception as e:
        print(f"FAILURE general: {e}")
        return False

if __name__ == "__main__":
    key = "AIzaSyBjdY77vxDM_CtX7qRVo6_YqzJRsw7_Ucs"
    test_api_key(key)
