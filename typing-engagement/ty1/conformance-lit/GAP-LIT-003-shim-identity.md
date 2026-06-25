# GAP-LIT-003 — `Literal` shim identity postcondition unreachable

**Construct:** `Literal` (PEP 586)
**Spec clause:** LR3 (§2.1), LR7 (§2.4) — the shim is identity, no validation.
**Driver:** `typing-engagement/ty1/conformance-lit/LR3_no_enforcement.py`
**Classification:** Runtime-plane gap (NOT a blend; NOT `Literal`-specific).

## Symptom

Running `python3 src/pycsl/pycsl.py LR3_no_enforcement.py` produces a Why3 type
error and the proof fails:

```
Warnings/Errors from Why3:
File ".../pycsl_06jxwqbb.mlw", line 16, characters 13-14:
This expression has type int, but is expected to have type ()

[-] Verification FAILED or INCOMPLETE. Check the solver output.
```

No VC is discharged.

## Expected (from spec)

LR3 (literal-twoplane-spec.md §2.1) requires the runtime shim to be identity:
`Literal(*args, val)` returns `val` unchanged, with the identity postcondition
`#@ ensures \result == val` discharging for ANY value (a string, a list, None).
LR7 (§2.4) forbids the shim from validating value-set membership — a faithful
shim performs no enforcement. The driver calls `Literal(1, 2, val)` with values
outside the declared set {1, 2} and expects the identity postcondition to
discharge regardless.

## Actual

The shim's identity postcondition is unreachable: the WhyML emitted at the
call site does not match the shim's `int`-returning identity contract, and
Why3 rejects the call with `int vs ()` type mismatch.

## Root cause (spec-only diagnosis)

The `Literal` shim lives in `src/pycsl_lib/typ/__init__.py` (the same seam
as the `Union` shim, per the §12.9 surface). The `Union`-side GAP-003
documents the identical symptom on the `Union(x0, x1, val)` shim: the
call shape produced by the lowering does not match the shim's declared
return type. `Literal` reuses the same seam and inherits the same
lowering-level call-shape mismatch — there is no `Literal`-specific
lowering bug here.

This gap is NOT a blend: the static L1 value-set obligation is a
precondition VC, invisible to the runtime shim (per §12.9). The shim
could not discharge any static clause even if its identity
postcondition were reachable. The no-blend rule (LD3) is intact.

## Fix direction (for the core-agent)

The call-shape mismatch at the `Literal(*args, val)` seam should be
reconciled — the lowering's emitted WhyML for the call site should match
the shim's declared identity contract. The fix should be shared with the
`Union`-side GAP-003 since both shims live in the same seam and exhibit
the same symptom.
