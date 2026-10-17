# Lines' skills

Portable Agent Skills for planning, development, debugging, review, and verification, plus a meta skill for creating and evaluating skills. The collection follows three design goals:

1. **Single source, any harness.** Core instructions stay independent of platform integrations. Optional helpers declare their runtime and provider requirements; discovery depends on the client.
2. **Concrete instructions.** Skills provide ordered steps, failure branches, evidence records, and completion checks. Skills reuse supplied context and respect authorization. Performance across model sizes still needs separate evaluation.
3. **Follows my workflow.** These skills were 'written' based from my own development workflow - so if you happen to relate with how I do stuff, feel free to check these out.

## Skills

All skill folders live under `skills/`. Install individual folders; keep their internal references and helper paths relative to each skill root.

| Skill | Description |
|-------|-------------|
| [craft-skill](skills/craft-skill/SKILL.md) | Meta skill for creating Agent Skills. Three modes: **Extract** (capture from conversation history), **Design** (build from scratch), **Refine** (improve an existing skill). Includes a bundled eval and description-optimization pipeline. |
| [debug-systematically](skills/debug-systematically/SKILL.md) | Diagnose failures with evidence; apply and verify fixes only when authorized. |
| [design-modules](skills/design-modules/SKILL.md) | Assess or migrate ownership and interfaces using caller obligations, change locality, dependency-aware verification, and compatibility checks. |
| [execute-plan](skills/execute-plan/SKILL.md) | Execute and resume approved plans or established phased work inline, with optional check logs, handoffs, and Git review reports. |
| [plan-work](skills/plan-work/SKILL.md) | Turn requirements or an agreed design into dependency-ordered steps and acceptance checks. |
| [review-code](skills/review-code/SKILL.md) | Assess code, docs, and implementation plans against requirements; report findings and verify review feedback. |
| [strategize](skills/strategize/SKILL.md) | Clarify intent, compare viable approaches, and settle a buildable design before detailed planning; no visual companion or required tooling. |
| [test-first](skills/test-first/SKILL.md) | Develop behavior through red-green-refactor cycles, design diagnostic and isolated tests, and protect refactors with characterization coverage. |
| [verify-work](skills/verify-work/SKILL.md) | Check completion and readiness against requirements and evidence at the correct scope. |

The skills use inline execution, user-authorized Git actions, and checks scoped to the requirements.

## Selecting a workflow

Choose the primary skill by the result you need:

| Requested result | Primary skill |
| --- | --- |
| Settle an idea, approach, or feasibility question | `strategize` |
| Produce or revise an implementation plan | `plan-work` |
| Execute or resume an approved plan or established authorized phases | `execute-plan` |
| Establish the cause of a failure | `debug-systematically` |
| Assess or migrate ownership and interfaces | `design-modules` |
| Report defects or omissions in code, docs, or plans; evaluate review feedback | `review-code` |
| Implement specified behavior or an established correction | `test-first` |
| Establish completion or readiness against requirements | `verify-work` |
| Create, assess, refine, or package reusable skills | `craft-skill` |

Supporting checks do not restart the primary workflow or expand authorization. “Continue” retains the task but does not approve a plan; reviewing reports findings, while revising changes the plan. Prose uses document checks, and each skill stands alone. Clarify ambiguity with context or focused questions; domain/tool guidance can support any workflow. Specified changes and proven corrections proceed without restarting discovery or diagnosis, though an undecided correction may still need design.

Each skill's entry route gives required context, first action, and stop condition. The eight engineering skills also have compact route cards (condition, action/minimum evidence, stop or handoff) and optional hypothetical examples in `references/worked-examples.md`; scope and safety gates remain in `SKILL.md`. Branches cover existing implementations, assessment-only work, and unavailable runtimes. Authored examples are not checkout results; disposable fixtures prove only their observed scope. Activation and instruction-following require model/harness trials.

An unavailable host leaves acceptance unverified, not failed. Verification does not authorize fixes. Migrations start with coverage for affected consumers; extra plans/specs need purpose and writing authority. Under no-write scope, inspect checks for cache/output effects and use verified suppression, redirection, or disposable copies with explicit limits. Passing checks or unchanged Git status do not prove no writes.

## Working with `specs` and `plans`

Keep small tasks in conversation. Use specs for substantial designs and compatibility decisions, and plans for resumable, reviewable multi-phase work. Resume unfinished work in its existing record. Follow project locations and naming; otherwise use `YYYY-MM-DD-<descriptive-name>.md` for new files. The date is the creation date; don't rename or overwrite existing files to fit the convention. Local layout:

