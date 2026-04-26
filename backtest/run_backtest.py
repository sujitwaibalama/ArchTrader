"""ArcTrader backtester.

Replays a StrategyConfig on historical data 2024-2026.

Run baseline:
    uv run python run_backtest.py

Run all variants and compare:
    uv run python run_variants.py

Execution model:
    - Decisions use data through close of day T.
    - Fills at open of day T+1.
    - Slippage: 10 bps per side.
    - Initial capital: $100,000.
    - Benchmark: buy-and-hold SPY.
"""

from __future__ import annotations

import json
import math
import pickle
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

from universe import UNIVERSE, SECTOR_ETF, BENCHMARK, stocks_in_sector
from strategy import (
    StrategyConfig, atr, momentum, pullback_score, earnings_gap_score,
)

START_DATE = "2024-01-01"
END_DATE = "2026-04-25"
INITIAL_CAPITAL = 100_000.0
SLIPPAGE_BPS = 10  # one-side

DATA_CACHE = Path(__file__).parent / "data_cache.pkl"
REPORT_PATH = Path(__file__).parent.parent / "memory" / "BACKTEST-RESULTS.md"


# --- Data -----------------------------------------------------------------

def fetch_prices(tickers: list[str], start: str, end: str) -> dict[str, pd.DataFrame]:
    if DATA_CACHE.exists():
        with DATA_CACHE.open("rb") as f:
            cached = pickle.load(f)
        if cached.get("_meta") == (start, end, sorted(tickers)):
            print(f"[data] loaded {len(tickers)} tickers from cache")
            return cached["data"]

    print(f"[data] fetching {len(tickers)} tickers from yfinance ({start} -> {end}) ...")
    raw = yf.download(
        tickers, start=start, end=end, progress=False,
        auto_adjust=True, group_by="ticker",
    )

    out: dict[str, pd.DataFrame] = {}
    for t in tickers:
        if t in raw.columns.get_level_values(0):
            df = raw[t][["Open", "High", "Low", "Close"]].dropna()
            if len(df) > 0:
                out[t] = df

    with DATA_CACHE.open("wb") as f:
        pickle.dump({"_meta": (start, end, sorted(tickers)), "data": out}, f)
    print(f"[data] got {len(out)} tickers with usable data")
    return out


# --- Portfolio ------------------------------------------------------------

@dataclass
class Position:
    ticker: str
    sector: str
    entry_date: date
    entry_price: float
    shares: int
    peak_close: float
    trail_pct: float
    atr_at_entry: float | None = None  # for atr-based stops


@dataclass
class ClosedTrade:
    ticker: str
    sector: str
    entry_date: date
    exit_date: date
    entry_price: float
    exit_price: float
    shares: int
    pnl: float
    pnl_pct: float
    exit_reason: str

    def is_win(self) -> bool:
        return self.pnl > 0


@dataclass
class Portfolio:
    cash: float = INITIAL_CAPITAL
    positions: dict[str, Position] = field(default_factory=dict)
    closed: list[ClosedTrade] = field(default_factory=list)
    equity_curve: list[tuple[date, float]] = field(default_factory=list)
    trades_this_week: dict[date, int] = field(default_factory=dict)
    sector_consec_losses: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    sector_ban_until: dict[str, date] = field(default_factory=dict)


# --- Stop computation ----------------------------------------------------

def compute_stop_price(pos: Position, cfg: StrategyConfig) -> float:
    if cfg.stop_type == "atr_trail" and pos.atr_at_entry is not None:
        return pos.peak_close - cfg.atr_mult * pos.atr_at_entry
    return pos.peak_close * (1 - pos.trail_pct)


# --- Sector ranking ------------------------------------------------------

def rank_sectors(prices: dict[str, pd.DataFrame], asof: date,
                 cfg: StrategyConfig) -> list[str]:
    scored = []
    for sector, etf in SECTOR_ETF.items():
        if etf not in prices:
            continue
        m = momentum(prices[etf], asof, cfg.momentum_lookback)
        if m is not None:
            scored.append((m, sector))
    scored.sort(reverse=True)
    return [s for _, s in scored]


