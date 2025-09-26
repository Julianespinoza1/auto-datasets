#!/usr/bin/env python3
# Generador.py — generador robusto de datasets sintéticos con metadata y fingerprint
# Uso:
#   export ROWS_PER_DATASET=5000
#   export SEED=12345
#   export OUT_DIR=./
#   python Generador.py

import os
import json
import random
import time
import uuid
import gzip
import hashlib
import math
from datetime import datetime, timezone

# CONFIG via ENV
ROWS = int(os.getenv("ROWS_PER_DATASET", "5000"))
SEED = os.getenv("SEED", None)
PREFIX = os.getenv("PREFIX", "dataset")
OUT_DIR = os.getenv("OUT_DIR", ".")
DP_EPSILON = float(os.getenv("DP_EPSILON", "0.0"))   # 0.0 = off
DP_SENSITIVITY = float(os.getenv("DP_SENSITIVITY", "1.0"))
COMPRESS = os.getenv("COMPRESS", "1") not in ("0", "false", "False")
GENERATOR_VERSION = "gen-1.1"

def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def laplace_sample(mu=0.0, b=1.0):
    # Robust Laplace sampler using inverse CDF
    u = random.random() - 0.5
    return mu - b * math.copysign(1.0, u) * math.log(1 - 2 * abs(u))

def sha256_of_file(path, bufsize=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def generate_row(i):
    base_value = max(0.0, random.gauss(1000.0, 300.0) * random.random())
    if DP_EPSILON > 0.0:
        scale = DP_SENSITIVITY / DP_EPSILON
        value = round(max(0.0, base_value + laplace_sample(0, scale)), 6)
    else:
        value = round(base_value, 6)
    return {
        "uid": f"{int(time.time())}-{uuid.uuid4().hex[:6]}-{i}",
        "ts": now_iso(),
        "value": value,
        "category": random.choice(["A","B","C","D"]),
        "flag": random.choice([True, False]),
        "geo": {"lat": round(random.uniform(-90,90),6), "lon": round(random.uniform(-180,180),6)},
        "synthetic": True
    }

def write_stream_jsonl(rows_generator, outpath, compress=True):
    if compress:
        with gzip.open(outpath, "wt", encoding="utf-8") as f:
            for row in rows_generator:
                f.write(json.dumps(row, separators=(",",":")) + "\n")
    else:
        with open(outpath, "w", encoding="utf-8") as f:
            for row in rows_generator:
                f.write(json.dumps(row, separators=(",",":")) + "\n")

def rows_gen(n):
    for i in range(n):
        yield generate_row(i)

def ensure_outdir(path):
    os.makedirs(path, exist_ok=True)

def main():
    # seed deterministically if provided
    if SEED is not None:
        try:
            s = int(SEED)
        except:
            s = sum(map(ord, str(SEED)))
        random.seed(s)
    else:
        s = int(time.time()) ^ os.getpid()
        random.seed(s)

    ensure_outdir(OUT_DIR)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"{PREFIX}_{stamp}.jsonl" + (".gz" if COMPRESS else "")
    outpath = os.path.join(OUT_DIR, fname)

    print(f"[info] Generating dataset rows={ROWS} seed={s} -> {outpath}")

    # stream write (no large list in memory)
    try:
        write_stream_jsonl(rows_gen(ROWS), outpath, compress=COMPRESS)
    except Exception as e:
        print(f"[error] Writing dataset failed: {e}")
        raise

    # metadata & provenance
    meta = {
        "file": fname,
        "rows": ROWS,
        "generated_at": now_iso(),
        "generator_version": GENERATOR_VERSION,
        "seed_used": s,
        "schema": {
            "uid":"string",
            "ts":"datetime(UTC)",
            "value":"float (synthetic)",
            "category":"string",
            "flag":"bool",
            "geo":"object{lat,lon}",
            "synthetic":"bool"
        },
        "dp": {
            "enabled": DP_EPSILON > 0.0,
            "epsilon": DP_EPSILON if DP_EPSILON > 0.0 else None,
            "sensitivity": DP_SENSITIVITY if DP_EPSILON > 0.0 else None,
            "note": "Laplace noise applied to 'value' if enabled; not a formal DP proof"
        },
        "disclaimer": "THIS DATASET IS FULLY SYNTHETIC. NO REAL PERSONS OR ADDRESSES. FOR TESTING / MODELING ONLY.",
        "license": "Data marked synthetic; buyer must acknowledge synthetic nature."
    }

    # compute fingerprint
    try:
        fingerprint = sha256_of_file(outpath)
        meta["file_sha256"] = fingerprint
    except Exception as e:
        meta["file_sha256"] = None
        print(f"[warn] fingerprint computation failed: {e}")

    meta_path = outpath + ".meta.json"
    try:
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(meta, mf, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[error] Writing metadata failed: {e}")
        raise

    print(f"[info] Wrote dataset {outpath}")
    print(f"[info] Wrote metadata {meta_path}")
    print(f"[info] SHA256: {meta.get('file_sha256')}")
    print("[info] DONE")

if __name__ == "__main__":
    main()
