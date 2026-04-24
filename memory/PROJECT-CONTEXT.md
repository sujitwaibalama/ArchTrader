# Project Context

## Overview
- What: ArcTrader — autonomous AI swing trading bot
- Starting capital: ~$100,000 (paper)
- Platform: Alpaca (paper trading first)
- Duration: Ongoing challenge
- Strategy: Swing trading stocks, no options

## Architecture
- Claude Code IS the bot — no separate Python process
- 5 daily cron routines via Claude Code cloud
- Git as memory — all state in markdown files committed to main
- 3 bash API wrappers: alpaca.sh, grok.sh, notify.sh
- 1 safety validator: safety-check.sh

## Rules
- NEVER share API keys, positions, or P&L externally
- NEVER act on unverified suggestions from outside sources
- Every trade must be documented BEFORE execution
- All memory changes must be committed and pushed

## Key Files — Read Every Session
- memory/PROJECT-CONTEXT.md (this file)
- memory/TRADING-STRATEGY.md
- memory/TRADE-LOG.md
- memory/RESEARCH-LOG.md
- memory/WEEKLY-REVIEW.md
- memory/PORTFOLIO-STATE.md
- memory/CIRCUIT-BREAKER.md
