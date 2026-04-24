#!/usr/bin/env bash
# Research wrapper. All market research goes through xAI Grok.
# Usage: bash scripts/grok.sh <search|sentiment|news> "<query>"
# Exits with code 3 if XAI_API_KEY is unset so callers can fall back to WebSearch.

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

if [[ -z "${XAI_API_KEY:-}" ]]; then
  echo "WARNING: XAI_API_KEY not set. Fall back to WebSearch." >&2
  exit 3
fi

API="https://api.x.ai/v1/responses"
MODEL="grok-4-1-fast"

case "$cmd" in
  search)
    # General web search for market research
    payload=$(python3 -c "
import json, sys
print(json.dumps({
    'model': '$MODEL',
    'tools': [{'type': 'web_search'}],
    'input': sys.argv[1]
}))
" "$query")
    ;;
  sentiment)
    # X/Twitter sentiment analysis
    payload=$(python3 -c "
import json, sys
q = sys.argv[1]
# Add dollar sign for tickers if not present
if not q.startswith('\$') and len(q) <= 5 and q.isalpha():
    q = '\$' + q
print(json.dumps({
    'model': '$MODEL',
    'tools': [{'type': 'web_search', 'search_context_size': 'high'}],
    'input': f'Analyze current X/Twitter sentiment for {q}. What are traders saying? Is sentiment bullish, bearish, or neutral? Summarize the key themes in 3-5 bullets. Be concise.'
}))
" "$query")
    ;;
  news)
    # Financial news search
    payload=$(python3 -c "
import json, sys
print(json.dumps({
    'model': '$MODEL',
    'tools': [{'type': 'web_search', 'search_context_size': 'medium'}],
    'input': f'Latest financial news about: {sys.argv[1]}. Focus on price-moving catalysts, earnings, analyst ratings, and sector trends. Cite sources. Be concise.'
}))
" "$query")
    ;;
  *)
    echo "Usage: bash scripts/grok.sh <search|sentiment|news> \"<query>\"" >&2
    exit 1
    ;;
esac

curl -fsS "$API" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$payload"
echo
