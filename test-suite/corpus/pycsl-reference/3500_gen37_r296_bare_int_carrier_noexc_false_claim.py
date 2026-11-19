r"""Test 3500 — gen #37 route #296 (expected FAIL): an INT carrier iterated bare under `no_exception \all`: CPython raises TypeError; the R2b
element path gives it no constant/empty iteration and the claim must not prove.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
#@ no_exception \all
def walk(d: Dict[str, PyVal]) -> bool:
    n = d["n"]
    for x in n:
        pass
    return True

if __name__ == "__main__":
    try:
        print(walk({"n": 1}))
    except TypeError:
        print("raises TypeError")
