r"""Test 10000 -- lvT generator-as-seq CONTROL (expected PASS): a PURE, TERMINATING,
EXCEPTION-FREE generator (`no_exception \all`, `assigns \nothing`, `str` parameter, no other name
read, no call but `len`) is lowered as the LIST OF ITS YIELDS, so the generator's own `\result` is the
list of its two yields. Twins (must FAIL): 10001-10007.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import Iterator, List


#@ requires True
#@ ensures len(\result) == 2
#@ assigns \nothing
#@ no_exception \all
def two(s: str) -> Iterator[str]:
    yield s
    yield "x"


if __name__ == "__main__":
    for s in ["", "a", "bc"]:
        r = list(two(s))
        print("VIOLATION contract" if len(r) != 2 else "result", r)
