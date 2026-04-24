#!/usr/bin/env bash
# Research wrapper. Uses OpenRouter (NVIDIA free tier) for market research.
# Usage: bash scripts/grok.sh <search|sentiment|news> "<query>"
# Exits with code 3 if OPENROUTER_API_KEY is unset so callers can fall back to WebSearch.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

cmd="${1:-}"
shift || true

query="${1:-}"
if [[ -z "$query" ]]; then
  echo "usage: bash scripts/grok.sh <search|sentiment|news> \"<query>\"" >&2
  exit 1
fi

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "WARNING: OPENROUTER_API_KEY not set. Fall back to WebSearch." >&2
  exit 3
fi

API="https://openrouter.ai/api/v1/chat/completions"
MODEL="nvidia/nemotron-3-super-120b-a12b:free"

case "$cmd" in
  search)
    prompt="You are a market research assistant. Answer concisely with the most relevant information you know about: $query. Focus on price-moving factors, key data points, and market implications. Note your knowledge cutoff if the query requires real-time data."
    ;;
  sentiment)
    ticker="$query"
    if [[ ${#ticker} -le 5 && "$ticker" =~ ^[A-Za-z]+$ ]]; then
      ticker="\$$ticker"
    fi
    prompt="Analyze market sentiment for $ticker. Based on recent trends, news, and analyst coverage you know about: Is sentiment bullish, bearish, or neutral? What are the key themes driving sentiment? Summarize in 3-5 bullets. Be concise."
    ;;
  news)
    prompt="Summarize the latest financial news about: $query. Focus on price-moving catalysts, earnings, analyst ratings, and sector trends. Be concise and cite what you know. Note if data may be dated."
    ;;
  *)
    echo "Usage: bash scripts/grok.sh <search|sentiment|news> \"<query>\"" >&2
    exit 1
    ;;
esac

payload=$(python3 -c "
import json, sys
print(json.dumps({
    'model': '$MODEL',
    'messages': [{'role': 'user', 'content': sys.argv[1]}]
}))
" "$prompt")

curl -fsS "$API" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Title: ArcTrader" \
  -d "$payload"
echo
