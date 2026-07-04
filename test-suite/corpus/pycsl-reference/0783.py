"""Test 0783 — call list comprehension is content-faithful.

cleared-array.md item 1 (round 3). `[g(x) for x in a]`, where `g` is a PURE
module function (`assigns \nothing`, non-diverging → emitted as a Why3
`let function`, a logic symbol usable in a contract term), now lowers to a
per-instance `list_content_comp_<n>` val whose `ensures` gives
`length result = length a` and `forall i. result[i] = g(a[i])` — the SAME
`let function g` a driver's own `\result[k] == g(a[k])` lowers to. So a driver
can prove the result is the element-wise image of the source under `g`, which
the old opaque `list_comp` could not express.

The enabling feature (a pure function being spec-callable) already existed via
`emits_as_logic_symbol`; the round-3 work was lifting the CALL element in the
comprehension whitelist and deferring the content-law `val` so it is declared
AFTER `g` (an early abstract-op block would leave `g` unbound). No global axiom —
the content law is a definitional `ensures` on the abstract val, discharged at
the use site.
"""
_ = 0  # anchor
from typing import List


#@ ensures \result == 2 * x + 1
#@ assigns \nothing
def g(x: int) -> int:
    return 2 * x + 1


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == g(a[k])
#@ ensures \length(\result) == \length(a)
#@ assigns \nothing
def map_g(a: List[int]) -> List[int]:
    return [g(x) for x in a]
