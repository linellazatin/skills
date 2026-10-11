# Portable skill-testing protocol

This protocol tests a skill against declared tasks and evidence. It is designed for manual use with any model interface; automation is optional. Follow the steps in order and report only what the tested setup demonstrates. See [schemas](schemas.md) for case, run, grading, and report records.

## 1. State the question and freeze the target

Before running a model, record:

- **Question:** route selection, instruction-following, tool-enabled task outcome, or a controlled comparison. Avoid combining these into one score.
- **Skill under test:** name, source location, version/commit if available, and content hash. Preserve an immutable copy or exact hash for each tested variant.
- **Scope:** intended users/tasks, behavior and safety/authorization constraints, relevant neighboring skills, and explicit exclusions.
- **Environment:** interface/harness, skill-loading method, model/provider identifier as exposed, tools and permissions, date, and available settings.
- **Privacy/authority:** confirm permission to send the skill, task fixture, and any project data to the chosen model/service; state retention implications. Exclude credentials and unnecessary private data.

If the skill contract or expected behavior is too unclear to write observable assertions, resolve the ambiguity or label affected cases exploratory. Do not manufacture an answer key from the tested model's response.

## 2. Author a small, discriminating case set

Write cases before observing responses. Keep each request realistic and focused. Use only case types that exercise a relevant risk:

- intended triggers and neighboring/non-matching tasks;
- normal use, ambiguous inputs, meaningful boundaries, and failure/recovery branches;
- scope, authorization, or safety constraints;
- follow-up turns that introduce new or contradictory evidence;
- where applicable, a task requiring observable tool interaction and verifiable acceptance.

For every case, define the request, supplied context/fixture, expected observable behavior, prohibited behavior, evidence mode, and assertions. Assertions should distinguish plausible correct and incorrect behavior, including evidence invented, unsafe side effects, and unjustified completion. Keep expected labels/assertions out of model-visible prompts when they would reveal the answer. Use identical case text for variants in a comparison. Freeze the case set and record its version/hash before the measured run; changes require a new case-set version and invalidate direct comparability for affected cases.

Do not infer universal coverage from a fixed case count. Explain why each selected case represents a risk in this particular skill, and note important risks not covered.

## 3. Choose one evidence mode per run

### Routing simulation

Provide the skill catalog/descriptions and user request. Record the selected primary skill and any supporting skills. This measures selection in the supplied simulation only. It does not test the host's actual discovery, ranking, activation, or competition with its full installed catalog unless those mechanisms are genuinely exercised and traced.

### No-tools procedural simulation

Provide the exact skill text (or disclose another loading mechanism), task, and fixture. Explicitly state which observations are fixture data and prohibit claims that unperformed checks/edits occurred. Grade the proposed actions, decisions, evidence needs, scope, and completion/gaps. This tests a response to supplied instructions, not actual task execution.

### Tool-enabled task

Load the skill using the stated real interface, declare available tools/permissions, and execute a bounded task in an authorized, isolated or otherwise safe environment. Preserve relevant interaction traces, outputs, state changes, and acceptance observations. Do not infer an inaccessible host/product behavior from a mock or substitute. Testing does not authorize edits to the skill, persistent environment, or external service; obtain the necessary authority and isolate side effects first.

Record mixed-mode work as separate linked runs rather than blending simulation and execution evidence. If the intended skill depends on native harness behavior, test that behavior directly when possible and report it as unverified when not.

## 4. Run with controlled conditions

For each attempt, record exact model-visible instructions and content, skill hash/loading method, model/runtime identity, interface, tool configuration, available sampling/context limits, relevant system prompts, session/history state, cache controls, timeout, and start time. Record settings as **requested**, **reported by interface**, or **unknown**; do not present a requested setting as effective unless observed. Do not assume a cache bypass or independent repeat without evidence from the interface.

For comparisons, hold constant the task text, case version, skill-loading conditions, harness, tools, and settings wherever possible. Change only the intended variable (for example, skill version); disclose unavoidable differences. Keep histories isolated unless continuation is the tested behavior. Run repeated attempts when variability matters; distinguish:

- **paired repeat:** same case and conditions across variants;
- **fresh repeat:** new independent session/attempt under the same declared conditions;
- **follow-up:** a deliberately continued session receiving a fixed new observation.

Preserve all attempts, including errors and incomplete responses. Never silently discard an inconvenient run. A fix to prompts, cases, adapter behavior, settings, or target skill creates a changed condition; mark it and rerun affected comparisons.

## 5. Capture and assess results

Store raw model output and, for tool-enabled tasks, the minimal traces needed to substantiate actions and results. Redact secrets before persistence without altering substantive evidence; document redaction. Preserve errors, truncation, refusal, malformed output, and unavailable metadata.

Grade each prewritten assertion as:

- **pass:** supported by a specific response quote or observed trace;
- **fail:** contradicted by that evidence or a required behavior is demonstrably absent in the completed response/task;
- **not_applicable:** the case condition did not apply, with reason;
- **unscored:** evidence is unavailable/incomplete or the assertion cannot fairly be judged.

Every result needs evidence and a short rationale. A missing statement in a deliberately concise or intermediate response is not proof that the full task would fail unless the case asks for that final behavior. Conversely, do not pass a case solely because its expected keywords appear: inspect whether the reasoning and observed actions satisfy the contract. Flag invented observations, unauthorized action, unsafe behavior, stale conclusions after new evidence, and false completion separately as critical concerns when relevant.

A human reviewer is accountable for final judgments. Scripts may check record shape or compute descriptive counts. Model-assisted grading is optional and must be identified, independently checked against human-reviewed examples, and never treated as ground truth. Keep route accuracy, assertion outcomes, actual task acceptance, and critical violations as separate measures.

## 6. Handle errors and incomplete attempts

Record transport/setup errors, timeouts, truncation, refusal, invalid output, and missing evidence with a clear status and available raw details. Such attempts remain in the report denominator/table but are **not behavioral failures** unless the tested behavior is specifically handling that condition. Do not claim a model failed a skill when the request did not reach it or the response was incomplete. Rerun only under documented conditions; retain both the original and rerun, and do not replace one silently.

If the interface cannot provide a setting, trace, or outcome needed for a claim, mark it unavailable and narrow the claim. If credentials or reachability are prerequisites, troubleshoot without exposing secrets or changing installed/user configuration without permission.

## 7. Report bounded findings

Report the tested skill/case-set versions, question, mode, model/interface/harness and known settings, tools, attempts and repetitions, case-level outcomes with evidence links, errors/incomplete attempts, critical violations, and coverage gaps. State what was not tested. In comparisons, identify matched cases, changed conditions, and how missing attempts were handled. Use counts with denominators and retain per-case detail; small samples are descriptive, not significance evidence.

Do not generalize from one model/interface to local/cloud categories, model sizes, all skills, or other harnesses. Do not use a universal pass threshold unless a separate, justified domain contract defines one. Report results as evidence about this target, conditions, and cases. Validation of frontmatter, schemas, or runner behavior establishes structure only.

## 8. Keep the procedure safe and portable

The manual route is always available. Optional runners/adapters may automate prompt delivery and capture, but must preserve the case and skill content, report actual available metadata/settings, and represent errors/incomplete output explicitly. Missing metadata is unknown, never guessed. Adapter-specific commands and dependencies belong in optional guidance, not as requirements of the protocol.

Keep credentials out of case files and records. Use authorized models, tools, data, and environments; disclose hosted data handling. Keep generated records outside read-only references and the skill under test. Testing does not authorize skill edits, installation, publication, or persistent changes. Report a blocked check as blocked/unverified, not passed or failed.
