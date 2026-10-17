# Skill Buffer prototype

A standalone, unreleased CLI and [skill wrapper](SKILL.md) for frozen skill assessment and separate candidate revisions. Requires Python 3.13+ and `PyYAML==6.0.3`; install with `python -m pip install -r requirements.txt`. No repository/reference imports or inferred installations, endpoints or credential files. Paths are explicit and caller-relative; each command supports `--help`.

## Commands

```sh
python skill_buffer.py inspect --input examples/baseline --output /tmp/inspection.json
python skill_buffer.py freeze --baseline examples/baseline --candidate examples/candidate --suite examples/suite.json --output /tmp/buffer-run
python skill_buffer.py import-responses --workspace /tmp/buffer-run --input /tmp/responses.json
python skill_buffer.py evaluate --workspace /tmp/buffer-run --endpoint http://localhost:8000/v1/chat/completions --model explicit-model
python skill_buffer.py grade --workspace /tmp/buffer-run --input /tmp/author-grades.json --output /tmp/validated-grades.json
python skill_buffer.py compare --workspace /tmp/buffer-run --input /tmp/validated-grades.json --output /tmp/buffer-report
python skill_buffer.py enhance brief --workspace /tmp/buffer-run --input /tmp/validated-grades.json --output /tmp/brief.json
python skill_buffer.py enhance record --workspace /tmp/buffer-run --candidate /tmp/authored-candidate --input /tmp/findings.json --output /tmp/enhanced-run
```

Choose HTTP evaluation or external imports per workspace. `--api-key-env NAME` reads only that variable, stores its name and redacts its value from responses/diagnostics; authorization headers are never stored. Endpoint credentials, query strings, fragments and redirects are rejected. Importers must sanitize their own records.

Transport failures go to `failures.json`, return exit 1 and leave the job unfinished. Repeat `evaluate` with `--resume` and identical endpoint, model, credential-variable name, token cap, settings and frozen inputs. No automatic retries or completed-attempt replacement; rerunning malformed/truncated attempts needs a new workspace. Structural findings return exit 1; invalid inputs return exit 2.

`freeze --settings PATH` accepts JSON overrides: `temperature=0.6`, `seed=42`, `max_tokens=4096`, `repeats=1`, `timeout=300` seconds and `provider_parameters={}`. Provider parameters cannot contain credentials, override core fields or add token caps. `evaluate --token-field max_completion_tokens` substitutes that cap explicitly; never sends both. Calls are sequential with alternating baseline/candidate order. Sanitized requests/raw responses, actual parameters and elapsed times are saved; missing/unsupported usage is null and supplied usage is unverified.

## JSON contracts

All contracts use integer `version: 1`; [schemas](schemas/contracts.json) define fields and the CLI enforces domain constraints. JSON/YAML duplicate keys are rejected. Skill YAML uses SafeLoader, supports block scalars and requires nonempty `name`/`description`; name matches the directory in lowercase hyphenated words, and optional metadata is a mapping. Inspection separates structural findings from semantic review and checks Markdown relative file links, excluding plain-text/backtick references and URL/heading validation. All symlinks are rejected. Freeze requires a new, nonoverlapping output and copies every resource/license without executing scripts.

| Contract | Required details |
| --- | --- |
| Suite | Unique case IDs, `routing`/`procedure` type, prompt, optional fixture, assertions with unique IDs/text and optional `critical` flags. Routing declares `acceptable_primary`; procedure names a skill and explicitly selected `resources`. Partition defaults to `development`; mark held-out cases `acceptance`. Catalog descriptions or entrypoint/selected resources enter inference prompts; expected choices/assertions do not. |
| Manifest | Frozen trees/resource hashes, suite, templates, exposure, settings, jobs and fingerprint. Later commands verify frozen inputs. |
| Imports | `attempts` with frozen `job_id`, string `response`, `completion_status` (`complete`, `truncated`, `transport-error`), `provenance` object and optional object/null `telemetry`. Adds `external-import`, fingerprint and classification. Unknown/duplicate jobs reject the entire batch; supplied cache observations retain importer attribution. |
| Author grades | `grades` with `job_id`, `case_id`, `fingerprint`, `response_sha256` and complete `assertion_results`: exact assertion `id`/`text`, Boolean `verdict`, nonempty `evidence`. Evidence uses `source: "response"`, zero-based Unicode `start`/exclusive `end` and exact `quote`. Empty grades are valid for routing-only runs. |
| Findings | `findings_addressed`, e.g. `["procedure:0:baseline"]`, identifying frozen development jobs. Records author claims, not verified semantic resolution. |

