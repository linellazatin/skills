# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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
