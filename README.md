# Lines' skills

I put these Agent Skills together from my own development workflow. They cover repository inspection, planning, development, debugging, review, and verification. The collection also includes skills for writing and evaluating other skills.

The same instructions work without platform integrations. Your client handles discovery, and each optional helper lists the runtime and provider it needs. The skills tell you what to do in order, what to check when a step fails, and what evidence to record before calling the work done. They use the context and permissions you already have. How well they work across model sizes still needs testing.

## Skills

Install the folders you need from `skills/`. Keep references and helper paths relative to each skill's own folder.

| Skill | Description |
|-------|-------------|
| [craft-skill](skills/craft-skill/SKILL.md) | Three modes: Extract from conversation history, Design from scratch, and Refine an existing skill. Includes tools for evaluation and description optimization. |
| [skill-buffer](skills/skill-buffer/SKILL.md) | Assess an existing skill against realistic cases, compare revisions, and turn findings into a focused candidate change and recheck. [Usage guide](skills/skill-buffer/README.md). |
| [strategize](skills/strategize/SKILL.md) | Clarify intent, compare viable approaches, and settle a buildable design before detailed planning; no visual companion or required tooling. |
| [plan-work](skills/plan-work/SKILL.md) | Break requirements or an agreed design into phases sized to the work. Order the steps, define checks and reassessment, and record when to ask for approval or commit. |
| [design-modules](skills/design-modules/SKILL.md) | Assess or migrate ownership and interfaces using caller obligations, change locality, dependency-aware verification, and compatibility checks. |
| [execute-plan](skills/execute-plan/SKILL.md) | Run or resume authorized phases. Reassess the work, fix findings, and keep pending approvals in place. Record evidence if needed. |
| [inspect-code](skills/inspect-code/SKILL.md) | Map a repository's structure, entry points, and tests from source. Use scc for measurements and get a reading map. Trace behavior, look for maintenance candidates, or map dependencies if needed. Static and read-only by default. |
| [review-code](skills/review-code/SKILL.md) | Assess code, docs, plans, and completed phases against requirements; report findings and evaluate feedback without granting phase acceptance. |
| [debug-systematically](skills/debug-systematically/SKILL.md) | Diagnose failures with evidence; apply and verify fixes only when authorized. |
| [test-first](skills/test-first/SKILL.md) | Develop behavior through red-green-refactor cycles, design diagnostic and isolated tests, and protect refactors with characterization coverage. |
| [verify-work](skills/verify-work/SKILL.md) | Check scoped readiness against current evidence; distinguish required gaps, explicit user deferrals, and user acceptance. |

Work inline, run only the checks the task calls for, and get permission before taking Git actions.

## Selecting a workflow

Choose the primary skill by the result you need:

| Requested result | Primary skill |
| --- | --- |
| Understand a repository, measure composition, or map a focused code path/dependency | `inspect-code` |
| Settle an idea, approach, or feasibility question | `strategize` |
| Produce or revise an implementation plan | `plan-work` |
| Execute or resume an approved plan or established authorized phases | `execute-plan` |
| Establish the cause of a failure | `debug-systematically` |
| Assess or migrate ownership and interfaces | `design-modules` |
| Report defects or omissions in code, docs, or plans; evaluate review feedback | `review-code` |
| Implement specified behavior or an established correction | `test-first` |
| Establish completion or readiness against requirements | `verify-work` |
| Create, extract, rewrite, validate, or package a reusable skill | `craft-skill` |
| Assess an existing skill against cases, compare revisions, or recheck a fix | `skill-buffer` |

1. Confirm what the user wants. Ask a focused question if context doesn't settle it. Reviewing a plan produces findings; revising it changes the plan. Implement specified changes and proven fixes directly. If the fix is undecided, design it first. A bare "continue" resumes the task without approving a plan. If approval is pending, read the reply in that context.
2. Open `SKILL.md` for the inputs, first action, and stopping point. The original eight engineering skills have route cards with the condition, minimum action or evidence, and when to stop or hand off. They also have optional, hypothetical examples in `references/worked-examples.md`. Check for branches covering existing implementations, assessment-only work, and unavailable runtimes. Follow the scope and safety rules in `SKILL.md`.
3. Use each skill on its own. Bring in domain guidance or supporting checks when useful, within the same workflow and permissions. Reuse traces and measurements: `inspect-code` maps what exists and suggests where to look; `review-code` reports failures against a contract. Complexity and churn aren't evidence of a defect on their own.
4. Check prose as documentation. Before a migration, cover the affected consumers. If writes are off-limits, check for caches and outputs; verify they're suppressed, redirected, or confined to a disposable copy. Green checks or a clean Git status don't prove there were no writes. Fixture results cover only the behavior you observed. Test activation and instruction-following on the model and harness. If the host is unavailable, leave acceptance unverified. Verification gives no permission to fix the work.

