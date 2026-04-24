#!/usr/bin/env bash
# Runs an ArcTrader routine via Claude Code CLI (non-interactive).
# Usage: bash scripts/run-routine.sh <pre-market|market-open|midday|daily-summary|weekly-review>

set -euo pipefail

ROUTINE="${1:?usage: run-routine.sh <pre-market|market-open|midday|daily-summary|weekly-review>}"
ROOT="/home/sujit-waiba/Documents/ArchTrader"
LOG_DIR="$ROOT/logs"
ROUTINE_FILE="$ROOT/routines/${ROUTINE}.md"

if [[ ! -f "$ROUTINE_FILE" ]]; then
  echo "ERROR: routine file not found: $ROUTINE_FILE" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

# Find latest installed Claude Code binary
CLAUDE=$(ls /home/sujit-waiba/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | sort -V | tail -1)
if [[ -z "$CLAUDE" ]]; then
  echo "ERROR: Claude Code binary not found" >&2
  exit 1
fi

LOG="$LOG_DIR/${ROUTINE}.log"
echo "" >> "$LOG"
echo "========================================" >> "$LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S NPT') — START $ROUTINE" >> "$LOG"
echo "========================================" >> "$LOG"

# Run routine non-interactively, bypass permission prompts for unattended operation
HOME=/home/sujit-waiba \
  "$CLAUDE" \
    --dangerously-skip-permissions \
    --model claude-sonnet-4-6 \
    --print \
    "$(cat "$ROUTINE_FILE")" \
  >> "$LOG" 2>&1

echo "" >> "$LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S NPT') — END $ROUTINE" >> "$LOG"
