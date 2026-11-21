r"""Test 3140 — gen #37 ch26 (expected PASS): the receiver-form defaulted read over a heterogeneous
`Dict[str, PyVal]` record, `(rec.get(k1) or {}).get(k2, "") or ""` (the shape of the emitter's own
`pycsl._record_answer`, the soundness chokepoint's reader). At base the outer `.get` fell to the
receiver-dropped `get_2 <hash k2> <hash "">` (the record erased, an int where a string is
expected: L3-tc failed). Now it is the K7 `pairs_get` match over the LOWERED receiver (missing key
or non-map receiver -> the default), and `<hval> or "<lit>"` keeps the operand when truthy,
projected to its `HStr` carrier. A record WITHOUT the outer key answers "" (CPython: "").
Twins: 3141, 3142 (must FAIL).
ch27: in ch26 this PASS timed out (z3 + alt-ergo). Root cause: the key test `hpairs_key_eq` was a
program `val`, so `pairs_get` / `hval_truthy` (whose bodies call it) got NO logic definition and
`pairs_get PNil k = None` was unprovable. It is now a `val function` (pure, uninterpreted, no axiom).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer_of_empty() -> str:
    rec: Dict[str, PyVal] = {}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    assert answer_of_empty() == ""
    print("ok")