def pick_leader(sector: str, prices: dict[str, pd.DataFrame],
                asof: date, excluded: set[str], cfg: StrategyConfig) -> str | None:
    """Pick best stock in sector based on cfg.entry_type."""
    candidates = []
    for t in stocks_in_sector(sector):
        if t in excluded or t not in prices:
            continue
        if cfg.entry_type == "pullback":
            score = pullback_score(prices[t], asof, cfg)
        elif cfg.entry_type == "earnings_gap":
            score = earnings_gap_score(prices[t], asof, cfg)
        else:
            score = momentum(prices[t], asof, cfg.momentum_lookback)
            if score is not None and score <= 0:
                score = None  # require positive momentum
        if score is not None:
            candidates.append((score, t))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def scan_all_for_gap(prices: dict[str, pd.DataFrame], asof: date,
                     excluded: set[str], cfg: StrategyConfig) -> list[tuple[str, str]]:
    """Sector-agnostic scan for gap-up setups. Returns [(ticker, sector), ...]
    sorted by gap score, strongest first."""
    from universe import UNIVERSE
    scored = []
    for t, sector in UNIVERSE.items():
        if t in excluded or t not in prices:
            continue
        score = earnings_gap_score(prices[t], asof, cfg)
        if score is not None:
            scored.append((score, t, sector))
    scored.sort(reverse=True)
    return [(t, s) for _, t, s in scored]


# --- Engine --------------------------------------------------------------

def week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def run(cfg: StrategyConfig, prices: dict[str, pd.DataFrame],
        cal: list[date]) -> dict:
    pf = Portfolio()
    spy_open0 = float(prices[BENCHMARK]["Open"].iloc[0])
    spy_shares = INITIAL_CAPITAL / spy_open0

    pending: list[tuple[str, str]] = []

    for i, today in enumerate(cal):
        # 1. Execute pending entries at TODAY's open
        for ticker, sector in pending:
            if len(pf.positions) >= cfg.max_positions:
                continue
            df = prices.get(ticker)
            if df is None or today not in df.index.date:
                continue
            row = df.loc[df.index.date == today].iloc[0]
            fill_px = float(row["Open"]) * (1 + SLIPPAGE_BPS / 10_000)

            # equity at fill (use today's open for held positions)
            equity_now = pf.cash + sum(
                p.shares * float(prices[t].loc[prices[t].index.date == today].iloc[0]["Open"])
                for t, p in pf.positions.items()
                if today in prices[t].index.date
            )
            target = equity_now * cfg.position_target_pct
            shares = int(target / fill_px)
            cost = shares * fill_px
            if shares <= 0 or cost > pf.cash:
                continue

            atr_entry = atr(df, today, cfg.atr_period) if cfg.stop_type == "atr_trail" else None

            pf.cash -= cost
            pf.positions[ticker] = Position(
                ticker=ticker, sector=sector, entry_date=today,
                entry_price=fill_px, shares=shares, peak_close=fill_px,
                trail_pct=cfg.initial_trail, atr_at_entry=atr_entry,
            )
            wk = week_start(today)
            pf.trades_this_week[wk] = pf.trades_this_week.get(wk, 0) + 1
        pending = []

        # 2. Mark-to-market & check exits at TODAY's close
        prices_close: dict[str, float] = {}
        for t in list(pf.positions.keys()):
            df = prices[t]
            if today not in df.index.date:
                continue
            close = float(df.loc[df.index.date == today].iloc[0]["Close"])
            prices_close[t] = close
            pos = pf.positions[t]

            if close > pos.peak_close:
                pos.peak_close = close

            unr = close / pos.entry_price - 1.0
            for thresh, new_trail in cfg.tighten:
                if unr >= thresh:
                    pos.trail_pct = min(pos.trail_pct, new_trail)
                    break

            stop = compute_stop_price(pos, cfg)
            hard = pos.entry_price * (1 - cfg.hard_cut) if cfg.hard_cut else float("-inf")
            exit_reason = None
            if close <= hard:
                exit_reason = f"hard_cut_-{int(cfg.hard_cut*100)}%"
            elif close <= stop:
                if cfg.stop_type == "atr_trail":
                    exit_reason = f"atr_{cfg.atr_mult:g}x"
                else:
                    exit_reason = f"trail_{int(pos.trail_pct*100)}%"
            elif cfg.max_hold_days is not None:
                held = (today - pos.entry_date).days
                if held >= cfg.max_hold_days:
                    exit_reason = f"time_{cfg.max_hold_days}d"

            if exit_reason:
                # exit at next open (with slippage); else today's close
                if i + 1 < len(cal):
                    nxt = cal[i + 1]
                    if nxt in df.index.date:
                        nrow = df.loc[df.index.date == nxt].iloc[0]
                        exit_px = float(nrow["Open"]) * (1 - SLIPPAGE_BPS / 10_000)
                        exit_d = nxt
                    else:
                        exit_px = close * (1 - SLIPPAGE_BPS / 10_000)
                        exit_d = today
                else:
                    exit_px = close * (1 - SLIPPAGE_BPS / 10_000)
                    exit_d = today

                pf.cash += exit_px * pos.shares
                pnl = (exit_px - pos.entry_price) * pos.shares
                trade = ClosedTrade(
                    ticker=t, sector=pos.sector,
                    entry_date=pos.entry_date, exit_date=exit_d,
                    entry_price=pos.entry_price, exit_price=exit_px,
                    shares=pos.shares, pnl=pnl,
                    pnl_pct=exit_px / pos.entry_price - 1.0,
                    exit_reason=exit_reason,
                )
                pf.closed.append(trade)
                if trade.is_win():
                    pf.sector_consec_losses[pos.sector] = 0
                else:
                    pf.sector_consec_losses[pos.sector] += 1
                    if pf.sector_consec_losses[pos.sector] >= cfg.sector_ban_consec_losses:
                        pf.sector_ban_until[pos.sector] = today + timedelta(days=cfg.sector_ban_days)
                        pf.sector_consec_losses[pos.sector] = 0
                del pf.positions[t]

        # 3. Equity curve
        eq_today = pf.cash + sum(
            pf.positions[t].shares * prices_close.get(t, pf.positions[t].entry_price)
            for t in pf.positions
        )
        pf.equity_curve.append((today, eq_today))

        # 4. Scan for new entries.
        # Earnings-gap strategies scan EVERY trading day (catalysts don't wait
        # for Monday). Sector-momentum strategies scan only on Mondays.
        scan_today = (cfg.entry_type == "earnings_gap") or (today.weekday() == 0)
        if scan_today:
            wk = week_start(today)
            placed = pf.trades_this_week.get(wk, 0)
            slots = min(cfg.max_new_per_week - placed,
                       cfg.max_positions - len(pf.positions) - len(pending))
            if slots > 0:
                excluded = set(pf.positions.keys()) | {t for t, _ in pending}
                queued: list[tuple[str, str]] = []
                if cfg.entry_type == "earnings_gap":
                    # Sector-agnostic scan
                    candidates = scan_all_for_gap(prices, today, excluded, cfg)
                    # respect sector bans
                    for ticker, sector in candidates:
                        if pf.sector_ban_until.get(sector, date.min) > today:
                            continue
                        queued.append((ticker, sector))
                        if len(queued) >= slots:
                            break
                else:
                    top = rank_sectors(prices, today, cfg)[:cfg.top_sectors_n]
                    top = [s for s in top if pf.sector_ban_until.get(s, date.min) <= today]
                    for sector in top:
                        leader = pick_leader(sector, prices, today, excluded, cfg)
                        if leader:
                            queued.append((leader, sector))
                            excluded.add(leader)
                pending = queued[:slots]

    # close remaining at last close
    last = cal[-1]
    for t in list(pf.positions.keys()):
        df = prices[t]
        if last in df.index.date:
            close = float(df.loc[df.index.date == last].iloc[0]["Close"])
            pos = pf.positions[t]
            pf.cash += close * pos.shares
            pf.closed.append(ClosedTrade(
                ticker=t, sector=pos.sector,
                entry_date=pos.entry_date, exit_date=last,
                entry_price=pos.entry_price, exit_price=close,
                shares=pos.shares, pnl=(close - pos.entry_price) * pos.shares,
                pnl_pct=close / pos.entry_price - 1.0,
                exit_reason="end_of_backtest",
            ))
            del pf.positions[t]

    spy_close_last = float(prices[BENCHMARK]["Close"].iloc[-1])
    return {
        "cfg": cfg,
        "portfolio": pf,
        "spy_initial": INITIAL_CAPITAL,
        "spy_final": spy_shares * spy_close_last,
        "spy_return_pct": (spy_shares * spy_close_last) / INITIAL_CAPITAL - 1,
        "calendar": cal,
    }


