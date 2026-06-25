# GAP-004 — O3 `return None` from `Optional[X]` not lowered (None-arm return injection missing)

**Construct:** `Optional` (TY1 tier)
**Clause:** O3 (optional-twoplane-spec.md §1.1) — None is always assignable
**Plane:** Static
**Finding type:** Lowering gap (static obligation unimplemented)
**Severity:** High — O3 is the defining asymmetry of `Optional`; the `None`
arm must be reachable as a return value from any `Optional[X]`-typed function.

## Witness
- Driver: `typing-engagement/ty1/conformance-opt/O3_none_assignable.py`
- Body: `def f(x: Optional[int]) -> Optional[int]: return None`
- Expected (from spec): PASS — `None` is always assignable to `Optional[X]`
  (O3); the `return None` auto-injects into the `Arm_None` nullary constructor
  of the synthesized variant `_union_f_1 = Arm_0_0 int | Arm_0_None`.
- Actual (from run): FAIL.

## Evidence
```
Warnings/Errors from Why3:
File "/tmp/.pycsl_jqf6xk3u.mlw", line 14, characters 4-5:
This expression has type int, but is expected to have type PyCSL_Program.
_union_f_1
[-] Verification FAILED or INCOMPLETE.
```

The lowering emits `return None` as the WhyML literal `0` (the Python `None`
singleton is modelled as `0` in the hoare memory model), but the function's
declared return type is the synthesized variant `_union_f_1`. The
`Arm_None` injection that should wrap the `None` into the variant's nullary
constructor is NOT emitted on the return path. Per §12.4 of
`test-suite/annotations.md`, "a function returning `Optional[int]` whose
body returns an `int` auto-injects into the matching arm constructor
(`Arm_0_0 (expr)`)" — but the symmetric auto-injection for a `None`-valued
return into `Arm_None` is missing.

## Why this is distinct from O6
O6 (the `is None` narrowing) PASSes: the False-branch projection of the
variant to the `int` carrier is correctly lowered. O3 is the REVERSE
direction: a `None` value flowing INTO the variant (return-path injection
into `Arm_None`). The two are independent lowerings; O3 is unimplemented
even though O6 is fixed.

## NO-BLEND
The runtime shim is NOT invoked: the driver does not call `Union(...)` or
any `pycsl_lib.typ` surface. The failure is a pure static-plane lowering
gap. NOT a blend.

## Recommendation to core-agent
On `return None` (or `return <None-typed expr>`) from a function whose
declared return type is `Optional[X]` (= `Union[X, None]`), emit the
`Arm_None` nullary constructor injection: `Arm_0_None` (matching the
synthesized variant name). This is the symmetric counterpart to the
existing int-return auto-injection (`Arm_0_0 (expr)`).

## Status
Open. Awaiting core-agent fix.
