#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
Aggregate grading.json files from an eval workspace iteration into benchmark.json.

Reads every eval-<id>/with_skill/grading.json and eval-<id>/without_skill/grading.json
(and matching timing.json files) inside the given iteration directory, then writes
benchmark.json with mean pass rate, tokens, and time — plus the delta.

Usage:
  python scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <name>
  python scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name myskill --output results.json

Exit 0 always (partial data is reported, not an error).
"""
import argparse
import json
import sys
from pathlib import Path
from statistics import mean, stdev


def stats(values: list[float]) -> dict:
    if not values:
        return {"mean": None, "stddev": None, "n": 0}
    m = round(mean(values), 4)
    s = round(stdev(values), 4) if len(values) > 1 else 0.0
    return {"mean": m, "stddev": s, "n": len(values)}


def collect(iteration_dir: Path, config: str) -> dict:
    pass_rates, tokens, times = [], [], []
    for eval_dir in sorted(iteration_dir.iterdir()):
        if not eval_dir.is_dir():
            continue
        grading = eval_dir / config / "grading.json"
        timing = eval_dir / config / "timing.json"
        if grading.exists():
            data = json.loads(grading.read_text(encoding="utf-8"))
            results = data.get("assertion_results", [])
            if results:
                passed = sum(1 for r in results if r.get("passed"))
                pass_rates.append(passed / len(results))
        if timing.exists():
            t = json.loads(timing.read_text(encoding="utf-8"))
            if "total_tokens" in t:
                tokens.append(t["total_tokens"])
            if "duration_ms" in t:
                times.append(t["duration_ms"] / 1000)
    return {"pass_rate": stats(pass_rates), "tokens": stats(tokens), "time_seconds": stats(times)}


def delta(a: dict, b: dict, key: str) -> float | None:
    ma = a[key]["mean"]
    mb = b[key]["mean"]
    if ma is None or mb is None:
        return None
    return round(ma - mb, 4)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("iteration_dir", help="Path to iteration directory (e.g. skill-workspace/iteration-1)")
    parser.add_argument("--skill-name", required=True, help="Skill name")
    parser.add_argument("--output", help="Output path (default: <iteration_dir>/benchmark.json)")
    args = parser.parse_args()

    base = Path(args.iteration_dir)
    if not base.is_dir():
        print(f"ERROR: {base} is not a directory", file=sys.stderr)
        sys.exit(1)

    with_stats = collect(base, "with_skill")
    without_stats = collect(base, "without_skill")

    report = {
        "skill_name": args.skill_name,
        "iteration": base.name,
        "run_summary": {
            "with_skill": with_stats,
            "without_skill": without_stats,
            "delta": {
                "pass_rate": delta(with_stats, without_stats, "pass_rate"),
                "tokens": delta(with_stats, without_stats, "tokens"),
                "time_seconds": delta(with_stats, without_stats, "time_seconds"),
            },
        },
    }

    out = Path(args.output) if args.output else base / "benchmark.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nWritten to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
