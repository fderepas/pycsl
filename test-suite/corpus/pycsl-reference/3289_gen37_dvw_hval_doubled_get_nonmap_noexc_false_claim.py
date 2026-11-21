r"""Test 3289 — gen #37 dict-value-wall (expected FAIL): R5 twin on the DOUBLED read:
`rec["a"]` is the int 5, so `.get` raises AttributeError in CPython and `no_exception \all` is
FALSE. Under an active no_exception context the receiver must now be shown to be a map.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "" or \result != ""
#@ assigns \nothing
#@ no_exception \all
def answer() -> str:
    rec: Dict[str, PyVal] = {"a": 5}
    return rec["a"].get("x")


if __name__ == "__main__":
    try:
        answer(); print("no exception")
    except AttributeError as e:
        print("AttributeError:", e)
