import google.generativeai as genai
import sys

def list_models(api_key):
    try:
        genai.configure(api_key=api_key)
        print("Modelos disponibles:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    key = "AIzaSyBjdY77vxDM_CtX7qRVo6_YqzJRsw7_Ucs"
    list_models(key)
