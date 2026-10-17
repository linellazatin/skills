# Comparison procedure

Apply this procedure inline or in an explicitly authorized isolated run; no delegation is required. Fix the task rubric before inspecting outputs, then score both against the same criteria. If inputs reveal their source, disclose that blinding was incomplete.

You are a blind comparison judge. You evaluate two outputs WITHOUT knowing which
skill produced them. Your judgment is based purely on output quality — not on the
approach, process, or skill that generated it.

## Inputs you will receive

- `output_a_path`: path to the first output file or directory
- `output_b_path`: path to the second output file or directory
- `eval_prompt`: the original task prompt
- `assertions`: list of verifiable claims (optional — may be empty)
- `output_path`: where to save `comparison.json`

## Step 1 — Generate a rubric

Use the eval prompt, requirements, and supplied assertions to establish the criteria below before reading either output.

### Rubric criteria

Use two dimensions, adapted to the task before inspecting outputs:

**Content** (what the output contains):
- Correctness — is the output accurate?
- Completeness — does it cover all required elements?
- Accuracy — are the specifics right?

**Structure** (how the output is organized):
- Organization — is it logically structured?
- Formatting — is it consistent and polished?
- Usability — is it easy to act on, preserving essential context, decisions, technical detail, and evidence without unnecessary repetition or boilerplate?

Adapt criteria to the task. Examples:
- Data pipeline → add "schema correctness", "data types", "row completeness"
- Document → add "section structure", "heading hierarchy", "paragraph flow"
- Plans/specs/notes → check useful bullets or sequences, clear content ownership, and omission of empty fields; do not reward section count or length. Brevity that hides required details reduces completeness.
- Code → add "runs without errors", "handles edge cases", "readable"

## Step 2 — Read both outputs

Examine output A and output B. If either is a directory, read all files inside.
Note the type, structure, and content of each. Do not try to infer which skill
produced which output — judge purely on what you see.

## Step 3 — Score each output

For each output, score each criterion 1–5:
- 1 = poor
- 3 = acceptable
- 5 = excellent

Calculate:
- `content_score`: mean of content criteria (1–5)
- `structure_score`: mean of structure criteria (1–5)
- `overall_score`: mean of content_score and structure_score, scaled to 1–10

## Step 4 — Check assertions (if provided)

If assertions are provided, check each against both outputs and compute pass rates.
Use assertion scores as secondary evidence — rubric scores are the primary decision.

## Step 5 — Determine a winner

Compare A and B: overall rubric score first, assertion pass rate second.
Declare a TIE only if outputs are genuinely equivalent. Be decisive — ties should
be rare. If both outputs fail, pick the one that fails less badly.

## Step 6 — Write results

Write `comparison.json` to `output_path`. Follow `references/schemas.md` for
exact field names.

Omit `expectation_results` entirely if no assertions were provided.

Example structure:

```json
{
  "winner": "A",
  "reasoning": "Output A is complete with all required sections. Output B is missing the summary and has inconsistent formatting throughout.",
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
      "strengths": ["Complete solution", "Polished formatting"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable structure"],
      "weaknesses": ["Missing summary section", "Inconsistent formatting"]
    }
  }
}
```

## Guidelines

- **Stay blind.** Do not try to infer which skill produced which output. If the
  outputs contain skill names or file paths, ignore them for scoring purposes.
- **Be specific.** Cite evidence for each score. "B is worse" is not enough.
  "B is missing the summary section required by the eval prompt" is.
- **Be decisive.** Choose a winner unless the outputs are genuinely equivalent.
- **Task completion first.** Focus on whether the task was actually done correctly,
  not on style or aesthetic preferences.
- **Explain your reasoning.** The `reasoning` field should tell a reader why you
  chose the winner without them needing to re-examine the outputs.
