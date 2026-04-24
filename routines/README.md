# Cloud Routine Prompts

Each file in this directory is the prompt for a Claude Code cloud routine.
Paste the content of each file verbatim into the routine's prompt field.
Do not paraphrase — the env-var check block and commit-and-push step are load-bearing.

| Routine | Schedule (ET) | Cron |
|---------|--------------|------|
| pre-market | 6:00 AM Mon-Fri | `0 6 * * 1-5` |
| market-open | 9:35 AM Mon-Fri | `35 9 * * 1-5` |
| midday | 12:00 PM Mon-Fri | `0 12 * * 1-5` |
| daily-summary | 3:45 PM Mon-Fri | `45 15 * * 1-5` |
| weekly-review | 4:15 PM Fridays | `15 16 * * 5` |
