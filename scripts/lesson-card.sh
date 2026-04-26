#!/usr/bin/env bash
# Create a lesson card for a closed trade.
#
# Usage:
#   bash scripts/lesson-card.sh TICKER SECTOR ENTRY_DATE EXIT_DATE \
#        ENTRY_PRICE EXIT_PRICE SHARES PNL_PCT EXIT_REASON ONE_LINE_LESSON [tag1,tag2,...]
#
# Creates memory/lessons/YYYY-MM-DD-TICKER.md from the template
# and appends a one-line entry to memory/lessons/INDEX.md.
#
# After creating, the agent should open the file and fill in the
# Setup / What I expected / What actually happened / Why sections.

set -euo pipefail

if [[ $# -lt 10 ]]; then
  echo "Usage: $0 TICKER SECTOR ENTRY_DATE EXIT_DATE ENTRY_PRICE EXIT_PRICE SHARES PNL_PCT EXIT_REASON LESSON [tags]" >&2
  exit 2
fi

TICKER="$1"
SECTOR="$2"
ENTRY_DATE="$3"
EXIT_DATE="$4"
ENTRY_PRICE="$5"
EXIT_PRICE="$6"
SHARES="$7"
PNL_PCT="$8"
EXIT_REASON="$9"
LESSON="${10}"
TAGS="${11:-}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LESSONS_DIR="$REPO_ROOT/memory/lessons"
TEMPLATE="$LESSONS_DIR/_TEMPLATE.md"
INDEX="$LESSONS_DIR/INDEX.md"

# WIN/LOSS based on sign of PNL_PCT
if awk "BEGIN {exit !($PNL_PCT > 0)}"; then
  OUTCOME="WIN"
else
  OUTCOME="LOSS"
fi

OUT_PATH="$LESSONS_DIR/${EXIT_DATE}-${TICKER}.md"
if [[ -e "$OUT_PATH" ]]; then
  echo "Lesson card already exists: $OUT_PATH" >&2
  exit 1
fi

# Generate the card from template
sed \
  -e "s|^ticker:.*|ticker: $TICKER|" \
  -e "s|^sector:.*|sector: $SECTOR|" \
  -e "s|^entry_date:.*|entry_date: $ENTRY_DATE|" \
  -e "s|^exit_date:.*|exit_date: $EXIT_DATE|" \
  -e "s|^entry_price:.*|entry_price: $ENTRY_PRICE|" \
  -e "s|^exit_price:.*|exit_price: $EXIT_PRICE|" \
  -e "s|^shares:.*|shares: $SHARES|" \
  -e "s|^pnl_pct:.*|pnl_pct: $PNL_PCT|" \
  -e "s|^exit_reason:.*|exit_reason: $EXIT_REASON|" \
  -e "s|^outcome:.*|outcome: $OUTCOME|" \
  -e "s|{{TICKER}}|$TICKER|g" \
  -e "s|{{ENTRY_DATE}}|$ENTRY_DATE|g" \
  -e "s|{{EXIT_DATE}}|$EXIT_DATE|g" \
  -e "s|{{PNL_PCT}}|$PNL_PCT|g" \
  "$TEMPLATE" > "$OUT_PATH"

# One-line index entry (newest at top, after the comment marker)
ENTRY="$EXIT_DATE | $TICKER | $SECTOR | ${PNL_PCT}% | $EXIT_REASON | $LESSON | [$TAGS]"
# Insert after the marker comment
awk -v e="$ENTRY" '
  /<!-- Entries appended below by scripts\/lesson-card.sh -->/ {
    print; print ""; print e; next
  } { print }
' "$INDEX" > "$INDEX.tmp" && mv "$INDEX.tmp" "$INDEX"

echo "Created: $OUT_PATH"
echo "Indexed: $ENTRY"
echo ""
echo "Now open $OUT_PATH and fill in the Setup / Expected / Actual / Why sections."