def compute_stats(pf: Portfolio) -> dict:
    eq = [v for _, v in pf.equity_curve]
    final = eq[-1]
    total_return = final / INITIAL_CAPITAL - 1.0

    peak = eq[0]
    max_dd = 0.0
    for v in eq:
        peak = max(peak, v)
        max_dd = max(max_dd, (peak - v) / peak)

    rets = [eq[i] / eq[i-1] - 1.0 for i in range(1, len(eq))]
    if rets:
        mean_r = sum(rets) / len(rets)
        var_r = sum((r - mean_r) ** 2 for r in rets) / len(rets)
        sd = math.sqrt(var_r)
        sharpe = (mean_r / sd) * math.sqrt(252) if sd > 0 else 0.0
    else:
        sharpe = 0.0

    wins = [t for t in pf.closed if t.is_win()]
    losses = [t for t in pf.closed if not t.is_win()]
    pf_ratio = (sum(t.pnl for t in wins) /
                -sum(t.pnl for t in losses)) if losses else float("inf")
    win_rate = len(wins) / len(pf.closed) if pf.closed else 0.0
    avg_hold = (sum((t.exit_date - t.entry_date).days for t in pf.closed)
                / len(pf.closed)) if pf.closed else 0.0

    return {
        "final_equity": final,
        "total_return_pct": total_return,
        "max_drawdown_pct": max_dd,
        "sharpe": sharpe,
        "n_trades": len(pf.closed),
        "win_rate": win_rate,
        "wins": len(wins),
        "losses": len(losses),
        "profit_factor": pf_ratio,
        "avg_hold_days": avg_hold,
        "best_trade": max(pf.closed, key=lambda t: t.pnl_pct, default=None),
        "worst_trade": min(pf.closed, key=lambda t: t.pnl_pct, default=None),
    }


