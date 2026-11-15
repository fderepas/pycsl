r"""Test 9909 -- lvS hval-element filter (expected FAIL): the filter's result is the REAL fold over the
callee's (unknown) records, so `len(\result) == 0` is FALSE whenever one of them has key "k" (CPython:
1 for "x") and must NOT prove; a constant-empty stand-in would prove it. Control: 9908.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ \trusted
#@ assigns \nothing
def parse(s: str) -> List[Dict[str, PyVal]]:
    return [{"k": 1}, {"j": 2}] if s else []


#@ ensures len(\result) == 0
#@ assigns \nothing
def keep(s: str) -> List[Dict[str, PyVal]]:
    return [r for r in parse(s) if "k" in r]


if __name__ == "__main__":
    r = keep("x")
    print("VIOLATION contract" if len(r) != 0 else "result", r)
