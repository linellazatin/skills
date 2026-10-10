#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

REQUIRES: Claude Code CLI (`claude -p` must be available in PATH).
This script is Tier 2 (Claude Code only) — it uses `claude -p` as a subprocess
to test whether a skill's description causes the model to trigger the skill.

Outputs results as JSON (stdout). Progress and errors go to stderr.

Usage:
  python3 scripts/run_eval.py --eval-set <eval.json> --skill-path <skill-dir/> \\
    --runs-per-query 3 [--model <model>] [--verbose]

Eval set JSON format:
  [
    {"query": "user message here", "should_trigger": true},
    {"query": "unrelated message", "should_trigger": false}
  ]

Measures a temporary Claude command surrogate, not full skill execution or other harnesses.
Execution failures remain unscored. Exit 0 = valid eval ran. Exit 1 = error.
"""

import argparse
import json
import os
import select
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.utils import parse_skill_md


def find_project_root() -> Path:
    """Walk up from cwd looking for .claude/ — same heuristic as Claude Code."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> bool:
    """Run one query via `claude -p` and return True if the skill triggered."""
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    commands_dir = Path(project_root) / ".claude" / "commands"
    command_file = commands_dir / f"{clean_name}.md"

    try:
        commands_dir.mkdir(parents=True, exist_ok=True)
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_file.write_text(
            f"---\ndescription: |\n  {indented_desc}\n---\n\n"
            f"# {skill_name}\n\nThis skill handles: {skill_description}\n"
        )

        cmd = [
            "claude", "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=project_root,
            env=env,
        )

        triggered = False
        start_time = time.monotonic()
        buffer = ""
        pending_tool_name = None
        accumulated_json = ""

        try:
            while time.monotonic() - start_time < timeout:
                ready, _, _ = select.select([process.stdout], [], [], min(0.1, timeout))
                if not ready:
                    continue
                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    raise RuntimeError("Evaluator exited without a completed result")
                buffer += chunk.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if event.get("type") == "stream_event":
                        se = event.get("event", {})
                        se_type = se.get("type")
                        if se_type == "content_block_start":
                            cb = se.get("content_block", {})
                            pending_tool_name = cb.get("name") if cb.get("type") == "tool_use" else None
                            accumulated_json = ""
                        elif se_type == "content_block_delta" and pending_tool_name in ("Skill", "Read"):
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                accumulated_json += delta.get("partial_json", "")
                        elif se_type == "content_block_stop":
                            if pending_tool_name in ("Skill", "Read"):
                                try:
                                    tool_input = json.loads(accumulated_json)
                                except json.JSONDecodeError:
                                    tool_input = {}
                                key = "skill" if pending_tool_name == "Skill" else "file_path"
                                triggered |= clean_name in tool_input.get(key, "")
                            pending_tool_name = None
                            accumulated_json = ""
                    elif event.get("type") == "assistant":
                        for item in event.get("message", {}).get("content", []):
                            if item.get("type") != "tool_use":
                                continue
                            tool_name = item.get("name")
                            tool_input = item.get("input", {})
                            if tool_name in ("Skill", "Read"):
                                key = "skill" if tool_name == "Skill" else "file_path"
                                triggered |= clean_name in tool_input.get(key, "")
                    elif event.get("type") == "result":
                        if event.get("is_error"):
                            raise RuntimeError("Harness reported an evaluation error")
                        return triggered
            raise TimeoutError("Trigger evaluation timed out before completion")
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
            process.stdout.close()

    finally:
        if command_file.exists():
            command_file.unlink()


def run_eval(
    eval_set: list,
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
) -> dict:
    """Run the full eval set and return results."""
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for _ in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    str(project_root),
                    model,
                )
                future_to_info[future] = item

        query_triggers: dict = {}
        query_items: dict = {}
        query_errors: dict = {}
        for future in as_completed(future_to_info):
            item = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            query_triggers.setdefault(query, [])
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_errors.setdefault(query, []).append(str(e))

    results = []
    for query, triggers in query_triggers.items():
        item = query_items[query]
        errors = query_errors.get(query, [])
        trigger_rate = sum(triggers) / len(triggers) if triggers else None
        should_trigger = item["should_trigger"]
        passed = None if errors else (trigger_rate >= trigger_threshold if should_trigger else trigger_rate < trigger_threshold)
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "attempted_runs": len(triggers) + len(errors),
            "errors": errors,
            "pass": passed,
        })

    passed_count = sum(r["pass"] is True for r in results)
    failed_count = sum(r["pass"] is False for r in results)
    error_count = sum(r["pass"] is None for r in results)
    total = len(results)
    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {"total": total, "passed": passed_count, "failed": failed_count, "errors": error_count},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Parallel workers (default: 10)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds (default: 30)")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Runs per query for trigger rate (default: 3)")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold (default: 0.5)")
    parser.add_argument("--model", default=None, help="Model for claude -p (default: session model)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"ERROR: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, _ = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Testing: {description}", file=sys.stderr)
        print(f"Project root: {project_root}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        s = output["summary"]
        print(f"Results: {s['passed']}/{s['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "ERROR" if r["pass"] is None else ("PASS" if r["pass"] else "FAIL")
            print(f"  [{status}] rate={r['triggers']}/{r['runs']} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))
    if output["summary"]["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
