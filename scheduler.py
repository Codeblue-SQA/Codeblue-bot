"""
Portable scheduler for the lead submission bot.

Two ways to use it:

1. STANDALONE LOOP (no external scheduler needed):
     python scheduler.py
   Runs forever: waits a random 0-N minute jitter, runs the suite,
   then sleeps until the next hourly slot, repeating indefinitely.
   Works fine in a long-running container, VM, or `screen`/`tmux`
   session on any cloud provider.

2. ONE-SHOT MODE (let an external scheduler own the timing):
     SCHEDULER_RUN_ONCE=true python scheduler.py
   Applies the random jitter once, runs the suite a single time, then
   exits. Point cron, a Kubernetes CronJob, AWS EventBridge, GCP Cloud
   Scheduler, or GitHub Actions' `schedule:` trigger at this and let
   the platform handle the hourly cadence - this just adds the jitter
   and runs the tests.
"""

import random
import sys
import time
from datetime import datetime

from config import SchedulerConfig
from run_tests import run_all


def _sleep_with_jitter():
    jitter_minutes = random.uniform(0, SchedulerConfig.max_jitter_minutes)
    jitter_seconds = jitter_minutes * 60
    print(
        f"[scheduler] Waiting {jitter_minutes:.1f} min before this run "
        f"(random jitter, max {SchedulerConfig.max_jitter_minutes} min)."
    )
    time.sleep(jitter_seconds)


def run_once():
    _sleep_with_jitter()
    print(f"[scheduler] Starting run at {datetime.now().isoformat()}")
    run_all(headless=True)


def run_forever():
    interval_seconds = SchedulerConfig.interval_minutes * 60
    while True:
        cycle_start = time.monotonic()
        run_once()

        elapsed = time.monotonic() - cycle_start
        remaining = max(interval_seconds - elapsed, 0)
        print(
            f"[scheduler] Cycle complete. Sleeping {remaining / 60:.1f} min "
            f"until next scheduled run."
        )
        time.sleep(remaining)


if __name__ == "__main__":
    if SchedulerConfig.run_once:
        run_once()
        sys.exit(0)
    else:
        run_forever()
