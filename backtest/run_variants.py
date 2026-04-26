"""Run all StrategyConfig presets and write a comparison report.

    uv run python run_variants.py
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from run_backtest import load_data, run, compute_stats, INITIAL_CAPITAL
from strategy import PRESETS

REPORT_PATH = Path(__file__).parent.parent / "memory" / "BACKTEST-RESULTS.md"


def main() -> None:
    print("[start] running variants")
    prices, cal = load_data()

    rows = []
    spy_return = None
    spy_final = None
    for cfg in PRESETS:
        print(f"\n[{cfg.name}] running ...")
        result = run(cfg, prices, cal)
        stats = compute_stats(result["portfolio"])
        spy_return = result["spy_return_pct"]
        spy_final = result["spy_final"]
        alpha = stats["total_return_pct"] - spy_return
        rows.append({
            "name": cfg.name,
            "final": stats["final_equity"],
            "ret": stats["total_return_pct"],
            "alpha": alpha,
            "sharpe": stats["sharpe"],
            "maxdd": stats["max_drawdown_pct"],
            "trades": stats["n_trades"],
            "win_rate": stats["win_rate"],
            "pf": stats["profit_factor"],
            "avg_hold": stats["avg_hold_days"],
            "exits": _exits_summary(result["portfolio"].closed),
        })
        print(f"  Bot: ${stats['final_equity']:>10,.0f} ({stats['total_return_pct']*100:+.2f}%)  "
              f"alpha {alpha*100:+.2f}%  trades {stats['n_trades']}  "
              f"win {stats['win_rate']*100:.0f}%  PF {stats['pf'] if False else stats['profit_factor']:.2f}")

    # ranked table (best alpha first)
    rows_sorted = sorted(rows, key=lambda r: -r["alpha"])

    out = []
    out.append("# Backtest Results — Variant Comparison\n")
    out.append(f"**Window:** {cal[0]} → {cal[-1]} "
               f"({len(cal)} trading days)\n")
    out.append(f"**Benchmark (SPY buy-hold):** ${spy_final:,.0f} "
               f"({spy_return*100:+.2f}%)\n")
    out.append(f"**Initial capital:** ${INITIAL_CAPITAL:,.0f}\n")
    out.append("\n## Variants ranked by alpha vs SPY\n")
    out.append("| Variant | Final $ | Return | Alpha | Sharpe | MaxDD | Trades | Win | PF | AvgHold |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows_sorted:
        out.append(
            f"| {r['name']} | ${r['final']:,.0f} | {r['ret']*100:+.1f}% | "
            f"**{r['alpha']*100:+.1f}%** | {r['sharpe']:.2f} | "
            f"{r['maxdd']*100:.1f}% | {r['trades']} | {r['win_rate']*100:.0f}% | "
            f"{r['pf']:.2f} | {r['avg_hold']:.0f}d |"
        )
    out.append("")

    out.append("## Exit-reason breakdown by variant\n")
    for r in rows_sorted:
        out.append(f"### {r['name']}")
        out.append("")
        out.append("| Reason | N | Avg P&L % | Win rate |")
        out.append("|---|---|---|---|")
        for reason, n, avg, wr in r["exits"]:
            out.append(f"| {reason} | {n} | {avg*100:+.2f}% | {wr*100:.0f}% |")
        out.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(out))
    print(f"\n[report] wrote {REPORT_PATH}")

    print("\n=== TOP 3 ===")
    for r in rows_sorted[:3]:
        print(f"  {r['name']:35s}  alpha {r['alpha']*100:+6.2f}%  "
              f"return {r['ret']*100:+6.2f}%  Sharpe {r['sharpe']:5.2f}  "
              f"MaxDD {r['maxdd']*100:.1f}%  PF {r['pf']:.2f}")


def _exits_summary(closed):
    by_reason: dict[str, list] = defaultdict(list)
    for t in closed:
        by_reason[t.exit_reason].append(t)
    rows = []
    for reason, ts in sorted(by_reason.items(), key=lambda x: -len(x[1])):
        avg = sum(t.pnl_pct for t in ts) / len(ts)
        wr = sum(1 for t in ts if t.is_win()) / len(ts)
        rows.append((reason, len(ts), avg, wr))
    return rows


if __name__ == "__main__":
    main()
