"""Live gap-up scan for v10 production strategy.

Scans the universe for stocks that had a >=GAP_MIN% gap-up in the last
GAP_LOOKBACK trading days, held the gap (close >= open on the gap day),
and are still above their 50-day SMA today.

Mirrors backtest/strategy.py earnings_gap_score logic exactly so live
behavior matches the backtested edge.

Usage:
    uv run python scan_live.py            # JSON output, scan as of today
    uv run python scan_live.py 2026-04-24 # scan as of a historical date
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd
import yfinance as yf

from universe import UNIVERSE
from strategy import StrategyConfig, earnings_gap_score, sma

# Production config — match the v10 backtest preset exactly
CFG = StrategyConfig(
    name="v10_live",
    entry_type="earnings_gap",
    gap_min_pct=0.03,
    gap_lookback_days=5,
    gap_must_hold=True,
    sma_filter_window=50,
    stop_type="atr_trail",
    atr_mult=2.5,
    atr_period=20,
    hard_cut=None,
    max_hold_days=60,
)


@dataclass
class Candidate:
    ticker: str
    sector: str
    score: float
    last_close: float
    sma50: float


def fetch(tickers: list[str], asof: date) -> dict[str, pd.DataFrame]:
    # Need ~70 trading days of history (50 for SMA + 5 lookback + buffer)
    start = asof - timedelta(days=120)
    end = asof + timedelta(days=2)
    raw = yf.download(
        tickers, start=start.isoformat(), end=end.isoformat(),
        progress=False, auto_adjust=True, group_by="ticker",
    )
    out: dict[str, pd.DataFrame] = {}
    for t in tickers:
        if t in raw.columns.get_level_values(0):
            df = raw[t][["Open", "High", "Low", "Close"]].dropna()
            if len(df) > 0:
                out[t] = df
    return out


def scan(asof: date) -> list[Candidate]:
    tickers = list(UNIVERSE.keys())
    prices = fetch(tickers, asof)
    out: list[Candidate] = []
    for t, sector in UNIVERSE.items():
        df = prices.get(t)
        if df is None:
            continue
        score = earnings_gap_score(df, asof, CFG)
        if score is None:
            continue
        last = df[df.index.date <= asof]
        if len(last) == 0:
            continue
        out.append(Candidate(
            ticker=t,
            sector=sector,
            score=round(score, 6),
            last_close=round(float(last["Close"].iloc[-1]), 2),
            sma50=round(sma(df, asof, CFG.sma_filter_window) or 0, 2),
        ))
    out.sort(key=lambda c: -c.score)
    return out


def main() -> None:
    if len(sys.argv) > 1:
        asof = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        asof = date.today()

    candidates = scan(asof)
    print(json.dumps({
        "asof": asof.isoformat(),
        "config": {
            "gap_min_pct": CFG.gap_min_pct,
            "gap_lookback_days": CFG.gap_lookback_days,
            "sma_filter_window": CFG.sma_filter_window,
            "atr_mult": CFG.atr_mult,
            "max_hold_days": CFG.max_hold_days,
        },
        "n_candidates": len(candidates),
        "candidates": [
            {
                "rank": i + 1,
                "ticker": c.ticker,
                "sector": c.sector,
                "score": c.score,
                "last_close": c.last_close,
                "sma50": c.sma50,
            }
            for i, c in enumerate(candidates)
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
