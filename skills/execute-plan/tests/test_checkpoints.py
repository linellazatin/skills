"""Exercise checkpoint behavior through the public CLI in isolated directories."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "checkpoints.py"


class Checkpoints(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = self.root / "plan.md"
        self.plan.write_text("A normal plan without numbered tasks.")

    def run_cli(self, action, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), action, str(self.plan)] + list(args),
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stderr + result.stdout)
        return json.loads(result.stdout) if result.returncode == 0 else result

    def start(self):
        self.run_cli("start", "phase", "--summary", "Expected behavior", "--workdir", str(self.root))

    def check(self, label, code, ok=True):
        return self.run_cli("check", "phase", "--label", label, "--", sys.executable, "-c", code, ok=ok)

    def test_read_only_status(self):
        self.assertEqual(self.run_cli("status")["state"], {})
        self.assertFalse((self.root / ".workflow").exists())

    def test_named_checks_and_latest_failure_gate(self):
        self.start()
        self.check("unit", "print('verified')")
        self.check("docs", "raise SystemExit(1)", ok=False)
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", "--check", "docs", ok=False)
        self.check("docs", "pass")
        self.assertEqual(self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", "--check", "docs")["status"], "awaiting_review")
        self.check("unit", "raise SystemExit(2)", ok=False)
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)

    def test_revision_and_phase_isolation(self):
        self.start()
        self.check("unit", "pass")
        self.plan.write_text("Changed scope")
        self.assertTrue(self.run_cli("status")["stale"])
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)
        self.start()
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)
        self.run_cli("check", "other", "--label", "unit", "--", sys.executable, "-c", "pass", ok=False)

    def test_timeout_and_launch_error_are_incomplete(self):
        self.start()
        self.run_cli("check", "phase", "--label", "timeout", "--timeout", "0.01", "--", sys.executable, "-c", "import time; time.sleep(1)", ok=False)
        self.run_cli("check", "phase", "--label", "missing", "--", str(self.root / "missing-program"), ok=False)
        state = self.run_cli("status")["state"]
        self.assertEqual(state["checks"]["timeout"]["result"], "incomplete")
        self.assertEqual(state["checks"]["missing"]["result"], "incomplete")

    def test_literal_arguments_workdir_and_logs(self):
        self.start()
        literal = "$(touch forbidden); `touch forbidden`"
        result = self.run_cli("check", "phase", "--label", "arguments", "--", sys.executable,
                              "-c", "import os,sys; print(os.getcwd()); print(sys.argv[1]); print('stderr',file=sys.stderr)", literal)
        log = Path(result["log"]).read_text()
        self.assertIn(str(self.root), log)
        self.assertIn(literal, log)
        self.assertIn("stderr", log)
        self.assertFalse((self.root / "forbidden").exists())

    def test_lock_and_invalid_options_do_not_replace_evidence(self):
        self.start()
        before = self.run_cli("status")["state"]
        checkpoint = next((self.root / ".workflow").glob("*/checkpoint.json"))
        lock = checkpoint.parent / "lock"
        lock.write_text("active writer")
        self.run_cli("start", "other", "--summary", "Other outcome", ok=False)
        self.assertTrue(lock.exists())
        self.assertEqual(before, self.run_cli("status")["state"])
        lock.unlink()
        self.run_cli("handoff", "phase", "--summary", "Ready", ok=False)
        self.run_cli("status", "--", sys.executable, "-c", "pass", ok=False)
        self.run_cli("check", "phase", "--label", "invalid", "--timeout", "nan", "--", sys.executable, "-c", "pass", ok=False)
        self.assertEqual(before, self.run_cli("status")["state"])

    def test_review_includes_untracked_and_staged_without_mutation(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "tracked.txt").write_text("staged\n")
        subprocess.run(["git", "add", "tracked.txt"], cwd=self.root, check=True)
        (self.root / "tracked.txt").write_text("unstaged\n")
        self.start()
        before = subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root)
        report = self.run_cli("review")
        data = json.loads(Path(report["review"]).read_text())
        self.assertIn("staged", data["staged"])
        self.assertIn("unstaged", data["unstaged"])
        self.assertIn("plan.md", data["untracked_paths"])
        self.assertEqual(before, subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root))


if __name__ == "__main__":
    unittest.main()
