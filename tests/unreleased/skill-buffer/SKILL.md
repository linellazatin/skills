---
name: skill-buffer
description: Inspect portable skills, freeze paired response assessments, import evidence-backed author grades, compare outcomes and record separate candidate revisions. Use for explicit skill assessment or enhancement prototypes; does not install skills, activate hosts or execute proposed tasks.
license: MIT
compatibility: Python 3.13+ and PyYAML==6.0.3. Offline imports need no credentials; optional HTTP evaluation needs an explicit chat-completions endpoint and model.
---

# Skill Buffer

Work inline in the current agent session. Read [README](README.md) for commands and [contracts](schemas/contracts.json) for versioned formats. Use `python /absolute/path/to/skill_buffer.py <command>` from any working directory. Keep candidates and runtime workspaces separate from source skills. Never infer installations, endpoints or credential files.

1. Inspect explicit baseline and candidate directories. Resolve structural findings before freezing; perform semantic review separately.
2. Author a suite with unique routing/procedure cases and explicit procedure resources. Mark held-out cases `acceptance`. Keep assertions and expected choices outside inference prompts.
3. Freeze both trees, suite and settings into a new workspace. Use snapshots for every later operation. Default settings are temperature 0.6, seed 42, max_tokens 4096, one repeat and 300-second timeout.
4. Evaluate through an explicitly supplied endpoint/model, or import responses tied to frozen job IDs with completion status and available provenance. A transport failure stops evaluation; only explicit `--resume` continues it. Never reinterpret missing cache observations as fresh inference.
5. Grade valid procedure attempts inline as author review. Supply every assertion text, Boolean verdict and exact quoted response character range. The CLI validates identity and evidence locations, not the truth of the judgment. Compare only valid, graded matched pairs; retain missing and invalid attempts in reports.
6. Export an enhancement brief. Revise a separate candidate directory using development findings; preserve licenses and resources. Record findings addressed and resource diffs into a new frozen development workspace, then assess it with the same development cases. Do not use acceptance cases in revision briefs.
7. Report paired outcomes, critical failures, invalid/missing records, telemetry and limits. Response simulations show proposed decisions only. Native activation, tool-enabled execution, Pi integration, automatic grading/revision generation, installation and publishing remain deferred.
