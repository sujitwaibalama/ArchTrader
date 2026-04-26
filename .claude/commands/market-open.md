---
description: Run market-open execution workflow manually (local mode)
---

Run the market-open workflow using local .env credentials.

1. Read today's RESEARCH-LOG entry. If missing, run pre-market steps inline first.
2. Re-validate each planned trade with fresh quotes.
3. Run safety-check.sh on each planned buy. Skip any that fail.
4. Execute approved buys (market orders, day TIF).
5. Compute ATR(20) for each new position via `bash scripts/atr.sh SYM`, then place a `trailing_stop` GTC order with `trail_price` = trail_dollars (NOT trail_percent). Fallback: fixed stop at entry - trail_dollars -> queue for tomorrow if blocked.
6. Log each trade to memory/TRADE-LOG.md (include catalyst_type).
6b. Append one decision-journal line per candidate (BUY / SKIP / BLOCKED) to memory/DECISION-JOURNAL.md with reason.
7. Notify only if a trade was placed.

Local mode: no commit/push needed.
