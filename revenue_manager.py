#!/usr/bin/env python3
# AdministradorDeIngresos.py — registra ventas reales en ledger.json sin simulación ni reinversiones

import os
import json
import time
from datetime import datetime
import argparse

LEDGER_FILE = os.getenv("LEDGER_FILE", "ledger.json")

def ensure_ledger():
    """Crea el ledger si no existe"""
    if not os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def record_sale(amount, currency="USD", source="market", tx_id=None, buyer=None, cid=None, notes=None):
    """Registra una venta real"""
    ensure_ledger()
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "epoch": time.time(),
        "amount": float(amount),
        "currency": currency,
        "source": source,
        "tx_id": tx_id,
        "buyer": buyer,
        "cid": cid,
        "notes": notes
    }
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    ledger.append(entry)
    with open(LEDGER_FILE, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    return entry

def show_ledger():
    """Muestra todo el ledger"""
    ensure_ledger()
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    return ledger

def cli():
    parser = argparse.ArgumentParser(description="Administrador de ventas reales")
    sub = parser.add_subparsers(dest="cmd")

    rec = sub.add_parser("record", help="Registrar una venta")
    rec.add_argument("--amount", required=True, type=float)
    rec.add_argument("--currency", default="USD")
    rec.add_argument("--source", default="market")
    rec.add_argument("--tx-id")
    rec.add_argument("--buyer")
    rec.add_argument("--cid")
    rec.add_argument("--notes")

    show = sub.add_parser("show", help="Mostrar ledger completo")

    args = parser.parse_args()
    if args.cmd == "record":
        entry = record_sale(
            amount=args.amount,
            currency=args.currency,
            source=args.source,
            tx_id=args.tx_id,
            buyer=args.buyer,
            cid=args.cid,
            notes=args.notes
        )
        print(json.dumps(entry, indent=2))
    elif args.cmd == "show":
        ledger = show_ledger()
        print(json.dumps(ledger, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()