Routing responses must be exactly `{"primary":"catalog-name"}`: valid wrong choices score zero; malformed JSON, unsupported shapes/IDs, truncation and transport failures stay unscored. Procedures require nonempty, complete responses and score the fraction of passing author assertions. Reports expose critical failures, invalid/missing records, transport failures, telemetry and provenance; deltas use only valid/scored matched pairs.

Enhancement briefs export failed valid development responses, quoted evidence and relevant instructions; missing grades/invalid attempts need assessment repair. Record an agent-authored candidate separately: retain the original baseline/settings/development cases, exclude acceptance cases, and emit resource-aware additions/removals/text/binary diffs. Existing LICENSE/NOTICE files cannot change or disappear. Source skills are never revised by the CLI.

## End-to-end walkthrough for a skill developer

The workflow is **inspect → write cases → freeze → collect responses → author grades → compare → revise a separate candidate → reassess**. Skill Buffer manages artifacts and validates records; you or your agent author cases, judge procedural responses and make revisions. Run the following commands from the Skill Buffer directory. Replace the example source path with your checkout path.

### 1. Inspect the skill

```sh
mkdir -p /tmp/design-modules-assessment
python3 skill_buffer.py inspect \
  --input /Users/lines/workspace/my/proj/openlines-skills/skills/design-modules \
  --output /tmp/design-modules-assessment/inspection.json
```

`structural_findings: []` means no supported metadata or resource-link problems were found. `semantic_review: "not performed"` means the tool has not assessed whether the instructions or resulting responses are good. Inspection is the structural starting point, not a behavioral assessment.

### 2. Try the complete synthetic walkthrough

```sh
python3 examples/walkthrough.py --output /tmp/skill-buffer-demo
```

Use a new output directory. This demonstrates the file flow with authored synthetic responses and makes no model calls. Open these outputs:

| Output under `/tmp/skill-buffer-demo/` | Purpose |
| --- | --- |
| `report/report.md` | Initial comparison |
| `brief.json` | Development failures exported for revision |
| `enhanced/enhancement.json` | Candidate resource diffs |
| `enhanced-report/report.md` | Reassessment |

### 3. Define what the skill should accomplish

For `design-modules`, start with **procedure cases**: give the model the skill and assess its proposed response. Author `/tmp/design-modules-assessment/suite.json`:

```json
{
  "version": 1,
  "cases": [
    {
      "id": "assessment-scope",
      "type": "procedure",
      "skill": "design-modules",
      "partition": "development",
      "prompt": "Two adapters duplicate a discount calculation. Assess whether it should have a shared owner. This is assessment only; do not implement a migration. Describe your investigation and proposed handoff.",
      "fixture": {
        "consumers": ["CLI adapter", "HTTP adapter"],
        "current_behavior": "Both calculate the same discount, but expose different error formats."
      },
      "resources": ["references/worked-examples.md"],
      "assertions": [
        {
          "id": "scope",
          "text": "Keeps the response in assessment scope without claiming an implemented migration.",
          "critical": true
        },
        {
          "id": "contracts",
          "text": "Plans to compare shared policy and consumer contracts before recommending consolidation."
        }
      ]
    }
  ]
}
```

Use realistic prompts, observable assertions and concrete fixtures. Cover normal requests, boundaries and likely failures. Keep additional held-out cases in a separate suite for final acceptance, or mark them `"partition": "acceptance"` so enhancement briefs exclude them. To keep acceptance responses out of the revision process entirely, evaluate the separate acceptance suite only after settling the candidate.

For **routing cases**, assess a collection containing neighboring skills. A catalog containing only `design-modules` gives the model no meaningful competing choice. Routing exposes names/descriptions; procedure cases expose `SKILL.md` and only the resources explicitly listed. Expected answers and assertions stay outside inference prompts.

### 4. Freeze the assessment

The CLI requires both baseline and candidate. For a newly created skill with no previous revision, use the same directory for both:

