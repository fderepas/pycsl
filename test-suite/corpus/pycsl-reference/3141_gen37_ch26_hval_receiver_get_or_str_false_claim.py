r"""Test 3141 — gen #37 ch26 (expected FAIL): FALSE twin of 3140. The record CARRIES
`{"prover-result": {"answer": "Valid"}}`, so CPython returns "Valid", and `\result == ""` must
stay UNPROVED. Non-vacuity of the seam: the receiver-form `.get` reads the record (a facade that
answered the default whatever the record held would prove this false claim).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer_of_valid() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {"answer": "Valid"}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    print(repr(answer_of_valid()))
