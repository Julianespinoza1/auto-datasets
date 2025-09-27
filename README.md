# Auto Datasets — Seed Swarm

Automatic generation, upload, and sales tracking of **synthetic datasets** with metadata, fingerprints, and revenue logging.  
This workflow allows you to generate datasets for testing or modeling, upload them to **IPFS via Pinata**, and record each **real sale** in a JSON ledger.

---

## Quickstart

1. **Create a GitHub repository** and push all files:
   - `Generador.py` — generates high-quality synthetic datasets with metadata and file fingerprints.
   - `CargadorDePiñata.py` — securely uploads files and metadata to Pinata (IPFS).
   - `AdministradorDeIngresos.py` — records real sales in `ledger.json`.

2. **Set up GitHub Secrets**:
   - `PINATA_API_KEY` — your Pinata API Key.
   - `PINATA_API_SECRET` — your Pinata API Secret.
   - `WALLET_ADDRESS` — your wallet address for sales logging.

   > Optional: `REINVEST_PERCENT` is no longer used since this workflow no longer reinvests; all revenue is fully recorded.

3. **Enable the automatic workflow**:
   - Runs on the schedule defined in `.github/workflows/auto_pipeline.yml`.
   - Can also be triggered manually using `workflow_dispatch`.

4. **Check the ledger**:
   - Every sale is recorded in `ledger.json` with timestamp, amount, source, and currency (`USD`).
   - Fully **real and transparent**, no simulation.

---

## Important Notes

- All **datasets are synthetic**:  
  > `disclaimer`: `"THIS DATASET IS FULLY SYNTHETIC. NO REAL PERSONS OR ADDRESSES. FOR TESTING / MODELING ONLY."`
- Full **metadata** is generated with SHA256 fingerprint to ensure data integrity.
- No automatic reinvestment; **100% of revenue is under my control**.
- Keep your keys private and rotate any accidentally exposed credentials.
- Compatible with GitHub Actions, Replit, or any Python 3.11+ environment.

---

## Workflow Summary

1. `Generador.py` → generates a `.jsonl.gz` dataset + `.meta.json`.
2. `CargadorDePiñata.py` → uploads dataset and metadata to Pinata, stores the CIDs.
3. `AdministradorDeIngresos.py` → logs each real sale into `ledger.json`.
4. GitHub Actions → automates dataset generation, upload, and revenue logging.

---

With this setup, your workflow is **autonomous, secure, and legally compliant**, with synthetic datasets, real revenue tracking, and full control over your files and sales.
