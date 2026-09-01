---
name: clean-code-change
description: Clean code practices for whoever writes code - clarifying the contract before coding, local readability, safe refactoring and debt triage. Use in every task that creates or changes code, when planning (002) and when executing (004). Code projects only.
---

# clean-code-change

**Principle: clean code is code that someone who didn't write it understands and modifies safely.** Clean code is neither a single metric nor an aesthetic checklist — it is evidence: a clear contract, a test that protects, a diff with one intention. This skill accompanies whoever **writes** code; review uses the sibling `clean-code-review`.

**Parametrization:** the verification commands (formatter, linter, tests) are the ones declared in the **"Project verification"** section of the project's AGENTS.md. This skill never imposes numeric limits (lines, parameters, nesting), SOLID or OO patterns — cohesion and domain decide, not counting.

## 1. Clarify before coding

**Trigger:** the requirement, bug or diff still doesn't let you explain behavior, boundaries and observable effect in a few sentences.

1. State the change's **input, output, invariants, error cases and external effects**.
2. Locate the existing contract: API, type, test, documentation or a representative call.
3. Choose the **smallest change point** that preserves that contract; without a verifiable contract, write or update the test **before** the structural change.
4. Separate preparation/refactoring from the functional change when mixing them makes the diff hard to review.

**Verifiable output:** a description of the behavior + a test/scenario that **fails before and passes after** the change. In a kanban task, this feeds the "Acceptance criteria and verification" table of the plan (002).

## 2. Local readability

**Trigger:** the reader has to simulate too many states, guess the intention of a name or hop between files to understand one unit.

1. Rename symbols for **domain, role and unit** — neither opaque acronyms nor redundant phrases.
2. Make the happy path and the exceptional cases **distinguishable**; reduce negations and nesting only when the flow gets more direct.
3. Extract a function/concept **only** if the result is a name that explains one idea while keeping cohesion — don't split a cohesive operation into artificial layers to "shorten" it.
4. A comment exists for **motive, constraint, trade-off or external protocol**; delete comments that merely narrate the code.

**Verifiable output:** a new reader explains the "what" and the "why" by looking at names, organization and minimal commentary.

## 3. Refactor safely

**Trigger:** a recurring change is expensive due to coupling, duplication with a genuinely shared rule, opaque flow or a confusing module boundary.

1. **Characterize** the current behavior with tests, executable examples or another reliable observation — without a net, reduce the risk first.
2. Name the **hypothesis** (which reading/maintenance becomes simpler) and the **risk** (which behavior must not change).
3. Apply **one small transformation at a time**: rename, extract, move, encapsulate, simplify a condition.
4. Compile, run the relevant tests and review the diff **at every step**; stop when the goal is met.
5. Broad refactoring goes in a **separate** change from the feature (in the PoP: another task), except obvious local cleanup.

**Verifiable output:** behavior preserved by tests and a diff with **a single structural intention**.

## 4. Duplication and abstraction

- Unify duplication **only** if the rule and the rate of change are the same — premature abstraction mixes distinct cases and costs more than the repetition.
- An abstraction is valuable when it simplifies a **real variation**; don't generalize by guessing and don't create a single-use interface.
- Simplicity = the **smallest number of concepts** that meets the current requirement.

## 5. Debt triage within the change

**Trigger:** the change introduces complexity, duplication or a tool warning — don't wait for the repository to degrade.

1. Run the **project's** formatter, linter, static analysis and tests ("Project verification" section of the AGENTS.md).
2. Distinguish **mechanical warning from real risk**: prioritize the critical path, frequently changed code, test failures, security and cost of understanding. A smell is a signal for investigation, not proof of a defect.
3. Fix what is **local and safe** within the task; larger debt becomes a trackable item (note on the card, the spec's "Open" section or a task proposal) with context, impact and next step.
4. The yardstick is **improving overall health with every change**, not demanding perfection before integrating.

**Verifiable output:** evidence of the commands executed and an explicit decision for every relevant deviation.

## What this skill is not

- It is not maximizing the number of files, classes, interfaces or layers.
- It is not obeying rigid limits of lines, parameters or nesting while ignoring cohesion and domain.
- It does not replace architecture, security, performance, accessibility, requirements or integration tests.
- It does not justify refactoring without value: inelegant but stable and rarely changed code may not be a priority — never rewrite stable code without a demonstrable benefit.
