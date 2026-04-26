# Portfolio State

Updated by every routine run. Current snapshot of account and positions.

## Last Updated
2026-04-26 EOD (daily-summary, weekend — no market)

## Account
- Equity: $100,010.16
- Cash: $60,329.93
- Buying Power: $160,340.09
- Deployed: ~39.7% ($39,680.23 in 2 positions)
- Daytrade Count: 0

## Benchmark — vs SPY (phase start 2026-04-24, $100,000)
Update on every daily-summary run via: `bash scripts/spy-benchmark.sh`
- Bot equity: $100,010.16 (+0.01%)
- SPY equiv:  $100,457.97 (+0.46%)
- Alpha:      −0.45% (last update 2026-04-26 EOD)

## Open Positions
| Symbol | Shares | Entry | Sector | Cost Basis | Stop |
|--------|--------|-------|--------|------------|------|
| XOM | 135 | $147.44 | Energy | $19,904.40 | 10% trail (init $132.67) |
| NVDA | 94 | $210.27 | Technology | $19,765.38 | 10% trail (init $189.32) |

## Pending Orders
| Type | Symbol | Qty | Trail | Order ID |
|------|--------|-----|-------|----------|
| Trailing Stop GTC | XOM | 135 | 10% (legacy v1) | fa892987-5f63-43af-8e58-af2aa8153e9f |
| Trailing Stop GTC | NVDA | 94 | 10% (legacy v1) | 5af7082f-46b1-4041-9c85-913f471a884e |

## Planned for 2026-04-27 (Mon market open)
**v10 migration** (approved by user, plan in RESEARCH-LOG 2026-04-27 entry):
1. Cancel both legacy stops above
2. Close XOM and NVDA at market
3. Run fresh gap-scan + Grok catalyst confirmation
4. Deploy 2-3 v10 candidates with ATR-based trail_price stops
