# Best Practices for Skill Creators

> Source: https://agentskills.io/skill-creation/best-practices.md

How to write skills that are well-scoped and calibrated to the task.

---

## Start from Real Expertise

A common pitfall: asking an LLM to generate a skill without providing domain-specific context. The result is vague, generic procedures rather than the specific API patterns, edge cases, and project conventions that make a skill valuable.

**Effective skills are grounded in real expertise.**

### Extract from a Hands-on Task

Complete a real task in conversation with an agent, providing context, corrections, and preferences along the way. Then extract the reusable pattern into a skill. Pay attention to:

- **Steps that worked** — the sequence of actions that led to success
- **Corrections you made** — places where you steered the agent's approach (e.g., "use library X instead of Y," "check for edge case Z")
- **Input/output formats** — what the data looked like going in and coming out
- **Context you provided** — project-specific facts, conventions, or constraints the agent didn't already know

### Synthesize from Existing Project Artifacts

When you have a body of existing knowledge, feed it into an LLM and ask it to synthesize a skill. A data-pipeline skill synthesized from your team's actual incident reports and runbooks will outperform one from a generic article — because it captures *your* schemas, failure modes, and recovery procedures.

Good source material:
- Internal documentation, runbooks, and style guides
- API specifications, schemas, and configuration files
- Code review comments and issue trackers (captures recurring concerns)
- Version control history, especially patches and fixes
- Real-world failure cases and their resolutions

---

## Refine with Real Execution

The first draft of a skill usually needs refinement. Run the skill against real tasks, then feed the results — all of them, not just failures — back into the creation process. Ask: what triggered false positives? What was missed? What could be cut?

Even a single pass of execute-then-revise noticeably improves quality.

> **Tip**: Read agent execution traces, not just final outputs. If the agent wastes time on unproductive steps, common causes are: instructions too vague (agent tries several approaches), instructions that don't apply to the current task (agent follows them anyway), or too many options without a clear default.

For a structured approach, see [Evaluating Skill Output Quality](04-evaluating-skills.md).

---

## Spending Context Wisely

Once a skill activates, its full `SKILL.md` body loads into the agent's context window alongside conversation history, system context, and other active skills. Every token competes for the agent's attention.

### Add What the Agent Lacks, Omit What It Knows

Focus on what the agent *wouldn't* know without your skill: project-specific conventions, domain-specific procedures, non-obvious edge cases, the particular tools or APIs to use. You don't need to explain what a PDF is, how HTTP works, or what a database migration does.

```markdown
<!-- Too verbose — the agent already knows what PDFs are -->
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. pdfplumber is recommended because it handles most cases well.

<!-- Better — jumps straight to what the agent wouldn't know on its own -->
## Extract PDF text

Use pdfplumber for text extraction. For scanned documents, fall back to
pdf2image with pytesseract.

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

Ask yourself about each piece of content: "Would the agent get this wrong without this instruction?" If no, cut it.

### Design Coherent Units

Deciding what a skill should cover is like deciding what a function should do: encapsulate a coherent unit of work that composes well. Skills scoped too narrowly force multiple skills to load for a single task. Skills scoped too broadly become hard to activate precisely.

### Aim for Moderate Detail

Overly comprehensive skills can hurt — the agent struggles to extract what's relevant and may pursue unproductive paths triggered by instructions that don't apply to the current task. Concise, stepwise guidance with a working example tends to outperform exhaustive documentation.

### Structure Large Skills with Progressive Disclosure

Keep `SKILL.md` under 500 lines and 5,000 tokens — just the core instructions the agent needs on every run. Move detailed reference material to `references/` or similar directories.

Tell the agent *when* to load each file:

> "Read `references/api-errors.md` if the API returns a non-200 status code"

is more useful than a generic:

> "see references/ for details"

---

## Calibrating Control

Not every part of a skill needs the same level of prescriptiveness. Match specificity to fragility.

### Give the Agent Freedom for Flexible Tasks

When multiple approaches are valid, explaining *why* can be more effective than rigid directives:

```markdown
## Code review process

1. Check all database queries for SQL injection (use parameterized queries)
2. Verify authentication checks on every endpoint
3. Look for race conditions in concurrent code paths
4. Confirm error messages don't leak internal details
```

### Be Prescriptive for Fragile Operations

```markdown
## Database migration

