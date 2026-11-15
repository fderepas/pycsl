r"""Test 10003 -- lvT generator-as-seq (expected FAIL): a generator with an explicit `raise` is not
lowered as a list (the gate refuses a `raise`), so it stays a generator for route #271, whose (G1)
refuses its `ensures` about the eagerly-run body. CPython: `list(g(-1))` raises ValueError.
Control: 10000.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List


#@ requires True
#@ ensures len(\result) == 1
#@ assigns \nothing
#@ no_exception \all
def g(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError("negative")
    yield n


if __name__ == "__main__":
    try:
        print("result", list(g(-1)))
    except ValueError:
        print("VIOLATION ValueError")
