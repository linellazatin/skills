# Project guide

Portable engineering Agent Skills plus `craft-skill` for creating/evaluating skills: standalone Markdown instructions and optional helpers, not an application or harness plugin.

## Layout

- `skills/<name>/SKILL.md`: metadata, triggers, standalone workflow.
- Each skill's `references/`, `agents/`, `assets/`, `scripts/`: optional shipped resources; `tests/`: deterministic helper regressions where present.
- `README.md`: catalog, installation, artifact policy, writing methodology.
- `CHANGELOG.md`: release history; 0.2.0 added eight engineering skills and renamed/refactored `opencraft-skill` as `craft-skill`.
- `docs/guides/`: Agent Skills format and implementation guidance.
- `.your/specs/`, `.your/plans/`: ignored local records for substantial work; their wildcard ignore setup is not distributed by Git.

## Authoring

- Read affected skills and referenced resources before editing. Preserve standalone use, relative resource paths and optional supporting workflows. Core instructions describe capabilities without requiring a harness, provider, plugin or subagent system; helpers declare requirements and retain manual fallbacks.
- Triggers target requested results and distinguish neighboring workflows. Procedures specify ordered actions, observable evidence, failure recovery and completion criteria. Reuse context and decisions; separate assessment from authorized implementation.
- Execute inline. Git writes/commits, publishing and installation into real user directories require user authorization.
- Keep prose concise and paragraphs unwrapped; prefer existing files over new docs. Permanent tests belong in normal test directories; disposable probes in temporary workspaces. Update related docs/current changelog for behavior, scope, tooling or installation changes; preserve historical releases.

## Working records

- Requested or established locations and project naming conventions take precedence. New fallback plans/specs use `YYYY-MM-DD-<descriptive-name>.md`; retain creation dates and don't automatically rename existing files. Resume unfinished same-scope work across sessions; small work stays inline.
- Preserve closed records. New authorized work needing persistence gets a linked successor; living canonical specs receive authorized contract updates, not competing contracts.
- Keep active records concise with evidence links. Record closure outcome, actual acceptance and gaps once; don't hide required pending work, evidence or acceptance.
- Only execute-plan's optional helper creates `.workflow/` beside the selected plan. Manual tracking needs none; `status` creates no files.

## Validation

Run relevant checks from the repository root:

```bash
# Changed skill: supported metadata/structure
python3 skills/craft-skill/scripts/quick_validate.py skills/plan-work
# Affected helper regressions
python3 skills/craft-skill/tests/test_run_eval.py
python3 skills/execute-plan/tests/test_checkpoints.py
# Repository CI; PyYAML required only here
python3 -m pip install PyYAML==6.0.3
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
# Discovery without installation
npx --yes skills add . --list
# Whitespace
git diff --check
```

- Prose: factual consistency, local links, resource paths, whitespace. Helpers: affected regressions. Distribution: package contents and isolated temporary installation, preserving supporting files/licenses.
- Metadata proves limited structure; helper tests/discovery don't establish native activation or model compliance. Performance claims need controlled execution evidence.
- Retain synthetic release-note extraction/rejection tests, not permanent wording assertions. Check actual version-note extraction when preparing releases.
- GitHub validates PRs and pushes to `main`; `v*` tag releases reuse validation. Notes use the exact matching changelog section; missing, duplicate or empty sections block publication. Workflows/helpers live in `.github/workflows/`, `scripts/`, `tests/`.
- Pinned discovery: `skills@1.7.2 add . --list`; installation has no `--dry-run` flag.

## Installation

Vercel Labs' `npx skills add` is recommended; manual copy and persistent-checkout symlinks remain supported. No custom npm package or harness bootstrap. Installation checks specify skill, agent and scope; never use broad `--all` against the user's environment. [README](README.md#using-these-skills) covers commands and the current remote publication caveat.
