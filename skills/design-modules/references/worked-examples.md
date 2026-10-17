# Worked ownership decisions

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Shared rule and host boundaries

- **Request:** “Assess CLI and adapter policy owners; no refactor.”
- **Given evidence:** CLI and adapter independently implement the same documented byte cap and error condition. Changing that rule currently requires two edits. The adapter additionally converts host payloads and registers reload callbacks; CLI argument parsing differs.
- **Decision and action:** Trace one over-budget input through both callers. Recommend a shared owner for the byte-cap decision/error contract, leaving CLI parsing and adapter payload/lifecycle obligations at their boundaries. Compare retaining duplication against consolidation: consolidation removes two policy-update obligations without moving host registration into shared code.
- **Result and limit:** Recommend the shared byte-cap owner, retaining adapter conversion/lifecycle and CLI parsing at their boundaries; identify both consumer checks and migration order. A compact bullet can express this single-rule proposal without a full ownership table. No migration, new package, or SDK dependency is authorized.

## Similar code, different contracts

- **Request:** “Should these adapters share their similar retry loops? Assess only.”
- **Given evidence:** Adapter A's owned protocol requires one retry for an idempotent request; adapter B's host requires no retry because its operation may duplicate an effect. No common retry policy is established.
- **Decision and action:** Compare inputs, effects, errors, ordering, and host obligations before extracting code. The loops look alike but enforce different supported contracts. Retain separate behavior unless a genuinely shared calculation or coordination rule is found.
- **Result and limit:** Recommend retaining the current structure for this evidence. Do not create a configurable shared retry framework merely to consolidate syntax or assume a test double justifies another public abstraction.

## Characterize before migration

- **Request:** “Migrate the agreed shared owner without changing behavior. No new package.”
- **Given evidence:** Two adapters consume the policy. A is characterized; B lacks its boundary test. An existing forwarding entrypoint is public and callers still use it.
- **Decision and action:** Run existing tests and add B's missing characterization while its old implementation remains. Observe green before moving the owner. Migrate both consumers in dependency order, preserve host-specific conversion, and retain the public forwarder until agreed compatibility handling permits removal. Check installed/generated wiring and affected docs.
- **Result and limit:** Establish migrated consumer contracts with current evidence; keep inaccessible host checks pending. Retire a test only if retained assertions cover its contract or the behavior is intentionally obsolete. Directory consolidation alone is not a successful migration.
