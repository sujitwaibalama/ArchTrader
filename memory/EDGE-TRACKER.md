# Edge Tracker

**Which catalyst types are working RIGHT NOW.** Backtest tells us PEAD works on average over 2 years. This file tells us which flavors of PEAD are paying THIS MONTH. Alpha decays — this is how we see it.

## How it works

Every closed trade gets one row. The catalyst_type is one of:
`earnings_beat`, `earnings_miss_buy`, `fda_approval`, `contract_win`, `m_and_a`, `analyst_upgrade`, `product_launch`, `guidance_raise`, `macro_news`, `other`.

Daily-summary appends a row for each position closed that day. Pre-market reads the rolling last-30 and last-90 day stats and biases candidate selection (e.g., if `fda_approval` is 0/4 over 90 days, demote any FDA-driven candidate; if `earnings_beat` is 8/10, weight those higher).

## Rolling Stats (auto-updated by daily-summary)

### Last 30 days
| Catalyst Type | Trades | Wins | Win % | Avg P&L % | Status |
|---------------|--------|------|-------|-----------|--------|
| _no data yet_ |        |      |       |           |        |

### Last 90 days
| Catalyst Type | Trades | Wins | Win % | Avg P&L % | Status |
|---------------|--------|------|-------|-----------|--------|
| _no data yet_ |        |      |       |           |        |

### Status legend
- ✅ FAVOR  — win% ≥ 55% AND ≥4 trades
- ⚠️ NEUTRAL — 4-trade min not met yet, or win% 40-55%
- 🚫 DEMOTE — win% < 40% on ≥4 trades. Demote in pre-market candidate ranking.

## Trade-by-trade ledger (raw data)

Newest at the bottom. Daily-summary appends here when a position closes.

| Date | Ticker | Sector | Catalyst Type | Entry | Exit | P&L % | Hold Days | Exit Reason |
|------|--------|--------|---------------|-------|------|-------|-----------|-------------|
| _no closed trades yet_ | | | | | | | | |

---

## Notes on use

- A catalyst type with <4 trades is statistically meaningless. Don't act on it.
- If 30d differs sharply from 90d, the regime is changing — flag in next weekly-review.
- This tracker only sees CLOSED trades. Open positions don't count until they exit.
