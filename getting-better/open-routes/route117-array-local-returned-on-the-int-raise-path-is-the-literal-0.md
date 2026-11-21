# ROUTE #117 — a LIST local returned early from a function whose WhyML return type is `int`
# is replaced by the LITERAL `0`

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15)** — see THE REPAIR AS LANDED at the bottom. Original finding preserved below.
**Severity: SEV-1. First-order.** Needs no annotation at all: an unannotated function that
returns a list on one path.

## PROVENANCE

Generator `witness-census` (census site in `stmt_control_flow.py`'s return handler).

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/stmt_control_flow.py`, the `raise (Return ...)` path:

```
            # int return path: an array-typed val here is structurally
            # incompatible — `Return int` can't carry it. Collapse to 0
            # (matches the pre-existing lossy behaviour).
            if (val_ir and val_ir.get("type") == "Var"
                    and val_ir.get("name") in self._array_locals):
                val = "0"
```

and its twin earlier in the same file ("on the raise-Return int path we collapse the value to
0 (lossy but at least type-correct)"). **"Lossy" is the wrong word: `0` is a definite value,
and it is wrong.**

## MEASURED at baseline worktree `21d5029e` (source == HEAD `6f36d67f`)

`w_arrret_noann.py`:

```python
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int):
    xs: List[int] = [x, 1]
    if x > 0:
        return xs
    return 0
```

`[+] Verification SUCCESS` rc=0; emitted `if (x > 0) then raise (Return 0) else raise
(Return 0)`. **CPython `f(1)` returns `[1, 1]`, which is not `0`.** Same verdict with
`-> Any`. With `-> Union[int, List[int]]` the claim is refused only by a Why3 TYPE ERROR
(the union result against `int`) — and the emission still carries `(Arm_0_1 0)`, the List arm
holding the literal `0`.

## REPAIR SKETCH

Where the value cannot be carried, REFUSE (the function's result type is not `int`; a
`-> List[int]` function already takes the array return path), or return an UNCONSTRAINED int —
never `0`. The union arm's payload needs the same treatment.

---

# THE REPAIR AS LANDED — gen #23 (2026-09-15)

Landed with routes #111–#117 as ONE combined battery (commit recorded in `driver-progress.log`).
Every verdict was PREDICTED in the progress log before it ran:
metric 459/484/25/0 · doc-coherency rc=0 · mirror sync 887 verbatim · mirror-check same 3
pre-existing drifts · trusted-raises 13/62 · trusted-reasons 459↔459 · type-only 53, 0
ill-typed · dropped-mutation 0/51/9/0 · byte-diff pycsl-ref 22 MOVED / GONE only 0996 (an
expected-FAIL witness now refused) · python-ref 6 MOVED · mirror emission 7 MOVED, every hunk
read and attributed · suite 3444/3462, the SAME 18 failures, ZERO XPASS · whole-file proofs of
all 7 moved mirrors SUCCESS, 0 bad (statements 17630, expressions 21347, stmt_control_flow
12284, pure_ast 3372, functions 1199, Module5_IREmitter 2109, preamble 216 Valid) · planes
34/34 `ok` COUNTED (after narrowing `check-singleton-constant-lowering`'s baseline: the split arm orphaned two entries whose justifications #115/#116 had just refuted — removed — and renamed the GenExp half's key; constant arms 14 -> 12; emission re-verified byte-identical).

**What landed.** `stmt_control_flow.py` (live + verbatim mirror), both Return-int collapses of
an array local: `(any int)`, never `0`. Unannotated and `-> Any` carriers refused. Corpus 1316
(XFAIL). The union-annotated sibling's `(Arm_0_1 0)` payload is NOT addressed (fail-closed by
type error today) — recorded, not fixed.
