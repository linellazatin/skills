---
name: skills-enhancer
description: Design and run evidence-bounded tests for an Agent Skill's routing, instruction-following, or tool-enabled task behavior. Use for any skill and any model interface, local or hosted; no particular provider or runner is required. Does not certify general model performance, authorize skill edits, or replace an actual host test.
---

# Test an Agent Skill

Use this procedure to evaluate a skill against realistic, observable cases. Work manually with any model interface; optional adapters may automate runs but are not required. Preserve authorization, privacy, and the tested skill unchanged.

## Entry route

- **Inputs:** target skill and intended contract, task examples/context, model interface or manual access, available tools/permissions, and requested scope.
- **First action:** state the claim being tested and identify the exact skill snapshot and relevant behavior.
- **Stop condition:** return case-level evidence, incomplete/error attempts, findings, coverage limits, and claims bounded to the tested conditions. A test does not authorize edits, installation, publication, or persistent environment changes.

## Procedure

1. **Define the question.** Select one or more distinct modes: routing simulation, no-tools procedural simulation, or tool-enabled task. Record target skill/version or content hash, intended scope, model/interface/harness when known, loading method, tools, settings, and data/privacy constraints.
2. **Prepare cases before running.** Use realistic requests with explicit expected behavior and prohibited actions. Cover relevant intended and neighboring triggers, normal and consequential boundary/failure paths, and follow-up evidence when applicable. Keep answer keys and grader assertions out of model-visible prompts unless disclosure is intentional. Freeze case text and version it before comparison.
3. **Run and capture.** Apply the chosen mode as described in [the protocol](references/protocol.md). Hold conditions constant for comparisons; label changes and repeats. Save exact model-visible inputs, tested skill hash, raw output, available settings, and relevant traces. Never record credentials. Keep all generated artifacts outside the skill under test and any read-only reference data.
4. **Assess evidence.** Grade each assertion with a quote or observable trace and rationale. Separate model statements from actions actually performed. Flag invented evidence, unsafe or unauthorized actions, stale conclusions, and false completion. Keep transport errors, timeouts, refusals, truncations, and malformed outputs visible and unscored as behavior unless that condition itself is under test. Human review owns final judgments.
5. **Report limits.** Give per-case outcomes, denominators, repeats, errors, critical violations, environment, and uncovered risks. Distinguish route selection from native activation, simulation from tool use, and task outcome from instruction compliance. Do not generalize beyond tested skill versions, cases, models, interfaces, and reachable surfaces.

See [record schemas and examples](references/schemas.md) for optional JSON artifacts and [case examples](references/examples.md) for illustrative fixtures. Structural validation does not prove skill effectiveness. A successful test is evidence about its tested conditions, not a universal pass or performance guarantee.
