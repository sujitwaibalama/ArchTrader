"""Strategy configurations + entry / stop helpers.

A StrategyConfig fully describes one variant we want to backtest.
The engine in run_backtest.py reads the config and dispatches.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import pandas as pd


@dataclass
class StrategyConfig:
    name: str
    # Entry signal
    entry_type: str = "momentum_leader"     # 'momentum_leader' | 'pullback' | 'earnings_gap'
    momentum_lookback: int = 60
    pullback_min: float = 0.05               # how far off recent high (min)
    pullback_max: float = 0.15               # how far off recent high (max)
    pullback_high_window: int = 20           # recent-high window for pullback
    sma_filter_window: int = 50              # uptrend filter
    # Earnings-gap entry (PEAD proxy)
    gap_min_pct: float = 0.03                # min gap-up size to register as catalyst
    gap_lookback_days: int = 5               # how recent the gap must be
    gap_must_hold: bool = True               # gap day must close >= open (held the gap)
    # Time-based exit (for catalyst-driven setups that mean-revert eventually)
    max_hold_days: int | None = None         # None = no time exit
    # Stop logic
    stop_type: str = "pct_trail"             # 'pct_trail' | 'atr_trail'
    initial_trail: float = 0.10
    atr_mult: float = 2.5
    atr_period: int = 20
    hard_cut: float | None = 0.07            # None = disabled
    # Tightening: list of (gain_threshold, new_trail_pct), checked top-down
    tighten: list[tuple[float, float]] = field(
        default_factory=lambda: [(0.20, 0.05), (0.15, 0.07)]
    )
    # Sizing / structure (held constant across variants for fair comparison)
    position_target_pct: float = 0.18
    max_positions: int = 6
    max_new_per_week: int = 3
    top_sectors_n: int = 3
    sector_ban_consec_losses: int = 2
    sector_ban_days: int = 14


def atr(df: pd.DataFrame, asof: date, period: int) -> float | None:
    """Average true range over `period` days ending on asof."""
    df = df[df.index.date <= asof]
    if len(df) < period + 1:
        return None
    sub = df.tail(period + 1)
    high = sub["High"].values
    low = sub["Low"].values
    close = sub["Close"].values
    trs = []
    for i in range(1, len(sub)):
        tr = max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i] - close[i-1]),
        )
        trs.append(tr)
    return float(sum(trs) / len(trs))


def sma(df: pd.DataFrame, asof: date, window: int) -> float | None:
    df = df[df.index.date <= asof]
    if len(df) < window:
        return None
    return float(df["Close"].tail(window).mean())


def momentum(df: pd.DataFrame, asof: date, lookback: int) -> float | None:
    df = df[df.index.date <= asof]
    if len(df) < lookback + 1:
        return None
    recent = df["Close"].iloc[-1]
    past = df["Close"].iloc[-(lookback + 1)]
    if past <= 0 or pd.isna(past) or pd.isna(recent):
        return None
    return float(recent / past - 1.0)


def earnings_gap_score(df: pd.DataFrame, asof: date, cfg: StrategyConfig) -> float | None:
    """Higher score = stronger recent positive gap (PEAD proxy).

    Rules:
      - In the last `gap_lookback_days` trading days, must have at least one day
        where (open / prev_close - 1) >= gap_min_pct.
      - That day must have closed >= open (gap held), if cfg.gap_must_hold.
      - Stock must still be above 50d SMA today (trend filter).
      - Score = gap magnitude × recency weight (more recent = higher).
    """
    sub = df[df.index.date <= asof]
    if len(sub) < max(cfg.sma_filter_window, cfg.gap_lookback_days + 2):
        return None
    s50 = sma(df, asof, cfg.sma_filter_window)
    if s50 is None or float(sub["Close"].iloc[-1]) <= s50:
        return None  # trend filter

    # scan last N days for a gap event (most recent first)
    best = None
    for k in range(1, cfg.gap_lookback_days + 1):
        if k >= len(sub):
            break
        day = sub.iloc[-k]
        prev = sub.iloc[-k - 1]
        prev_close = float(prev["Close"])
        if prev_close <= 0:
            continue
        gap = float(day["Open"]) / prev_close - 1.0
        if gap < cfg.gap_min_pct:
            continue
        if cfg.gap_must_hold and float(day["Close"]) < float(day["Open"]):
            continue
        recency_weight = 1.0 - (k - 1) / cfg.gap_lookback_days  # 1.0 today, decays
        score = gap * recency_weight
        if best is None or score > best:
            best = score
    return best


def pullback_score(df: pd.DataFrame, asof: date, cfg: StrategyConfig) -> float | None:
    """Higher score = better pullback candidate.

    Rules:
      - Must be in uptrend (close > sma50).
      - Must be `pullback_min` to `pullback_max` below the `pullback_high_window` high.
      - Score = 60d momentum * (1 - distance_from_high)  -> rewards strong trend
                                                            with mild pullback.
    """
    sub = df[df.index.date <= asof]
    if len(sub) < max(cfg.sma_filter_window, cfg.momentum_lookback) + 1:
        return None
    close = float(sub["Close"].iloc[-1])
    s50 = sma(df, asof, cfg.sma_filter_window)
    if s50 is None or close <= s50:
        return None  # not in uptrend
    recent_high = float(sub["Close"].tail(cfg.pullback_high_window).max())
    if recent_high <= 0:
        return None
    dist = 1.0 - close / recent_high  # 0 = at high, positive = below high
    if not (cfg.pullback_min <= dist <= cfg.pullback_max):
        return None
    mom = momentum(df, asof, cfg.momentum_lookback)
    if mom is None or mom <= 0:
        return None
    return mom * (1 - dist)


# --- Preset configs to compare -------------------------------------------

PRESETS: list[StrategyConfig] = [
    StrategyConfig(
        name="v1_baseline",
        # current production rules — the one that lost 32%
    ),
    StrategyConfig(
        name="v3_atr_2.5x_no_hardcut",
        stop_type="atr_trail",
        atr_mult=2.5,
        hard_cut=None,
    ),
    StrategyConfig(
        name="v8_gap_up_atr2.5",
        entry_type="earnings_gap",
        stop_type="atr_trail",
        atr_mult=2.5,
        hard_cut=None,
    ),
    StrategyConfig(
        name="v9_gap_up_atr3",
        entry_type="earnings_gap",
        stop_type="atr_trail",
        atr_mult=3.0,
        hard_cut=None,
    ),
    StrategyConfig(
        name="v10_gap_up_atr2.5_60d_max",
        entry_type="earnings_gap",
        stop_type="atr_trail",
        atr_mult=2.5,
        hard_cut=None,
        max_hold_days=60,
    ),
    StrategyConfig(
        name="v11_gap_up_atr2.5_5pct_min",
        entry_type="earnings_gap",
        gap_min_pct=0.05,        # require stronger gap (5%+)
        stop_type="atr_trail",
        atr_mult=2.5,
        hard_cut=None,
    ),
    StrategyConfig(
        name="v12_gap_up_more_signals",
        entry_type="earnings_gap",
        gap_lookback_days=10,    # widen lookback so we catch more setups
        stop_type="atr_trail",
        atr_mult=2.5,
        hard_cut=None,
    ),
]
