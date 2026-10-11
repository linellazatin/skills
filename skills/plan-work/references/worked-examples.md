# Worked plans

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Shared-contract migration

- **Request:** “Plan the agreed policy migration, preserving public behavior. Keep the plan inline; do not implement.”
- **Given evidence:** In this fixture, `core/policy.py` is the agreed owner; `cli.py`, `adapter_a.py`, and `adapter_b.py` consume the rule. Adapter B lacks boundary characterization. Existing entrypoints must remain compatible, and installation docs describe the old ownership.
- **Decision and action:** Plan characterization for all three consumers before moving policy, especially B's uncovered boundary. Then change the shared owner, migrate each caller's conversion/invocation, retain public forwarding where required, and check final packaging/docs. Give every requirement a phase, path, prerequisite, and observable check using inspected project commands. An unavailable host check remains pending with setup identified.
- **Result and limit:** The plan contains implementation and consumer migration steps even though execution is unauthorized. It identifies all three consumers, required checks, and affected docs. Nothing has been implemented or verified merely because those steps are written.

## Unconfirmed integration command

- **Request:** “Plan integrating this CLI with our adapter. Do not change files.”
- **Given evidence:** The desired operation is known, but the installed CLI's flags and output contract are not confirmed. A proposed command in an old note is not evidence that it works.
- **Decision and action:** First inspect the installed help and version and replay a representative invocation in an authorized disposable setup. Schedule payload/exit-status inspection before adapter implementation. Mark downstream tasks dependent on that result; do not invent a `--json` flag or promise a correction for an unconfirmed cause.
- **Result and limit:** Return a provisional integration phase with a named investigation and expected observation. The exact invocation stays unresolved until inspected; the plan does not claim a passing integration check.

## Successor after closure

- **Request:** “Plan the next substantial migration; the earlier migration was completed and accepted in another session. Save a local plan.”
- **Given evidence:** The old task plan records its accepted outcome; a new migration scope is authorized. No project naming convention overrides the fallback.
- **Decision and action:** Create `.your/plans/YYYY-MM-DD-next-migration.md` using today's creation date and link the old plan. Preserve the predecessor and its evidence; do not append the new migration to it or copy its check results as current verification. Keep the successor focused on actionable phases, acceptance checks, blockers, and evidence links.
- **Result and limit:** The new work has its own concise plan. If required old acceptance were still unresolved, it would not be closed merely because its steps were checked. A small follow-up would stay inline instead of forcing a new file.

## Inline document plan

- **Request:** “Plan a README rewrite inline. No files or software changes.”
- **Given evidence:** Only installation wording and local links are affected. No behavior, release, or host requirement changed.
- **Decision and action:** Give a short sequence: inspect current instructions, rewrite within the stated scope when authorized, compare commands with their implementation, and resolve affected links. Use document checks rather than a software failing-test cycle.
- **Result and limit:** Deliver the inline plan and stop. Do not create `.your/` artifacts, alter the README during planning, or add unrelated host acceptance gates.
