# GAP-LIT-004 — `isinstance(v, Literal[1, 2])` treated as opaque uninterpreted boolean

**Construct:** `Literal` (PEP 586)
**Spec clause:** LR4 (§2.2), LR8 (§2.4) — `isinstance` against `Literal` is not supported.
**Driver:** `typing-engagement/ty1/conformance-lit/LR4_isinstance_rejected.py`
**Classification:** Runtime-plane clarity gap (NOT a blend; NOT a spec violation).

## Symptom

Running `python3 src/pycsl/pycsl.py LR4_isinstance_rejected.py` produces
two VCs for the `if isinstance(v, Literal[1, 2]):` branches. The True-branch
postcondition discharges trivially (`Valid (0.01s, 275 steps)`); the
False-branch narrowed postcondition `ensures \result == 0` times out:

```
Sub-goal postcondition of goal f'vc.
Prover result is: Valid (0.01s, 275 steps).

Sub-goal postcondition of goal f'vc.
Prover result is: Timeout (30.00s, 16709024 steps).

[-] 1 goal(s) remain unproven after all provers:
    Prover result is: Timeout (30.00s, 16709024 steps).
```

The proof fails, which is the spec-correct outcome (the narrowed postcondition
is unprovable), but the failure surfaces as a solver timeout rather than a
clear static-plane diagnostic.

## Expected (from spec)

LR4 (literal-twoplane-spec.md §2.2) requires `isinstance(v, Literal[1, 2])`
to raise `TypeError` at runtime — `typing.Literal` aliases are not valid
second arguments to `isinstance`. LR8 (§2.4) forbids the shim from
introducing a distinct `Literal` runtime class. The driver's narrowed
postcondition `ensures \result == 0` (which holds only on the True branch,
where the body returns 0) cannot be discharged from the uninterpreted
boolean — the shim does not make `Literal` a valid `isinstance` argument.

## Actual

The construct is correctly treated as opaque (no narrowing of `v`'s value),
so the False-branch postcondition is unprovable. However, the failure surfaces
as a Z3 timeout (30s, 16M steps) rather than a `Valid` (the False branch
returns 1, so `\result == 0` is plainly `False` — Z3 should return `Invalid`
immediately, not time out).

## Root cause (spec-only diagnosis)

The `isinstance` lowering does not appear to recognize `Literal[1, 2]` as
an explicitly-unsupported second argument (per LR4); it is treated as an
opaque boolean predicate. The True-branch postcondition discharges trivially
because the body returns 0 there; the False-branch postcondition is
unprovable (the body returns 1, contradicting `\result == 0`), but Z3
spends 30s exploring the search space before timing out.

This gap is NOT a blend: the static L2 narrowing obligation (which is
the load-bearing Literal narrowing) is NOT discharged by the runtime
`isinstance` test — the LD2 no-blend rule is intact. The gap is a
diagnostic-clarity issue: the runtime rejection should surface as a
clearer static-plane diagnostic (e.g. an `isinstance`-against-`Literal`
rejection at normalization time, mirroring the L4a bytes rejection)
rather than a solver timeout.

## Fix direction (for the core-agent)

Consider adding a static-plane normalization-time rejection for
`isinstance(v, Literal[...])` forms, mirroring the L4a `Literal[b"x"]`
rejection at the normalization seam. This would surface the LR4
runtime-`TypeError` analogue as a clear static diagnostic rather than
a solver timeout. The fix is orthogonal to the no-blend rule.