```sh
python3 skill_buffer.py freeze \
  --baseline /Users/lines/workspace/my/proj/openlines-skills/skills/design-modules \
  --candidate /Users/lines/workspace/my/proj/openlines-skills/skills/design-modules \
  --suite /tmp/design-modules-assessment/suite.json \
  --output /tmp/design-modules-assessment/run
```

| Output | Purpose |
| --- | --- |
| `snapshots/` | Copies of both skill trees and resources |
| `manifest.json` | Cases, settings, prompts, job IDs and hashes |
| `attempts.json` | Initially empty response records |

**Identical inputs let you assess initial behavior but establish no improvement between revisions.** This also does not compare against running without the skill. Use an earlier revision as baseline when available. Leave frozen files unchanged; later commands verify their hashes. The output workspace must be new and outside the source trees.

### 5. Collect responses

Choose one route per workspace.

**A. Call a model through your endpoint.** Set these environment variables to your actual endpoint and model:

```sh
python3 skill_buffer.py evaluate \
  --workspace /tmp/design-modules-assessment/run \
  --endpoint "$CHAT_COMPLETIONS_ENDPOINT" \
  --model "$MODEL_NAME"
```

For authentication, add `--api-key-env YOUR_KEY_VARIABLE_NAME`. Defaults are temperature `0.6`, seed `42`, token cap `4096`, one repeat and timeout `300` seconds. Calls are sequential with alternating baseline/candidate order. A transport failure stops evaluation; repeat the same command with `--resume` to continue. Completed attempts are preserved.

**B. Run frozen prompts elsewhere and import responses.** Read each job's `prompt` in `manifest.json`, obtain its response and author `/tmp/design-modules-assessment/responses.json`:

```json
{
  "version": 1,
  "attempts": [
    {
      "job_id": "assessment-scope:0:baseline",
      "response": "The actual response goes here.",
      "completion_status": "complete",
      "provenance": {
        "model": "actual model identifier",
        "method": "manual external run",
        "cache_observation": "unknown"
      }
    }
  ]
}
```

Replace the sample response/provenance and include a record for each job, including `assessment-scope:0:candidate`. Sanitize imported records yourself. Then run:

```sh
python3 skill_buffer.py import-responses \
  --workspace /tmp/design-modules-assessment/run \
  --input /tmp/design-modules-assessment/responses.json
```

Use the exact frozen prompts for evaluation. Sharing assertions or expected answers with the responding model contaminates the assessment. An author-created example response demonstrates mechanics only; it is not inference evidence.

### 6. Judge each valid procedural response

**`grade` validates your judgments; it does not generate them.** Author `/tmp/design-modules-assessment/author-grades.json` with one grade per valid procedure attempt. This sample shows the shape, not a completed grade:

```json
{
  "version": 1,
  "grades": [
    {
      "job_id": "assessment-scope:0:baseline",
      "case_id": "assessment-scope",
      "fingerprint": "COPY FROM manifest.json",
      "response_sha256": "SHA256 OF THE EXACT RESPONSE STRING",
      "assertion_results": [
        {
          "id": "scope",
          "text": "Keeps the response in assessment scope without claiming an implemented migration.",
          "verdict": true,
          "evidence": [
            {
              "source": "response",
              "start": 0,
              "end": 5,
              "quote": "EXACT"
            }
          ]
        },
        {
          "id": "contracts",
          "text": "Plans to compare shared policy and consumer contracts before recommending consolidation.",
          "verdict": false,
          "evidence": [
            {
              "source": "response",
              "start": 0,
              "end": 5,
              "quote": "EXACT"
            }
          ]
        }
      ]
    }
  ]
}
```

Replace every placeholder, verdict and evidence reference with your actual judgment. Include both assertions and grades for all valid procedure jobs, including the candidate. Evidence offsets are zero-based Unicode character positions with an exclusive end; the quote must exactly match that response slice. For an omission, quote the relevant passage or whole response and judge the omission yourself. The response hash is SHA-256 of the exact UTF-8 response string, not the attempts file. An agent can prepare these records inline, including hashes and offsets, while explaining its verdicts.

```sh
python3 skill_buffer.py grade \
  --workspace /tmp/design-modules-assessment/run \
  --input /tmp/design-modules-assessment/author-grades.json \
  --output /tmp/design-modules-assessment/grades.json
```

