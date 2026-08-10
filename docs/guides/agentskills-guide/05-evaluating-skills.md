# Evaluating Skill Output Quality

> Source: https://agentskills.io/skill-creation/evaluating-skills.md

How to test whether your skill produces good outputs using eval-driven iteration.

You wrote a skill, tried it on a prompt, and it seemed to work. But does it work reliably — across varied prompts, in edge cases, better than no skill at all? Running structured evaluations (evals) answers these questions and gives you a feedback loop for improving the skill systematically.

---

## Designing Test Cases

A test case has three parts:

- **Prompt**: a realistic user message — the kind of thing someone would actually type.
- **Expected output**: a human-readable description of what success looks like.
- **Input files** (optional): files the skill needs to work with.

Store test cases in `evals/evals.json` inside your skill directory:

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?",
      "expected_output": "A bar chart image showing the top 3 months by revenue, with labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"]
    },
    {
      "id": 2,
      "prompt": "there's a csv in my downloads called customers.csv, some rows have missing emails — can you clean it up and tell me how many were missing?",
      "expected_output": "A cleaned CSV with missing emails handled, plus a count of how many were missing.",
      "files": ["evals/files/customers.csv"]
    }
  ]
}
```

### Tips for Writing Good Test Prompts

- **Start with 2–3 test cases.** Don't over-invest before you've seen your first round of results. Expand later.
- **Vary the prompts.** Use different phrasings, levels of detail, and formality. Some casual ("hey can you clean up this csv"), some precise ("Parse the CSV at data/input.csv, drop rows where column B is null...").
- **Cover edge cases.** At least one prompt should test a boundary condition — a malformed input, an unusual request, or an ambiguous instruction.
- **Use realistic context.** Real users mention file paths, column names, and personal context. "Process this data" is too vague to test anything useful.

Don't define specific pass/fail checks yet — just prompts and expected outputs. Add assertions after you see what the first run produces.

---

## Running Evals

The core pattern: run each test case **with the skill** and **without it** (or against a previous version). This gives you a baseline to compare against.

### Workspace Structure

```
csv-analyzer/
├── SKILL.md
└── evals/
    └── evals.json
csv-analyzer-workspace/
└── iteration-1/
    ├── eval-top-months-chart/
    │   ├── with_skill/
    │   │   ├── outputs/       # Files produced by the run
    │   │   ├── timing.json    # Tokens and duration
    │   │   └── grading.json   # Assertion results
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    ├── eval-clean-missing-emails/
    │   ├── with_skill/  ...
    │   └── without_skill/  ...
    └── benchmark.json         # Aggregated statistics
```

The main file you author is `evals/evals.json`. The other JSON files are produced during the eval process.

### Spawning Runs

Each eval run should start with a **clean context** — no leftover state from previous runs. In environments that support subagents, each child task starts fresh naturally. Without subagents, use a separate session for each run.

For each run, provide:
- The skill path (or no skill for the baseline)
- The test prompt
- Any input files
- The output directory

Example instructions for a single with-skill run:

```
Execute this task:
- Skill path: /path/to/csv-analyzer
- Task: I have a CSV of monthly sales data in data/sales_2025.csv.
  Can you find the top 3 months by revenue and make a bar chart?
