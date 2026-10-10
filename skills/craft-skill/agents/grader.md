# Grading procedure

Evaluate whether a skill-guided run met its expected output, once per eval and configuration (`with_skill` or `without_skill`). Apply this procedure inline or in an explicitly authorized isolated run; this document does not require delegation.

## Inputs you will receive

- `eval_id`: identifier for this test case
- `expected_output`: one sentence describing what success looks like
- `assertions`: list of verifiable claims about the output
- `outputs_dir`: path to the directory containing files produced by the run

## Step 1 — Read output files

List all files in `outputs_dir`. Read every file relevant to the assertions.

Also check these optional files:
- `outputs_dir/../timing.json` — if present, read `total_tokens` and `duration_ms`
- `outputs_dir/user_notes.md` — if present, read it; the executor may have flagged
  uncertainties or workarounds that affect the grade

## Step 2 — Grade each assertion

For each assertion in order:

1. Search the output files for evidence.
2. Determine **PASS** or **FAIL**.
3. Write `evidence`: a direct quote or specific file reference.

**PASS requires:**
- Positive evidence that the assertion holds
- Evidence of genuine substance — a file exists AND contains the correct content,
  not just a filename match or an empty file

**FAIL requires:**
- A counter-example, OR
- Evidence of absence (no matching file or pattern found), OR
- Superficial compliance: technically meets the assertion but the underlying task
  outcome is wrong or incomplete

**When uncertain:** burden of proof is on PASS. If you cannot verify from the
available output files, write `evidence: "unverifiable from outputs"` → FAIL.

Partial credit does not exist. Each assertion is PASS or FAIL.

## Step 3 — Extract implicit claims (optional but encouraged)

Beyond the assertions, extract implicit claims the outputs make and verify them:

- **Factual claims** — "The report has 5 sections" (count them)
- **Process claims** — "The validation script was used" (look for evidence in output)
- **Quality claims** — "All required fields were populated" (spot-check a sample)

Flag claims that cannot be verified: `"unverifiable from outputs — transcript needed"`.

This catches issues that predefined assertions miss and feeds useful signal back into
the eval design.

## Step 4 — Note user context (if user_notes.md was present)

Summarize any uncertainties or workarounds the executor flagged. Include these even
when the assertions pass — a passing grade on shaky inputs is still worth flagging.

## Step 5 — Critique the evals (optional but encouraged)

After grading, check whether the assertions themselves are strong. Only raise a
critique when there is a real gap worth flagging:
- An assertion that passed but would also pass for a clearly wrong output
- An important outcome you observed that no assertion checks
- An assertion that is unverifiable from the available outputs

Keep the bar high. Only flag things the eval author would say "good catch" about —
not every possible nitpick.

## Output

Write `grading.json` beside `outputs_dir`, at `<eval-dir>/<configuration>/grading.json`, not inside `outputs/`. Keep `timing.json` at the same configuration level. Follow `references/schemas.md`, resolved from the skill root, for exact field names.

**Use `assertion_results[]`, NOT `expectations[]`.** `aggregate_benchmark.py` reads
`assertion_results` by name; any other key produces zero data silently.

```json
{
  "eval_id": "<id>",
  "assertion_results": [
    {
      "text": "<assertion text>",
      "passed": true,
      "evidence": "<direct quote or specific file reference>"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
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

Omit `timing` if no timing.json was found. Omit `claims` if no implicit claims were
extracted. Omit `user_notes_summary` if no user_notes.md was found. Omit
`eval_critique` if no issues were found with the assertions.
