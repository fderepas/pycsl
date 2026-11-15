r"""Test 10001 -- lvT generator-as-seq (expected FAIL): the list of the yields of `two` has length
2, so its claim `len(\result) == 3` is false (CPython:
`len(list(two(s)))` is 2). Control: 10000.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List


#@ ensures len(\result) == 3
#@ assigns \nothing
#@ no_exception \all
def two(s: str) -> Iterator[str]:
    yield s
    yield "x"


if __name__ == "__main__":
    r = list(two("a"))
    print("VIOLATION contract" if len(r) != 3 else "result", r)
