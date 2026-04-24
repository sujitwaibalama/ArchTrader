#!/usr/bin/env bash
# Installs ArcTrader cron jobs (Nepal Time / NPT = UTC+5:45).
# Run once: bash scripts/setup-cron.sh
# To remove: bash scripts/setup-cron.sh remove

ROOT="/home/sujit-waiba/Documents/ArchTrader"
RUNNER="bash $ROOT/scripts/run-routine.sh"

# All times converted from US ET to NPT (UTC+5:45)
# US market is EDT (UTC-4) Apr-Nov, EST (UTC-5) Nov-Mar
# Current offset used: EDT → NPT = +9h45m
#
#  6:00 AM ET  = 3:45 PM NPT  → pre-market
#  9:35 AM ET  = 7:20 PM NPT  → market-open
# 12:00 PM ET  = 9:45 PM NPT  → midday
#  3:45 PM ET  = 1:30 AM NPT  → daily-summary  (next day, so Tue-Sat)
#  4:15 PM ET  = 2:00 AM NPT  → weekly-review  (Sat only)

CRON_JOBS="
# ArcTrader — automated trading routines (NPT times)
45 15 * * 1-5 $RUNNER pre-market    >> $ROOT/logs/cron.log 2>&1
20 19 * * 1-5 $RUNNER market-open   >> $ROOT/logs/cron.log 2>&1
45 21 * * 1-5 $RUNNER midday        >> $ROOT/logs/cron.log 2>&1
30 1  * * 2-6 $RUNNER daily-summary >> $ROOT/logs/cron.log 2>&1
0  2  * * 6   $RUNNER weekly-review >> $ROOT/logs/cron.log 2>&1
"

if [[ "${1:-}" == "remove" ]]; then
  crontab -l 2>/dev/null | grep -v "ArcTrader" | grep -v "run-routine" | crontab -
  echo "ArcTrader cron jobs removed."
  exit 0
fi

mkdir -p "$ROOT/logs"

# Merge with existing crontab (skip if already installed)
if crontab -l 2>/dev/null | grep -q "run-routine"; then
  echo "ArcTrader cron jobs already installed. Run with 'remove' first to reinstall."
  crontab -l | grep "run-routine"
  exit 0
fi

(crontab -l 2>/dev/null; echo "$CRON_JOBS") | crontab -
echo "ArcTrader cron jobs installed:"
crontab -l | grep "run-routine"