### Phases, reassessment, and approval

1. Use `plan-work` to define the outcome, dependencies, checks, and when approval is needed. One phase is enough for a bounded change. Add parts or steps only if they help, and keep phase IDs stable when revising what's left.
2. Use `execute-plan` to do the authorized work and check its real consumers. If you're resuming, find the pending gates and the next action you're allowed to take. Run technical checks like red/green without waiting for human approval unless asked to wait.
3. Use `review-code` for findings and `verify-work` to check which requirements have current evidence. Fix supported findings within scope, rerun the checks they affect, and update any assumptions the fix changes for later phases. TDD, diagnosis, and migration checks don't replace the phase gate.
4. Update the affected docs and active plan. Record the evidence, what happened to each finding, what's still open, and what to do next.
5. Stop for completion approval if required. If the user authorized the full run, continue. Starting approval, green checks, a review with no findings, or a helper handoff don't grant acceptance. If the user explicitly defers some work or accepts a narrower scope, leave the omitted work unverified.

Commit only with separate permission and within the requested timing and file scope. Leave out withheld tests or docs and unrelated changes. Permission to update docs isn't permission to commit them. A research phase needs no empty commit. The [worked examples](skills/execute-plan/references/worked-examples.md#completion-approval-before-commit) show both approval-gated and full runs. They don't enforce gates or prove that a model follows them.

## Working with `specs` and `plans`

1. Keep small tasks in the conversation. Write a spec for a substantial design or compatibility decision. Use a plan for work that spans phases and needs to be reviewed or resumed. Pick up an unfinished record where you left off. Create or move files only when you have a reason and permission. Selecting a skill doesn't change write or Git permissions.
2. Follow the project's naming and location conventions. For shared records, agree on a tracked location. Use the creation date for new files without renaming or overwriting old ones to fit. Keep existing ignore rules. In a fresh checkout, recreate the local `.gitignore` because `*` ignores the file itself.

   ```text
   .your/
     .gitignore   # contents: *
     specs/
       YYYY-MM-DD-<descriptive-name>.md
     plans/
       YYYY-MM-DD-<descriptive-name>.md
       .workflow/ # optional: execute-plan checkpoint helper storage
   ```

3. Put behavior, constraints, decisions, acceptance, and review state in the spec. Link those decisions from the plan and track steps, files, checks, progress, and gaps there. Put new observations in notes. Use handoffs to summarize results, evidence, and gaps that matter. Use bullets for parallel items, checklists to track progress, numbers when order matters, and prose to explain. Link to evidence instead of copying logs. Leave out empty fields and repeated context.
4. Track checkpoints by hand or use the optional `execute-plan` helper. It stores JSON, snapshots, and check logs in `.workflow/` beside the plan, with separate storage for each plan path. `status` writes nothing. The helper keeps one phase active without enforcing approval of earlier phases. Keep acceptance and allowed next actions in the plan, and run fresh checks for new work.
5. When closing a record, say what happened, what the user accepted, and what's still open. A checked list alone doesn't establish completion. Leave closed records alone. Link a successor only when it's useful and authorized. Keep small follow-ups in the conversation, and update living specs so there's one contract to follow.

Keep regression tests in project test directories and disposable probes in temporary workspaces. Ignored records remain inspectable and do not ship.

## How these came to be

The collection started with `opencraft-skill`. I used it to pull workflows from finished work, design new skills, and improve the ones I had. It became `craft-skill` and kept those three modes. Interviews, provider integrations, and isolated evaluation are used when needed.

I wrote the engineering skills from my own Pi and Codex sessions, using the requests I made and the corrections that came up during development. I also took ideas from obra and mattpocock.

### Writing methodology

1. Base instructions on user requests, corrections, project artifacts, and outcomes you can support. Keep injected context, synthetic tasks, and unverified model claims separate from that evidence.
2. Give the skill one responsibility. Say what should trigger it, which similar requests belong elsewhere, what inputs it needs, and what it can change. Keep assessment, design, planning, and authorized implementation distinct. Carry existing decisions forward.
3. Put the route, inputs, first action, and stopping point near the top. Give consequential actions their own steps, with exceptions beside them. Separate what to inspect from what to write. Adapt templates to the task without dropping contracts, acceptance conditions, or material gaps. Keep paragraphs unwrapped. Where workflows overlap, show a matching request and a neighboring one. Each skill must work without its optional supporting guidance.
4. Write for file access, command execution, and runtime observations. Use helpers for deterministic work where they pay off. List their requirements and keep a manual fallback. Work inline and get separate permission for Git actions.
5. Check normal use, failures, and boundaries. Look at the order of actions and what the workflow withholds at a gate as well as what the report says. Distinguish author review from execution evidence, and check metadata, references, packages, and helpers separately. Until you run controlled model and harness trials, activation and relative performance remain unmeasured.
6. Tie each change to a failure or a gap in the instructions. Update the affected artifacts and docs, then rerun the relevant checks. Fix the underlying issue before adding rules or files just to fit a layout.

