r"""Test 3281 — gen #37 dict-value-wall Step 0, R5 (expected FAIL): red-team round 7 p078. The
record's outer value is the STRING "oops" (truthy), so `(rec.get("prover-result") or {})` is
"oops" and `.get` raises AttributeError in CPython. `no_exception \all` is FALSE; it PROVED in
land27 because the non-map arm answered the default "". Must stay UNPROVED (the map assertion on
the receiver cannot hold for `HStr "oops"`).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
#@ no_exception \all
def answer() -> str:
    rec: Dict[str, PyVal] = {"prover-result": "oops"}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    try:
        answer()
        print("no exception")
    except AttributeError as e:
        print("AttributeError:", e)
