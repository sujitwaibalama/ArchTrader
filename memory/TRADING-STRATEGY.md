# Trading Strategy

## Mission
Beat the S&P 500 over the challenge window. Stocks only — no options, ever.

## Capital & Constraints
- Starting capital: ~$100,000
- Platform: Alpaca (paper first, then live)
- Instruments: Stocks ONLY
- PDT limit: 3 day trades per 5 rolling days (account < $25k)

## Core Rules (v3 — backtest-validated, see memory/BACKTEST-RESULTS.md)

1. NO OPTIONS — ever
2. 75-85% deployed
3. 5-6 positions at a time, max 20% each
4. **ATR-based trailing stop** on every position as a real GTC order. Trail = 2.5 × ATR(20) in DOLLARS, computed at entry via `bash scripts/atr.sh SYM`. Use `trail_price` (not `trail_percent`) on the Alpaca order.
5. **NO fixed -7% hard cut.** The ATR trail handles risk. Cutting at a fixed -7% was firing on normal pullbacks and turned 48% of trades into losers. (Backtest evidence: removing the hard cut + switching to ATR took the strategy from −32% to +7%.)
6. Tighten the trail at gain milestones: at +15% unrealized, tighten to MAX(2×ATR, 7%); at +20%, tighten to MAX(1.5×ATR, 5%). These rules had 100% win rates in the backtest — they are the only consistently winning behavior in the rulebook.
7. Never tighten within 3% of current price. Never move a stop down (only up).
8. Max 3 new trades per week
9. Follow sector momentum at the entry signal layer
10. Exit a sector after 2 consecutive failed trades (sector ban for 14 days)
11. **Thesis-break exit (manual)**: if the catalyst behind a position is invalidated (news, earnings miss, macro shift), close immediately even before the trail fires. This is the ONLY discretionary exit.
12. Patience > activity. Default to HOLD if no edge.
13. Every trade must have a documented catalyst before execution

## Entry Checklist
- Specific catalyst documented in today's RESEARCH-LOG?
- Sector in top 3 by 60-day momentum (XLE/XLK/XLF/XLV/XLY/XLC/XLP/XLI/XLB/XLRE/XLU)?
- ATR(20) computed and stop placed?
- Position size = 18% of equity (within 20% rule, leaves slack for slippage)?
- Lessons: did `memory/lessons/INDEX.md` flag any matching patterns? Apply the lesson.

## Sell Rules
- Trailing stop fires (handled automatically by Alpaca GTC order). Done.
- Thesis broke (catalyst invalidated, sector rolling over): close even if trail hasn't fired
- Up >= +20%: tighten trailing stop to MAX(1.5×ATR, 5%)
- Up >= +15%: tighten trailing stop to MAX(2×ATR, 7%)
- 2 consecutive failed trades in a sector: exit all positions in that sector and ban for 14 days

## Backtest Reality Check (2024-01 → 2026-04, 580 days)

| Variant | Return | Alpha vs SPY | Sharpe | Max DD | PF |
|---|---|---|---|---|---|
| **v3 — current ruleset** (ATR 2.5×, no hard cut) | **+7.2%** | **−48.2%** | 0.27 | 23.4% | **1.12** |
| v1 — old ruleset (10% trail + −7% hard cut) | −31.9% | −87.3% | −1.09 | 37.4% | 0.43 |

v3 is the best of 7 tested variants but still loses to SPY (+55.4% buy-and-hold). The current strategy preserves capital and grows it modestly; it does NOT outperform a passive index hold yet. Phase 2C (post-earnings drift) is the planned attempt to find an edge that beats SPY.

## Things proven NOT to work (don't reintroduce without re-backtesting)

- Fixed-percentage trailing stops (10%, 15%): too tight on volatile names, too loose on calm names
- −7% hard cut: fires on normal pullbacks; 3% win rate in backtest
- Tightening sooner than +15%: strangles winners; v7_baseline_tighten_sooner backtested −29.3%
- Pullback-entry filtering (was tested as v5/v6): no meaningful improvement
