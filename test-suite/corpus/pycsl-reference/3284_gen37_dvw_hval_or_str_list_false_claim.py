r"""Test 3284 — gen #37 dict-value-wall Step 0, R6 (expected FAIL): red-team round 7 p084. The
value is the non-empty LIST ["a"] (truthy), so CPython returns ["a"] and `\result == ""` is FALSE;
it PROVED in land27 (`hstr_of (HArr ..) = ""`). Must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"answer": ["a"]}
    return rec.get("answer") or ""


if __name__ == "__main__":
    print(repr(answer()))
