# Daily Reflection

**The bridge between yesterday and today.** Every daily-summary appends one entry. Every pre-market reads the most recent entry FIRST, before generating ideas.

## Format

Each entry is short. Four sections, ≤2 bullets each. The point is to compress a day into something tomorrow's bot can act on in 30 seconds.

```
## YYYY-MM-DD — Reflection

### What worked today
- <specific action / signal / lesson that paid off>

### What didn't work
- <action / setup that misfired — name the pattern, not just the ticker>

### Market regime read
- Risk-on / risk-off / mixed. Leadership: <sectors>. VIX: X. SPY: ±X%.

### Watching tomorrow
- <specific tickers, sectors, levels, or catalysts to track>
- <any rule we should bias toward or away from given today's evidence>
```

## Why this file exists

Lesson cards are per-trade. This file is per-day. Markets have *days* and *regimes*, not just trades. A bot that only reads lesson cards misses regime shifts (e.g., "tech leadership rolled over today, lighten new tech entries tomorrow").

The pre-market routine reads only the **most recent entry**. To look back further, scan this file or grep.

---

<!-- Entries appended below by daily-summary, newest at the bottom -->

## 2026-04-26 — Reflection

### What worked today
- No closes today; weekend non-trading day. Both positions tracking near-flat since Friday open: XOM +1.0%, NVDA −0.95%.

### What didn't work
- Stops are still legacy 10% trail_percent (v1) — not v10 ATR-dollar stops. Migration planned for Mon market-open.

### Market regime read
- Last trading day (Fri Apr 24): mixed. SPY closed at $714.01, +0.46% since phase start. Bot equity $100,010 (+0.01%). Alpha: −0.45%.
- Energy (XOM) holding gains; Technology (NVDA) slightly underwater on AI infrastructure position.

### Watching tomorrow
- Execute v10 migration at Mon open: cancel legacy stops on XOM + NVDA, close both, run gap-scan, redeploy 2-3 v10 candidates with ATR trail_price stops.
- Watch for gap-scan candidates with fresh earnings/catalyst catalysts from weekend news.
- Bias toward earnings_beat catalyst type (strongest PEAD signal from backtest).
