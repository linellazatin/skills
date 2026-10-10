# Project guide

This repository contains portable Agent Skills for engineering workflows and `craft-skill`, a meta skill for creating and evaluating skills. The skills are Markdown instructions with optional helpers, not an application or a harness plugin.

## Repository layout

- `skills/<name>/SKILL.md`: metadata, triggers, and standalone workflow instructions.
- `skills/<name>/references/`, `agents/`, `assets/`, and `scripts/`: optional resources shipped with that skill.
- `skills/<name>/tests/`: deterministic helper regression tests where present.
- `README.md`: skill catalog, installation, artifact policy, and writing methodology.
- `CHANGELOG.md`: release history; `0.2.0` introduces eight engineering skills and renames/refactors `opencraft-skill` as `craft-skill`.
- `docs/guides/`: Agent Skills format and implementation guidance.
- `.your/specs/` and `.your/plans/`: ignored local working artifacts when substantial work warrants written records. Preserve existing artifact locations first. The local wildcard ignore setup is not distributed by Git.

## Authoring conventions

Read the affected skill and its referenced resources before editing. Keep each skill independently usable, with relative resource paths and optional supporting workflows. Core instructions must describe capabilities rather than require a particular harness, provider, plugin, or subagent system. Declare helper requirements and retain manual fallbacks.

Write triggers around the requested result and distinguish neighboring workflows. Procedures should specify ordered actions, observable evidence, failure recovery, and completion criteria. Reuse supplied context, preserve established decisions, and keep assessment separate from authorized implementation. Execute work inline; Git writes, commits, publishing, and installation into real user directories require appropriate user authorization.

Keep prose concise and paragraphs unwrapped. Prefer existing files over new documentation. Keep permanent tests in normal test directories and disposable probes in temporary workspaces. Update related documentation and the current changelog when behavior, skill scope, tooling, or installation changes; preserve historical release entries.

## Validation

Run checks appropriate to the change from the repository root:

```bash
# Validate a changed skill's supported metadata and structure
python3 skills/craft-skill/scripts/quick_validate.py skills/plan-work

# Run affected helper regressions
python3 skills/craft-skill/tests/test_run_eval.py
python3 skills/execute-plan/tests/test_checkpoints.py

# Confirm CLI discovery without installing
npx --yes skills add . --list

# Check patch whitespace
git diff --check
```

For prose-only changes, check factual consistency, local links, resource paths, and whitespace. For helper changes, run the affected regression suite. For distribution changes, inspect package contents and test installation in an isolated temporary destination, preserving supporting files and licenses. Metadata validation is limited structural evidence; helper tests and discovery do not establish native harness activation or model compliance. Performance claims require controlled execution evidence.

## Installation

Vercel Labs' `npx skills add` is the recommended installer; manual copy and persistent-checkout symlinks remain supported. No custom npm package or harness bootstrap is required. Use explicit skill, agent, and scope selections in installation checks; never use broad `--all` against the user's environment. See [README.md](README.md#using-these-skills) for commands and the current remote publication caveat.
