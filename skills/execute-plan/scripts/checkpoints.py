#!/usr/bin/env python3
"""Record inline phase checks. Python 3.9+, standard library only."""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    command = []
    if "--" in argv:
        split = argv.index("--")
        argv, command = argv[:split], argv[split + 1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "start", "check", "handoff", "review"])
    parser.add_argument("plan", type=Path)
    parser.add_argument("phase", nargs="?")
    parser.add_argument("--workdir", type=Path)
    parser.add_argument("--summary", default="")
    parser.add_argument("--label")
    parser.add_argument("--check", action="append", default=[])
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args(argv)
    if command and args.action != "check":
        parser.error("only check accepts an execution command")
    if args.workdir and args.action != "start":
        parser.error("--workdir is set when starting the phase")
    plan = args.plan.resolve(strict=True)
    revision = digest(plan)
    folder = plan.parent / ".workflow" / hashlib.sha256(str(plan).encode()).hexdigest()[:16]
    state_file = folder / "checkpoint.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    if args.action == "status":
        print(json.dumps({"state": state, "stale": bool(state) and state["revision"] != revision}, indent=2))
        return 0
    if args.action != "start" and (not state or state["revision"] != revision):
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
        if args.action != "start" and (not state or state["revision"] != revision or
                                       (args.phase and args.phase != state["phase"])):
            parser.error("checkpoint changed; inspect status before continuing")
        if args.action == "start":
            if not args.summary:
                parser.error("start requires --summary describing the phase outcome")
            workdir = (args.workdir or Path.cwd()).resolve(strict=True)
            if not workdir.is_dir():
                parser.error("workdir must be a directory")
            state = {"plan": str(plan), "revision": revision, "phase": args.phase,
                     "workdir": str(workdir), "summary": args.summary, "status": "working", "checks": {}}
            save()
        elif args.action == "check":
            if not args.label or not command or not math.isfinite(args.timeout) or args.timeout <= 0:
                parser.error("check requires --label, a positive finite timeout, and -- PROGRAM ARGS")
            log = folder / ("check-" + str(time.time_ns()) + ".log")
            evidence = {"argv": command, "log": str(log), "result": "running", "started": time.time()}
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
