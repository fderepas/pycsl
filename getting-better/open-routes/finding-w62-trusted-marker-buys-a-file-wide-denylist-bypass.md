# FINDING w62 — A `\trusted` MARKER ON *ANY* FUNCTION BUYS A **FILE-WIDE** C-EXTENSION DENY-LIST BYPASS

**STATUS: FOUND AND MEASURED 2026-09-13 (gen #12). NOT A ROUTE — classified honestly below.**

**CLASS: a TCB-ACCOUNTING finding, NOT the #69 class.** No false postcondition about total
Python is proved here. It is recorded because the `\trusted` marker is the unit the campaign's
headline metric counts (459), and this shows one marker buys strictly more than its own
function.

## MEASURED, BOTH DIRECTIONS

```python
# z1 — CONTROL: the gate fires.
import ctypes
#@ ensures \result == 5
def f() -> int:
    return 5
```
→ **REFUSED**: ``import 'ctypes' is on the C-extension deny-list``.

```python
# z2 — the SAME import, plus an UNRELATED helper marked \trusted.
import ctypes

#@ \trusted
#@ ensures \result == 0
def helper() -> int:            # imports nothing, touches nothing
    return 0

#@ ensures \result == 5
def f() -> int:                 # NOT trusted, acknowledges NOTHING
    return 5
```
→ **Verification SUCCESS.**

`f` is not trusted, does not use `ctypes`, and never opted in to anything — yet it is verified
normally alongside a deny-listed import, purely because some *other* function in the file
carries a marker.

## THE MECHANISM — THE MESSAGE SAYS `importing`, THE CODE SAYS `any`

`src/pycsl/frontend/import_classifier.py:126` computes `has_trusted =
any_function_trusted(tree)`, and `any_function_trusted` (`:94-105`) is a whole-tree walk:

```python
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if getattr(node, "csl_trusted", False):
            return True
```

It checks **no relationship whatsoever** between the trusted function and the import. But the
refusal it gates says:

> `Either annotate the importing function(s) with #@ \trusted to acknowledge that the
> boundary is excluded from verification, or pass --allow-unverified-imports to opt out.`

**"the importing function(s)" IS A PRECISION THE CODE DOES NOT HAVE.** A user following the
advice literally — marking only the function that actually touches `ctypes` — gets the same
result as a user who marks an unrelated getter, and neither is told the acknowledgment was
applied file-wide.

**IS IT INTENDED?** Partly, and that is why this is a finding and not a route: the
`any_function_trusted` docstring says *"A file with `\trusted` somewhere is opt-in for the
unverified boundary."* So the CODE's intent is file-level. **The defect is that the MESSAGE
describes it as function-level**, and the two have drifted. One of them is wrong; the message
is the one users act on.

## WHY IT IS RECORDED DESPITE NOT BEING A ROUTE

This is the gen-#12 generator's discriminator, confirmed a third time: **ADVICE THAT NAMES
CONDITIONS THE EMITTER ACTUALLY CHECKS IS SAFE; ADVICE THAT NAMES A MARKER THE EMITTER MERELY
*READS* IS THE HAZARD.** Route #90 was the soundness version of this shape; this is the
TCB-accounting version. The marker count (459) measures how many functions are excluded from
verification — it does **not** record that each one also silently widens an unrelated,
file-scoped policy gate.

## REOPENING CONDITION — WHAT WOULD MAKE THIS A ROUTE

Escalate to severity-1 the moment a deny-listed module's imported NAMES become usable in a
proof under the bypass. Today the bypass only lets the FILE be processed; a `ctypes` value
that reaches a contract would either be refused downstream or become a trusted stub. **The
probe that settles it: under the z2 bypass, call something from `ctypes` and try to prove a
definite value about its result in a NON-trusted function.** If that proves, this becomes the
#69 class immediately. NOT RUN — recorded as the next step rather than claimed either way.

## THE CHEAP HONEST FIX (not built)

Either (a) narrow the gate to the functions that actually contain the import, matching the
message; or (b) keep the file-wide semantics and **fix the message to say so** —
"annotate ANY function in this file with `#@ \trusted` to acknowledge, FILE-WIDE, that ...".
(b) is a one-line change and is strictly better than leaving the two disagreeing.

## WITNESSES

`scratchpad/w62/r95/z1_ctl_ctypes_no_trusted.py` (control — the gate fires),
`scratchpad/w62/r95/z2_ctypes_unrelated_trusted.py` (the bypass).
