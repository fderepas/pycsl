# OPEN ROUTE #255 — ERASURE IS LOST THROUGH A WALRUS BINDING AND THROUGH AN UNANNOTATED RETURN

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Red-team finding; driver-reproduced at HEAD fa283db6
(all four rc=0; CPython 7).

## Witnesses (`witnesses-r255/`)
- `p50_walrus_sub.py`: `if (v := x) is not None: return v - v` on `x: Any`, `ensures \result == 0` proves.
- `p45_walrus.py`: walrus value passed to `g(a: int, b: int)` — bypasses #252's refusal.
- `p51_unannot_sub.py`: `def h(z): return z`; `v = h(x); return v - v` proves `\result == 0`.
- `p47_untyped_local_from_call.py`: the unannotated-return value passed to int params.

## Mechanism
#249's erased-local fixpoint does not treat a `NamedExpr` target as bound from an erased value, and treats a
MISSING return annotation (and unannotated params lowered to `int`) as non-erased, so #251's uninterpreted
arithmetic and #252's flow refusal are bypassed.

## Repair direction
Walrus targets join the fixpoint; a function with no return annotation (and its unannotated params) counts as
erased (or the unannotated callee's return is erased at the call site). Census every binding form the fixpoint
might miss (for-targets, with-as, except-as, comprehension targets, tuple unpack, augassign, global/nonlocal).
