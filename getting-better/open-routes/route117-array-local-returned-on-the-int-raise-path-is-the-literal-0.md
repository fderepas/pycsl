# ROUTE #117 — a LIST local returned early from a function whose WhyML return type is `int`
# is replaced by the LITERAL `0`

**Status: FOUND, REPRODUCED (gen #23, 2026-09-14). NOT REPAIRED.**
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
