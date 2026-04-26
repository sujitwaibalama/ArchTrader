"""Trading universe + sector mapping for ArcTrader backtest.

A representative ~50-stock subset of the S&P 100 covering all 11 sectors.
Mapped to SPDR sector ETFs for momentum ranking.
"""

# ticker -> sector
UNIVERSE = {
    # Technology
    "AAPL": "Technology", "MSFT": "Technology", "NVDA": "Technology",
    "AVGO": "Technology", "ORCL": "Technology", "CRM": "Technology",
    "ADBE": "Technology", "AMD": "Technology", "CSCO": "Technology",
    "QCOM": "Technology",
    # Financials
    "JPM": "Financials", "BAC": "Financials", "WFC": "Financials",
    "GS": "Financials", "MS": "Financials", "BLK": "Financials",
    "AXP": "Financials", "MA": "Financials", "V": "Financials",
    # Health Care
    "UNH": "Health Care", "JNJ": "Health Care", "LLY": "Health Care",
    "ABBV": "Health Care", "MRK": "Health Care", "ABT": "Health Care",
    "TMO": "Health Care", "AMGN": "Health Care",
    # Consumer Discretionary
    "TSLA": "Consumer Discretionary", "HD": "Consumer Discretionary",
    "MCD": "Consumer Discretionary", "NKE": "Consumer Discretionary",
    "LOW": "Consumer Discretionary", "BKNG": "Consumer Discretionary",
    # Communication Services
    "GOOGL": "Communication Services", "META": "Communication Services",
    "NFLX": "Communication Services", "DIS": "Communication Services",
    "CMCSA": "Communication Services",
    # Consumer Staples
    "WMT": "Consumer Staples", "PG": "Consumer Staples",
    "KO": "Consumer Staples", "PEP": "Consumer Staples",
    "COST": "Consumer Staples",
    # Energy
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy", "SLB": "Energy",
    # Industrials
    "BA": "Industrials", "CAT": "Industrials", "GE": "Industrials",
    "HON": "Industrials", "RTX": "Industrials", "DE": "Industrials",
    # Materials
    "LIN": "Materials",
    # Real Estate
    "AMT": "Real Estate", "PLD": "Real Estate",
    # Utilities
    "NEE": "Utilities", "DUK": "Utilities",
}

# Sector -> SPDR sector ETF (used to rank sector momentum)
SECTOR_ETF = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Health Care": "XLV",
    "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
}

BENCHMARK = "SPY"


def stocks_in_sector(sector: str) -> list[str]:
    return [t for t, s in UNIVERSE.items() if s == sector]
