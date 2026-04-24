---
description: Run end-of-day summary workflow manually (local mode)
---

Run the EOD summary workflow using local .env credentials.

1. Pull live account state: bash scripts/alpaca.sh account, positions, orders.
2. Update memory/PORTFOLIO-STATE.md with fresh snapshot.
3. Append EOD snapshot to memory/TRADE-LOG.md.
4. Final sell-side check: cut anything at -7%, verify stop tightening on winners.
5. Send one Telegram summary (always sends — portfolio, day P&L, open positions).

Local mode: no commit/push needed.
