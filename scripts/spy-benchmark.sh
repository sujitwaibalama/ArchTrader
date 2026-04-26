#!/usr/bin/env bash
# Compute the SPY buy-and-hold equivalent for the bot's starting capital.
#
# Output: JSON with phase_start_date, starting_equity, spy_anchor_price,
# spy_now, spy_shares_equiv, spy_value_now, spy_return_pct.
#
# Usage:
#   bash scripts/spy-benchmark.sh                 # JSON output
#   bash scripts/spy-benchmark.sh --line          # one-line summary
#
# Used by daily-summary and weekly-review to compare bot performance to
# a passive SPY hold from the same phase start.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$ROOT/memory/spy-anchor.json"

if [[ ! -f "$CONFIG" ]]; then
  echo "ERROR: $CONFIG missing. Run yfinance bootstrap or create manually." >&2
  exit 1
fi

START_PRICE=$(jq -r '.spy_anchor_price' "$CONFIG")
START_EQUITY=$(jq -r '.starting_equity' "$CONFIG")
PHASE_START=$(jq -r '.phase_start_date' "$CONFIG")

QUOTE=$(bash "$ROOT/scripts/alpaca.sh" quote SPY)
BID=$(echo "$QUOTE" | jq -r '.quote.bp')
ASK=$(echo "$QUOTE" | jq -r '.quote.ap')

if [[ "$BID" == "0" || "$ASK" == "0" || "$BID" == "null" || "$ASK" == "null" ]]; then
  echo "ERROR: SPY quote returned bid=$BID ask=$ASK (market closed or halted)." >&2
  exit 2
fi

NOW_PX=$(awk -v b="$BID" -v a="$ASK" 'BEGIN { printf "%.4f", (b+a)/2 }')
SHARES=$(awk -v eq="$START_EQUITY" -v sp="$START_PRICE" 'BEGIN { printf "%.6f", eq/sp }')
VALUE=$(awk -v sh="$SHARES" -v p="$NOW_PX" 'BEGIN { printf "%.2f", sh*p }')
PCT=$(awk -v eq="$START_EQUITY" -v v="$VALUE" 'BEGIN { printf "%.4f", v/eq - 1 }')

if [[ "${1:-}" == "--line" ]]; then
  PCT_DISPLAY=$(awk -v p="$PCT" 'BEGIN { printf "%+.2f%%", p*100 }')
  echo "SPY (buy-hold from $PHASE_START): \$$VALUE ($PCT_DISPLAY)"
  exit 0
fi

jq -n \
  --arg phase_start "$PHASE_START" \
  --argjson start_eq "$START_EQUITY" \
  --argjson anchor_px "$START_PRICE" \
  --argjson now_px "$NOW_PX" \
  --argjson shares "$SHARES" \
  --argjson value "$VALUE" \
  --argjson pct "$PCT" \
  '{
    phase_start_date: $phase_start,
    starting_equity: $start_eq,
    spy_anchor_price: $anchor_px,
    spy_now: $now_px,
    spy_shares_equiv: $shares,
    spy_value_now: $value,
    spy_return_pct: $pct
  }'
