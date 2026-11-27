# Skill Buffer

Assess a skill, compare revisions, or improve a separate candidate. Use the [review guide](SKILL.md) with file access alone, or the optional CLI for repeatable response simulations. Neither requires a particular agent or harness.

| Goal | Start here |
| --- | --- |
| Review instructions without Python or inference | [Static review](#static-review) |
| Check metadata and resource links only | [Inspect and prepare](#1-inspect-and-prepare); set `BASELINE` and `WORK`, then run the first inspection only |
| Try every offline command without a model | [Offline demo](#offline-demo) |
| Assess one version, test routing, or compare two versions | [Paired assessment](#paired-assessment); choose imports or HTTP |
| Fix a finding and check for regressions | [Revise and recheck](#revise-and-recheck) |

## Static review

1. Read the target `SKILL.md`, relevant resources, and helper interfaces. Note what the skill promises, when it should apply, and what it must not do.
2. Walk through a normal request, a likely failure or missing prerequisite, and a scope boundary. Cite the instruction that leads to each decision.
3. Report the expected behavior, evidence, smallest correction, and proposed recheck. Label it static author review: no behavioral score. Review does not authorize edits or sending content to an endpoint.

## CLI setup

Run the shell examples from this directory. `python` must point to Python 3.13+; if your interpreter is named `python3` or launched with `py -3.13`, substitute it in every command. Adapt shell syntax and paths as needed.

```sh
python -m pip install -r requirements.txt  # PyYAML==6.0.3
python scripts/skill_buffer.py --help
```

Paths are explicit and caller-relative. The [CLI](scripts/skill_buffer.py) runs from elsewhere via its absolute script path, with no repo imports or endpoint/credential discovery. Use new output paths outside live skill trees and frozen snapshots. File exports never overwrite; `inspect` rejects output inside its input tree, and workspace review commands reject output inside frozen snapshots.

## Offline demo

```sh
DEMO=$(mktemp -d)
python examples/walkthrough.py --output "$DEMO/demo"
python -B -m unittest discover -s tests -v
```

Under `$DEMO/demo`, open `report/report.md`, `brief.json`, `enhanced/enhancement.json`, and `enhanced-report/report.md` in order. `run/responses-input.json` and `run/grades-input.json` show complete input files; `inventories.json` and `summary.json` record the source check and run summary. The demo invokes every offline command from a different working directory. The responses and grades are synthetic, not inference evidence. See the retained comparison reports ([Markdown](examples/reports/walkthrough-report.md), [JSON](examples/reports/walkthrough-report.json)) and inspection examples ([sample](examples/reports/inspection-sample.json), [design-modules](examples/reports/inspection-design-modules.json)).

## Paired assessment

### 1. Inspect and prepare

Set `BASELINE` and `CANDIDATE` to a single skill directory or a collection of immediate skill directories. For an initial assessment with no earlier revision, use the same path for both; this measures neither improvement nor performance without the skill.

```sh
BASELINE=/path/to/baseline
CANDIDATE=/path/to/candidate  # Or: CANDIDATE=$BASELINE
WORK=$(mktemp -d)  # Must be outside both input trees
RUN=$WORK/run
python scripts/skill_buffer.py inspect --input "$BASELINE" --output "$WORK/baseline.json"
python scripts/skill_buffer.py inspect --input "$CANDIDATE" --output "$WORK/candidate.json"
```

Stop on structural findings. Fix them if authorized, then inspect again with fresh output paths. `structural_findings: []` clears only the supported metadata/link checks; `semantic_review: "not performed"` leaves instruction quality unassessed.

### 2. Write the suite and freeze

Save `suite.json` in `$WORK` with the envelope `{"version":1,"cases":[...]}`. Use the [bundled suite](examples/fixtures/suite.json) as a template. To try it unchanged, use the bundled [baseline](examples/fixtures/baseline) and [candidate](examples/fixtures/candidate) trees and copy `examples/fixtures/suite.json` to `$WORK/suite.json`. Each case needs a unique `id`, `type`, `prompt`, and `assertions` array. Define observable assertions before collecting responses.

| Case | What to enter |
| --- | --- |
| Procedure | Set `type: "procedure"`, `skill` to a name present in both inputs, and `resources` to the relative text files the case needs in both versions. Add an optional `fixture` and one or more assertions with unique `id`, `text`, and optional `critical: true`. Cover normal use, failure recovery, and a scope boundary. |
| Routing | Set `type: "routing"`, `assertions: []`, and `acceptable_primary` to valid names from both catalogs or `null`, e.g. `["sample"]` or `[null]`. Use a catalog with meaningful alternatives. Test an intended match, a neighboring skill, and a request no skill should handle. |
| Held-out | Reserve fresh cases with `partition: "acceptance"`; the default is `development`. Keep acceptance in a separate suite and run it after the candidate settles if the reviser should not see it. |

Routing prompts expose catalog names/descriptions; procedure prompts expose `SKILL.md`, selected resources, and the fixture. The CLI withholds expected choices and assertions. Keep them out of your prompt and fixture too.

```sh
python scripts/skill_buffer.py freeze --baseline "$BASELINE" --candidate "$CANDIDATE" --suite "$WORK/suite.json" --output "$RUN"
```

`$RUN/snapshots/` contains copies of both skill trees. `manifest.json` contains the suite, templates, settings, job IDs, exact prompts, resource hashes, and fingerprint. `attempts.json` starts empty. Leave the manifest and snapshots unchanged; later commands verify them.

### 3. Collect responses: choose one mode per workspace

**External imports.** For each `manifest.json` job, send only its exact `prompt` to your chosen model under the same conditions for both variants. Save each response unchanged under its `job_id` in `$RUN/responses.json`. Sanitize records before importing. Example record in the `attempts` array:

```json
{"job_id":"procedure:0:baseline","response":"Check the parser.","completion_status":"complete","provenance":{"model":"your-model-id","method":"manual external run","cache_observation":"unknown"}}
```

Use `{"version":1,"attempts":[...]}` as the envelope. Use actual IDs, including candidate jobs and any repeats. `completion_status` is `complete`, `truncated`, or `transport-error`; `telemetry` is optional (object or `null`). Unknown or duplicate job IDs reject the whole batch. Imported attempts get an `external-import` label, fingerprint, and classification; supplied cache data is attributed to the importer.

```sh
python scripts/skill_buffer.py import-responses --workspace "$RUN" --input "$RUN/responses.json"
```

**HTTP evaluation.** Authorize sending the frozen prompts and selected skill content. Set `CHAT_COMPLETIONS_ENDPOINT` to the full chat-completions URL and `MODEL_NAME` to the provider's model ID. The CLI sends a non-streaming request and reads `choices[0].message.content` as text. A `finish_reason` of `stop` is complete; `length` is truncated. Other response shapes or finish reasons stay unscored. Run:

```sh
python scripts/skill_buffer.py evaluate --workspace "$RUN" --endpoint "$CHAT_COMPLETIONS_ENDPOINT" --model "$MODEL_NAME"
```

Add `--api-key-env NAME` if authentication is required. The CLI reads only that credential variable, records its name, replaces literal matches of its value in stored records, and does not store the authorization header. Requests and responses can still contain sensitive content; choose what you send and where you store it. It rejects URL credentials, queries, fragments, and redirects. Use `--token-field max_completion_tokens` only when required; the CLI sends one token cap. Calls are sequential and alternate baseline/candidate order across pairs. The CLI saves sanitized requests, raw responses, parameters, and elapsed time. Missing/unsupported usage is `null`; supplied usage is unverified.

An HTTP transport failure writes `failures.json`, leaves the job unfinished, and exits `1`. After fixing the connection, repeat the same command with `--resume`: identical endpoint, model, credential-variable name, token field, settings, and frozen inputs. No automatic retries or replacement of completed attempts. Use a new workspace to rerun malformed/truncated responses or switch collection modes. Even a failed first HTTP request blocks imports; imported responses block HTTP.

### 4. Grade and compare

- **Routing only:** Save `{"version":1,"grades":[]}` as `$RUN/author-grades.json`. The only valid response shapes are `{"primary":"catalog-name"}` and `{"primary":null}`. A valid wrong choice scores zero; an unknown name, malformed shape, truncation, or transport error stays unscored. Older frozen prompts retain original scoring; freeze a fresh pair for no-match cases.
- **Procedure or mixed:** Use `{"version":1,"grades":[...]}`. Add one entry per valid procedure attempt for both variants, with its `job_id`, `case_id`, manifest `fingerprint`, and `response_sha256` (SHA-256 of the exact UTF-8 `response` string in `attempts.json`, not the file). Copy every assertion's `id` and `text` into `assertion_results`, add a Boolean `verdict`, and include one or more exact evidence quotes. For an omission, quote the relevant passage or the whole response and judge the omission yourself. See the [grading schema](schemas/contracts.json#/$defs/grading) and the complete grade file generated by the demo.

Example `assertion_results` entry for the bundled `procedure` case. Compute offsets on the decoded response: `start` is zero-based, `end` is exclusive, and both count Unicode characters, not bytes.

```json
{"id":"evidence","text":"States expected evidence.","verdict":false,"evidence":[{"source":"response","start":0,"end":17,"quote":"Check the parser."}]}
```

To get the hash and character count for a grade, replace `procedure:0:baseline` with its actual job ID:

```sh
python -c 'import hashlib,json,sys; r=next(a["response"] for a in json.load(open(sys.argv[1]))["attempts"] if a["job_id"]==sys.argv[2]); print(hashlib.sha256(r.encode("utf-8")).hexdigest(), len(r))' "$RUN/attempts.json" procedure:0:baseline
```

After saving `author-grades.json`, run:

```sh
python scripts/skill_buffer.py grade --workspace "$RUN" --input "$RUN/author-grades.json" --output "$RUN/grades.json"
python scripts/skill_buffer.py compare --workspace "$RUN" --input "$RUN/grades.json" --output "$RUN/report"
```

`grade` checks record identity, assertion coverage, and quote locations. You judge the verdicts. A nonempty, complete procedure response scores the fraction of passing assertions once graded. Check `$RUN/report/report.md` for critical failures, missing attempts/grades, invalid responses, telemetry, and provenance. It shows the transport failure count; `$RUN/report/report.json` has the detailed failure records. Only valid, scored pairs contribute to deltas; Markdown separates development and acceptance. A successful command can still report incomplete evidence.

## Revise and recheck

1. Export the brief from the completed assessment:

   ```sh
   ORIGINAL_RUN=$RUN
   python scripts/skill_buffer.py enhance brief --workspace "$ORIGINAL_RUN" --input "$ORIGINAL_RUN/grades.json" --output "$WORK/brief.json"
   ```

   `assessment_gaps` lists missing or invalid attempts and missing grades; repair or disclose these before drawing conclusions. `failures` contains scored development failures, response evidence, and relevant instructions. An empty list is not a pass if evidence or coverage is missing.
2. If authorized, copy the full frozen catalog to a new location outside the workspace to retain routing neighbors:

   ```sh
   cp -R "$ORIGINAL_RUN/snapshots/candidate" "$WORK/edited"
   ```

   Change only the copy. Keep working resources and existing `LICENSE`/`NOTICE` files intact. Save `$WORK/findings.json` with `{"version":1,"findings_addressed":["procedure:0:baseline"]}`, substituting unique development `finding_id` values from the brief. Then record:

   ```sh
   python scripts/skill_buffer.py enhance record --workspace "$ORIGINAL_RUN" --candidate "$WORK/edited" --input "$WORK/findings.json" --output "$WORK/revised"
   RUN=$WORK/revised
   ```

   `enhancement.json` records the claims and resource additions, removals, or changes, with text diffs or a marker for binary changes. The new workspace retains the original baseline, settings, and development cases. Recording a change does not prove it fixed a finding.
3. Repeat [collection](#3-collect-responses-choose-one-mode-per-workspace) and [grading/comparison](#4-grade-and-compare) with `$RUN` under the same model and collection conditions. Use the new manifest, attempts, grade identities, and output paths. Check the targeted failures and regressions before moving to acceptance.
4. Save fresh held-out cases in `$WORK/acceptance-suite.json`, each marked `acceptance`. Freeze against the settled revision using the same settings; extract them from the original manifest so this also works with overrides:

   ```sh
   python -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))["settings"]))' "$ORIGINAL_RUN/manifest.json" > "$WORK/frozen-settings.json"
   python scripts/skill_buffer.py freeze --baseline "$ORIGINAL_RUN/snapshots/baseline" --candidate "$RUN/snapshots/candidate" --suite "$WORK/acceptance-suite.json" --settings "$WORK/frozen-settings.json" --output "$WORK/acceptance"
   RUN=$WORK/acceptance
   ```

   Collect, grade, and compare again. Report held-out failures separately. Further revisions need fresh acceptance cases and output paths.

To hand this off to an agent, provide the target paths, intended behavior, assessment or revision scope, and permitted collection mode. Ask for cases, quoted evidence, report paths, and rechecks. No delegation or installation is required.

## Reference and limits

- [JSON contracts](schemas/contracts.json) use integer `version: 1`; the CLI enforces domain rules and rejects duplicate JSON/YAML keys. Skill YAML uses SafeLoader and supports block scalars. `name` and `description` must be nonempty; the name must match its lowercase hyphenated directory. Optional `metadata` must be a mapping.
- Inspection checks relative Markdown file links, not headings, URLs, or plain-text/backtick references. Inventory rejects symlinks inside input trees. Freeze requires a new, nonoverlapping workspace and copies resources and licenses without executing scripts. Exit `1` means structural findings or an HTTP transport stop; exit `2` means invalid input or I/O error. See each command's `--help`.
- `freeze --settings PATH` accepts JSON overrides. Defaults: `temperature: 0.6`, `seed: 42`, `max_tokens: 4096`, `repeats: 1`, `timeout: 300` seconds, `provider_parameters: {}`. Provider parameters cannot carry credentials, override core fields, or add token caps.
- Semantic grades and findings are author judgments. Simulations show proposed decisions, not native activation, tool execution, absence of writes, or host readiness. Mock HTTP tests do not prove provider compatibility. Unknown cache observations do not prove fresh inference.
- Inventories detect persistent changes only; hashes detect accidental changes, not adversarial manifest rewrites. The directory works as a standalone copy. Keep runtime workspaces and virtual environments outside the skill tree: Git ignore rules do not guarantee that a direct copy or `.skill` archive excludes them. Host integrations (including Pi) and automated grading/revision remain deferred. Skill Buffer does not install or publish the skills it assesses.
