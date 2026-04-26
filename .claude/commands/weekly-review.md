---
description: Run weekly review workflow manually (local mode)
---

Run the Friday weekly review using local .env credentials.

1. Read full week of TRADE-LOG and RESEARCH-LOG entries, WEEKLY-REVIEW template, strategy doc, memory/lessons/INDEX.md AND every lesson card created this week (full body — pull concrete patterns into the review).
2. Pull Friday close account state and positions.
3. Compute: starting/ending portfolio, week return, S&P comparison, W/L/open, win rate, best/worst trade, profit factor.
4. Append full review to memory/WEEKLY-REVIEW.md matching template exactly.
5. If a rule proved out for 2+ weeks or failed badly, update TRADING-STRATEGY.md.
6. Reset weekly trade counter in CIRCUIT-BREAKER.md. Update sector bans.
7. Send Telegram review (always, <= 15 lines).

Local mode: no commit/push needed.
