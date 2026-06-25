# GAP-001 — C5 `is None` narrowing not lowered

**Construct:** `Union` (TY1 tier)
**Clause:** C5 (union-twoplane-spec.md §1.2)
**Plane:** Static
**Finding type:** Lowering gap (static obligation unimplemented)
**Severity:** High — C5 is a load-bearing narrowing clause

## Witness
- Driver: `typing-engagement/ty1/conformance/C5_is_none_narrowing.py`
- Body: `def f(x: Union[int, None]) -> int: if x is None: return 0; return x`
- Expected (from spec): PASS — the False branch narrows `x` to `int`, so `return x` typechecks and the postcondition `\\result >= 0` discharges.
- Actual (from run): FAIL.

## Evidence
```
File ".../.pycsl_mn74_tzn.mlw", line 21, characters 18-19:
This expression has type PyCSL_Program._union_f_0,
but is expected to have type int
[-] Verification FAILED or INCOMPLETE.
```

The lowering emits `x` on the False branch of `if x is None:` as the
synthesized variant value (`_union_f_0`), not as the projected `int` arm.
The narrowing obligation of C5 (False branch drops `None`, refines `x` to
`A`) is not implemented: there is no constructor projection emitted for
the narrowed path.

## NO-BLEND
The runtime shim (`Union(*args) -> int: return 0`) does NOT pass this case:
the driver does not call the shim, and the shim's identity postcondition
does not discharge a narrowing VC. So this is a pure static-plane gap —
NOT a blend.

## Recommendation to core-agent
On `if x is None:` where `x: Union[A, None]`, emit a WhyML constructor
match: `match x with | Arm_None -> 0 | Arm_0 v -> v end`. The False
branch must project the variant to the non-`None` arm's carrier type.

## Status
Open. Awaiting core-agent fix.
