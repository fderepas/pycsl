r"""Test 3160 — gen #37 ch27 (expected PASS): the receiver-form defaulted read with a NON-LITERAL
key, `(rec.get("a") or {}).get(k, "") or ""`, over a heterogeneous `Dict[str, PyVal]` record. At
base (and in the ch26 seam, which required a string-literal key) the outer `.get` fell to the
receiver-dropped `get_2 (str_hash_op k) <hash "">`: the record erased, an int where a string is
expected (L3-tc failed). Now it is the `pairs_get` read of the LOWERED receiver at the LOWERED key.
A record without "a" answers "" whatever `k` is (CPython: ""). Twin: 3161 (must FAIL).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer_of_empty(k: str) -> str:
    rec: Dict[str, PyVal] = {}
    return (rec.get("a") or {}).get(k, "") or ""


if __name__ == "__main__":
    assert answer_of_empty("x") == ""
    print("ok")
