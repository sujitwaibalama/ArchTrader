#!/usr/bin/env bash
# Production gap-up scanner for v10 strategy.
#
# Usage:
#   bash scripts/gap-scan.sh              # scan as of today
#   bash scripts/gap-scan.sh 2026-04-24   # scan as of a historical date
#   bash scripts/gap-scan.sh --top 5      # show only top 5 candidates
#
# Output: JSON with ranked list of (ticker, sector, score, last_close, sma50).
# Used by the pre-market routine to generate v10 trade ideas.
#
# Logic: stock had >=3% gap-up in last 5 trading days, held the gap
# (close >= open on the gap day), is still above its 50-day SMA today.
# Mirrors backtest/strategy.py earnings_gap_score exactly.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKTEST_DIR="$ROOT/backtest"

# Ensure uv is on PATH (fallback for non-interactive shells)
if ! command -v uv >/dev/null 2>&1; then
  export PATH="$HOME/.local/bin:$PATH"
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv not on PATH. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 3
fi

ASOF=""
TOP=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --top) TOP="$2"; shift 2 ;;
    *) ASOF="$1"; shift ;;
  esac
done

OUTPUT=$(uv run --project "$BACKTEST_DIR" python "$BACKTEST_DIR/scan_live.py" $ASOF)

if [[ -n "$TOP" ]]; then
  echo "$OUTPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
data['candidates'] = data['candidates'][:int('$TOP')]
data['n_candidates_total'] = len(data['candidates'])
print(json.dumps(data, indent=2))
"
else
  echo "$OUTPUT"
fi
