r"""Test 10088 -- lvV law-free `sorted(List[str])` (expected FAIL): nothing is claimed about the
sorted copy, so `",".join(sorted(xs)) == ",".join(xs)` must NOT prove (CPython: ["b", "a"]).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib
from typing import List


#@ ensures \result == True
#@ assigns \nothing
def keyed(xs: List[str]) -> bool:
    a = hashlib.sha256(",".join(sorted(xs)).encode()).hexdigest()
    b = hashlib.sha256(",".join(xs).encode()).hexdigest()
    return a == b


if __name__ == "__main__":
    r = keyed(["b", "a"])
    print("VIOLATION contract" if r is not True else "result", r)
