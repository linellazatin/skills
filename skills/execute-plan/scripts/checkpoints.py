#!/usr/bin/env python3
"""Record inline phase checks. Python 3.9+, standard library only."""
import argparse
import difflib
import hashlib
import json
import math
import subprocess
import sys
import time
from itertools import islice
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_bytes(state, folder):
    snapshot = folder / ("plan-" + state["revision"] + ".txt")
    if state.get("plan_snapshot") != str(snapshot):
        return None
    try:
        data = snapshot.read_bytes()
    except FileNotFoundError:
        return None
    return data if hashlib.sha256(data).hexdigest() == state["revision"] else None


def plan_change(state, folder, data, revision):
    old = snapshot_bytes(state, folder)
    change = {"from_revision": state["revision"], "to_revision": revision,
              "from_snapshot": state.get("plan_snapshot"), "diff": None,
              "snapshot_available": old is not None, "truncated": False}
    if old is not None:
        lines = list(islice(difflib.unified_diff(
            old.decode("utf-8", errors="replace").splitlines(),
            data.decode("utf-8", errors="replace").splitlines(),
            fromfile=state["plan_snapshot"], tofile=state["plan"], lineterm=""), 201))
        text = "\n".join(lines[:200])
        change.update(diff=text[:16000], truncated=len(lines) > 200 or len(text) > 16000)
    return change


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    command = []
    if "--" in argv:
        split = argv.index("--")
        argv, command = argv[:split], argv[split + 1:]
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: checkpoints.py status /project/plan.md. Inspect its diff and revisions before "
               "reconcile; material changes require start and rerun. No checkout freshness is certified.")
    parser.add_argument("action", choices=["status", "start", "check", "reconcile", "handoff", "review"])
    parser.add_argument("plan", type=Path, help="existing plan file")
    parser.add_argument("phase", nargs="?", help="active phase; optional for status/review")
    parser.add_argument("--workdir", type=Path, help="check directory for start (default: current directory)")
    parser.add_argument("--summary", default="", help="outcome, handoff, or reconciliation reason (default: empty)")
    parser.add_argument("--label", help="check label (default: none)")
    parser.add_argument("--check", action="append", default=[], help="required handoff label; repeatable (default: none)")
    parser.add_argument("--timeout", type=float, default=300, help="check timeout in seconds (default: 300)")
    parser.add_argument("--from-revision", help="inspected checkpoint digest for reconcile (default: none)")
    parser.add_argument("--to-revision", help="inspected current plan digest for reconcile (default: none)")
    parser.add_argument("--progress-only", action="store_true",
                        help="attest only progress changed and checked inputs are unchanged (default: false)")
    args = parser.parse_args(argv)
    if command and args.action != "check":
        parser.error("only check accepts an execution command")
    if args.workdir and args.action != "start":
        parser.error("--workdir is set when starting the phase")
    if args.action != "reconcile" and (args.from_revision is not None or args.to_revision is not None or args.progress_only):
        parser.error("revision flags and --progress-only are only for reconcile")
    if args.action == "reconcile" and (not args.from_revision or not args.to_revision or
                                        not args.progress_only or not args.summary.strip()):
        parser.error("reconcile requires --from-revision, --to-revision, --progress-only, and a nonempty --summary reason")
    plan = args.plan.resolve(strict=True)
    plan_data = plan.read_bytes()
    revision = hashlib.sha256(plan_data).hexdigest()
    folder = plan.parent / ".workflow" / hashlib.sha256(str(plan).encode()).hexdigest()[:16]
    state_file = folder / "checkpoint.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    if args.action == "status":
        stale = bool(state) and state["revision"] != revision
        print(json.dumps({"state": state, "stale": stale, "current_revision": revision,
                          "plan_change": plan_change(state, folder, plan_data, revision) if stale else None}, indent=2))
        return 0
    if args.action != "start" and (not state or (args.action != "reconcile" and state["revision"] != revision)):
        parser.error("start a phase for this plan revision first")
    if args.action not in ("review",) and not args.phase:
        parser.error("phase is required")
    if args.action != "start" and args.phase and args.phase != state["phase"]:
        parser.error("phase does not match the active checkpoint")
    folder.mkdir(parents=True, exist_ok=True)
    (folder.parent / ".gitignore").write_text("*\n", encoding="utf-8")
    lock = folder / "lock"
    try:
        handle = lock.open("x")
    except FileExistsError:
        parser.error("checkpoint locked; confirm no helper is running before removing its lock")
    def save():
        temporary = folder / "checkpoint.tmp"
        temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        temporary.replace(state_file)
    try:
        with handle:
            handle.write(str(time.time()))
        state = json.loads(state_file.read_text()) if state_file.exists() else {}
        if digest(plan) != revision:
            parser.error("plan changed; inspect status before continuing")
        if args.action != "start" and (not state or
                                       (args.action != "reconcile" and state["revision"] != revision) or
                                       (args.phase and args.phase != state["phase"])):
            parser.error("checkpoint changed; inspect status before continuing")
        if args.action == "start":
            if not args.summary:
                parser.error("start requires --summary describing the phase outcome")
            workdir = (args.workdir or Path.cwd()).resolve(strict=True)
            if not workdir.is_dir():
                parser.error("workdir must be a directory")
            snapshot = folder / ("plan-" + revision + ".txt")
            snapshot.write_bytes(plan_data)
            state = {"plan": str(plan), "revision": revision, "plan_snapshot": str(snapshot), "phase": args.phase,
                     "workdir": str(workdir), "summary": args.summary, "status": "working", "checks": {},
                     "reconciliations": []}
            save()
        elif args.action == "reconcile":
            if args.from_revision != state["revision"] or args.to_revision != revision:
                parser.error("revisions do not match checkpoint/current plan; inspect status before reconciling")
            if state["revision"] == revision:
                parser.error("plan is unchanged; no reconciliation needed")
            if snapshot_bytes(state, folder) is None:
                parser.error("checkpoint snapshot missing or corrupt; start a fresh phase and rerun checks")
            snapshot = folder / ("plan-" + revision + ".txt")
            snapshot.write_bytes(plan_data)
            record = {"from_revision": state["revision"], "to_revision": revision,
                      "from_snapshot": state["plan_snapshot"], "to_snapshot": str(snapshot),
                      "reason": args.summary.strip(), "recorded": time.time(),
                      "attestation": "caller-declared progress-only; checked inputs unchanged"}
            state.setdefault("reconciliations", []).append(record)
            state.update(revision=revision, plan_snapshot=str(snapshot), status="working")
            state.pop("handoff", None)
            save()
        elif args.action == "check":
            if not args.label or not command or not math.isfinite(args.timeout) or args.timeout <= 0:
                parser.error("check requires --label, a positive finite timeout, and -- PROGRAM ARGS")
            log = folder / ("check-" + str(time.time_ns()) + ".log")
            evidence = {"argv": command, "log": str(log), "plan_revision": revision,
                        "result": "running", "started": time.time()}
            state["checks"][args.label] = evidence
            state["status"] = "working"
            save()
            with log.open("wb") as output:
                try:
                    result = subprocess.run(command, cwd=state["workdir"], stdin=subprocess.DEVNULL,
                                            stdout=output, stderr=subprocess.STDOUT, timeout=args.timeout)
                    evidence.update(result="passed" if result.returncode == 0 else "failed", exit_code=result.returncode)
                except (OSError, subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
                    output.write(("\n" + str(exc)).encode())
                    evidence["result"] = "incomplete"
            evidence["finished"] = time.time()
            save()
            print(json.dumps(evidence, indent=2))
            return 0 if evidence["result"] == "passed" else 1
        elif args.action == "handoff":
            if not args.summary or not args.check:
                parser.error("handoff requires --summary and at least one --check LABEL")
            if any(state["checks"].get(label, {}).get("result") != "passed" for label in args.check):
                parser.error("each required check must have a successful latest result")
            state.update(status="awaiting_review", handoff={"summary": args.summary, "checks": args.check})
            save()
        elif args.action == "review":
            reports = {}
            for label, git_args in [("status", ["status", "--short"]),
                                    ("staged", ["diff", "--cached", "--no-ext-diff", "--no-textconv"]),
                                    ("unstaged", ["diff", "--no-ext-diff", "--no-textconv"]),
                                    ("untracked_paths", ["ls-files", "--others", "--exclude-standard"])]:
                result = subprocess.run(["git"] + git_args, cwd=state["workdir"], capture_output=True, text=True)
                if result.returncode:
                    raise RuntimeError(result.stderr.strip())
                reports[label] = result.stdout
            target = folder / ("review-" + str(time.time_ns()) + ".json")
            target.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"review": str(target), "scope": "current staged and unstaged changes; untracked paths only"}))
            return 0
        print(json.dumps(state, indent=2))
        return 0
    finally:
        lock.unlink()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
