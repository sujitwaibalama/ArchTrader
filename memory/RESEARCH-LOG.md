# Research Log

Daily pre-market research entries will be appended here. Format each entry:

## YYYY-MM-DD — Pre-market Research

### Account
- Equity: $X
- Cash: $X
- Buying power: $X
- Daytrade count: N

### Market Context
- WTI / Brent:
- S&P 500 futures:
- VIX:
- Today's catalysts:
- Earnings before open:
- Economic calendar:
- Sector momentum:

### Trade Ideas
1. TICKER — catalyst, entry $X, stop $X, target $X, R:R X:1
2. ...

### Risk Factors
- ...

### Decision
TRADE or HOLD (default HOLD if no edge)

---

## 2026-04-24 — Pre-market Research (run at market-open, 12:36 PM ET)

### Account
- Equity: $100,000.00
- Cash: $100,000.00
- Buying power: $200,000.00 (2x margin, using cash only)
- Daytrade count: 0/3

### Market Context
- S&P 500: ~7,121 (+0.18% today), pulled back from all-time highs. YTD roughly flat after rocky start.
- VIX: ~18.84 (below 19 — calm, declining from peak of 31 on March 27)
- Oil (Brent): ~$93-95/barrel, up from $70s earlier in 2026 due to Iran war; peaked near $120, now easing. EIA forecasts $115/b peak in Q2.
- Iran conflict: Persistent macro catalyst for energy. US/Israeli strikes on Iran since late Feb 2026 upended global energy markets.
- Sector momentum YTD: Energy +25% >> S&P 500 +2%. Technology also strong in April. Healthcare decent.
- Earnings catalyst today: Intel Q1 beat boosted semiconductor sentiment; NVDA +4.46% in sympathy.
- No major economic releases flagged today (Friday).

### Live Quotes Checked (via Alpaca)
- XOM: ask $147.28 / bid $147.24 — tight spread ✅
- CVX: ask $187.59 / bid $175.98 — WIDE $11.61 spread, skip (halted/illiquid) ❌
- NVDA: ask $210.87 / bid $210.84 — tight spread ✅

### Trade Ideas

1. **XOM (ExxonMobil) — Energy**
   - Catalyst: Iran war driving oil to $93-95/b with potential Q2 spike to $115/b; energy sector #1 YTD +25%; XOM is the sector leader with 2.7% dividend yield providing downside cushion
   - Entry: ~$147.28 (ask)
   - Shares: 135 (cost $19,882.80 = 19.9% of equity)
   - 10% trailing stop: auto via GTC order
   - Target: $167 (+13.5%, R:R ~1.3:1 vs 10% stop) — conservative; upside to $115/b oil is bigger
   - Sector: Energy (not banned, 0 consecutive losses)

2. **NVDA (NVIDIA) — Technology**
   - Catalyst: Intel Q1 beat created semiconductor sector tailwind today; NVDA +4.46%; AI infrastructure demand secular trend; 12-month analyst target $227
   - Entry: ~$210.87 (ask)
   - Shares: 94 (cost $19,821.78 = 19.8% of equity)
   - 10% trailing stop: auto via GTC order
   - Target: $240 (+13.8%, R:R ~1.4:1 vs 10% stop)
   - Sector: Technology (not banned)
   - Risk: Friday buy, high P/E, momentum name — gap risk over weekend

### Risk Factors
- Friday afternoon entry — weekend gap risk on both names
- Iran war: any ceasefire news over weekend = oil/energy drops sharply
- VIX falling = complacency risk; reversal could hit both positions
- CVX wide spread signals possible energy sector issue — monitor XOM closely

### Decision
**TRADE** — XOM first (clearest sector momentum + persistent catalyst). NVDA as optional second position if XOM safety check passes cleanly and capital allows.
- Weekly trade count after: 1 of 3 (XOM), 2 of 3 (NVDA if added)

---

## 2026-04-27 — Pre-market Plan (v10 migration, written 2026-04-25 Sat)

### Strategy version
v10 (catalyst-driven gap-up) — promoted in commit 3d645b5. Replaces v1 sector-momentum entry signal. See memory/TRADING-STRATEGY.md and memory/BACKTEST-RESULTS.md.

