# Auto Datasets — Seed Swarm

## Quickstart
1. Create GitHub repo and push files.
2. Add GitHub Secrets:
   - PINATA_API_KEY
   - PINATA_API_SECRET
   - WALLET_ADDRESS
   - REINVEST_PERCENT (optional, default 0.20)
3. Ensure generator.py, uploader_pinata.py, revenue_manager.py are in repo.
4. Trigger the workflow or wait for schedule.

## Notes
- **Rotate** any keys you accidentally shared publicly.
- Use market webhooks to record real sales into ledger.json (revenue_manager).
