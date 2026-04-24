---
description: Run market-open execution workflow manually (local mode)
---

Run the market-open workflow using local .env credentials.

1. Read today's RESEARCH-LOG entry. If missing, run pre-market steps inline first.
2. Re-validate each planned trade with fresh quotes.
3. Run safety-check.sh on each planned buy. Skip any that fail.
4. Execute approved buys (market orders, day TIF).
5. Place 10% trailing stop GTC for each new position. Fallback: fixed stop -> queue for tomorrow.
6. Log each trade to memory/TRADE-LOG.md.
7. Notify only if a trade was placed.

Local mode: no commit/push needed.
