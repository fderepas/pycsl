r"""Test 3290 — gen #37 dict-value-wall Step 1 / R2a (expected PASS): a PRESENT key read at the HEAD of a nested record.
`(rec.get("prover-result") or {}).get("answer", "") or ""` over
`{"prover-result": {"answer": "Valid"}}` is "Valid" in CPython. Before R2a the key test
`hpairs_key_eq` was an uninterpreted `val function` with no spec, so `pairs_get (PCons "answer"
v PNil) "answer"` could not be reduced and this timed out in z3 and alt-ergo. With the spec
`result <-> a = b` it proves. Twin: 3291.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "Valid"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {"answer": "Valid"}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    assert answer() == "Valid"; print("ok")
