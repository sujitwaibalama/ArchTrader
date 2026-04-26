# Backtest Results — Variant Comparison

**Window:** 2024-01-02 → 2026-04-24 (580 trading days)

**Benchmark (SPY buy-hold):** $155,368 (+55.37%)

**Initial capital:** $100,000


## Variants ranked by alpha vs SPY

| Variant | Final $ | Return | Alpha | Sharpe | MaxDD | Trades | Win | PF | AvgHold |
|---|---|---|---|---|---|---|---|---|---|
| v10_gap_up_atr2.5_60d_max | $143,698 | +43.7% | **-11.7%** | 1.28 | 11.6% | 76 | 54% | 1.91 | 34d |
| v8_gap_up_atr2.5 | $142,210 | +42.2% | **-13.2%** | 1.17 | 13.3% | 68 | 56% | 2.03 | 45d |
| v9_gap_up_atr3 | $136,959 | +37.0% | **-18.4%** | 0.97 | 14.8% | 58 | 55% | 1.80 | 56d |
| v11_gap_up_atr2.5_5pct_min | $135,084 | +35.1% | **-20.3%** | 1.22 | 12.1% | 41 | 59% | 2.32 | 46d |
| v12_gap_up_more_signals | $133,875 | +33.9% | **-21.5%** | 0.91 | 16.0% | 68 | 53% | 1.76 | 47d |
| v3_atr_2.5x_no_hardcut | $107,158 | +7.2% | **-48.2%** | 0.27 | 23.4% | 99 | 39% | 1.12 | 33d |
| v1_baseline | $68,058 | -31.9% | **-87.3%** | -1.09 | 37.4% | 71 | 24% | 0.43 | 49d |

## Exit-reason breakdown by variant

### v10_gap_up_atr2.5_60d_max

| Reason | N | Avg P&L % | Win rate |
|---|---|---|---|
| atr_2.5x | 55 | -0.77% | 40% |
| time_60d | 16 | +14.36% | 94% |
| end_of_backtest | 5 | +6.61% | 80% |

### v8_gap_up_atr2.5

| Reason | N | Avg P&L % | Win rate |
|---|---|---|---|
| atr_2.5x | 63 | +2.91% | 54% |
| end_of_backtest | 5 | +6.61% | 80% |

### v9_gap_up_atr3

| Reason | N | Avg P&L % | Win rate |
|---|---|---|---|
| atr_3x | 53 | +3.46% | 53% |
| end_of_backtest | 5 | +2.66% | 80% |

### v11_gap_up_atr2.5_5pct_min

| Reason | N | Avg P&L % | Win rate |
|---|---|---|---|
| atr_2.5x | 39 | +4.28% | 56% |
| end_of_backtest | 2 | +6.21% | 100% |

### v12_gap_up_more_signals

| Reason | N | Avg P&L % | Win rate |
|---|---|---|---|
| atr_2.5x | 63 | +2.33% | 51% |
| end_of_backtest | 5 | +6.61% | 80% |

### v3_atr_2.5x_no_hardcut

| Reason | N | Avg P&L % | Win rate |
|---|---|---|---|
| atr_2.5x | 95 | +0.43% | 38% |
| end_of_backtest | 4 | +2.46% | 75% |

### v1_baseline

| Reason | N | Avg P&L % | Win rate |
|---|---|---|---|
| hard_cut_-7% | 34 | -9.06% | 3% |
| trail_10% | 20 | -3.40% | 10% |
| trail_7% | 7 | +6.86% | 100% |
| trail_5% | 5 | +22.10% | 100% |
| end_of_backtest | 5 | +2.45% | 40% |
