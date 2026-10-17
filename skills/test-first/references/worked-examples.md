# Worked test decisions

## Concise cycle note

Hypothetical note: “UTF-8 cap regression: `éé` under a 3-byte cap failed as expected before the fix; the same check and 4-byte equality case passed afterward. Details: linked regression log.” No refactor field is needed when none occurred. This evidence establishes the tested contract, not unobserved host behavior.

These are hypothetical walkthroughs, not results observed in your checkout. Use only the example relevant to an unclear decision; the entry route card is sufficient for routine work.

## Byte-budget cycle

- **Request:** “Implement a UTF-8 byte cap: reject excess, accept equality.”
- **Given evidence:** Each `é` encodes to two bytes, so `éé` occupies four. The expected results below come from that contract, not the implementation.

| Input and budget | Expected observation | Mistake detected |
| --- | --- | --- |
| `éé`, 3 bytes | Reject | Counting two characters instead of four bytes |
| `éé`, 4 bytes | Accept | Rejecting equality |
| `éé`, 5 bytes | Accept | Rejecting every input |

- **Decision and action:** Start with the 3-byte scenario. Run its focused test before implementation and inspect why it fails: accepting an over-budget input is meaningful red; absence of the promised new API can also be intended red. Add the smallest byte-counting behavior and rerun the same test. Cycle through equality and below-limit acceptance, then affected caller checks. Define invalid-budget behavior before inventing its cases.
- **Result and limit:** Claim a cycle only after its actual red and green observations. If behavior already exists, preserve it and record that no pre-implementation failure was observed. A unit result does not establish an unobserved host path.

## Unrelated import failure

- **Request:** “The regression test fails. Apply the established correction.”
- **Given evidence:** The test exits while loading an unrelated missing fixture dependency; the target input never reaches production logic.
- **Decision and action:** Repair the test setup or identify unavailable environment prerequisites, then rerun the focused test. Check its assertion reaches the wrong behavior before changing production. Do not count an unrelated import error as red; absence of the API being introduced is a different, potentially intended failure.
- **Result and limit:** If setup remains unavailable, report that gap rather than invent red evidence. Implement only after understood behavior-reaching failure or an honestly selected exception route.

## Characterize existing behavior

- **Request:** “Refactor this existing parser without changing behavior.”
- **Given evidence:** Production implementation already exists; tests pass, but its public boundary input is uncovered. No pre-implementation red is available.
- **Decision and action:** Keep the implementation. Add a characterization test for that input and observe it passing before restructuring. Move code while the public-contract and consumer checks remain green; retain assertions protecting required behavior.
- **Result and limit:** Report a green characterization/refactor sequence, not a new-behavior red-green cycle. Never delete user work or change expected behavior to manufacture a failing test.
