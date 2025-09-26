#!/usr/bin/env python3
# CargadorDePiñata.py — sube archivos y metadata a Pinata

import os, requests, json, sys, glob

PINATA_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET = os.getenv("PINATA_API_SECRET")
PINATA_PIN_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
PINATA_PIN_JSON = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
WALLET_ADDRESS= os.getenv("WALLET_ADDRESS","")

def upload_file(filepath):
    if not PINATA_KEY or not PINATA_SECRET:
        raise SystemExit("Missing PINATA_API_KEY / PINATA_API_SECRET env vars")
    headers = {"pinata_api_key": PINATA_KEY, "pinata_secret_api_key": PINATA_SECRET}
    with open(filepath, "rb") as fp:
        files = {"file": (os.path.basename(filepath), fp)}
        r = requests.post(PINATA_PIN_URL, files=files, headers=headers, timeout=120)
    if r.status_code not in (200,201):
        print("Pinata file upload failed", r.status_code, r.text)
        return None
    js = r.json()
    return js.get("IpfsHash")

def upload_json(meta):
    if not PINATA_KEY or not PINATA_SECRET:
        raise SystemExit("Missing PINATA_API_KEY / PINATA_API_SECRET env vars")
    headers = {"pinata_api_key": PINATA_KEY, "pinata_secret_api_key": PINATA_SECRET, "Content-Type":"application/json"}
    r = requests.post(PINATA_PIN_JSON, json=meta, headers=headers, timeout=60)
    if r.status_code not in (200,201):
        print("Pinata json upload failed", r.status_code, r.text)
        return None
    return r.json().get("IpfsHash")

if __name__ == "__main__":
    # upload latest dataset and metadata
    files = sorted(glob.glob("dataset_*.jsonl"), reverse=True)
    if not files:
        print("No dataset files found. Run Generador.py first.")
        sys.exit(1)
    latest = files[0]
    print("Uploading", latest)
    cid = upload_file(latest)
    if cid:
        meta_file = latest + ".meta.json"
        meta = {}
        if os.path.exists(meta_file):
            with open(meta_file,"r",encoding="utf-8") as mf:
                meta = json.load(mf)
        meta.update({"ipfs_cid": cid, "filename": latest, "publisher_wallet": WALLET_ADDRESS})
        meta_cid = upload_json(meta)
        print("FILE_CID:", cid, "META_CID:", meta_cid)
