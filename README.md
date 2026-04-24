# ArcTrader

Autonomous AI swing trading bot built on Claude Code. Claude IS the bot — no separate Python process. Five cron routines fire throughout each weekday, each spinning up a fresh Claude Code cloud container that reads memory, makes decisions, places real orders, and commits everything back to git.

## Architecture
- **Trading:** Alpaca API (paper first, then live)
- **Research:** xAI Grok (web search + X/Twitter sentiment)
- **Notifications:** Telegram
- **Memory:** Markdown files committed to git (stateless runs)
- **Safety:** Deterministic pre-trade validator (safety-check.sh)

## Quick Start

1. Copy `env.template` to `.env` and fill in credentials
2. Run `bash scripts/alpaca.sh account` to verify Alpaca connection
3. Run `bash scripts/grok.sh search "AAPL stock news"` to verify Grok
4. Run `bash scripts/notify.sh "Test"` to verify Telegram
5. Open in Claude Code and run `/portfolio` for a snapshot

## Daily Schedule (ET)
| Time | Routine | What it does |
|------|---------|-------------|
| 6:00 AM | pre-market | Research catalysts, write trade ideas |
| 9:35 AM | market-open | Execute planned trades, set trailing stops |
| 12:00 PM | midday | Cut losers, tighten stops on winners |
| 3:45 PM | daily-summary | EOD snapshot, send recap |
| 4:15 PM Fri | weekly-review | Grade performance, update strategy |

## Strategy
Swing trading US equities. Stocks only — no options, ever. See `memory/TRADING-STRATEGY.md` for full rules.

## Cloud Routines
See `routines/README.md` for setup instructions. Each routine prompt is in `routines/*.md`.
