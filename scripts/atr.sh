#!/usr/bin/env bash
# Compute ATR (Average True Range) for a ticker.
#
# Usage:
#   bash scripts/atr.sh SYM [PERIOD=20]
#
# Output: JSON {"symbol":"SYM","period":N,"atr":X.XX,"last_close":X.XX,"trail_dollars":X.XX}
# trail_dollars = 2.5 * ATR (the recommended trailing stop offset for v3).
#
# Used at order-placement time to set trail_price on Alpaca trailing-stop orders.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

SYM="${1:?usage: atr.sh SYM [PERIOD=20]}"
PERIOD="${2:-20}"
MULT="${ATR_TRAIL_MULT:-2.5}"

# Need PERIOD+1 bars to compute PERIOD true ranges
LIMIT=$((PERIOD + 5))

BARS=$(bash "$ROOT/scripts/alpaca.sh" bars "$SYM" 1Day "$LIMIT")

BARS_JSON="$BARS" python3 - "$SYM" "$PERIOD" "$MULT" <<'PY'
import json, os, sys

sym = sys.argv[1]
period = int(sys.argv[2])
mult = float(sys.argv[3])

data = json.loads(os.environ["BARS_JSON"])
bars = data.get("bars", [])
if len(bars) < period + 1:
    print(json.dumps({"error": f"need {period+1} bars, got {len(bars)}", "symbol": sym}), file=sys.stderr)
    sys.exit(2)

# alpaca returns sort=desc (newest first); reverse to chronological asc
bars = list(reversed(bars))
sub = bars[-(period + 1):]
trs = []
for i in range(1, len(sub)):
    h, l, c_prev = sub[i]["h"], sub[i]["l"], sub[i-1]["c"]
    tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
    trs.append(tr)

atr = sum(trs) / len(trs)
last_close = sub[-1]["c"]
trail = round(mult * atr, 2)

print(json.dumps({
    "symbol": sym,
    "period": period,
    "atr": round(atr, 4),
    "last_close": last_close,
    "trail_dollars": trail,
    "trail_pct_equiv": round(trail / last_close * 100, 2),
}, indent=2))
PY
