# `no_exception` annotation patterns

Load when writing or refining `#@ no_exception` clauses, especially
in inter-procedural calls.

> **Rulebook:** `config/skills/pycsl-exception-model/SKILL.md` is the
> normative reference for the trigger table, WhyML predicate
> vocabulary, inter-procedural propagation rules, and rules for
> extending the model. This file is the annotator-workflow
> summary only.

The `no_exception` directive turns implicit Python exceptions into
proof obligations. The annotator's job is to write a precondition
strong enough to discharge each operation's trigger:

```python
#@ requires n != 0
#@ ensures \result == 256 / n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def divide_256(n: int) -> int:
    return 256 // n
```

Two patterns the corpus has validated:

- **Direct precondition** — `requires n != 0` discharges
  `no_div_zero (n)` for `256 // n`. The whole value of `no_exception`
  is that a failed VC tells the caller exactly which precondition
  would discharge it.
- **Branching precondition (SMT-friendly)** — `requires n > 0 or n < 0`
  also discharges the zero-divisor obligation; Alt-Ergo splits and
  proves both branches.

**Inter-procedural call sites.** When a callee declares
`raises { E -> P }` and the caller declares `no_exception E`,
Module 6 wraps the call automatically (rulebook details in the
exception-model skill). The annotator's only responsibilities:

- Provide a caller precondition strong enough that `not P` holds at
  the call site.
- Avoid TR-BUG-2 in the callee — a `raises` callee with no
  local-variable mutation is emitted as `let function` (pure) which
  Why3 rejects as effectful. Add at least one local assignment in
  the callee body. (See [`real-world-patterns.md`](real-world-patterns.md)
  Transpiler workarounds for the worked example.)
