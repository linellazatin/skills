"""Exercise checkpoint behavior through the public CLI in isolated directories."""
import hashlib
import json
import os
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

    def reconcile(self, ok=True):
        revision = self.run_cli("status")["state"]["revision"]
        return self.run_cli("reconcile", "phase", "--from-revision", revision,
                            "--to-revision", hashlib.sha256(self.plan.read_bytes()).hexdigest(),
                            "--progress-only", "--summary", "Recorded results; checked inputs unchanged", ok=ok)

    def files(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

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

    def test_progress_reconciliation_retains_check_provenance_and_requires_handoff(self):
        self.start()
        original = self.plan.read_bytes()
        check = self.check("unit", "print('verified')")
        before = self.run_cli("status")["state"]
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit")
        self.plan.write_bytes(original + b"\nProgress: unit passed.\n")
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)
        state = self.reconcile()
        self.assertEqual(state["checks"], before["checks"])
        self.assertEqual(check["plan_revision"], before["revision"])
        self.assertEqual(Path(check["log"]).read_text(), "verified\n")
        self.assertEqual(state["status"], "working")
        self.assertNotIn("handoff", state)
        record = state["reconciliations"][0]
        self.assertEqual(record["from_revision"], before["revision"])
        self.assertEqual(record["to_revision"], hashlib.sha256(self.plan.read_bytes()).hexdigest())
        self.assertEqual(record["reason"], "Recorded results; checked inputs unchanged")
        self.assertEqual(record["attestation"], "caller-declared progress-only; checked inputs unchanged")
        self.assertEqual(Path(record["from_snapshot"]).read_bytes(), original)
        self.assertEqual(Path(record["to_snapshot"]).read_bytes(), self.plan.read_bytes())
        self.assertFalse(self.run_cli("status")["stale"])
        self.assertEqual(self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit")["status"],
                         "awaiting_review")

    def test_status_shows_bounded_plan_diff_without_writing(self):
        self.start()
        old = self.run_cli("status")["state"]["revision"]
        self.plan.write_text("Progress recorded\n" + "x\n" * 300)
        before = self.files()
        status = self.run_cli("status")
        self.assertTrue(status["stale"])
        self.assertEqual(status["current_revision"], hashlib.sha256(self.plan.read_bytes()).hexdigest())
        change = status["plan_change"]
        self.assertEqual(change["from_revision"], old)
        self.assertEqual(change["to_revision"], status["current_revision"])
        self.assertIn("-A normal plan", change["diff"])
        self.assertIn("+Progress recorded", change["diff"])
        self.assertTrue(change["truncated"])
        self.assertLessEqual(len(change["diff"].splitlines()), 200)
        self.assertEqual(self.files(), before)
        self.plan.write_text("x" * 20000)
        change = self.run_cli("status")["plan_change"]
        self.assertTrue(change["truncated"])
        self.assertLessEqual(len(change["diff"]), 16000)

    def test_reconciliation_requires_attestation_reason_and_exact_revisions(self):
        self.start()
        old = self.run_cli("status")["state"]["revision"]
        self.plan.write_text("Progress recorded")
        new = hashlib.sha256(self.plan.read_bytes()).hexdigest()
        before = self.files()
        valid = ["--from-revision", old, "--to-revision", new, "--progress-only", "--summary", "Progress only"]
        invalid = [valid[:4] + valid[5:], valid[:5], valid[:2] + valid[4:],
                   valid[2:], ["--from-revision", "wrong"] + valid[2:],
                   valid[:3] + ["wrong"] + valid[4:], valid[:6] + ["   "]]
        for args in invalid:
            with self.subTest(args=args):
                self.run_cli("reconcile", "phase", *args, ok=False)
                self.assertEqual(self.files(), before)
        self.run_cli("reconcile", "other", *valid, ok=False)
        self.assertEqual(self.files(), before)
        checkpoint = next((self.root / ".workflow").glob("*/checkpoint.json"))
        lock = checkpoint.parent / "lock"
        lock.write_text("active writer")
        self.run_cli("reconcile", "phase", *valid, ok=False)
        self.assertTrue(lock.exists())
        lock.unlink()
        self.assertEqual(self.files(), before)
        self.run_cli("reconcile", "phase", *valid)
        before = self.files()
        self.reconcile(ok=False)
        self.assertEqual(self.files(), before)

    def test_reconciliation_history_does_not_promote_failed_or_incomplete_checks(self):
        self.start()
        self.check("unit", "pass")
        self.check("failed", "raise SystemExit(2)", ok=False)
        self.run_cli("check", "phase", "--label", "missing", "--", str(self.root / "missing"), ok=False)
        original = self.run_cli("status")["state"]
        for i in range(2):
            self.plan.write_text(f"Progress update {i}")
            state = self.reconcile()
            self.assertEqual(state["checks"], original["checks"])
            self.assertEqual(len(state["reconciliations"]), i + 1)
            self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit",
                         "--check", "failed", "--check", "missing", ok=False)
        self.assertEqual(state["reconciliations"][0]["to_revision"],
                         state["reconciliations"][1]["from_revision"])
        self.check("unit", "raise SystemExit(3)", ok=False)
        self.plan.write_text("Latest unit failure recorded")
        state = self.reconcile()
        self.assertEqual(state["checks"]["unit"]["result"], "failed")
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)
        self.start()
        state = self.run_cli("status")["state"]
        self.assertEqual(state["checks"], {})
        self.assertEqual(state["reconciliations"], [])

    def test_material_plan_change_stays_blocked_by_default(self):
        self.start()
        self.check("unit", "pass")
        self.plan.write_text("New acceptance requirement and different command")
        before = self.run_cli("status")["state"]
        self.run_cli("check", "phase", "--label", "unit", "--", sys.executable, "-c", "pass", ok=False)
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)
        self.assertEqual(self.run_cli("status")["state"], before)
        self.start()
        self.assertEqual(self.run_cli("status")["state"]["checks"], {})
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)

    def test_legacy_state_is_readable_but_reconciliation_requires_snapshot(self):
        self.start()
        self.check("unit", "pass")
        checkpoint = next((self.root / ".workflow").glob("*/checkpoint.json"))
        state = json.loads(checkpoint.read_text())
        state.pop("plan_snapshot")
        state.pop("reconciliations")
        state["checks"]["unit"].pop("plan_revision")
        checkpoint.write_text(json.dumps(state))
        for snapshot in checkpoint.parent.glob("plan-*.txt"):
            snapshot.unlink()
        self.assertFalse(self.run_cli("status")["stale"])
        self.run_cli("handoff", "phase", "--summary", "Legacy result", "--check", "unit")
        self.plan.write_text("Progress recorded")
        self.assertIsNone(self.run_cli("status")["plan_change"]["diff"])
        before = self.files()
        result = self.reconcile(ok=False)
        self.assertIn("snapshot", result.stderr)
        self.assertEqual(self.files(), before)
        self.start()
        self.assertEqual(self.run_cli("status")["state"]["checks"], {})

    def test_corrupt_snapshot_cannot_be_reconciled(self):
        self.start()
        state = self.run_cli("status")["state"]
        Path(state["plan_snapshot"]).write_text("Tampered snapshot")
        self.plan.write_text("Progress recorded")
        before = self.files()
        result = self.reconcile(ok=False)
        self.assertIn("snapshot", result.stderr)
        self.assertEqual(self.files(), before)

    def test_reconciliation_preserves_exact_snapshot_bytes(self):
        self.plan.write_bytes(b"Outcome: preserve behavior\r\nProgress: pending\r\n")
        original = self.plan.read_bytes()
        self.start()
        self.plan.write_bytes(b"Outcome: preserve behavior\r\nProgress: verified\r\n")
        state = self.reconcile()
        record = state["reconciliations"][0]
        self.assertEqual(Path(record["from_snapshot"]).read_bytes(), original)
        self.assertEqual(Path(record["to_snapshot"]).read_bytes(), self.plan.read_bytes())

    def test_inspected_revisions_cannot_adopt_later_edits(self):
        self.start()
        old = self.run_cli("status")["state"]["revision"]
        self.plan.write_text("First progress update")
        inspected = hashlib.sha256(self.plan.read_bytes()).hexdigest()
        self.plan.write_text("Second progress update")
        before = self.files()
        result = self.run_cli("reconcile", "phase", "--from-revision", old, "--to-revision", inspected,
                              "--progress-only", "--summary", "Inspected first update", ok=False)
        self.assertIn("revisions do not match", result.stderr)
        self.assertEqual(self.files(), before)
        self.reconcile()
        before = self.files()
        self.plan.write_text("Third progress update")
        result = self.run_cli("reconcile", "phase", "--from-revision", old,
                              "--to-revision", hashlib.sha256(self.plan.read_bytes()).hexdigest(),
                              "--progress-only", "--summary", "Old checkpoint inspection", ok=False)
        self.assertIn("revisions do not match", result.stderr)
        self.assertEqual({p: data for p, data in self.files().items() if p != "plan.md"},
                         {p: data for p, data in before.items() if p != "plan.md"})

    def test_interrupted_running_result_is_not_promoted(self):
        self.start()
        self.check("unit", "pass")
        checkpoint = next((self.root / ".workflow").glob("*/checkpoint.json"))
        state = json.loads(checkpoint.read_text())
        # Fixture for a process killed after saving running state, before completion.
        state["checks"]["unit"]["result"] = "running"
        state["checks"]["unit"].pop("exit_code")
        state["checks"]["unit"].pop("finished")
        checkpoint.write_text(json.dumps(state))
        self.plan.write_text("Interrupted check recorded")
        reconciled = self.reconcile()
        self.assertEqual(reconciled["checks"], state["checks"])
        self.run_cli("handoff", "phase", "--summary", "Ready", "--check", "unit", ok=False)

    def test_reconciliation_flags_are_rejected_for_other_actions(self):
        self.start()
        before = self.files()
        for args in (["--progress-only"], ["--from-revision", "old"], ["--to-revision", "new"]):
            self.run_cli("status", *args, ok=False)
            self.assertEqual(self.files(), before)

    def test_review_preserves_checkout_and_index_with_stale_stat_cache(self):
        checkout = self.root / "checkout"
        checkout.mkdir()
        subprocess.run(["git", "init", "-q", str(checkout)], check=True)
        subprocess.run(["git", "config", "diff.autoRefreshIndex", "true"], cwd=checkout, check=True)
        tracked = checkout / "tracked.txt"
        tracked.write_text("staged\n")
        modified = checkout / "modified.txt"
        modified.write_text("before\n")
        subprocess.run(["git", "add", "."], cwd=checkout, check=True)
        modified.write_text("user edit\n")
        (checkout / "user-notes.txt").write_text("untracked user work\n")
        timestamps = tracked.stat()
        os.utime(tracked, ns=(timestamps.st_atime_ns, timestamps.st_mtime_ns - 2000000000))
        self.run_cli("start", "phase", "--summary", "Read-only Git report", "--workdir", str(checkout))
        before = {str(path.relative_to(checkout)): path.read_bytes()
                  for path in checkout.rglob("*") if path.is_file()}
        report = self.run_cli("review")
        after = {str(path.relative_to(checkout)): path.read_bytes()
                 for path in checkout.rglob("*") if path.is_file()}
        self.assertEqual(hashlib.sha256(before[".git/index"]).hexdigest(),
                         hashlib.sha256(after[".git/index"]).hexdigest(), "review refreshed the Git index")
        self.assertEqual(before, after)
        data = json.loads(Path(report["review"]).read_text())
        self.assertIn("staged", data["staged"])
        self.assertIn("user edit", data["unstaged"])
        self.assertIn("user-notes.txt", data["untracked_paths"])
        self.assertEqual(Path(report["review"]).parents[1], (self.root / ".workflow").resolve())

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
