# Lead Submission Bot

Simplified Selenium QA suite: submits lead forms across your sites,
reports PASS/FAIL per site, routes through a US proxy, and can run on
a schedule.

## What changed from the old project

- **Removed:** PageSpeed analysis, `Pagespeed.py`, `reports/pagespeed/`,
  and all response/load-timing logic. Reporting now covers lead
  submission status only (`reporting.py`).
- **Added:** configurable US proxy at the ChromeOptions level
  (`config.py` + `driver_factory.py`), including authenticated proxy
  support via an auto-generated Chrome extension (Chrome's
  `--proxy-server` flag can't carry `user:pass@` credentials, so we
  work around that the standard way).
- **Added:** a portable scheduler (`scheduler.py`) with 0–60 min
  jitter before each hourly run.

## Migrating your existing tests

1. Delete `Pagespeed.py`, `reports/pagespeed/`, and any timing helper
   modules from your old project.
2. Search your old test files for imports of those modules
   (`grep -rn "pagespeed\|timing" your_old_project/`) and remove the
   calls.
3. For each site, copy `tests/test_lead_submission_example.py` to
   `tests/test_lead_submission_<sitename>.py`, and port over your
   existing form-fill logic into the `run(driver)` function. It must
   return `(success: bool, message: str)`.
4. Delete the example file once you've migrated your real sites (or
   leave it — the runner just skips it if `example.com` isn't
   reachable, it'll show as a FAIL in the report).

## Setup

```bash
pip install -r requirements.txt
cp config.ini.example config.ini   # then fill in your proxy details
```

Or use environment variables instead of `config.ini` (these take
precedence): `PROXY_HOST`, `PROXY_PORT`, `PROXY_USERNAME`,
`PROXY_PASSWORD`, `PROXY_SCHEME`, `PROXY_ENABLED`.

## Running manually

```bash
python run_tests.py
```

## Running on a schedule

You don't know yet where this will be deployed — three options that
all work with what's here:

**A. Standalone loop (simplest, works anywhere with a long-running process):**
```bash
python scheduler.py
```
Runs forever: random 0–60 min jitter, run the suite, sleep until the
next hourly slot, repeat. Fine in a VM, a `tmux`/`screen` session, or
as a systemd service.

**B. Docker (portable to any cloud - ECS, Cloud Run, a VM, etc.):**
```bash
docker build -t lead-bot .
docker run -d --env-file .env lead-bot
```

**C. External scheduler owns the timing (cron, Kubernetes CronJob,
AWS EventBridge, GCP Cloud Scheduler, GitHub Actions `schedule:`):**
```bash
SCHEDULER_RUN_ONCE=true python scheduler.py
```
This still applies the random jitter, runs once, and exits — let the
platform fire it hourly.

Example crontab (hourly, jitter handled inside the script):
```
0 * * * * cd /path/to/lead_bot && SCHEDULER_RUN_ONCE=true /usr/bin/python3 scheduler.py >> cron.log 2>&1
```

## Reports

Each run writes `reports/lead_report_<timestamp>.csv` and `.json`
with one row per site: `site, status (PASS/FAIL), message, timestamp`.