```text
.your/
  .gitignore   # contents: *
  specs/
    YYYY-MM-DD-<descriptive-name>.md
  plans/
    YYYY-MM-DD-<descriptive-name>.md
    .workflow/ # optional: execute-plan checkpoint helper storage
```

**Specs** record behavior, constraints, decisions, acceptance, and review state. **Plans** connect the design to delivery: steps, files, checks, progress, and gaps. Create the local layout only with writing authority, preserving ignore rules. Its wildcard ignores everything, including `.gitignore`, so recreate it in fresh checkouts; shared records can instead use a chosen tracked location. Selecting a skill does not authorize file creation/moves or Git changes, or override read-only scope.

Keep records concise without losing context or technical detail. Write shared context once: specs own behavior and decisions; plans link those decisions and track delivery; notes capture new observations; handoffs summarize results, evidence, and material gaps. Use bullets for parallel items, checklists for tracked work, numbered steps for required order, and prose for connected explanations. Omit empty fields and repeated summaries; link detailed evidence instead of copying logs. Close with outcome, actual acceptance, and remaining gaps; checked steps alone don't establish completion. Preserve closed records. Create a linked successor only when authorized and useful; keep small follow-ups inline and update living specs rather than creating competing contracts.

The optional `execute-plan` helper stores checkpoint JSON, snapshots, and check logs in `.workflow/` beside each plan. Manual tracking needs no helper; `status` creates no files. Each plan path has separate storage, and old checks don't verify new work. Put regression tests in project test directories and disposable probes in temporary workspaces. Ignored records remain inspectable and are not shipped documentation.

## How these came to be

The collection began with `opencraft-skill`, for extracting workflows from completed work, designing skills, and refining existing ones. Now it became `craft-skill`, retaining those three modes while making interviews, provider integrations, and isolated evaluation conditional.

The engineering set began as an exploration of my own workflows - literally written based from all my Pi and Codex sessions. These skills were focused on procedures grounded in actual development requests and corrections from those sessions - grabbing inspirations as well from obra's and mattpocock's.

### Writing methodology

1. **Start with observed work.** Ground instructions in user requests, corrections, project artifacts, and supported outcomes. Distinguish these from injected context, synthetic tasks, and unverified model claims.
2. **Define the result and scope.** Give each skill a focused responsibility, matching and neighboring trigger cases, required inputs, and side-effect boundaries. Assessment, design, planning, and authorized implementation stay distinct; existing decisions carry forward.
3. **Write procedures.** Put the route, inputs, first action, and stop condition near the top. Split consequential actions and state exceptions beside them. Separate internal inspection from required written output; adapt templates to the task while preserving contracts, acceptance, and material gaps. Keep paragraphs unwrapped. Use matching and neighboring examples where workflows overlap. Each skill works independently, with optional supporting guidance.
4. **Keep capabilities portable.** Base instructions on file access, commands, and runtime observations. Helpers handle justified deterministic work, declare their requirements, and retain manual fallbacks. Execution stays inline; Git actions need separate authority.
5. **Validate the claim.** Review normal, failure, and boundary cases. Distinguish author review from execution evidence. Metadata, references, packages, and helpers get separate checks. Activation and performance comparisons need controlled harness/model runs; without them, those claims remain unmeasured.
6. **Revise from evidence.** Tie changes to concrete failures or instruction gaps, update the relevant artifacts and docs, and repeat affected checks. Prefer coherent corrections over accumulating rules or adding files just to fit a layout.

## Using these skills

### Skills CLI (recommended)

You can run from this checkout:

```bash
npx skills add . --list
npx skills add . --skill '*' --agent codex --global

# Need help?
npx skills --help
```
or

```bash
# Browse available skills without installing
npx skills add linellazatin/skills --list

# Choose skills and agents interactively
npx skills add linellazatin/skills

# Install selected skills globally for Codex
npx skills add linellazatin/skills --skill plan-work execute-plan --agent codex --global

# Install all skills globally for Codex and Pi
npx skills add linellazatin/skills --skill '*' --agent codex pi --global

# Install all skills into the current project for Codex
npx skills add linellazatin/skills --skill '*' --agent codex
```