- Input files: evals/files/sales_2025.csv
- Save outputs to: csv-analyzer-workspace/iteration-1/eval-top-months-chart/with_skill/outputs/
```

For the baseline, use the same prompt without the skill path, saving to `without_skill/outputs/`.

When improving an existing skill, snapshot it before editing:
```bash
cp -r <skill-path> <workspace>/skill-snapshot/
```
Then use the snapshot as the baseline, saving to `old_skill/outputs/`.

### Capturing Timing Data

Record token count and duration for each run:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

This lets you measure what the skill costs (tokens, time) vs. what it buys (pass rate). Save immediately after each run — many harnesses expose token counts and duration in run completion events but do not persist them (e.g., Claude Code includes these in subagent task completion notifications). Check your client’s documentation for where to capture this data.

---

## Writing Assertions

Assertions are verifiable statements about what the output should contain or achieve. Add them **after** you see your first round of outputs.

**Good assertions:**
- `"The output file is valid JSON"` — programmatically verifiable
- `"The bar chart has labeled axes"` — specific and observable
- `"The report includes at least 3 recommendations"` — countable

**Weak assertions:**
- `"The output is good"` — too vague
- `"The output uses exactly the phrase 'Total Revenue: $X'"` — too brittle

Not everything needs an assertion. Writing style, visual design, whether the output "feels right" — these are better caught during human review. Reserve assertions for things that can be checked objectively.

Add assertions to each test case in `evals/evals.json`:

```json
{
  "id": 1,
  "prompt": "...",
  "expected_output": "...",
  "files": ["evals/files/sales_2025.csv"],
  "assertions": [
    "The output includes a bar chart image file",
    "The chart shows exactly 3 months",
    "Both axes are labeled",
    "The chart title or caption mentions revenue"
  ]
}
```

---

## Grading Outputs

Grading means evaluating each assertion against actual outputs and recording **PASS** or **FAIL** with specific evidence. Evidence should quote or reference the output, not just state an opinion.

The simplest approach: give outputs and assertions to an LLM and ask it to evaluate each one. For mechanical checks (valid JSON, correct row count, file exists), use a verification script — more reliable and reusable.

```json
{
  "assertion_results": [
    {
      "text": "The output includes a bar chart image file",
      "passed": true,
      "evidence": "Found chart.png (45KB) in outputs directory"
    },
    {
      "text": "Both axes are labeled",
      "passed": false,
      "evidence": "Y-axis is labeled 'Revenue ($)' but X-axis has no label"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  }
}
```

### Grading Principles

- **Require concrete evidence for a PASS.** If an assertion says "includes a summary" and the output has a section titled "Summary" with one vague sentence, that's a FAIL.
- **Review the assertions themselves.** Notice when assertions are too easy (always pass), too hard (always fail), or unverifiable. Fix these for the next iteration.

> **Tip — Blind comparison**: Present both outputs to an LLM judge without revealing which version is which. The judge scores holistic qualities — organization, formatting, usability, polish — free from bias. This complements assertion grading: two outputs might both pass all assertions but differ significantly in overall quality.

---

## Aggregating Results

Once all runs in an iteration are graded, compute summary statistics and save to `benchmark.json`:

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.83, "stddev": 0.06 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0 },
      "tokens": { "mean": 3800, "stddev": 400 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.33, "stddev": 0.10 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0 },
      "tokens": { "mean": 2100, "stddev": 300 }
    },
    "delta": {
      "pass_rate": 0.50,
      "time_seconds": 13.0,
      "tokens": 1700
    }
  }
}
```

The `delta` tells you what the skill costs and what it buys. A skill that adds 13 seconds but improves pass rate by 50 points is likely worth it. A skill that doubles token usage for a 2-point improvement might not be.

> **Note**: `stddev` is only meaningful with multiple runs per eval. In early iterations with 2–3 test cases and single runs, focus on raw pass counts and the delta.

---

## Analyzing Patterns

After computing benchmarks:

- **Remove assertions that always pass in both configurations.** They don't reflect actual skill value.
- **Investigate assertions that always fail in both.** Either the assertion is broken, the test is too hard, or it's checking the wrong thing.
- **Study assertions that pass with the skill but fail without.** This is where the skill is adding value — understand *why*.
- **Tighten instructions when results are inconsistent across runs.** High `stddev` on the same eval = flaky eval or ambiguous instructions. Add examples or more specific guidance.
- **Check time and token outliers.** If one eval takes 3× longer, read its execution transcript.

---

## Reviewing Results with a Human

Assertion grading only checks what you thought to write assertions for. A human reviewer catches issues you didn't anticipate, notices when output is technically correct but misses the point, and spots problems hard to express as pass/fail checks.

Record specific feedback per test case:

```json
{
  "eval-top-months-chart": "The chart is missing axis labels and the months are in alphabetical order instead of chronological.",
  "eval-clean-missing-emails": ""
}
```

Empty feedback = output looked fine. Focus improvements on test cases with specific complaints.

---

## Iterating on the Skill

After grading and reviewing, you have three sources of signal:

- **Failed assertions** — specific gaps: missing steps, unclear instructions, unhandled cases
- **Human feedback** — broader quality: wrong approach, poor structure, technically correct but unhelpful
- **Execution transcripts** — *why* things went wrong: ignored instructions, time on unproductive steps

The most effective approach: give all three (plus the current `SKILL.md`) to an LLM and ask it to propose changes. When prompting:

- **Generalize from feedback.** Fix underlying issues broadly, not narrow patches for specific examples.
- **Keep the skill lean.** Fewer, better instructions often outperform exhaustive rules. If transcripts show wasted work, remove those instructions.
- **Explain the why.** Reasoning-based instructions ("Do X because Y tends to cause Z") work better than rigid directives. Models follow instructions more reliably when they understand the purpose.
- **Bundle repeated work.** If every test run independently wrote a similar helper script, bundle it in `scripts/`.

### The Loop

1. Give eval signals + current `SKILL.md` to an LLM → get proposed improvements
2. Review and apply changes
3. Rerun all test cases in a new `iteration-<N+1>/` directory
4. Grade and aggregate new results
5. Review with a human → repeat

Stop when you're satisfied, feedback is consistently empty, or you're no longer seeing meaningful improvement between iterations.

> **Tip**: The [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) skill (Anthropic reference implementation) automates much of this workflow — running evals, grading assertions, aggregating benchmarks, and presenting results for human review. Your harness may offer equivalent tooling — check its documentation.
