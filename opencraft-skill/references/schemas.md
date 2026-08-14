# JSON schemas

This document defines the exact field contracts for every data file opencraft-skill
produces. Agents and scripts must follow these schemas exactly — wrong field names
cause silent failures (aggregate_benchmark.py, for example, silently skips
grading.json files that use `results` instead of `assertion_results`).

---

## evals.json

Defines the test cases for a skill. Write inline in the working file, or save to
`<skill-workspace>/evals.json`.

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's realistic task prompt",
      "expected_output": "One sentence describing what success looks like",
      "assertions": [
        "The output contains a summary table",
        "The output file is non-empty",
        "The validation script was invoked and passed"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Matches the skill's `name` frontmatter exactly
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: Realistic user prompt — not a test description
- `evals[].expected_output`: Human-readable success description (briefs the grader)
- `evals[].assertions`: Verifiable statements; each must be checkable from output files

---

## grading.json

Output from `agents/grader.md`. Located at
`<eval-dir>/<config>/grading.json` (e.g. `iteration-1/eval-1/with_skill/grading.json`).

```json
{
  "eval_id": "1",
  "assertion_results": [
    {
      "text": "The output contains a summary table",
      "passed": true,
      "evidence": "File report.md lines 14-20 contains a markdown table with 3 columns"
    },
    {
      "text": "The validation script was invoked and passed",
      "passed": false,
      "evidence": "No output file references the validation script; no error log found"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.5
  },
  "timing": {
    "total_tokens": 12400,
    "duration_ms": 18500
  },
  "claims": [
    {
      "claim": "The output has 5 sections",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 5 level-2 headings in output.md"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "workarounds": ["Fell back to text extraction for non-parseable rows"]
  },
  "eval_critique": [
    "Assertion 2 checks filename existence but not file content — weak discriminator"
  ]
}
```

**Fields:**
- `eval_id`: String or integer matching the eval's `id`
- `assertion_results[]`: One entry per assertion, in order
  - `text`: Assertion text verbatim
  - `passed`: Boolean
  - `evidence`: Direct quote or specific file reference supporting the verdict
- `summary.pass_rate`: `passed / total` as a float (0.0–1.0)
- `timing`: Optional — include when timing.json is available
  - `total_tokens`: Integer token count
  - `duration_ms`: Wall-clock milliseconds
- `claims`: Optional — implicit claims extracted and verified by the grader
- `user_notes_summary`: Optional — only include when user_notes.md was present
- `eval_critique`: Optional — only include when assertions are weak or unverifiable

**Critical:** `aggregate_benchmark.py` reads `assertion_results[].passed`. Using
`expectations`, `results`, or any other key name will produce zero data in the
benchmark. Always use `assertion_results`.

---

## timing.json

Wall-clock timing for a single eval run. Located at `<eval-dir>/<config>/timing.json`.

**How to capture:** When a subagent task completes, the task completion event includes
`total_tokens` and `duration_ms`. Save these immediately — they are not available
after the fact. In Path B (inline), record an approximate token count from the session.

```json
{
  "total_tokens": 12400,
  "duration_ms": 18500
}
```

**Fields:**
- `total_tokens`: Integer. Total tokens (input + output) for the run.
- `duration_ms`: Integer. Wall-clock elapsed time in milliseconds.

`aggregate_benchmark.py` reads `total_tokens` and `duration_ms`. Do not use
`tokens`, `duration_seconds`, or any other field name — they are silently ignored.

---

## benchmark.json

Output from `scripts/aggregate_benchmark.py`. Located at
`<skill-workspace>/iteration-N/benchmark.json`.

```json
{
  "skill_name": "my-skill",
  "iteration": "iteration-1",
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.07, "n": 3},
      "tokens":    {"mean": 12400.0, "stddev": 800.0, "n": 3},
      "time_seconds": {"mean": 18.5, "stddev": 2.1, "n": 3}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.10, "n": 3},
      "tokens":    {"mean": 8200.0, "stddev": 600.0, "n": 3},
      "time_seconds": {"mean": 12.0, "stddev": 1.5, "n": 3}
    },
    "delta": {
      "pass_rate":    0.5,
      "tokens":       4200.0,
      "time_seconds": 6.5
    }
  }
}
```

**Fields:**
- `skill_name`: Matches the skill's `name` frontmatter
- `iteration`: The iteration directory name (e.g. `"iteration-1"`)
- `run_summary.with_skill` / `run_summary.without_skill`: Statistics per configuration
  - Each metric contains `{mean, stddev, n}` where `n` is runs with data available
- `run_summary.delta`: `with_skill.mean - without_skill.mean` per metric; `null` when
  either side has no data

---

## comparison.json

Output from `agents/comparator.md`. Located at `<grading-dir>/comparison.json`.

```json
{
  "winner": "A",
  "reasoning": "Output A is complete and well-formatted. Output B is missing the summary section and has inconsistent formatting.",
  "rubric": {
    "A": {
      "content": {"correctness": 5, "completeness": 5, "accuracy": 4},
      "structure": {"organization": 4, "formatting": 5, "usability": 4},
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {"correctness": 3, "completeness": 2, "accuracy": 3},
      "structure": {"organization": 3, "formatting": 2, "usability": 3},
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Complete solution", "Well-formatted"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable structure"],
      "weaknesses": ["Missing summary", "Inconsistent formatting"]
    }
  }
}
```

**Fields:**
- `winner`: `"A"`, `"B"`, or `"TIE"`
- `reasoning`: 1–3 sentences explaining the decision
- `rubric`: Per-output criterion scores (1–5), averaged to `content_score` /
  `structure_score` / `overall_score` (1–10)
- `output_quality.score`: 1–10, should match `rubric.overall_score`
- `expectation_results`: Optional — only include when assertions were provided

---

## analysis.json

Output from `agents/analyzer.md` (post-hoc mode). Located at
`<grading-dir>/analysis.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner-skill",
    "loser_skill": "path/to/loser-skill",
    "comparator_reasoning": "One sentence summary of why A won"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for handling edge cases",
    "Validation script caught formatting errors before final output"
  ],
  "loser_weaknesses": [
    "Instruction 'process appropriately' is ambiguous — agent improvised",
    "No validation step; errors reached the final output"
  ],
  "instruction_following": {
    "winner": {"score": 9, "issues": ["Minor: skipped optional logging step"]},
    "loser":  {"score": 6, "issues": ["Did not use the formatting template", "Missed step 3"]}
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process appropriately' with explicit steps 1–3",
      "expected_impact": "Eliminates ambiguity that caused the agent to improvise"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> followed 5 steps -> validated -> output",
    "loser_execution_pattern": "Read skill -> unclear approach -> tried 3 methods -> no validation"
  }
}
```

**Priority levels:** `"high"` (would likely change the outcome), `"medium"` (quality
improvement, not outcome-changing), `"low"` (marginal improvement).

**Categories:** `"instructions"`, `"tools"`, `"examples"`, `"error_handling"`,
`"structure"`, `"references"`.
