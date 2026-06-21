# What is a formal test? — the canonical definition

A **formal test** in PyCSL is a `src/pycsl_lib_test/formal_<name>.py` driver that proves an
operation's promise holds **for all** inputs by exercising the operation's **observable
consequence through its public API**. It is the loop-closer for a module: the mechanism by
which the English specification (the source of truth) is propagated onto annotations and
*proved*.

This file is the standalone, checkable definition. The workflow that produces formal tests is
Step 5 of `../SKILL.md`; this doc is what an artifact is measured **against**.

## The three-rule checklist

An artifact is a formal test **only if all three hold**. Miss one and it is something else
(see "What a formal test is NOT").

1. **FOR-ALL (universal quantification).** Every parameter is symbolic, constrained by
   `#@ requires`; never a concrete literal. The prover discharges the postcondition over the
   whole precondition domain at once. *A concrete-valued driver is just a unit test in PyCSL
   syntax — it proves nothing new.*

2. **CONSEQUENCE (observe the effect, not the call).** The test is a scenario:
   **set up a state → OPERATE → observe the post-state reflects the change.** The assertion is
   on the *observed consequence*, never on the call's own return-code contract. Re-asserting an
   operation's own `ensures` (`\result == 0 or -1`) through a bare call is **VACUOUS** — true by
   construction, proving nothing about what the operation *did*.
   - Mutating op → round-trip: `write → read-back → equal`; `mkdir → present → rmdir → absent`.
   - Read-only op → observe against a KNOWN state you built: after N creates, `len(listdir())==N`.

3. **CALLS THE API (never simulate).** Import and call the module's **public** functions; observe
   the consequence *through* them. Never touch internals (private helpers, raw `disk[...]` bytes,
   `sys_*`), never inline the operation's logic. THE TELL of a simulated test: *if writing it
   required knowing the internal byte layout, you are simulating, not testing* — and you've proved
   a tautology about your own re-implementation.

Two postcondition *strengths* (state which you proved): **totality/safety** ("the API never faults
on any input", e.g. `\result == 0 or 1` over a composed scenario) vs **functional content** ("the
API returns the right answer on any input", e.g. read-back equals written). Don't conflate them.

## The canonical good shape

```python
from os import mkdir, unlink, access, F_OK
def unlink_then_absent(f: str) -> int:        # f is SYMBOLIC (rule 1)
    mkdir(f)                                   # set up — REAL syscall (rule 3)
    before = access(f, F_OK)                   # observe pre-state
    unlink(f)                                  # OPERATE
    after = access(f, F_OK)                    # observe post-state
    #@ assert before == True and after == False  # the CONSEQUENCE (rule 2)
    return 0
```

## What a formal test is NOT

- **A return-code echo.** `def t(n): return rmdir(n)` with `#@ ensures \result == 0 or -1`.
  Vacuous (rule 2). At best a totality check — never functional verification.
- **A concrete unit test.** `def t(): return gcd(12, 0)` — fails rule 1.
- **A simulation.** Hand-writing dirent bytes and re-running the lookup inline — fails rule 3;
  proves a tautology about the author's re-implementation.
- **A verified spec-subject** (the subtle one). A class annotated with policies/contracts where
  the proof shows the method *bodies* satisfy their own pre/postconditions, with **no driver that
  constructs an instance, calls the API, and observes a post-state**. This proves the *spec holds
  of the bodies* — valuable — but it is a **contract proof of the subject**, not a consequence
  test. It fails rules 2 and 3. Do not file it under `formal_<name>.py` without an accompanying
  consequence driver.

  *Worked example:* the HAPPY flagship `src/pycsl_lib_test/formal_bank_transfer.py` was first
  written as a `Bank` class carrying five policies on `transfer` — a verified spec-subject (the
  PyCSL analog of macsl's `tests/small_example/main.c`). It verified green but had no driver:
  nothing checked that after `transfer` the source balance dropped, the destination rose, and the
  audit grew. The fix was to add a `formal_transfer_moves_money(amount, src_bal, dst_bal)` driver
  that `Bank() → seed → transfer → reads balances/audit back` and asserts the consequence over
  symbolic inputs — making it satisfy all three rules **and** keep the policy proofs.

## Why the separation matters (the convergence principle)

The test author and the model author must be **different agents**. The **test-agent** is given
only the public API signatures + the English spec, never the model internals — so it *physically
cannot* simulate (rule 3). See `../SKILL.md` Step 5 and the Convergence Principle.

## Gate

A formal test counts only when it is **green AND non-vacuous** (`--check-vacuity`). A vacuous green
(inconsistent assumed context → `ensures false` → every assertion free) is the worst outcome: it
verifies nothing while looking verified. Always run the non-vacuity gate.

Related: `../SKILL.md` Step 5 (the workflow), `glossary/formal-test.md` in the repo (`docs/`).
