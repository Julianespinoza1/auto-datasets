#!/usr/bin/env python3
# CargadorDePiñata.py — uploader seguro a Pinata con validación de metadata y fingerprint

import os, requests, glob, json, sys, time, random, hashlib
from datetime import datetime

PINATA_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET = os.getenv("PINATA_API_SECRET")
PINATA_PIN_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
PINATA_PIN_JSON = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
WALLET = os.getenv("WALLET_ADDRESS","")
LOG_FILE = os.getenv("UPLOADED_LOG","uploaded.log")
MAX_RETRIES = int(os.getenv("PINATA_MAX_RETRIES","5"))

if not PINATA_KEY or not PINATA_SECRET:
    print("[ERR] Set PINATA_API_KEY and PINATA_API_SECRET in env.")
    sys.exit(1)

def sha256_of_file(path, bufsize=65536):
    h = hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def read_uploaded_log():
    s = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE,"r",encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    s.add(ln)
    return s

def append_uploaded_log(line):
    with open(LOG_FILE,"a",encoding="utf-8") as f:
        f.write(line + "\n")

def do_post_with_retry(url, headers=None, files=None, json_body=None, timeout=120):
    session = requests.Session()
    for attempt in range(1, MAX_RETRIES+1):
        try:
            if files:
                r = session.post(url, files=files, headers=headers, timeout=timeout)
            else:
                r = session.post(url, json=json_body, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            r = None
            err = str(e)
        else:
            err = None
        if r and r.status_code in (200,201):
            return r.json()
        wait = min(30, (2 ** attempt) + random.random())
        print(f"[WARN] request failed attempt={attempt} status={getattr(r,'status_code',None)} err={err}. backoff {wait:.1f}s")
        time.sleep(wait)
    print("[ERR] all retries failed for url:", url)
    return None

def validate_meta(meta_path, file_path):
    if not os.path.exists(meta_path):
        raise RuntimeError("Meta file missing: " + meta_path)
    with open(meta_path,"r",encoding="utf-8") as mf:
        meta = json.load(mf)
    # checks
    if not meta.get("disclaimer") or "synthetic" not in meta.get("disclaimer","").lower():
        raise RuntimeError("Meta disclaimer missing or does not state synthetic.")
    expected = meta.get("file_sha256")
    if not expected:
        raise RuntimeError("Meta missing file_sha256.")
    actual = sha256_of_file(file_path)
    if actual != expected:
        raise RuntimeError(f"SHA256 mismatch. meta:{expected} actual:{actual}")
    return meta

def upload_file(filepath):
    headers = {"pinata_api_key": PINATA_KEY, "pinata_secret_api_key": PINATA_SECRET}
    with open(filepath,"rb") as fp:
        files = {"file": (os.path.basename(filepath), fp)}
        js = do_post_with_retry(PINATA_PIN_URL, headers=headers, files=files)
    if not js:
        return None
    return js.get("IpfsHash")

def upload_json(meta):
    headers = {"pinata_api_key": PINATA_KEY, "pinata_secret_api_key": PINATA_SECRET, "Content-Type":"application/json"}
    js = do_post_with_retry(PINATA_PIN_JSON, headers=headers, json_body=meta)
    if not js:
        return None
    return js.get("IpfsHash")

def main():
    print(f"[INFO] Pinata uploader start {datetime.utcnow().isoformat()} UTC")
    # detect datasets .jsonl or .jsonl.gz
    files = sorted(glob.glob("dataset_*.jsonl*"), reverse=True)
    if not files:
        print("[INFO] No dataset files found. Run Generador.py first.")
        sys.exit(0)
    uploaded = read_uploaded_log()
    for fpath in files:
        fname = os.path.basename(fpath)
        if fname in uploaded:
            print(f"[SKIP] already uploaded {fname}")
            continue
        # corregir path meta (solo agregar .meta.json una vez)
        if fpath.endswith(".meta.json"):
            continue
        meta_path = fpath + ".meta.json"
        if not os.path.exists(meta_path):
            # si el meta tiene doble extensión por error, quitar un ".meta.json"
            base = fpath
            if fpath.endswith(".gz"):
                base = fpath[:-3]
            alt_meta = base + ".meta.json"
            if os.path.exists(alt_meta):
                meta_path = alt_meta
        try:
            meta = validate_meta(meta_path, fpath)
        except Exception as e:
            print(f"[ERR] Validation failed for {fname}: {e}")
            continue
        print(f"[INFO] validated meta for {fname} OK. proceeding to upload file...")
        cid = upload_file(fpath)
        if not cid:
            print(f"[ERR] failed uploading file {fname}.")
            continue
        # attach publisher_wallet and generated_at to meta and upload meta
        meta_update = dict(meta)
        meta_update.update({
            "ipfs_file_cid": cid,
            "publisher_wallet": WALLET,
            "uploaded_at": datetime.utcnow().isoformat()
        })
        meta_cid = upload_json(meta_update)
        if not meta_cid:
            print(f"[ERR] failed uploading meta for {fname} (file CID {cid})")
            continue
        print(f"[OK] FILE_CID: {cid} META_CID: {meta_cid}")
        append_uploaded_log(fname)
    print("[INFO] Uploader finished.")

if __name__ == "__main__":
    main()