## Using these skills

### Skills CLI (recommended)

Run these commands from the checkout:

```bash
npx skills add . --list
npx skills add . --skill '*' --agent codex --global

# Need help?
npx skills --help
```

To install from the remote repository, use the commands below. They do not include local changes; use the checkout commands to try work that has not been pushed.

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

The default is project scope. Use `--global` for user scope. For Codex and Pi, the two locations are `.agents/skills/` and `~/.agents/skills/`, respectively. Agent-directory symlinks point to one shared installation. Add `--copy` if you need independent copies.

Use `--skill '*'` for all skills on the agents you select. `--all` selects every agent too and skips prompts. The installer can detect a harness and run without prompting, so set `--skill` and `--agent` when you need a specific destination.

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

`inspect-code` uses an available [scc executable](skills/inspect-code/references/scc.md) for measurements. Without it, you can still map the repository from source, without metrics. Install scc separately if you need it; the skill never installs it. Git history analysis is optional. By default, the skill doesn't run project code, tests, or builds.

**Tier 1: Standard-library Python (command execution required)**

- `skills/craft-skill/scripts/quick_validate.py` checks supported metadata and structure, not full YAML/spec validity or behavior.
- `skills/craft-skill/scripts/aggregate_benchmark.py` aggregates eval results into a report.
- `skills/craft-skill/scripts/package_skill.py` creates a distributable `.skill` ZIP.
- `skills/execute-plan/scripts/checkpoints.py` requires Python 3.9+ and provides `status`, `start`, `check`, `reconcile`, `handoff`, and `review`. Use snapshots and bounded diffs to reconcile progress-only plan edits with explicit attestation and unchanged check inputs. For material plan changes, restart and rerun required checks. If only checked inputs changed, rerun the affected checks instead of relying on old results. Attestation doesn't prove the checkout is current or the work approved. Only `review` needs Git. It disables optional locks and diff index refresh, and writes authorized local report and workflow files. See [usage and evidence limits](skills/execute-plan/references/checkpoints.md). You don't need an agent API, shell, or provider. If Python isn't available, follow the skill manually.

**Tier 2: Optional harness and provider integrations**

- `skills/craft-skill/scripts/run_eval.py` uses Claude Code CLI and a temporary command surrogate for trigger evaluation.
- `skills/craft-skill/scripts/improve_description.py` proposes descriptions via Anthropic, an OpenAI-compatible endpoint, or Claude Code CLI.
- `skills/craft-skill/scripts/run_loop.py` runs configurable train/validation optimization; evaluation requires Claude Code CLI, improvement a supported provider.

`improve_description.py` looks for `ANTHROPIC_API_KEY`, then `OPENAI_API_KEY`, then `claude -p`. Use `OPENAI_API_BASE` to select the compatible endpoint. Trigger scores don't tell you whether the skill completes the task or activates in another harness. `run_eval.py` leaves execution errors unscored, and `run_loop.py` stops optimization when they occur. Resolve helper paths against the checkout if you run them from elsewhere. You can validate and package with standard-library Python without running evaluation.

To review a skill with Skill Buffer, you only need file access. Its [optional CLI](skills/skill-buffer/README.md#cli-setup) needs Python 3.13+ and PyYAML 6.0.3. For frozen paired simulations, import responses or supply an HTTP endpoint. Neither option ties you to a specific harness.

## References

### What are Agent Skills?

Agent Skills are plain Markdown files (`SKILL.md`) that give AI agents reusable, specialized behavior. A skill lives in a named directory. Clients that support automatic selection use its description to decide when to load it.

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── agents/           # Optional: subagent instruction files
├── scripts/          # Optional: executable helpers
├── references/       # Optional: reference docs loaded on demand
└── assets/           # Optional: templates, resources
```

Agent Skills use an open standard. Read the spec and guides in [`docs/guides/`](docs/guides/).

- [`docs/guides/agentskills-guide.md`](docs/guides/agentskills-guide.md): overview, spec, quickstart, best practices, evals, description optimization, scripts, and client implementation.
- [agentskills.io](https://agentskills.io): upstream standard.
