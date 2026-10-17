# Changelog

## 0.3.0

### New

- Added the unreleased `skill-buffer` prototype under `tests/unreleased/skill-buffer/`: a portable skill wrapper and Python CLI for inspection, frozen baseline/candidate evaluation, response imports, evidence-backed author grading, paired comparison and separate candidate revisions.
- Added versioned JSON contracts, synthetic examples, JSON/Markdown reports and an offline walkthrough. HTTP evaluation uses explicit endpoint/model settings, credential redaction and explicit resume without automatic retries.

### Changed

- Made plan, spec, note, and report guidance concise and adaptive across all nine skills: useful bullets/checklists, shared context recorded once, evidence links, and omission of empty fields while preserving technical detail and material gaps. Added concise worked examples and prose-quality comparison criteria.

### Validation

- Passed 20 prototype tests, repository/helper checks and a copied-directory synthetic walkthrough without inference credentials or paid calls.

## 0.2.1

### New

- Added explicit progress-only reconciliation to the optional execution checkpoint helper, with saved plan snapshots, bounded status diffs, exact revision binding, caller-attested reasons, and retained check/log provenance. Material plan changes still require restarting and rerunning checks; reconciliation neither verifies checkout freshness nor grants approval.
- Added compact route cards to all eight engineering skills and optional, decision-linked worked examples within each skill. Preserved entrypoint scope/safety gates and standalone use; examples and authored walkthroughs do not establish model performance or native activation.

### Changed

- Defined creation-date filenames for new fallback plans/specs and active/closed/living artifact lifecycle: resume unfinished scope across sessions, preserve closed task records, use authorized linked successors when warranted, and keep evidence-heavy history out of active instructions.
- Updated execution guidance and helper regression coverage for reconciliation, stale-plan gates, legacy state, and snapshot integrity.
- Clarified that `.workflow/` is optional storage owned by the `execute-plan` checkpoint helper, beside the selected plan; manual tracking needs none and `status` creates no files.
- Clarified no-write check handling in review, diagnosis, ownership assessment, planning, and verification: account for ignored caches/outputs, use verified suppression or disposable copies, and retain coverage limits.

### Fixed

- Clarified `strategize` routing for substantial specified changes and proven corrections: size alone does not reopen discovery, and diagnosis is for uncertain causes. Preserved design exploration when the cause is known but the correction or behavior remains undecided.
- Prevented checkpoint Git review queries from refreshing the index; added a public-CLI regression for stale stat-cache preservation and meaningful report output. Clarified that authorized local workflow/report writes remain separate from read-only Git inspection.

### Validation

- Retained synthetic release-note parser coverage for exact version extraction and rejection cases; removed permanent tests tied to actual release wording. Exact 0.2.1 note extraction was also checked during non-model verification.
- Source, helper, package and author-executed fixture checks retain coverage limits. The bounded model-response pilot does not establish general improvement, native activation or tool-execution safety.

## 0.2.0

### New

- Added eight standalone engineering skills:
  - `strategize`: clarify intent, assess feasibility, compare approaches, and define acceptance conditions.
  - `plan-work`: produce dependency-ordered phases with implementation, verification, documentation, and handoff steps.
  - `execute-plan`: resume approved work inline, track phase outcomes, and complete checks and documentation.
  - `debug-systematically`: establish a supported cause, with separate diagnosis-only and authorized-fix branches.
  - `design-modules`: assess or migrate ownership and interfaces using caller contracts, change locality, dependency-aware checks, and compatibility obligations.
  - `review-code`: report evidence-backed findings and evaluate feedback while preserving assessment and remediation scope.
  - `test-first`: develop behavior through red-green-refactor cycles and protect refactors with meaningful characterization coverage.
  - `verify-work`: establish scoped readiness from current code, documentation, packages, and runtime evidence.
- Added `execute-plan` and planning check routes for prose-only work, existing implementation, behavior-preserving refactors, and inaccessible hosts, preserving pending evidence instead of manufacturing failing tests or readiness.
- Added an optional standard-library checkpoint helper for `execute-plan`: named check logs, plan-revision isolation, phase handoffs, and read-only Git reports.
- Added conditional written specs and plans with existing-artifact/location precedence, an ignored `.your/specs/` and `.your/plans/` fallback, and phase evidence updates. Kept permanent regression tests in normal project test locations.
- Required need and authorization before extra working artifacts, characterization of uncovered consumers before migration, and preservation of established execution approval. Distinguished unavailable host evidence from failed behavior and kept verification-only requests free of corrective edits.
- Added collection history, writing methodology, workflow evidence, skill-selection guidance, and documentation of verification limits.
- Added GitHub PR/main validation for strict skill frontmatter, helper regressions and non-installing Skills CLI discovery, plus validated `v*` tag releases using only the matching changelog section and marking prerelease tags appropriately.
- Added a repository guide in `CLAUDE.md`, referenced by `AGENTS.md`, covering authoring, validation, and installation conventions.

### Changed

