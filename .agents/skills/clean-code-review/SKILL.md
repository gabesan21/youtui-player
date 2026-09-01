---
name: clean-code-review
description: Code review script with severity and evidence - verifying behavior, complexity, names and tests without turning into aesthetic policing. Use when verifying code tasks (005) and as a reading criterion in plan or PR gates. Code projects only.
---

# clean-code-review

**Principle: approve the change that improves the code's overall health, not the perfect change.** A review produces evidence, not opinion: every comment points to a snippet, an impact and a severity. Whoever writes the code uses the sibling skill `clean-code-change`.

**Parametrization:** run/verify the commands declared in the **"Project verification"** section of the project's AGENTS.md. Never block over personal preference, line counting or style that automated tooling already covers.

## Reading script

1. Read the **goal, affected contract and tests** first; only then the diff — in the order the system executes it or the user experiences it, not in the alphabetical order of the files.
2. Verify, in this order of importance:
   - **Behavior and edges:** does the code do what the contract promises? Error cases, limits and external effects covered?
   - **Tests:** do they exist, are they simple, and would they fail if the new behavior broke? A test that never fails protects nothing.
   - **Complexity and coupling:** does the change reduce — or at least not increase — accidental complexity? Does the new abstraction represent a real variation?
   - **Names and comments:** intention readable without deciphering details; comments explain the "why", they don't narrate the code.
   - **Local consistency and documentation:** follows the file's/project's idiom; affected documentation and specs updated.
3. Confirm the **automated evidence**: the project's formatter/linter/tests executed and clean (or a deviation justified in writing).

## Severity of each comment

| Severity | When | Effect |
|----------|------|--------|
| **blocking** | Correctness, risk, contract breakage, missing test for new behavior | Prevents approval until resolved |
| **suggestion** | Justifiable improvement in readability, cohesion or future cost | Author decides; record the reason |
| **nit** | Non-blocking preference | Never holds the change |

- Every comment carries **snippet + impact + reason** — "it's cleaner" is not a reason; "the reader has to simulate 3 states to know whether X happens" is.
- If the author's explanation lives only in the conversation, ask for it to become **simpler code or a motive comment** — conversation gets lost, code stays.

## Decision

- **Approve** when the change improves the code's health, even if imperfect.
- Debt identified but deferred requires an **explicit and trackable follow-up** (note on the card, the spec's "Open" section or a task proposal) — approving without recording it is losing the debt.
- **Send back** (in the PoP: return from 005 to 004/002) only over a blocking item, citing the violated criterion and the evidence.

## What this review is not

- It is not a gate of perfection or taste: automatable style belongs to the formatter/linter, not to the reviewer.
- It is not an audit of the whole repository: the scope is the diff and what it touches.
- It imposes no numeric limits or OO patterns — cohesion, domain and evidence decide.
