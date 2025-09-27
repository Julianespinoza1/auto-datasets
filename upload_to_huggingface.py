#!/usr/bin/env python3
# upload_to_huggingface_replit.py - Versión corregida para Replit

import os
import json
import glob

# Configuración para Replit
os.environ['HUGGINGFACE_HUB_TOKEN'] = "tu_token_aqui"  # ⚠️ Pega tu token

from huggingface_hub import HfApi, DatasetCard, DatasetCardData

def main():
    HF_USERNAME = "Victorespi6"  # ⚠️ Tu username
    PRICE_USD = 2000
    
    # EN REPLIT: Buscar en directorio actual porque ahí se generaron
    DATASETS_DIR = "."  # ← CAMBIO IMPORTANTE
    
    print(f"[INFO] Buscando datasets en: {os.path.abspath(DATASETS_DIR)}")
    
    # Listar archivos para debug
    print("Archivos en directorio actual:")
    for f in os.listdir(DATASETS_DIR):
        if 'dataset' in f:
            print(f" - {f}")
    
    # Buscar metadata files
    meta_files = glob.glob(f"{DATASETS_DIR}/dataset_*.meta.json")
    if not meta_files:
        print("[ERROR] No se encontraron archivos .meta.json")
        print("Asegúrate de que generator.py se ejecutó primero")
        return
    
    print(f"[INFO] Encontrados {len(meta_files)} archivos de metadata")
    
    # Tomar el más reciente
    latest_meta = max(meta_files, key=os.path.getmtime)
    dataset_file = latest_meta.replace('.meta.json', '')
    
    if not os.path.exists(dataset_file):
        print(f"[ERROR] Archivo de dataset no encontrado: {dataset_file}")
        return
    
    print(f"[INFO] Dataset más reciente: {os.path.basename(dataset_file)}")
    
    # Leer metadata
    with open(latest_meta, 'r') as f:
        meta = json.load(f)
    
    # Crear nombre para el dataset
    dataset_name = f"premium-{os.path.basename(dataset_file).replace('.', '-').replace('_', '-')}"
    repo_id = f"{HF_USERNAME}/{dataset_name}"
    
    print(f"[INFO] Subiendo a: {repo_id}")
    print(f"[INFO] Precio: ${PRICE_USD} USD")
    
    try:
        api = HfApi()
        
        # Crear repositorio
        api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
        
        # Subir archivos
        files_to_upload = [dataset_file, latest_meta]
        
        for file_path in files_to_upload:
            api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=os.path.basename(file_path),
                repo_id=repo_id,
                repo_type="dataset"
            )
            print(f"✅ Subido: {os.path.basename(file_path)}")
        
        # Descripción premium
        description = f"""
# 🏆 PREMIUM Synthetic Dataset - ${PRICE_USD} USD

**Filas:** {meta['rows']:,} | **SHA256:** {meta.get('file_sha256', 'Verificado')}
"""
        
        card_data = DatasetCardData(
            language="en",
            license="cc-by-nc-4.0",
            tags=["premium", "synthetic", "commercial"],
        )
        
        card = DatasetCard.from_template(card_data, template_str=description)
        card.push_to_hub(repo_id)
        
        print(f"✅ ÉXITO: https://huggingface.co/datasets/{repo_id}")
        print(f"💰 Precio: ${PRICE_USD} USD")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