### Migration plan
The two open legacy positions (XOM, NVDA) were entered Fri 2026-04-24 under v1. Under v10's gap-scan they would not have qualified. User has approved closing them and redeploying per v10. Specifically:
1. CANCEL existing trailing stops:
   - XOM stop order id `fa892987-5f63-43af-8e58-af2aa8153e9f` (10% trail_percent)
   - NVDA stop order id `5af7082f-46b1-4041-9c85-913f471a884e` (10% trail_percent)
2. CLOSE both positions at market (`bash scripts/alpaca.sh close XOM` and `... close NVDA`).
3. Log realized P&L to TRADE-LOG with reason `v10_migration` and create lesson cards (exit_reason=v10_migration, tags include `v1-rule-retired`).
4. Update CIRCUIT-BREAKER weekly trade counter for the new week — the migration closes do NOT count as new trades. Set `Trades this week: 0` with note about the one-time migration.

### Account snapshot at plan time (Sat 2026-04-25 ~20:30 ET)
- Equity: ~$100,010 (live), ~$100,005 EOD Fri
- Cash: $60,329.93 (~60% in cash, 40% in XOM+NVDA)
- Buying power: $160,335
- Daytrade count: 0 (Fri's trades were 1-day holds, will round-trip Mon — not day trades, PDT-safe)

### v10 gap-scan candidates (preview from `bash scripts/gap-scan.sh 2026-04-24`)

| Rank | Ticker | Sector | Score | Last Close | SMA50 | Notes |
|---|---|---|---|---|---|---|
| 1 | **AMD** | Technology | 0.103 | $347.78 | $221.57 | Massive +57% gap-up zone — ATR(20)=$12.74, trail_dollars=$31.86 (9.2%). Strong PEAD candidate. |
| 2 | **QCOM** | Technology | 0.087 | $148.93 | $134.31 | +11% above SMA50. ATR(20)=$3.81, trail_dollars=$9.52 (6.4%). |
| 3 | BA | Industrials | 0.022 | $232.44 | $218.59 | Mild signal — score below the conviction threshold; skip unless catalyst is exceptional. |

### Catalyst confirmation needed (Monday pre-market step)
Before Monday execution, run `bash scripts/grok.sh news "AMD earnings 2026-04-22..2026-04-24"` and same for QCOM. Confirm there is a real news catalyst (earnings beat / contract / FDA / acquisition / upgrade) behind each candidate's gap. Skip any candidate without a confirmable catalyst — v10 edge depends on real news, not noise.

### Monday execution plan
After closes:
- Cash on hand will be ~$100k (full cash, 0 positions)
- Run fresh `bash scripts/gap-scan.sh --top 10` (will reflect Monday morning data, may differ from this preview)
- For each top candidate confirmed by Grok catalyst:
  - `bash scripts/safety-check.sh BUY SYM QTY PRICE SECTOR`
  - `bash scripts/atr.sh SYM` -> trail_dollars
  - Buy 18% of equity (whole shares, rounded down)
  - Place trailing_stop GTC with `trail_price` (NOT trail_percent)
- Target 2-3 fresh positions Monday. Reserve any remaining buy slots for the rest of the week.

### Position size preview (if AMD + QCOM are still candidates Monday)
| Ticker | Target | Last $ | Shares | Cost | Trail$ | Initial Stop |
|---|---|---|---|---|---|---|
| AMD | 18% of $100k = $18,000 | $347.78 | 51 | $17,737 | $31.86 | $315.92 |
| QCOM | 18% of $100k = $18,000 | $148.93 | 120 | $17,872 | $9.52 | $139.41 |

Total deployed: ~$35,609 (35.6%). Leaves ~$64k cash for a 3rd position later this week if a gap surfaces.

### Risk Factors
- AMD is at extreme premium to SMA50 (+57%); a single-day mean reversion could take a chunk before the trail catches up. Wide ATR trail ($31.86) is sized to absorb volatility.
- 2 of 3 top candidates are Technology — sector concentration risk if tech rolls over. Monitor XLK Monday morning.
- Tech earnings season is ongoing — any peer miss could cascade.
- Universe is small (58 large-caps). Real PEAD edge is stronger on small/mid-caps; future iteration.

### Decision
**TRADE** — execute migration + 2-3 v10 entries Monday, with Grok-confirmed catalyst per candidate. Default HOLD on any candidate without a confirmable catalyst.
