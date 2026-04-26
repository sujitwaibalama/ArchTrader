---
description: Run midday scan workflow manually (local mode)
---

Run the midday position scan using local .env credentials.

1. Read strategy doc, tail of TRADE-LOG, today's RESEARCH-LOG, CIRCUIT-BREAKER.
2. Pull positions and open orders.
3. v10 time exit: for each position, compute days-since-entry from TRADE-LOG. If ≥60, close + cancel stop + lesson card (exit_reason=time_60d). PEAD drift exhausts past day 60.
4. Tighten trailing stops on winners. For each eligible position run `bash scripts/atr.sh SYM` and recompute trail. At +20% trail = MAX(1.5×ATR, 5% of price); at +15% trail = MAX(2×ATR, 7% of price). Cancel old stop, place new `trailing_stop` with `trail_price` (not trail_percent). Never move a stop down.
5. Thesis check on each remaining position via Grok news. If thesis broke -> close + cancel stop + create lesson card (exit_reason=thesis_break) and fill in Setup/Expected/Actual/Why.
6. Optional intraday research if something is moving sharply.
7. Notify only if action was taken.

Local mode: no commit/push needed.
