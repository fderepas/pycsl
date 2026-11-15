r"""Test 10004 -- lvT generator-as-seq (expected FAIL): a generator that reads module state is not
pure in the eager sense -- the consumer mutates `K` between two `next()` calls, so CPython yields
[0, 5] while an eager list would be [0, 0]. The gate refuses a non-local read (the generator stays one, for
route #271); the consumer's `global K` store is refused by its own route first. Control: 10000.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List

K = 0


#@ requires True
#@ ensures True
#@ assigns \nothing
#@ no_exception \all
def g() -> Iterator[int]:
    yield K
    yield K


#@ requires True
#@ ensures \result == 0
def total() -> int:
    global K
    t = 0
    for x in g():
        t = t + x
        K = 5
    return t


if __name__ == "__main__":
    r = total()
    print("VIOLATION contract" if r != 0 else "result", r)
