#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest

PY = sys.executable


def run(*args):
    r = subprocess.run([PY, "latefee.py", *args], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


class TestCompute(unittest.TestCase):
    def test_basic_fee_calculation(self):
        rc, out, _ = run("compute", "1000", "--due-date", "2026-09-01", "--today", "2026-10-17", "--json")
        self.assertEqual(rc, 0)
        d = json.loads(out)
        self.assertEqual(d["days_overdue"], 46)
        self.assertEqual(d["late_fee"], 23.0)
        self.assertEqual(d["total_due"], 1023.0)
        self.assertEqual(d["stage"], "final")

    def test_grace_period_reduces_days_overdue(self):
        rc, out, _ = run("compute", "1000", "--due-date", "2026-10-01", "--today", "2026-10-10",
                          "--grace-days", "5", "--json")
        self.assertEqual(rc, 0)
        d = json.loads(out)
        self.assertEqual(d["days_overdue"], 4)
        self.assertEqual(d["stage"], "friendly")

    def test_not_yet_due_exits_nonzero(self):
        rc, out, err = run("compute", "500", "--due-date", "2026-10-20", "--today", "2026-10-17")
        self.assertNotEqual(rc, 0)
        self.assertIn("Not yet due", err)

    def test_invalid_date_rejected(self):
        rc, out, err = run("compute", "500", "--due-date", "not-a-date")
        self.assertNotEqual(rc, 0)
        self.assertIn("Invalid", err)

    def test_custom_rate(self):
        rc, out, _ = run("compute", "2000", "--due-date", "2026-10-01", "--today", "2026-10-31",
                          "--rate", "3", "--json")
        self.assertEqual(rc, 0)
        d = json.loads(out)
        self.assertEqual(d["days_overdue"], 30)
        self.assertEqual(d["late_fee"], 60.0)

    def test_stages_command_runs(self):
        rc, out, _ = run("stages")
        self.assertEqual(rc, 0)
        self.assertIn("friendly", out)
        self.assertIn("final", out)


if __name__ == "__main__":
    unittest.main()
