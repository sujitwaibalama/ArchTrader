---
description: Run pre-market research workflow manually (local mode)
---

Run the pre-market research workflow using local .env credentials.

1. Read in this order: (a) memory/DAILY-REFLECTION.md (most recent entry — yesterday's brain), (b) memory/EDGE-TRACKER.md (Last-30/90 — apply FAVOR/DEMOTE), (c) memory/lessons/INDEX.md (open any card matching today's setups), (d) memory/TRADING-STRATEGY.md, tail of TRADE-LOG.md, tail of RESEARCH-LOG.md, PORTFOLIO-STATE.md, CIRCUIT-BREAKER.md.
1b. Run `bash scripts/gap-scan.sh --top 10` to get v10 entry candidates. For each top candidate, use Grok to identify the catalyst behind the gap day. Skip any without a clear catalyst.
2. Pull live account state: bash scripts/alpaca.sh account, positions, orders.
3. Research market context via Grok (search, sentiment, news on held tickers).
4. Write dated entry to memory/RESEARCH-LOG.md with account snapshot, "Yesterday's reflection applied" note, "Edge-tracker bias" note, market context, 2-3 trade ideas (each tagged catalyst_type), risk factors, decision.
4b. Append one decision-journal line per candidate (BUY-PLAN or SKIP) to memory/DECISION-JOURNAL.md.
5. Update memory/PORTFOLIO-STATE.md.
6. Notify only if urgent.

Local mode: no commit/push needed (you can commit manually if desired).
