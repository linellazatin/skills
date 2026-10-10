# Lines' skills

Portable Agent Skills for planning, development, debugging, review, and verification, plus a meta skill for creating and evaluating skills. The collection follows two design goals:

1. **Single source, any harness.** Core instructions stay independent of platform integrations. Optional helpers declare their runtime and provider requirements; discovery depends on the client.
2. **Concrete instructions.** Skills provide ordered steps, failure branches, evidence records, and completion checks. Skills reuse supplied context and respect authorization. Performance across model sizes still needs separate evaluation.
3. **Follows my workflow.** These skills were 'written' based from my own development workflow - so if you happen to relate with how I do stuff, feel free to check these out.

## Skills

All skill folders live under `skills/`. Install individual folders; keep their internal references and helper paths relative to each skill root.

| Skill | Description |
|-------|-------------|
| [craft-skill](skills/craft-skill/SKILL.md) | Meta skill for creating Agent Skills. Three modes: **Extract** (capture from conversation history), **Design** (build from scratch), **Refine** (improve an existing skill). Includes a bundled eval and description-optimization pipeline. |
| [debug-systematically](skills/debug-systematically/SKILL.md) | Reproduce the actual symptom, isolate its cause, and verify the fix. |
| [design-modules](skills/design-modules/SKILL.md) | Assess or migrate ownership and interfaces using caller obligations, change locality, dependency-aware verification, and compatibility checks. |
| [execute-plan](skills/execute-plan/SKILL.md) | Execute and resume approved plans or established phased work inline, with optional check logs, handoffs, and Git review reports. |
| [plan-work](skills/plan-work/SKILL.md) | Turn requirements into a scoped design and executable tasks with acceptance checks. |
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

Testing, diagnosis, review, and verification can support the primary workflow without restarting it or expanding authorization. “Continue” retains the established task; it does not establish plan approval. Reviewing a plan reports findings; revising it changes the plan. Prose-only work uses document checks rather than software test cycles. Each skill stands alone.

Entry routes state required context, first actions, and stop conditions. Matching and neighboring examples clarify overlaps; conditional branches cover existing implementation, assessment-only work, and unavailable runtimes. These changes target instruction clarity for small and medium models. Actual activation and instruction-following performance require model/harness trials; authored walkthroughs do not establish those results.

An unavailable host leaves its acceptance check unverified; it does not establish a product failure. Verification alone does not authorize fixes. Migration starts with coverage for affected consumers, and an extra plan or spec needs both a concrete purpose and writing authority.

## Working specs and plans

Keep small, clear, single-session work inline. Use written specs for substantial designs, consequential decisions, or compatibility obligations. Use written plans for substantial, multi-phase, resumable, or reviewable implementation when file writing is authorized. Update existing artifacts first and follow the project's established or requested location. The local fallback is:

```text
.your/
  .gitignore   # contents: *
  specs/
  plans/
```

Specs capture behavior, constraints, decisions, acceptance criteria, and review state. Plans link the governing spec and track execution order, affected paths, checks, phase status, deviations, evidence, and gaps. On first authorized use, the skills create missing directories and the wildcard ignore file, preserving existing ignore rules. The wildcard ignores `.gitignore` too, so fresh checkouts need this local setup recreated. For versioned collaboration, use a requested tracked location. Invoking a skill does not authorize migration, Git actions, or files prohibited by an assessment-only or no-file request.

Keep regression tests in the project's test directories and disposable probes in temporary workspaces. No default `.your/tests/` is needed. The optional execution helper stores `.workflow/` beside the selected plan: `.your/plans/.workflow/` with this layout. Ignored artifacts need direct inspection when in scope; shipped documentation stays separate.

## How these came to be

The collection began with `opencraft-skill`, for extracting workflows from completed work, designing skills, and refining existing ones. Now it became `craft-skill`, retaining those three modes while making interviews, provider integrations, and isolated evaluation conditional.

The engineering set began as an exploration of my own workflows - literally written based from all my Pi and Codex sessions. These skills were focused on procedures grounded in actual development requests and corrections from those sessions - grabbing inspirations as well from obra's and mattpocock's.

### Writing methodology

1. **Start with observed work.** Ground instructions in user requests, corrections, project artifacts, and supported outcomes. Distinguish these from injected context, synthetic tasks, and unverified model claims.
2. **Define the result and scope.** Give each skill a focused responsibility, matching and neighboring trigger cases, required inputs, and side-effect boundaries. Assessment, design, planning, and authorized implementation stay distinct; existing decisions carry forward.
3. **Write procedures.** Put the route, inputs, first action, and stop condition near the top. Split consequential actions and state exceptions beside the affected steps. Use matching and neighboring examples where workflows overlap. Each skill works independently, with optional supporting guidance.
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

Bundled helpers fall into two tiers:

**Tier 1: standard-library Python, with command execution:**

- `skills/craft-skill/scripts/quick_validate.py` - check supported metadata and structural constraints; not a complete YAML/spec or behavioral validator
- `skills/craft-skill/scripts/aggregate_benchmark.py` - aggregate eval results into a benchmark report
- `skills/craft-skill/scripts/package_skill.py` - zip a skill into a distributable `.skill` file

`skills/execute-plan/scripts/checkpoints.py` requires Python 3.9+ standard library and provides `status`, `start`, `check`, `handoff`, and `review`. Only `review` requires Git. See [helper usage and evidence limits](skills/execute-plan/references/checkpoints.md). It works without a particular agent API, shell, or provider; environments without Python can follow the skill manually.

**Tier 2: optional harness/provider integrations:**

- `skills/craft-skill/scripts/run_eval.py` - Claude Code CLI trigger evaluation using a temporary command surrogate
- `skills/craft-skill/scripts/improve_description.py` - description proposals using Anthropic, an OpenAI-compatible endpoint, or Claude Code CLI
- `skills/craft-skill/scripts/run_loop.py` - configurable train/validation optimization loop; requires Claude Code CLI for evaluation and a supported provider for improvement

Provider detection for `improve_description.py`: `ANTHROPIC_API_KEY` → `OPENAI_API_KEY` → `claude -p` fallback. `OPENAI_API_BASE` selects the OpenAI-compatible endpoint. Trigger scores do not establish full skill execution or activation in other harnesses. Execution errors are unscored and block optimization. Paths above are relative to the checkout; resolve absolute helper paths when running from another directory. Validation and packaging use only standard-library Python; evaluation is optional.

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
