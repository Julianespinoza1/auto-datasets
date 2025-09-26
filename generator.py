#!/usr/bin/env python3
# Generador.py — genera datasets sintéticos de alta calidad, metadata y schema

import json, random, time, uuid
from datetime import datetime, timezone

def generate_row(i):
    return {
        "uid": f"{int(time.time())}-{uuid.uuid4().hex[:6]}-{i}",
        "ts": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        "value": round(random.gauss(1000, 300) * random.random(), 4),
        "category": random.choice(["A","B","C","D"]),
        "flag": random.choice([True, False]),
        "geo": {"lat": round(random.uniform(-90,90),6), "lon": round(random.uniform(-180,180),6)}
    }

def generate_dataset(rows=10000):
    return [generate_row(i) for i in range(rows)]

def write_jsonl(dataset, outpath):
    with open(outpath, "w", encoding="utf-8") as f:
        for row in dataset:
            f.write(json.dumps(row, separators=(',',':')) + "\n")

if __name__ == "__main__":
    import os
    rows = int(os.getenv("ROWS_PER_DATASET","10000"))
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"dataset_{stamp}.jsonl"
    ds = generate_dataset(rows=rows)
    write_jsonl(ds, filename)

    # metadata
    meta = {
        "file": filename,
        "rows": len(ds),
        "generated_at": datetime.utcnow().isoformat(),
        "schema": {"uid":"string","ts":"datetime","value":"float","category":"string","flag":"bool","geo":"object"}
    }
    with open(filename + ".meta.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)

    print("Generated", filename)
