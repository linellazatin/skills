# Portable evaluation records

These are minimal JSON data contracts for optional machine-readable records. The protocol can also be followed manually; no JSON tooling is required. Fields marked **required** establish the minimum context needed to interpret results. Add fields when useful, but do not silently reinterpret existing ones. Use JSON `null` or an explicit `"unknown"` where appropriate rather than inventing values. Keep private credentials and unnecessary sensitive prompt data out of records.

## Case set

A case set is authored and frozen before a measured run. `cases` contains focused cases; every case has a unique stable `id` within the set.

```json
{
  "schema_version": "1",
  "case_set_id": "sample-skill-v1",
  "created_at": "2026-01-01",
  "skill": {
    "name": "sample-skill",
    "version": "commit-or-release-or-local",
    "content_sha256": "<sha256>"
  },
  "cases": [
    {
      "id": "route-neighbor-01",
      "mode": "routing_simulation",
      "category": "neighbor",
      "request": "Review this patch; do not edit it.",
      "context": "Optional model-visible context.",
      "fixture": null,
      "expected": {
        "observable": ["Select the review workflow as primary."],
        "prohibited": ["Do not implement or modify files."]
      },
      "assertions": [
        {"id": "a1", "criterion": "Selects the appropriate primary skill."},
        {"id": "a2", "criterion": "Does not infer authorization to edit."}
      ],
      "model_visible": {
        "expected": false,
        "assertions": false
      }
    }
  ]
}
```

### Case fields

- Required at set level: `schema_version`, `case_set_id`, `skill`, `cases`. `created_at` is recommended.
- Required per case: `id`, `mode`, `request`, `expected.observable`, `assertions`.
- `mode`: `routing_simulation`, `procedural_simulation`, or `tool_enabled_task`.
- `category`: descriptive label such as `intended`, `neighbor`, `normal`, `ambiguous`, `boundary`, `failure`, or `followup`; categories are not exhaustive requirements.
- `context`/`fixture`: exact model-visible material. Use `null` when absent. Keep answer keys outside model-visible content.
- `expected.prohibited`: actions/claims that violate task scope or contract.
- Each assertion has a stable `id` and a criterion that is observable and independently judgeable. Assertions are grader-side unless explicitly part of the user task.
- `model_visible` records whether the expected outcomes/assertions were revealed. Set `true` only when disclosure is intentional and explain it in case notes.
- Add `followup` only for multi-turn cases: fixed observation text, session policy, and the behavior expected to change or remain stable.

## Run record

One record represents one attempt on one case. Store it beside, or link it to, the raw response and relevant tool trace. Do not replace prior attempts when retrying.

```json
{
  "schema_version": "1",
  "run_id": "sample-skill-v1-route-neighbor-01-attempt-1",
  "case_set_id": "sample-skill-v1",
  "case_id": "route-neighbor-01",
  "attempt": 1,
  "repeat_kind": "initial",
  "started_at": "2026-01-01T12:00:00Z",
  "target": {
    "skill_content_sha256": "<sha256>",
    "model": "provider/model-id-or-unknown",
    "interface": "manual-or-adapter-name",
    "harness": "harness/version-or-not-applicable",
    "loading_method": "catalog-simulation-or-described-method"
  },
  "conditions": {
    "tools": [],
    "settings": {"temperature": {"requested": 0.2, "reported": "unknown"}},
    "session": "isolated",
    "cache_control": "unknown",
    "timeout_seconds": null
  },
  "input": {
    "system_prompt": "Exact system instruction or protected reference.",
    "user_prompt": "Exact request/context sent to model.",
    "skill_reference": "skill content hash or secure artifact path"
  },
  "result": {
    "status": "complete",
    "raw_output": "Primary response text or protected artifact reference.",
    "raw_output_ref": null,
    "error": null,
    "reported_metadata": {"input_tokens": null, "output_tokens": null, "stop_reason": "unknown"}
  },
  "evidence": {
    "tool_trace_ref": null,
    "observations": []
  }
}
```

