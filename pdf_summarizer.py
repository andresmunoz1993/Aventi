import os
import json
import time
import pandas as pd
import google.generativeai as genai
from google.api_core import exceptions
import schedule
import pytz
from datetime import datetime, timedelta

# Configuración
CONFIG = {
    "api_key": "AIzaSyBjdY77vxDM_CtX7qRVo6_YqzJRsw7_Ucs",
    "model_name": "models/gemini-2.0-flash-exp", 
    "source_folder": r"C:\Proyectos\Aventi\Fichas Tecnicas",
    "report_path": r"C:\Proyectos\Aventi\pdf_summary_report.xlsx",
    "registry_path": r"C:\Proyectos\Aventi\registry.json",
    "schedule_time": "5:00",  # 5:00 PM
    "timezone": "America/Bogota"
}

# Configurar Gemini
genai.configure(api_key=CONFIG["api_key"])

def load_registry():
    if os.path.exists(CONFIG["registry_path"]):
        try:
            with open(CONFIG["registry_path"], 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_registry(registry):
    with open(CONFIG["registry_path"], 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)

def pause_until_reset():
    """Calcula el tiempo hasta las 4:00 AM del día siguiente y espera."""
    tz = pytz.timezone(CONFIG["timezone"])
    now = datetime.now(tz)
    # Reset planeado a las 4:00 AM del día siguiente (seguro para el reset de medianoche Pacific Time)
    next_run = (now + timedelta(days=1)).replace(hour=4, minute=0, second=0, microsecond=0)
    wait_seconds = (next_run - now).total_seconds()
    
    print(f"\n--- CUOTA DIARIA AGOTADA ---")
    print(f"La ejecución se pausará hasta mañana a las 4:00 AM ({next_run.strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"Esperando {wait_seconds / 3600:.2f} horas...")
    
    time.sleep(wait_seconds)
    print("Resumiendo procesamiento...")

def generate_summary_ai(pdf_path, retries=3):
    """
    Usa Gemini para leer el PDF y generar un resumen profesional con reintentos y manejo de cuota.
    """
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel(CONFIG["model_name"])
            
            print(f"Intento {attempt + 1}: Subiendo a Gemini: {os.path.basename(pdf_path)}")
            file = genai.upload_file(pdf_path, mime_type="application/pdf")
            
            prompt = (
                "Eres un analista experto en fichas técnicas industriales. Resume este documento en UN SOLO PÁRRAFO corto "
                "(máximo 500 caracteres). El lenguaje debe ser profesional, técnico y muy bien estructurado. "
                "Incluye: nombre del producto, su función principal y las 2 especificaciones más importantes. "
                "REGLAS CRÍTICAS: NO uses viñetas (*), NO uses negritas (**), NO uses saltos de línea (\\n). "
                "NO incluyas introducciones como 'Aquí tienes el resumen' o 'El documento describe'. "
                "Empieza directamente con la información técnica. El resultado será pegado en una celda de Excel."
            )
            
            response = model.generate_content([file, prompt])
            
            # Limpieza inmediata
            try:
                file.delete()
            except:
                pass
            
            # Limpiar posibles marcadores de markdown
            clean_text = response.text.strip().replace("*", "").replace("#", "").replace("\n", " ")
            return clean_text
            
        except exceptions.ResourceExhausted as e:
            if "GenerateRequestsPerDayPerProjectPerModel" in str(e):
                pause_until_reset()
                return generate_summary_ai(pdf_path, retries) # Reintentar tras la pausa
            else:
                # Si es por minuto (RPM), esperar un poco más
                wait_time = (attempt + 1) * 30
                print(f"Límite por minuto alcanzado. Esperando {wait_time}s...")
                time.sleep(wait_time)
        except Exception as e:
            wait_time = (2 ** attempt) * 5
            print(f"Error en intento {attempt + 1} para {os.path.basename(pdf_path)}: {e}. Reintentando en {wait_time}s...")
            time.sleep(wait_time)
            
    return f"Error tras {retries} intentos: No se pudo procesar con IA."

def save_batch(new_data, registry):
    if not new_data:
        return
        
    print(f"Guardando lote de {len(new_data)} archivos en el Excel...")
    df_new = pd.DataFrame(new_data)
    
    if os.path.exists(CONFIG["report_path"]):
        try:
            df_existing = pd.read_excel(CONFIG["report_path"])
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
            # DEDUPLICACIÓN: Asegurar que cada archivo aparezca solo una vez
            df_final = df_final.drop_duplicates(subset=['Nombre del Archivo'], keep='last')
        except Exception as e:
            print(f"Error leyendo Excel existente: {e}. Creando uno nuevo.")
            df_final = df_new
    else:
        df_final = df_new
        
    df_final.to_excel(CONFIG["report_path"], index=False)
    save_registry(registry)
    print(f"Excel y registro actualizados correctamente.")

def process_pdfs():
    print(f"[{datetime.now()}] Iniciando procesamiento de PDFs...")
    registry = load_registry()
    new_data = []
    
    if not os.path.exists(CONFIG["source_folder"]):
        print(f"Error: La carpeta {CONFIG['source_folder']} no existe.")
        return

    files = [f for f in os.listdir(CONFIG["source_folder"]) if f.lower().endswith('.pdf')]
    to_process = [f for f in files if f not in registry]
    total_new = len(to_process)
    
    print(f"Encontrados {len(files)} PDFs. {total_new} archivos nuevos por procesar.")
    
    count = 0
    for filename in to_process:
        count += 1
        print(f"[{count}/{total_new}] Procesando: {filename}")
        file_path = os.path.join(CONFIG["source_folder"], filename)
        
        summary = generate_summary_ai(file_path)
        
        new_data.append({
            "Nombre del Archivo": filename,
            "Resumen Profesional (IA)": summary,
            "Fecha Procesado": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        registry[filename] = {
            "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Guardado parcial cada 5 archivos para dar feedback rápido al usuario
        if count % 5 == 0:
            save_batch(new_data, registry)
            new_data = [] # Limpiar para el siguiente lote
        
        # Pausa para Rate Limit (Free tier es 15 RPM para 1.5 flash / 2.0 flash)
        # 1 archivo cada 10 segundos es conservador y evita bloqueos por minuto
        time.sleep(10)

    # Guardar resto de archivos
    if new_data:
        save_batch(new_data, registry)
        print(f"Procesamiento finalizado. Total nuevos: {total_new}")
    else:
        print("No hay archivos nuevos pendientes.")

def job():
    process_pdfs()

if __name__ == "__main__":
    process_pdfs() # Ejecutar al inicio
    
    schedule.every().day.at(CONFIG["schedule_time"]).do(job)
    print(f"Servicio iniciado. Próxima revisión programada: {CONFIG['schedule_time']} hora Colombia.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
