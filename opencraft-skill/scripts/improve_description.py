#!/usr/bin/env python3
"""Improve a skill description based on trigger eval results.

LLM provider is auto-detected: ANTHROPIC_API_KEY → OPENAI_API_KEY → claude -p fallback.
Takes eval results (from run_eval.py) and outputs an improved description.

Usage:
  python3 scripts/improve_description.py \\
    --eval-results <run_eval_output.json> \\
    --skill-path <skill-dir/> \\
    --model <model> \\
    [--history <history.json>] [--verbose]

Exit 0 = success. Outputs JSON with {"description": "...", "history": [...]}.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.llm_call import call as _call_llm
from scripts.utils import parse_skill_md


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list,
    model: str | None,
    iteration: int | None = None,
) -> str:
    """Call Claude to produce an improved description based on eval failures."""
    failed_triggers = [r for r in eval_results["results"] if r["should_trigger"] and not r["pass"]]
    false_triggers = [r for r in eval_results["results"] if not r["should_trigger"] and not r["pass"]]

    train_score = f"{eval_results['summary']['passed']}/{eval_results['summary']['total']}"

    prompt = f"""You are optimizing a skill description for an Agent Skill called "{skill_name}".

A skill has a title and description that the agent sees when deciding whether to use it.
If it uses the skill, it reads the full SKILL.md. Your goal: write a description that
triggers for relevant queries and doesn't trigger for irrelevant ones.

Current description:
<current_description>
"{current_description}"
</current_description>

Current score: {train_score}

"""

    if failed_triggers:
        prompt += "FAILED TO TRIGGER (should have triggered, didn't):\n"
        for r in failed_triggers:
            prompt += f'  - "{r["query"]}" (triggered {r["triggers"]}/{r["runs"]} times)\n'
        prompt += "\n"

    if false_triggers:
        prompt += "FALSE TRIGGERS (triggered but shouldn't have):\n"
        for r in false_triggers:
            prompt += f'  - "{r["query"]}" (triggered {r["triggers"]}/{r["runs"]} times)\n'
        prompt += "\n"

    if history:
        prompt += "PREVIOUS ATTEMPTS (do NOT repeat — try something structurally different):\n\n"
        for h in history:
            score_str = f"{h.get('passed', 0)}/{h.get('total', 0)}"
            prompt += f'<attempt score={score_str}>\n'
            prompt += f'Description: "{h["description"]}"\n'
            if h.get("results"):
                for r in h["results"]:
                    status = "PASS" if r["pass"] else "FAIL"
                    prompt += f'  [{status}] "{r["query"][:80]}" (triggered {r["triggers"]}/{r["runs"]})\n'
            prompt += "</attempt>\n\n"

    prompt += f"""Skill content (for context):
<skill_content>
{skill_content}
</skill_content>

Write an improved description. Generalize from failures — don't enumerate specific
queries. Descriptions that list dozens of cases get long and overfit.

Tips that work well:
- Use imperative phrasing: "Use this skill when..." not "This skill does..."
- Focus on user intent, not implementation details
- Make it distinctive against other skills
- Stay under 200 words; hard limit is 1024 characters

Respond with only the new description in <new_description> tags."""

    text = _call_llm(prompt, model)
    match = re.search(r"<new_description>(.*?)</new_description>", text, re.DOTALL)
    description = match.group(1).strip().strip('"') if match else text.strip().strip('"')

    # Safety net: enforce 1024-char hard limit.
    if len(description) > 1024:
        shorten_prompt = (
            f"{prompt}\n\n---\n\n"
            f"The previous attempt was {len(description)} characters, over the 1024-char limit:\n\n"
            f'"{description}"\n\n'
            f"Rewrite under 1024 characters. Respond in <new_description> tags."
        )
        text2 = _call_llm(shorten_prompt, model)
        match2 = re.search(r"<new_description>(.*?)</new_description>", text2, re.DOTALL)
        description = match2.group(1).strip().strip('"') if match2 else text2.strip().strip('"')

    return description


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--eval-results", required=True, help="Path to run_eval.py output JSON")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--history", default=None, help="Path to history JSON (previous attempts)")
    parser.add_argument("--model", required=True, help="Model for claude -p")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"ERROR: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    eval_results = json.loads(Path(args.eval_results).read_text())
    history = json.loads(Path(args.history).read_text()) if args.history else []
    name, _, content = parse_skill_md(skill_path)
    current_description = eval_results["description"]

    if args.verbose:
        s = eval_results["summary"]
        print(f"Current: {current_description}", file=sys.stderr)
        print(f"Score: {s['passed']}/{s['total']}", file=sys.stderr)

    new_description = improve_description(
        skill_name=name,
        skill_content=content,
        current_description=current_description,
        eval_results=eval_results,
        history=history,
        model=args.model,
    )

    if args.verbose:
        print(f"Improved: {new_description}", file=sys.stderr)

    output = {
        "description": new_description,
        "history": history + [{
            "description": current_description,
            "passed": eval_results["summary"]["passed"],
            "failed": eval_results["summary"]["failed"],
            "total": eval_results["summary"]["total"],
            "results": eval_results["results"],
        }],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