Required run fields: `schema_version`, unique `run_id`, `case_set_id`, `case_id`, `attempt`, `repeat_kind`, `target`, `conditions`, `input`, `result.status`, and an output or explicit error. Record actual prompt and skill content, or a durable protected reference plus content hash; a hash alone cannot reconstruct a missing prompt. `started_at` is recommended.

- `repeat_kind`: `initial`, `paired_repeat`, `fresh_repeat`, or `followup`. Use `parent_run_id` for a follow-up; include the new observation in `input` or the case reference.
- `target` identifies the tested skill snapshot, model/interface/harness when known, and how the skill was supplied. Distinguish a manually pasted skill from native loading.
- `conditions.settings` separates `requested` from `reported` values. Record unavailable values as `unknown`; do not imply the model honored a requested value.
- `result.status`: `complete`, `transport_error`, `setup_error`, `timeout`, `truncated`, `refusal`, `malformed`, or `other_incomplete`. A test may define an additional status with explanation. Incomplete statuses are not behavioral failures by default.
- Keep `raw_output` when safe and permitted; otherwise use a protected `raw_output_ref` and document redactions. Never include credentials.
- For tool-enabled cases, `evidence` references observable traces/results. A model's assertion that it performed an action is not execution evidence.

## Assertion grading

Grade each assertion separately. Attach the grading record to `run_id` and `case_id`.

```json
{
  "schema_version": "1",
  "run_id": "sample-skill-v1-route-neighbor-01-attempt-1",
  "case_id": "route-neighbor-01",
  "reviewer": "human-or-review-process",
  "grading_method": "human",
  "assertion_results": [
    {
      "assertion_id": "a1",
      "status": "pass",
      "evidence_ref": "run output, paragraph 1",
      "evidence_quote": "The review skill is primary.",
      "rationale": "The response identifies the expected primary result."
    },
    {
      "assertion_id": "a2",
      "status": "pass",
      "evidence_ref": "run output, paragraph 2",
      "evidence_quote": "No edits are authorized.",
      "rationale": "The response preserves the assessment-only scope."
    }
  ],
  "critical_violations": [],
  "notes": []
}
```

Allowed assertion `status`: `pass`, `fail`, `not_applicable`, `unscored`. `pass`/`fail` require evidence and rationale. `not_applicable` and `unscored` require a reason. Use `unscored` when an attempt is incomplete or evidence cannot support a fair judgment. Keep critical safety/scope violations explicit even if other assertions pass. `grading_method` identifies human review or any disclosed automated assistance; human reviewer owns the final judgment. Do not map `not_applicable` or `unscored` to pass.

## Summary report

A report summarizes, but does not replace, per-case records. Include at minimum:

```json
{
  "schema_version": "1",
  "report_id": "sample-skill-report-1",
  "case_set_id": "sample-skill-v1",
  "question": "Does this skill guide the selected task correctly?",
  "scope": {"modes": ["routing_simulation"], "cases_run": 12, "cases_planned": 12},
  "conditions_summary": "Model/interface/settings and material differences, or links to run records.",
  "counts": {
    "complete": 11,
    "incomplete_or_error": 1,
    "assertion_pass": 18,
    "assertion_fail": 2,
    "assertion_not_applicable": 0,
    "assertion_unscored": 2,
    "critical_violations": 0
  },
  "findings": ["Case-level finding linked to run and evidence."],
  "coverage_gaps": ["Native host activation was not tested."],
  "inference_limits": ["Results apply only to this skill snapshot, model/interface, and case set."],
  "run_record_refs": ["runs/sample-skill-v1-route-neighbor-01-attempt-1.json"]
}
```

Counts must be derived from retained records and denominators stated. Do not calculate a single pass rate that hides incomplete attempts, critical violations, or mode differences. Keep routing accuracy, assertion outcomes, task acceptance, and safety observations separate. Claims about model size, provider, local/cloud behavior, or harness portability require corresponding varied evidence; otherwise list them as untested.

## Validation expectations

A structural validator may check required keys, unique IDs, allowed statuses, and references among case/run/grading records. It must not decide whether assertions are valid, evidence supports a judgment, a skill is effective, or a task is safe/complete. Manual review of a sample is still required. Any schema evolution must increment/document `schema_version` and preserve the ability to identify old records.
