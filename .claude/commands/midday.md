---
description: Run midday scan workflow manually (local mode)
---

Run the midday position scan using local .env credentials.

1. Read strategy doc, tail of TRADE-LOG, today's RESEARCH-LOG, CIRCUIT-BREAKER.
2. Pull positions and open orders.
3. Cut any position at -7% or worse. Cancel its stop. Log the exit.
4. Tighten trailing stops on winners (+20% -> 5% trail, +15% -> 7% trail).
5. Thesis check on each remaining position via Grok news.
6. Optional intraday research if something is moving sharply.
7. Notify only if action was taken.

Local mode: no commit/push needed.
