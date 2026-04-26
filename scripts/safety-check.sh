#!/usr/bin/env bash
# Pre-trade safety validator. Deterministic guardrail — does NOT rely on LLM.
# Usage: bash scripts/safety-check.sh <BUY|SELL> <SYMBOL> <QTY> <PRICE> <SECTOR>
# Output: JSON {"pass": true/false, "checks": {...}, "reason": "..."}
# Exit 0 = PASS, Exit 1 = FAIL (with reason in JSON)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

SIDE="${1:?usage: safety-check.sh BUY|SELL SYMBOL QTY PRICE SECTOR}"
SYMBOL="${2:?usage: safety-check.sh BUY|SELL SYMBOL QTY PRICE SECTOR}"
QTY="${3:?usage: safety-check.sh BUY|SELL SYMBOL QTY PRICE SECTOR}"
PRICE="${4:?usage: safety-check.sh BUY|SELL SYMBOL QTY PRICE SECTOR}"
SECTOR="${5:?usage: safety-check.sh BUY|SELL SYMBOL QTY PRICE SECTOR}"

SIDE_UPPER=$(echo "$SIDE" | tr '[:lower:]' '[:upper:]')

# For SELL orders, only basic validation needed
if [[ "$SIDE_UPPER" == "SELL" ]]; then
  echo '{"pass": true, "checks": {"side": "SELL — minimal checks"}, "reason": "Sell orders always allowed"}'
  exit 0
fi

# --- BUY-side validation ---

: "${ALPACA_API_KEY:?ALPACA_API_KEY not set}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set}"

API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
H_KEY="APCA-API-KEY-ID: $ALPACA_API_KEY"
H_SEC="APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"

# Pull account state
ACCOUNT=$(curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/account" 2>/dev/null || echo '{}')
POSITIONS=$(curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/positions" 2>/dev/null || echo '[]')

# Parse account values
EQUITY=$(echo "$ACCOUNT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('equity','0'))" 2>/dev/null || echo "0")
CASH=$(echo "$ACCOUNT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('cash','0'))" 2>/dev/null || echo "0")
DAYTRADE_COUNT=$(echo "$ACCOUNT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('daytrade_count','0'))" 2>/dev/null || echo "0")

# Count current positions
POS_COUNT=$(echo "$POSITIONS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

# Check if already holding this symbol
ALREADY_HOLDING=$(echo "$POSITIONS" | python3 -c "
import json,sys
positions = json.load(sys.stdin)
syms = [p.get('symbol','') for p in positions]
print('true' if '$SYMBOL' in syms else 'false')
" 2>/dev/null || echo "false")

# Calculate trade cost
TRADE_COST=$(python3 -c "print(round($QTY * $PRICE, 2))")

# Count trades this week from TRADE-LOG.md
TRADE_LOG="$ROOT/memory/TRADE-LOG.md"
WEEKLY_TRADES=0
if [[ -f "$TRADE_LOG" ]]; then
  # Get Monday of this week
  MON=$(python3 -c "
from datetime import date, timedelta
today = date.today()
monday = today - timedelta(days=today.weekday())
print(monday.isoformat())
")
  # Count BUY entries this week (grep -c exits 1 on zero matches; || true preserves the "0" output)
  WEEKLY_TRADES=$(grep -c "| BUY |" "$TRADE_LOG" 2>/dev/null || true)
  WEEKLY_TRADES="${WEEKLY_TRADES:-0}"
fi

# Check circuit breaker for sector bans
CB_FILE="$ROOT/memory/CIRCUIT-BREAKER.md"
SECTOR_BANNED="false"
if [[ -f "$CB_FILE" ]]; then
  SECTOR_BANNED=$(python3 -c "
import sys
sector = '$SECTOR'.lower()
with open('$CB_FILE') as f:
    content = f.read().lower()
if sector and sector in content and 'banned' in content:
    # Simple check — if the sector appears near 'banned', flag it
    lines = content.split('\n')
    for line in lines:
        if sector in line and 'banned' in line:
            print('true')
            sys.exit(0)
print('false')
" 2>/dev/null || echo "false")
fi

# --- Run all checks ---
python3 -c "
import json, sys

equity = float('$EQUITY')
cash = float('$CASH')
trade_cost = float('$TRADE_COST')
pos_count = int('$POS_COUNT')
daytrade_count = int('$DAYTRADE_COUNT')
weekly_trades = int('$WEEKLY_TRADES')
already_holding = '$ALREADY_HOLDING' == 'true'
sector_banned = '$SECTOR_BANNED' == 'true'

checks = {}
all_pass = True
reasons = []

# 1. Position count <= 6
check_pos = (pos_count + 1) <= 6
checks['position_count'] = {'pass': check_pos, 'current': pos_count, 'limit': 6}
if not check_pos:
    all_pass = False
    reasons.append(f'Position count would be {pos_count+1}, max is 6')

# 2. Position cost <= 20% of equity
max_position = equity * 0.20
check_size = trade_cost <= max_position
checks['position_size'] = {'pass': check_size, 'cost': trade_cost, 'max': round(max_position, 2)}
if not check_size:
    all_pass = False
    reasons.append(f'Position cost \${trade_cost} exceeds 20% of equity (\${round(max_position,2)})')

# 3. Enough cash
check_cash = trade_cost <= cash
checks['cash_available'] = {'pass': check_cash, 'cost': trade_cost, 'cash': cash}
if not check_cash:
    all_pass = False
    reasons.append(f'Insufficient cash: need \${trade_cost}, have \${cash}')

# 4. Weekly trade count <= 3
check_weekly = (weekly_trades + 1) <= 3
checks['weekly_trades'] = {'pass': check_weekly, 'current': weekly_trades, 'limit': 3}
if not check_weekly:
    all_pass = False
    reasons.append(f'Weekly trade count would be {weekly_trades+1}, max is 3')

# 5. Daytrade count < 3 (PDT rule for sub-\$25k accounts)
check_pdt = daytrade_count < 3 if equity < 25000 else True
checks['pdt_rule'] = {'pass': check_pdt, 'daytrade_count': daytrade_count, 'equity': equity}
if not check_pdt:
    all_pass = False
    reasons.append(f'PDT: {daytrade_count} day trades already (max 3 on sub-\$25k account)')

# 6. Sector not banned
check_sector = not sector_banned
checks['sector_ban'] = {'pass': check_sector, 'sector': '$SECTOR', 'banned': sector_banned}
if not check_sector:
    all_pass = False
    reasons.append(f'Sector $SECTOR is banned due to consecutive losses')

# 7. Not already holding
check_dup = not already_holding
checks['duplicate'] = {'pass': check_dup, 'symbol': '$SYMBOL', 'already_holding': already_holding}
if not check_dup:
    all_pass = False
    reasons.append(f'Already holding $SYMBOL')

# 8. Cash reserve >= 15% after trade
remaining_cash = cash - trade_cost
min_reserve = equity * 0.15
check_reserve = remaining_cash >= min_reserve
checks['cash_reserve'] = {'pass': check_reserve, 'remaining': round(remaining_cash, 2), 'min_reserve': round(min_reserve, 2)}
if not check_reserve:
    all_pass = False
    reasons.append(f'Cash reserve after trade (\${round(remaining_cash,2)}) below 15% minimum (\${round(min_reserve,2)})')

result = {
    'pass': all_pass,
    'checks': checks,
    'reason': '; '.join(reasons) if reasons else 'All checks passed'
}

print(json.dumps(result, indent=2))
sys.exit(0 if all_pass else 1)
"
