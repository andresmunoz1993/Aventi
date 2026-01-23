import pandas as pd
import json
import os

REPORT_PATH = r"C:\Proyectos\Aventi\pdf_summary_report.xlsx"
REGISTRY_PATH = r"C:\Proyectos\Aventi\registry.json"

def deduplicate():
    # 1. Deduplicar Excel
    if os.path.exists(REPORT_PATH):
        print("Deduplicando Excel...")
        df = pd.read_excel(REPORT_PATH)
        initial_count = len(df)
        # Mantener la última entrada (generalmente la más reciente/completa)
        df = df.drop_duplicates(subset=['Nombre del Archivo'], keep='last')
        final_count = len(df)
        df.to_excel(REPORT_PATH, index=False)
        print(f"Excel limpio: {initial_count} -> {final_count} filas.")
    else:
        print("Excel no encontrado.")

    # 2. Sincronizar Registro
    if os.path.exists(REGISTRY_PATH):
        print("Sincronizando registro con el Excel...")
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Si el Excel existe, asegurar que el registro solo tenga lo que está en el Excel
        if os.path.exists(REPORT_PATH):
            df = pd.read_excel(REPORT_PATH)
            valid_files = set(df['Nombre del Archivo'].tolist())
            
            new_registry = {k: v for k, v in registry.items() if k in valid_files}
            
            with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
                json.dump(new_registry, f, indent=4, ensure_ascii=False)
            print(f"Registro sincronizado. {len(registry)} -> {len(new_registry)} entradas.")
    else:
        print("Registro no encontrado.")

if __name__ == "__main__":
    deduplicate()
