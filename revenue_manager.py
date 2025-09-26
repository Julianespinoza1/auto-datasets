#!/usr/bin/env python3
import os, json, time

REINVEST_PERCENT = float(os.getenv("REINVEST_PERCENT","0.20"))
LEDGER_FILE = "ledger.json"

def record_sale(amount, source="market"):
    entry = {"ts": time.time(), "amount": float(amount), "source": source}
    ledger = []
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE,"r") as f:
            ledger = json.load(f)
    ledger.append(entry)
    with open(LEDGER_FILE,"w") as f:
        json.dump(ledger, f, indent=2)
    return entry

def settle_day():
    if not os.path.exists(LEDGER_FILE):
        print("No sales yet.")
        return
    with open(LEDGER_FILE,"r") as f:
        ledger = json.load(f)
    total = sum(e["amount"] for e in ledger)
    reinvest = total * REINVEST_PERCENT
    payout = total - reinvest
    with open(LEDGER_FILE,"w") as f:
        json.dump([], f)
    print(f"Total sales: ${total:.2f} | Reinvest: ${reinvest:.2f} | To you: ${payout:.2f}")
    return {"total":total,"reinvest":reinvest,"payout":payout}

if __name__ == "__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=="settle":
        settle_day()
    else:
        amt = float(os.getenv("SIM_SALE_AMT","100.0"))
        entry = record_sale(amt)
        print("Recorded sale", entry)