Routing choices are scored mechanically and need no author grades; use `{"version": 1, "grades": []}` for a routing-only run. Malformed, truncated and otherwise invalid attempts remain visible and unscored.

### 7. Generate and read the report

```sh
python3 skill_buffer.py compare \
  --workspace /tmp/design-modules-assessment/run \
  --input /tmp/design-modules-assessment/grades.json \
  --output /tmp/design-modules-assessment/report
```

Open `report/report.md`. Check assertion scores and critical failures, invalid responses and missing attempts/grades, baseline/candidate differences for matched valid/scored pairs, and telemetry/provenance. A high score means responses met your authored assertions; it does not establish native activation or successful task execution. Use a new report directory each time.

### 8. Revise a separate candidate and reassess

Export failed development cases:

```sh
python3 skill_buffer.py enhance brief \
  --workspace /tmp/design-modules-assessment/run \
  --input /tmp/design-modules-assessment/grades.json \
  --output /tmp/design-modules-assessment/brief.json
```

Copy the frozen skill into a separate candidate directory:

```sh
mkdir -p /tmp/design-modules-assessment/candidate
cp -R /tmp/design-modules-assessment/run/snapshots/candidate/design-modules \
  /tmp/design-modules-assessment/candidate/design-modules
```

Use a new candidate destination. Revise that copy using the brief; preserve resources and license notices. If there are no failed development cases, review your coverage before deciding whether a revision is needed. Author `/tmp/design-modules-assessment/findings.json` identifying the failed development job addressed:

```json
{
  "version": 1,
  "findings_addressed": ["assessment-scope:0:baseline"]
}
```

Record the revision:

```sh
python3 skill_buffer.py enhance record \
  --workspace /tmp/design-modules-assessment/run \
  --candidate /tmp/design-modules-assessment/candidate/design-modules \
  --input /tmp/design-modules-assessment/findings.json \
  --output /tmp/design-modules-assessment/revised-run
```

This produces resource diffs and a new workspace with the original baseline, revised candidate, original settings and development cases. It does not generate revisions or prove findings are fixed. Repeat **evaluate/import → author grades → grade → compare** against `revised-run`, using new grade identities and output paths.

Finally, assess the settled candidate against held-out cases. Author `acceptance-suite.json` using the same suite format, with fresh cases marked `acceptance`, then freeze a separate workspace:

```sh
python3 skill_buffer.py freeze \
  --baseline /tmp/design-modules-assessment/run/snapshots/baseline \
  --candidate /tmp/design-modules-assessment/candidate/design-modules \
  --suite /tmp/design-modules-assessment/acceptance-suite.json \
  --output /tmp/design-modules-assessment/acceptance-run
```

Use the same run settings as development; if you supplied settings overrides, pass the same settings file with `--settings`. Collect responses, author grades and compare against `acceptance-run`. Report held-out failures separately; further revisions need a fresh acceptance check.

### Agent-assisted workflow

> Use Skill Buffer inline to assess this skill. Author realistic development and held-out acceptance cases, freeze the assessment, collect responses through my specified endpoint, grade each procedure response with quoted evidence, and report failures. Revise only a separate candidate directory and reassess the same development cases.

You supply the intended behavior and inference endpoint/model; the agent handles assessment artifacts and author review. Source edits, installation and publishing remain separate actions requiring authorization.

## Offline verification

```sh
python -B -m unittest discover -s tests -v
python examples/walkthrough.py --output /tmp/skill-buffer-walkthrough
```

Copy this directory elsewhere to run independently. The walkthrough invokes every offline command from an unrelated working directory and writes synthetic responses/grades, frozen runs, candidate revisions, JSON/Markdown reports, inventories and a summary into a new output directory. Retained synthetic reports: [JSON](examples/walkthrough-report.json), [Markdown](examples/walkthrough-report.md). Runtime workspaces, virtual environments and caches are excluded from distribution.

## Limits

Semantic grades/findings are author review; evidence checks validate locations, not judgment. Simulations show proposed decisions, not execution, absence of writes or host readiness. Inventories detect persistent changes only; hashes detect accidental changes, not adversarial manifest rewrites. Mock HTTP tests do not prove provider compatibility; no paid inference was required. Pi integration, native activation, tool execution, automatic grading/revision, installation and publishing remain deferred.
