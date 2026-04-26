# Trading Strategy

## Mission
Beat the S&P 500 over the challenge window. Stocks only — no options, ever.

## Capital & Constraints
- Starting capital: ~$100,000
- Platform: Alpaca (paper first, then live)
- Instruments: Stocks ONLY
- PDT limit: 3 day trades per 5 rolling days (account < $25k)

## Strategy: v10 — catalyst-driven gap-up swing

**Mental model**: Don't buy what's already running. Buy stocks the *day after* a fresh positive catalyst (earnings beat, contract win, FDA decision, M&A news) when they gapped up and held the gap. Ride the post-catalyst drift for 30-60 days.

This is the academic Post-Earnings Announcement Drift effect (PEAD), generalized to all positive-catalyst gaps. Backtest evidence below.

## Core Rules

1. NO OPTIONS — ever
2. 5-6 positions at a time, max 20% per position
3. Position sizing: 18% of equity per entry (within 20% rule, leaves slippage slack)
4. Max 3 new trades per week (across the whole bot, all sectors)
5. **Entry signal — gap-up catalyst** (run `bash scripts/gap-scan.sh` every pre-market):
   - Stock had a ≥3% gap-up open in the last 5 trading days
   - That gap day closed at or above its open (the gap *held* — no fade)
   - Stock is currently above its 50-day SMA (uptrend filter)
   - Score = gap_size × recency_weight; take top candidates by score
   - Sector-agnostic — any stock in the universe qualifies
6. **ATR-based trailing stop** on every position as a real GTC order. Trail = 2.5 × ATR(20) in DOLLARS, computed at entry via `bash scripts/atr.sh SYM`. Use `trail_price` (not `trail_percent`) on the Alpaca order.
7. **NO fixed hard cut.** The ATR trail handles risk.
8. Tighten the trail at gain milestones: at +15% unrealized, tighten to MAX(2×ATR, 7%); at +20%, tighten to MAX(1.5×ATR, 5%). Never tighten within 3% of current price. Never move a stop down.
9. **60-day max hold**: if a position is still open 60 calendar days after entry, close it at next open. PEAD drift exhausts ~60 days post-catalyst; holding longer loses edge.
10. **Thesis-break exit (manual)**: if the catalyst is invalidated (earnings re-cut, FDA reject, M&A break), close immediately even before trail/time fires. The only discretionary exit.
11. Sector ban: 2 consecutive failed trades in the same sector → 14-day ban from new entries in that sector
12. Patience > activity. Default to HOLD if no scan candidates clear the bar.
13. Every trade must have a documented catalyst before execution

## Entry Checklist

Run before EVERY new buy order:
- [ ] `bash scripts/gap-scan.sh` produced a candidate list with score > 0
- [ ] Specific catalyst documented in today's RESEARCH-LOG (what happened on the gap day — earnings? news? contract?)
- [ ] `bash scripts/safety-check.sh BUY SYM QTY PRICE SECTOR` passed
- [ ] `bash scripts/atr.sh SYM` ran successfully — trail_dollars in hand
- [ ] `memory/lessons/INDEX.md` checked for matching pattern tags (e.g., `gap-up`, sector, similar setup)
- [ ] Position size = 18% of equity (rounded down to whole shares)

## Sell Rules

- ATR trailing stop fires automatically (Alpaca GTC). Don't preempt on price action alone.
- Position held ≥60 calendar days since entry: close at next open (time exit).
- Thesis broke (catalyst invalidated, sector rolling over, breaking news): close immediately.
- Up ≥+20%: tighten trail to MAX(1.5×ATR, 5% of current price).
- Up ≥+15%: tighten trail to MAX(2×ATR, 7% of current price).
- 2 consecutive failed trades in a sector: exit all positions in that sector.

## Backtest Evidence (2024-01 → 2026-04, 580 trading days)

| Variant | Return | Alpha vs SPY | Sharpe | Max DD | Win | PF |
|---|---|---|---|---|---|---|
| **v10 — current ruleset** (gap-up + ATR 2.5× + 60d max) | **+43.7%** | -11.7% | **1.28** | **11.6%** | 54% | 1.91 |
| v8 (gap-up + ATR 2.5×, no time cap) | +42.2% | -13.2% | 1.17 | 13.3% | 56% | 2.03 |
| v11 (gap-up 5%+ min) | +35.1% | -20.3% | — | — | **59%** | **2.32** |
| v3 (sector-momentum + ATR — old strategy) | +7.2% | -48.2% | 0.27 | 23.4% | 39% | 1.12 |
| v1 (sector-momentum + 10% trail + −7% cut — original) | -31.9% | -87.3% | -1.09 | 37.4% | 24% | 0.43 |
| SPY buy-and-hold (benchmark) | +55.4% | — | — | — | — | — |

**Honest read of v10**: still loses to SPY in this window — but the window is a roaring bull (+55% in 28 months). v10 has Sharpe 1.28, max drawdown 11.6%, win rate 54%, profit factor 1.91 — these are genuinely-good risk-adjusted numbers. In flat or bear regimes, v10's natural cash management (sits in cash when no catalysts qualify) should outperform a passive SPY hold.

## Things proven NOT to work (don't reintroduce without re-backtesting)

- Fixed-percentage trailing stops (10%, 15%): too tight on volatile names, too loose on calm names; v1/v2 backtests
- −7% hard cut: fires on normal pullbacks, 3% win rate when it fired; killed v1
- Sector-momentum entry (v1-v7 family): best variant gave -48% alpha; entry signal is the bottleneck
- Tightening sooner than +15%: strangles winners; v7 was -29.3%
- Pullback-entry filtering as standalone signal: v5/v6 gave -56% alpha
