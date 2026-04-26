---
description: Run pre-market research workflow manually (local mode)
---

Run the pre-market research workflow using local .env credentials.

1. Read memory/TRADING-STRATEGY.md, tail of TRADE-LOG.md, tail of RESEARCH-LOG.md, PORTFOLIO-STATE.md, CIRCUIT-BREAKER.md, memory/lessons/INDEX.md (scan; open matching lesson cards for any candidate idea before deciding).
2. Pull live account state: bash scripts/alpaca.sh account, positions, orders.
3. Research market context via Grok (search, sentiment, news on held tickers).
4. Write dated entry to memory/RESEARCH-LOG.md with account snapshot, market context, 2-3 trade ideas, risk factors, decision.
5. Update memory/PORTFOLIO-STATE.md.
6. Notify only if urgent.

Local mode: no commit/push needed (you can commit manually if desired).
