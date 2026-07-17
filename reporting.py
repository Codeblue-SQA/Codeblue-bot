"""
Lead submission status reporting.

This intentionally only tracks pass/fail + a message for each site's
lead form submission - no page-speed metrics, no load/response timing.
"""

import csv
import json
import os
from datetime import datetime, timezone

from config import ReportConfig


class LeadSubmissionReport:
    def __init__(self):
        self.results = []  # list of dicts

    def record(self, site_name: str, success: bool, message: str = ""):
        self.results.append(
            {
                "site": site_name,
                "status": "PASS" if success else "FAIL",
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def _output_paths(self, run_id: str):
        os.makedirs(ReportConfig.output_dir, exist_ok=True)
        csv_path = os.path.join(ReportConfig.output_dir, f"lead_report_{run_id}.csv")
        json_path = os.path.join(ReportConfig.output_dir, f"lead_report_{run_id}.json")
        return csv_path, json_path

    def save(self):
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        csv_path, json_path = self._output_paths(run_id)

        with open(json_path, "w") as f:
            json.dump(self.results, f, indent=2)

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["site", "status", "message", "timestamp"]
            )
            writer.writeheader()
            writer.writerows(self.results)

        print(f"[reporting] Saved lead submission report -> {csv_path}")
        return csv_path, json_path

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = total - passed
        return {"total": total, "passed": passed, "failed": failed}
