"""Failure receipts for the maintenance runner, without real host operations."""
from pathlib import Path
import json
import os
import subprocess
import sys

from test_distribution import DistributionFixture, ROOT


class InstallationRunnerFailureTests(DistributionFixture):
    def invoke(self, output, *, optimized=False, powershell=None):
        args = [sys.executable, "-B"]
        if optimized:
            args.append("-O")
        args += [str(ROOT / "scripts/verify_installation.py"), "--powershell", powershell or sys.executable,
                 "--powershell-major", "7", "--bash", sys.executable, "--smoke-only", "--output", str(output)]
        env = os.environ.copy()
        env.pop("PYTHONOPTIMIZE", None)
        return subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")

    def test_invalid_shell_creates_a_failure_receipt(self):
        output = self.work / "invalid-shell"
        result = self.invoke(output, powershell=str(self.work / "missing-shell"))
        self.assertNotEqual(0, result.returncode)
        record = json.loads((output / "result.json").read_text(encoding="utf-8"))
        self.assertEqual("FAIL", record["result"])
        self.assertIn("LOOPPILOT_TEST_POWERSHELL", record["error"])
        self.assertNotIn("lifecycle", record)

    def test_optimized_python_cannot_report_pass(self):
        output = self.work / "optimized"
        result = self.invoke(output, optimized=True)
        self.assertNotEqual(0, result.returncode)
        record = json.loads((output / "result.json").read_text(encoding="utf-8"))
        self.assertEqual("FAIL", record["result"])
        self.assertIn("Optimized Python", record["error"])
        self.assertNotIn("lifecycle", record)

    def test_failed_version_probe_retains_raw_output(self):
        output = self.work / "probe-failure"
        result = self.invoke(output)
        self.assertNotEqual(0, result.returncode)
        record = json.loads((output / "result.json").read_text(encoding="utf-8"))
        self.assertEqual("FAIL", record["result"])
        self.assertIn("version probe exited", record["error"])
        self.assertTrue((output / "powershell-version.stderr.log").read_bytes())
        self.assertNotIn("lifecycle", record)
