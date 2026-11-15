r"""Test 10005 -- lvT generator-as-seq (expected FAIL): a generator object that is STORED and
consumed twice is single-pass in CPython (the second `list(it)` is []), which a list model would
not see; the gate refuses any reference but an immediate `list(g(..))` / `for` / comprehension
iterable, so the generator stays one and route #271 (G2) refuses the call. Control: 10000.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List


#@ requires True
#@ ensures True
#@ assigns \nothing
#@ no_exception \all
def two(s: str) -> Iterator[str]:
    yield s
    yield "x"


#@ requires True
#@ ensures \result == 4
#@ assigns \nothing
def twice(s: str) -> int:
    it = two(s)
    a = list(it)
    b = list(it)
    return len(a) + len(b)


if __name__ == "__main__":
    r = twice("a")
    print("VIOLATION contract" if r != 4 else "result", r)