- Renamed and refactored `opencraft-skill` as `craft-skill`, retaining Extract, Design, and Refine modes. Reused supplied context, kept core work portable and inline, and made interviews, providers, and isolated evaluation conditional.
- Aligned `craft-skill` grading paths, measured timing records, raw-data analysis, and comparison criteria with its evaluation contracts. Separated behavioral and trigger schemas and documented surrogate measurement limits.
- Clarified installation layouts, helper paths, provider requirements, and optional evaluation in the README and reference guide.

### Fixed

- Kept `craft-skill` assessment-only refinement read-only through revision and evaluation steps, reporting findings without claiming changed paths.
- Corrected the trigger evaluator to inspect later tool events and leave failed or incomplete executions unscored; rejected invalid scores before description optimization.
- Corrected guide navigation links and removed obsolete backup-preservation notes.

## [0.1.0] — 2026-08-14

First beta release. Introduces **opencraft-skill**, a harness-agnostic meta skill for
creating, extracting, and refining Agent Skills.

### Added

#### opencraft-skill — meta skill

- **Three modes** routed automatically from the user's description:
  - **Mode 1: Extract** — capture a workflow the agent just completed into a reusable skill
  - **Mode 2: Design** — build a new skill from scratch with material collection and domain interviews
  - **Mode 3: Refine** — diagnose and improve an existing skill; escalates to restructure when 3+ failures share a root cause
- **Mode selection gate** — checks whether the task warrants a skill at all (one-off tasks, volatile workflows, and trivially simple prompts are routed away)
- **Smaller-model hardening** — interview sequences use explicit `"Send ONE question. Wait."` formatting; reference files gate behind `"Stop. Read this file in full before continuing."` directives; Mode 3 escalation uses an explicit count-first gate before patching
- **Eval loop** with two paths:
  - Path A (subagents available): parallel with_skill / without_skill runs, subagent grading, benchmark aggregation
  - Path B (inline fallback): fresh-session or inline execution with thumbs-up/down review
- **Harness-agnostic design**: no tool-specific names anywhere in SKILL.md; capability descriptions only; works across Claude Code, Pi, Cursor, Copilot, Gemini CLI, and any Agent Skills-compatible harness

#### Tier 1 scripts — stdlib Python 3, no install required

- `scripts/quick_validate.py` — validates SKILL.md: frontmatter present, `name` format, `description` required, no unknown frontmatter keys, body ≤ 500 lines; exit 0 = valid
- `scripts/aggregate_benchmark.py` — reads `grading.json` and `timing.json` from an iteration workspace, computes mean/stddev/n for pass rate, tokens, and time per configuration, writes `benchmark.json` with delta
- `scripts/package_skill.py` — validates first, then zips the skill directory into a distributable `<name>.skill` file; excludes `evals/`, `__pycache__`, `.pyc`, `.DS_Store`

#### Tier 2 scripts — require an LLM provider

- `scripts/llm_call.py` — shared LLM call utility (stdlib urllib); provider auto-detected: `ANTHROPIC_API_KEY` → `OPENAI_API_KEY` → `claude -p` fallback; used by improve_description.py and run_loop.py
- `scripts/run_eval.py` — parallel trigger-rate measurement via `claude -p --output-format stream-json`; Claude Code CLI only (trigger testing is harness-specific); supports configurable runs-per-query, trigger threshold, and worker count
- `scripts/improve_description.py` — LLM-driven description rewriting based on eval failures; enforces 1024-char hard limit with an automatic shorten pass; tracks attempt history to prevent repetition; works with any provider via llm_call.py
- `scripts/run_loop.py` — full optimization loop: evaluates, improves, and re-evaluates up to N iterations with a 60/40 stratified train/test split; picks best description by test score; outputs JSON with full iteration history; eval step requires Claude Code CLI (via run_eval.py); improvement step uses any LLM provider via llm_call.py
- `scripts/utils.py` — shared `parse_skill_md()` parser with YAML block scalar support (`>`, `|`, `>-`, `|-`)

#### Agents

- `agents/grader.md` — grades eval assertions with evidence; reads `timing.json` for token/duration data; extracts and verifies implicit claims beyond predefined assertions; reads `user_notes.md` when present; critiques weak assertions
- `agents/comparator.md` — blind A/B quality judge; generates a task-specific rubric (content: correctness/completeness/accuracy; structure: organization/formatting/usability); scores 1–5 per criterion, 1–10 overall; writes `comparison.json`
- `agents/analyzer.md` — two roles: (1) post-hoc win/loss analysis with actionable improvement suggestions for the losing skill; (2) benchmark pattern analysis surfacing per-assertion and cross-eval patterns that aggregate metrics hide

#### References

- `references/schemas.md` — exact field contracts for all data files: `evals.json`, `grading.json`, `timing.json`, `benchmark.json`, `comparison.json`, `analysis.json`; documents the `assertion_results` field name requirement that `aggregate_benchmark.py` depends on
- `references/description-optimization.md` — three principles for effective descriptions (imperative phrasing, user intent not implementation, near-miss negatives); manual workflow with 5 candidates, ~20 test queries, 60/40 train/validation split
- `references/scripts.md` — Command/Script/Validator taxonomy with disambiguation questions; language selection table; four authoring rules; per-type quality checklists

[0.1.0]: https://github.com/linellazatin/openlines-skills/releases/tag/v0.1.0