def write_report(result: dict, stats: dict) -> None:
    pf: Portfolio = result["portfolio"]
    cfg: StrategyConfig = result["cfg"]
    spy_ret = result["spy_return_pct"]
    bot_ret = stats["total_return_pct"]
    alpha = bot_ret - spy_ret

    lines = [
        f"# Backtest Results — {cfg.name}",
        "",
        f"**Window:** {result['calendar'][0]} → {result['calendar'][-1]} "
        f"({len(result['calendar'])} trading days)",
        f"**Universe:** {len(UNIVERSE)} S&P 100 names across {len(SECTOR_ETF)} sectors",
        "",
        "## Headline",
        "",
        "| Metric | Bot | SPY |",
        "|---|---|---|",
        f"| Final equity | ${stats['final_equity']:,.0f} | ${result['spy_final']:,.0f} |",
        f"| Total return | {bot_ret*100:+.2f}% | {spy_ret*100:+.2f}% |",
        f"| **Alpha vs SPY** | **{alpha*100:+.2f}%** | — |",
        "",
        "## Risk",
        "",
        f"- Max drawdown: {stats['max_drawdown_pct']*100:.2f}%",
        f"- Sharpe (annualized, rf=0): {stats['sharpe']:.2f}",
        "",
        "## Trade stats",
        "",
        f"- Trades: {stats['n_trades']}",
        f"- Win rate: {stats['win_rate']*100:.1f}% ({stats['wins']}W / {stats['losses']}L)",
        f"- Profit factor: {stats['profit_factor']:.2f}",
        f"- Avg holding: {stats['avg_hold_days']:.1f} days",
    ]
    if stats["best_trade"]:
        bt = stats["best_trade"]
        lines.append(f"- Best: {bt.ticker} {bt.pnl_pct*100:+.1f}% ({bt.exit_reason})")
    if stats["worst_trade"]:
        wt = stats["worst_trade"]
        lines.append(f"- Worst: {wt.ticker} {wt.pnl_pct*100:+.1f}% ({wt.exit_reason})")
    lines.append("")

    by_reason: dict[str, list[ClosedTrade]] = defaultdict(list)
    for t in pf.closed:
        by_reason[t.exit_reason].append(t)
    lines.append("## Exits by reason")
    lines.append("")
    lines.append("| Reason | N | Avg P&L % | Win rate |")
    lines.append("|---|---|---|---|")
    for reason, trades in sorted(by_reason.items(), key=lambda x: -len(x[1])):
        avg = sum(t.pnl_pct for t in trades) / len(trades)
        wr = sum(1 for t in trades if t.is_win()) / len(trades)
        lines.append(f"| {reason} | {len(trades)} | {avg*100:+.2f}% | {wr*100:.0f}% |")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"[report] wrote {REPORT_PATH}")


def load_data() -> tuple[dict[str, pd.DataFrame], list[date]]:
    tickers = list(UNIVERSE.keys()) + list(SECTOR_ETF.values()) + [BENCHMARK]
    prices = fetch_prices(tickers, START_DATE, END_DATE)
    if BENCHMARK not in prices:
        raise SystemExit("No SPY data — cannot build trading calendar.")
    cal = [d.date() for d in prices[BENCHMARK].index]
    return prices, cal


if __name__ == "__main__":
    print("[start] ArcTrader backtest — baseline (v1) config")
    prices, cal = load_data()
    cfg = StrategyConfig(name="v1_baseline")
    result = run(cfg, prices, cal)
    stats = compute_stats(result["portfolio"])
    print(f"\n=== {cfg.name} ===")
    print(f"  Bot: ${stats['final_equity']:>12,.0f} ({stats['total_return_pct']*100:+.2f}%)")
    print(f"  SPY: ${result['spy_final']:>12,.0f} ({result['spy_return_pct']*100:+.2f}%)")
    print(f"  Alpha: {(stats['total_return_pct']-result['spy_return_pct'])*100:+.2f}%  "
          f"Sharpe: {stats['sharpe']:.2f}  MaxDD: {stats['max_drawdown_pct']*100:.1f}%")
    print(f"  Trades: {stats['n_trades']}  Win: {stats['win_rate']*100:.1f}%  "
          f"PF: {stats['profit_factor']:.2f}")
    write_report(result, stats)