Run exactly this sequence:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
```

### Provide Defaults, Not Menus

When multiple tools or approaches could work, pick a default and mention alternatives briefly:

```markdown
<!-- Too many options -->
You can use pypdf, pdfplumber, PyMuPDF, or pdf2image...

<!-- Clear default with escape hatch -->
Use pdfplumber for text extraction:

```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Favor Procedures over Declarations

A skill should teach the agent *how to approach* a class of problems, not *what to produce* for a specific instance:

```markdown
<!-- Specific answer — only useful for this exact task -->
Join the `orders` table to `customers` on `customer_id`, filter where
`region = 'EMEA'`, and sum the `amount` column.

<!-- Reusable method — works for any analytical query -->
1. Read the schema from `references/schema.yaml` to find relevant tables
2. Join tables using the `_id` foreign key convention
3. Apply any filters from the user's request as WHERE clauses
4. Aggregate numeric columns as needed and format as a markdown table
```

---

## Patterns for Effective Instructions

### Gotchas Sections

The highest-value content in many skills is a list of gotchas — environment-specific facts that defy reasonable assumptions:

```markdown
## Gotchas

- The `users` table uses soft deletes. Queries must include
  `WHERE deleted_at IS NULL` or results will include deactivated accounts.
- The user ID is `user_id` in the database, `uid` in the auth service,
  and `accountId` in the billing API. All three refer to the same value.
- The `/health` endpoint returns 200 as long as the web server is running,
  even if the database connection is down. Use `/ready` to check full
  service health.
```

Keep gotchas in `SKILL.md` where the agent reads them before encountering the situation.

> **Tip**: When an agent makes a mistake you have to correct, add the correction to the gotchas section. This is one of the most direct ways to improve a skill iteratively.

### Templates for Output Format

When you need the agent to produce output in a specific format, provide a template:

```markdown
## Report structure

Use this template, adapting sections as needed for the specific analysis:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
```

Short templates live inline in `SKILL.md`; longer templates go in `assets/` and are referenced when needed.

### Checklists for Multi-Step Workflows

An explicit checklist helps the agent track progress and avoid skipping steps:

```markdown
## Form processing workflow

Progress:
- [ ] Step 1: Analyze the form (run `scripts/analyze_form.py`)
- [ ] Step 2: Create field mapping (edit `fields.json`)
- [ ] Step 3: Validate mapping (run `scripts/validate_fields.py`)
- [ ] Step 4: Fill the form (run `scripts/fill_form.py`)
- [ ] Step 5: Verify output (run `scripts/verify_output.py`)
```

### Validation Loops

Instruct the agent to validate its own work before moving on:

```markdown
## Editing workflow

1. Make your edits
2. Run validation: `python scripts/validate.py output/`
3. If validation fails:
   - Review the error message
   - Fix the issues
   - Run validation again
4. Only proceed when validation passes
```

### Plan-Validate-Execute

For batch or destructive operations, have the agent create a plan, validate it, and only then execute:

```markdown
## PDF form filling

1. Extract form fields: `python scripts/analyze_form.py input.pdf` → `form_fields.json`
2. Create `field_values.json` mapping each field name to its intended value
3. Validate: `python scripts/validate_fields.py form_fields.json field_values.json`
4. If validation fails, revise `field_values.json` and re-validate
5. Fill the form: `python scripts/fill_form.py input.pdf field_values.json output.pdf`
```

The key ingredient is step 3: a validation script that checks the plan against the source of truth, providing actionable error messages the agent can self-correct from.

### Bundling Reusable Scripts

When iterating on a skill, compare execution traces across test cases. If the agent independently reinvents the same logic each run — building charts, parsing a specific format, validating output — write a tested script once and bundle it in `scripts/`.

See [Using Scripts in Skills](06-using-scripts.md) for details.

---

## Next Steps

- **[Evaluating skill output quality](04-evaluating-skills.md)** — Set up test cases, grade results, and iterate systematically.
- **[Optimizing skill descriptions](05-optimizing-descriptions.md)** — Test and improve your skill's `description` field so it triggers on the right prompts.
