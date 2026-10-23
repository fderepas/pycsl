"""Test 1220 — ROUTE #86: a `map int (option int)` PARAMETER COERCION substituted the EMPTY
MAP for the actual, and the callee's contract was then evaluated against it.

An actual that is neither a bare identifier nor an already-map expression — a FIELD READ
`c.d` — fell to an `else` branch that emitted `(const (None: option int))`. The carve-out
justified it as:

    "No known int->map coercion. Use `const None` as a placeholder empty map; the abstract
     val has no axioms about its contents anyway."

**THAT IS A CLAIM ABOUT THE CALLEE BEING ABSTRACT, NOT ABOUT THE LOWERING**, and it is false
the moment the callee is a REAL emitted function carrying a contract — as here, where `g`'s
postcondition relates its result to the map's contents. Measured: `\\result == 0` PROVED
where CPython returns 1, with the true twin refused.

**THIS ROUTE WAS ONLY VISIBLE BECAUSE ROUTE #85 WAS FIXED FIRST.** Both erasures emitted the
SAME wrong constant, so one masked the other. With #85 repaired the emission reads:

    let c = { d = (map_update_some (const (None: option int)) 1 5) } in   (* CORRECT *)
    (g (const (None: option int)))                                       (* WRONG   *)

**TWO INDEPENDENT ERASURES THAT PRODUCE THE SAME WRONG VALUE ARE INDISTINGUISHABLE UNTIL ONE
OF THEM IS FIXED, SO FIXING ONE IS A MEASUREMENT INSTRUMENT FOR THE OTHER.** Operationally:
after landing a repair, re-run the carriers and look for one that STILL PROVES — a surviving
carrier is not a failed repair, it is a second route the first one was masking.

The repair emits a POLYMORPHIC UNCONSTRAINED map: "no known coercion" must mean "nothing is
known", not "it is empty".

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ requires True
#@ ensures (1 in d) ==> (\result == 1)
#@ ensures (1 not in d) ==> (\result == 0)
#@ assigns \nothing
def g(d: Dict[int, int]) -> int:
    if 1 in d:
        return 1
    return 0


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return g(c.d)