Project scope is the default; `--global` selects user scope. For Codex and Pi, these locations are `.agents/skills/` and `~/.agents/skills/`. Agent-directory symlinks share a canonical installation; add `--copy` for independent copies. Use `--skill '*'` to select all skills while retaining explicit agent selection; `--all` also selects all agents and skips prompts. A detected harness may select non-interactive installation, so specify `--skill` and `--agent` when the destination matters.

### Direct copy

1. Copy the skill directory (e.g. `skills/craft-skill/`) into your agent's skills directory.
   - Use `~/.agents/skills/<skill-name>/SKILL.md` when your harness supports that shared location.
   - Otherwise use your client's documented skill directory.
2. Start a session and select the skill explicitly, or use your harness's automatic selection if supported.

### Symlink

Keep the checkout outside the client's installed skill folders, then symlink each selected folder into them. For example, clone beside `~/.agents/skills/`:

```bash
git clone https://github.com/linellazatin/skills.git
ln -s /path/to/checkout/skills/plan-work ~/.agents/skills/plan-work
```

Use your client's documented location if it differs. Keep the checkout in place while its symlinks are installed. For other paths:

```bash
# macOS / Linux
ln -s /path/to/checkout/skills/skill-name /path/to/client/skills/skill-name
```

```cmd
:: Windows
mklink /d "X:\client\skills\skill-name" "X:\checkout\skills\skill-name"
```

### Bundled tooling tiers

Bundled helpers have two tiers:

**Tier 1: standard-library Python (command execution required):**

- `skills/craft-skill/scripts/quick_validate.py` checks supported metadata and structure, not full YAML/spec validity or behavior.
- `skills/craft-skill/scripts/aggregate_benchmark.py` aggregates eval results into a report.
- `skills/craft-skill/scripts/package_skill.py` creates a distributable `.skill` ZIP.
- `skills/execute-plan/scripts/checkpoints.py` requires Python 3.9+ and provides `status`, `start`, `check`, `reconcile`, `handoff`, and `review`. Snapshots and bounded diffs allow explicitly attested progress-only reconciliation when check inputs are unchanged; material changes require restarting and rerunning checks. Attestation is not proof of checkout freshness or approval. Only `review` needs Git; it disables optional locks and diff index refresh, but writes authorized local report/workflow files. It is not a no-file command. See [usage and evidence limits](skills/execute-plan/references/checkpoints.md). No agent API, shell, or provider is required; without Python, follow the skill manually.

**Tier 2: optional harness/provider integrations:**

- `skills/craft-skill/scripts/run_eval.py` uses Claude Code CLI and a temporary command surrogate for trigger evaluation.
- `skills/craft-skill/scripts/improve_description.py` proposes descriptions via Anthropic, an OpenAI-compatible endpoint, or Claude Code CLI.
- `skills/craft-skill/scripts/run_loop.py` runs configurable train/validation optimization; evaluation requires Claude Code CLI, improvement a supported provider.

`improve_description.py` detects `ANTHROPIC_API_KEY`, then `OPENAI_API_KEY`, then `claude -p`; `OPENAI_API_BASE` selects the compatible endpoint. Trigger scores don't prove full execution or activation in other harnesses. Execution errors are unscored and block optimization. Helper paths are checkout-relative; resolve them when running elsewhere. Validation and packaging use standard-library Python; evaluation is optional.

## Unreleased - On-going Tests

Prototypes live under `tests/unreleased/`, outside the installable skill collection.

| Prototype | Scope and status |
| --- | --- |
| [Skill Buffer](tests/unreleased/skill-buffer/README.md) | Portable wrapper and Python 3.13+/PyYAML 6.0.3 CLI for inspection, frozen paired evaluation, response imports, evidence-backed author grading, comparison and separate candidate revisions. Includes 20 offline/mock-HTTP tests and a synthetic walkthrough; native activation, tool execution, automatic grading/revision, installation and publishing are deferred. |

## References

### What are Agent Skills?

Agent Skills are plain Markdown files (`SKILL.md`) that give AI agents reusable, specialized behavior. A skill lives in a named directory and is loaded by the agent when a task matches its description.

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── agents/           # Optional: subagent instruction files
├── scripts/          # Optional: executable helpers
├── references/       # Optional: reference docs loaded on demand
└── assets/           # Optional: templates, resources
```

The format is an open standard. The spec and guides are available in [`docs/guides/`](docs/guides/).

- [`docs/guides/agentskills-guide.md`](docs/guides/agentskills-guide.md) - full guide (overview, spec, quickstart, best practices, evals, description optimization, scripts, client implementation)
- [agentskills.io](https://agentskills.io) - upstream standard
