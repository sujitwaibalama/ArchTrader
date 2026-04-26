# Decision Journal

**Every BUY, SKIP, HOLD, EXIT decision with a one-line reason.** This is what real prop traders do. Most learning lives in "I almost bought X" — without this file, those decisions vanish.

## Format

One line per decision. Append-only. Newest at the bottom.

```
YYYY-MM-DD HH:MM | <ROUTINE> | <ACTION> | <TICKER> | <REASON>
```

Where:
- `ROUTINE` ∈ {pre-market, market-open, midday, daily-summary}
- `ACTION` ∈ {BUY, SKIP, HOLD, TIGHTEN, EXIT, NO-OP}
- `REASON` is ≤120 chars, names the rule or pattern (e.g., "gap-scan rank 1 + earnings beat catalyst", "skipped — no Grok-confirmable catalyst", "tightened to 2×ATR at +15%")

## Why this file exists

- **SKIP decisions are gold.** If we skipped AMD because no catalyst confirmed, and AMD ran +30%, we learn our catalyst filter was too tight.
- **BUY decisions get auditable.** Every entry has a paper trail; lesson cards reference these lines.
- **Weekly review** counts BUYs vs SKIPs and checks if our skips were right (defended capital) or wrong (missed gains).

## Entries

```
2026-04-26 08:30 | pre-market | NO-OP | -      | journal initialized; system upgrade — no trades today (Saturday)
```
