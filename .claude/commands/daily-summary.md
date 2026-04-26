---
description: Run end-of-day summary workflow manually (local mode)
---

Run the EOD summary workflow using local .env credentials.

1. Pull live account state: bash scripts/alpaca.sh account, positions, orders.
2. Update memory/PORTFOLIO-STATE.md with fresh snapshot. Refresh the SPY benchmark via `bash scripts/spy-benchmark.sh` and update the Benchmark section with bot equity, SPY equiv, alpha.
3. Append EOD snapshot to memory/TRADE-LOG.md.
4. Final sell-side check (v10): close any position held ≥60 days, verify stop tightening on winners (+15% / +20%). No -7% hard cut.
4b. For every position closed today, create a lesson card via scripts/lesson-card.sh and fill in Setup/Expected/Actual/Why.
4c. Update memory/EDGE-TRACKER.md: append a row per closed trade, then recompute Last-30 / Last-90 win% per catalyst type and reset FAVOR/NEUTRAL/DEMOTE statuses.
4d. Append today's reflection to memory/DAILY-REFLECTION.md (always — even on no-trade days). Sections: What worked / What didn't / Market regime / Watching tomorrow.
5. Send one Telegram summary (always sends — portfolio, day P&L, open positions).

Local mode: no commit/push needed.
