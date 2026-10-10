#!/usr/bin/env python3
"""Run the eval + improve loop until all queries pass or max iterations reached.

LLM provider is auto-detected (see llm_call.py): ANTHROPIC_API_KEY → OPENAI_API_KEY →
claude -p fallback. Only run_eval.py still requires Claude Code CLI.
Combines run_eval.py and improve_description.py in a loop, tracking history and returning
the best description found. Supports a 60/40 train/test split to prevent overfitting.

Usage:
  python3 scripts/run_loop.py \\
    --skill-path <skill-dir/> \\
    --eval-set <eval.json> \\
    --model <model> \\
    [--holdout 0.4] [--max-iterations 5] [--runs-per-query 3] [--verbose]

  Outputs JSON with best description and full iteration history.

Eval set JSON format (list of objects):
  [
    {"query": "user message", "should_trigger": true},
    {"query": "unrelated message", "should_trigger": false}
  ]

Exit 0 = completed. Exit 1 = error.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.improve_description import improve_description
from scripts.run_eval import find_project_root, run_eval
from scripts.utils import parse_skill_md


def split_eval_set(eval_set: list, holdout: float, seed: int = 42) -> tuple:
    """Split into train and test sets, stratified by should_trigger."""
    random.seed(seed)
    trigger = [e for e in eval_set if e["should_trigger"]]
    no_trigger = [e for e in eval_set if not e["should_trigger"]]
    random.shuffle(trigger)
    random.shuffle(no_trigger)
    n_trigger_test = max(1, int(len(trigger) * holdout))
    n_no_trigger_test = max(1, int(len(no_trigger) * holdout))
    test_set = trigger[:n_trigger_test] + no_trigger[:n_no_trigger_test]
    train_set = trigger[n_trigger_test:] + no_trigger[n_no_trigger_test:]
    return train_set, test_set


def run_loop(
    eval_set: list,
    skill_path: Path,
    description_override: str | None,
    num_workers: int,
    timeout: int,
    max_iterations: int,
    runs_per_query: int,
    trigger_threshold: float,
    holdout: float,
    model: str,
    verbose: bool,
) -> dict:
    """Run the eval + improvement loop and return results."""
    project_root = find_project_root()
    name, original_description, content = parse_skill_md(skill_path)
    current_description = description_override or original_description

    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
        if verbose:
            print(f"Split: {len(train_set)} train, {len(test_set)} test (holdout={holdout})", file=sys.stderr)
    else:
        train_set = eval_set
        test_set = []

    history = []
    exit_reason = "unknown"

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Iteration {iteration}/{max_iterations}: {current_description[:80]}", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)

        all_queries = train_set + test_set
        t0 = time.time()
        all_results = run_eval(
            eval_set=all_queries,
            skill_name=name,
            description=current_description,
            num_workers=num_workers,
            timeout=timeout,
            project_root=project_root,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
            model=model,
        )
        eval_elapsed = time.time() - t0
        if all_results["summary"].get("errors", 0):
            raise RuntimeError("Trigger evaluation has unscored execution errors; resolve them before optimizing")

        train_queries = {q["query"] for q in train_set}
        train_list = [r for r in all_results["results"] if r["query"] in train_queries]
        test_list = [r for r in all_results["results"] if r["query"] not in train_queries]

        train_passed = sum(1 for r in train_list if r["pass"])
        train_total = len(train_list)
        train_results = {
            "results": train_list,
            "summary": {"passed": train_passed, "failed": train_total - train_passed, "total": train_total},
        }

        test_summary = None
        test_results = None
        if test_set:
            test_passed = sum(1 for r in test_list if r["pass"])
            test_total = len(test_list)
            test_summary = {"passed": test_passed, "failed": test_total - test_passed, "total": test_total}
            test_results = {"results": test_list, "summary": test_summary}

        history.append({
            "iteration": iteration,
            "description": current_description,
            "train_passed": train_passed,
            "train_failed": train_total - train_passed,
            "train_total": train_total,
            "train_results": train_list,
            "test_passed": test_summary["passed"] if test_summary else None,
            "test_failed": test_summary["failed"] if test_summary else None,
            "test_total": test_summary["total"] if test_summary else None,
            "test_results": test_list if test_results else None,
            # Backward compat fields for downstream tools.
            "passed": train_passed,
            "failed": train_total - train_passed,
            "total": train_total,
            "results": train_list,
        })

        if verbose:
            print(f"Train: {train_passed}/{train_total} passed ({eval_elapsed:.1f}s)", file=sys.stderr)
            for r in train_list:
                status = "PASS" if r["pass"] else "FAIL"
                print(f"  [{status}] rate={r['triggers']}/{r['runs']}: {r['query'][:60]}", file=sys.stderr)
            if test_summary:
                print(f"Test:  {test_summary['passed']}/{test_summary['total']} passed", file=sys.stderr)

        if train_results["summary"]["failed"] == 0:
            exit_reason = f"all_passed (iteration {iteration})"
            if verbose:
                print(f"\nAll train queries passed at iteration {iteration}!", file=sys.stderr)
            break

        if iteration == max_iterations:
            exit_reason = f"max_iterations ({max_iterations})"
            if verbose:
                print(f"\nMax iterations reached ({max_iterations}).", file=sys.stderr)
            break

        if verbose:
            print("\nImproving description...", file=sys.stderr)

        # Strip test scores from history so the improvement model can't see them.
        blinded_history = [
            {k: v for k, v in h.items() if not k.startswith("test_")}
            for h in history
        ]
        current_description = improve_description(
            skill_name=name,
            skill_content=content,
            current_description=current_description,
            eval_results=train_results,
            history=blinded_history,
            model=model,
            iteration=iteration,
        )
        if verbose:
            print(f"New description: {current_description[:80]}", file=sys.stderr)

    # Best iteration: by test score if test set exists, else train score.
    if test_set:
        best = max(history, key=lambda h: h["test_passed"] or 0)
        best_score = f"{best['test_passed']}/{best['test_total']}"
    else:
        best = max(history, key=lambda h: h["train_passed"])
        best_score = f"{best['train_passed']}/{best['train_total']}"

    if verbose:
        print(f"\nExit: {exit_reason}", file=sys.stderr)
        print(f"Best: {best_score} at iteration {best['iteration']}", file=sys.stderr)
        print(f"Best description: {best['description']}", file=sys.stderr)

    return {
        "exit_reason": exit_reason,
        "original_description": original_description,
        "best_description": best["description"],
        "best_score": best_score,
        "best_train_score": f"{best['train_passed']}/{best['train_total']}",
        "best_test_score": f"{best['test_passed']}/{best['test_total']}" if test_set else None,
        "final_description": current_description,
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "history": history,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--model", required=True, help="Model for claude -p (improvement step)")
    parser.add_argument("--description", default=None, help="Override starting description")
    parser.add_argument("--num-workers", type=int, default=10, help="Parallel workers for eval (default: 10)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds (default: 30)")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations (default: 5)")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Runs per query for trigger rate (default: 3)")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold (default: 0.5)")
    parser.add_argument("--holdout", type=float, default=0.4, help="Test set fraction 0–1; 0 to disable (default: 0.4)")
    parser.add_argument("--output", default=None, help="Save JSON output to this file (also printed to stdout)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"ERROR: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    eval_set = json.loads(Path(args.eval_set).read_text())

    output = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=args.description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        max_iterations=args.max_iterations,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        holdout=args.holdout,
        model=args.model,
        verbose=args.verbose,
    )

    json_output = json.dumps(output, indent=2)
    print(json_output)
    if args.output:
        Path(args.output).write_text(json_output)
        print(f"Saved to {args.output}", file=sys.stderr)

    # Remind the user to apply the best description.
    best = output["best_description"]
    print(f"\nBest description ({output['best_score']}):\n{best}", file=sys.stderr)
    print("\nApply it: update the `description` field in SKILL.md.", file=sys.stderr)


if __name__ == "__main__":
    main()
