import google.generativeai as genai
import sys

def test_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model.generate_content("Hola, ¿puedes leerme?")
        print(f"SUCCESS: {response.text}")
        return True
    except Exception as e:
        print(f"FAILURE: {e}")
        return False

if __name__ == "__main__":
    key = "AIzaSyBjdY77vxDM_CtX7qRVo6_YqzJRsw7_Ucs"
    test_api_key(key)
