---
name: skill-buffer
description: Assess an existing skill against realistic cases, check routing and procedure, compare revisions, or turn evidence-backed findings into a candidate fix and recheck. Does not create new skills, install skills, or execute the tasks being assessed.
license: MIT
compatibility: Static review needs access to the target skill's files. The optional CLI needs Python 3.13+ and PyYAML==6.0.3; only HTTP evaluation needs an explicit chat-completions endpoint and model.
---

# Skill Buffer

Use this workflow manually or with an agent in any environment that can read the target files. Use the [CLI](scripts/skill_buffer.py) with the [usage guide](README.md) and [JSON contracts](schemas/contracts.json) for repeatable comparisons. Assessment does not authorize edits, installation, task execution, or sending skill content to an endpoint.

## 1. Establish what the skill should do

Read the target's `SKILL.md`, relevant linked resources, and any helper interfaces and tests needed to understand its claims. Identify who should use it, which requests should route to it or elsewhere, what outcome it promises, and which prerequisites, scope limits, and completion checks matter. Use the user's intent and authoritative docs or examples as the rubric; flag conflicts rather than treating current behavior as correct by definition. Note which claims need actual execution or host evidence.

## 2. Choose checks that match the claims

- **Structure:** Inspect metadata, resource links, dependencies, and whether documented commands match their implementation. Use `inspect` for supported structural checks and review the rest manually. Resolve structural blockers before freezing.
- **Routing:** When checking activation guidance, use a realistic match, a neighboring request that belongs to a different skill, and an out-of-scope case where no skill applies. Include meaningful alternatives in the catalog. This checks a proposed selection, not native activation.
- **Procedure:** Check a normal request, a likely failure or missing prerequisite, and a consequential scope boundary. Include realistic fixtures and only the resources needed for each case. Write observable assertions before seeing responses; mark scope or safety violations critical when appropriate. A stated intention to run a tool is not evidence that it ran.

Use only the checks that answer the request. Keep assertions and expected choices out of prompts. Set aside fresh acceptance cases before revising; keep them in a separate suite if the author must not see them. Without permitted inference or the CLI, walk the instructions against the cases and cite file locations. Label this static author review, with no behavioral score. Report host- or execution-dependent claims as unverified.

## 3. Collect and judge evidence

For a paired simulation, freeze explicit baseline and candidate directories, cases, and settings in a new workspace. Use the same cases and collection conditions for both. If both snapshots are identical, treat results as initial observations, not improvement. Keep outputs outside source trees and frozen snapshots.

Use one collection mode per workspace: import responses to the exact frozen prompts, or call an explicitly authorized endpoint and model. A transport failure stops HTTP evaluation; continue only with explicit `--resume`. Grade valid procedure responses against every assertion with exact quoted evidence. The CLI validates the records, not the judgments. Compare scored pairs and report critical failures, invalid or missing evidence, and development versus acceptance results separately.

## 4. Turn findings into focused improvements

For each actionable finding, record the case or file location, expected result, observed evidence, likely cause, smallest correction, and recheck. Distinguish a weak trigger, missing decision or recovery step, misleading resource, or helper defect from a bad case, missing grade, or invalid response. Repair assessment gaps before drawing conclusions from them; do not treat an empty failure list as success if evidence is missing. Mark a cause provisional if the evidence does not support it.

If asked to revise, use a separate candidate copy and keep source skills unchanged. Use `enhance brief` for development findings and `enhance record` for the authored revision and resource diffs. Preserve licenses and working resources. Recheck the same development cases, then evaluate the settled candidate on held-out cases. Report changes, remaining critical failures or gaps, and what was not verified. Simulations do not establish host activation, tool execution, or absence of side effects.
