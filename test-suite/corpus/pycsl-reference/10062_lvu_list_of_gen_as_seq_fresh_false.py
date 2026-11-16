r"""Test 10062 -- lvU `list(<generator-as-seq call>)` (expected FAIL): each `list(..)` is a FRESH
list, so appending to `a` leaves `b` at length 2 and `\result == 3` is false (CPython: 2). The
lowering must not alias the two copies (`Array.copy` allocates). Measured verdict: refused
earlier -- `.append` on the copy is outside the modelled fragment today (the local is typed
`array int` at its append: L3-tc, fail closed). Control: 10060.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List


#@ ensures len(\result) == 2
#@ assigns \nothing
#@ no_exception \all
def two(s: str) -> Iterator[str]:
    yield s
    yield "x"


#@ ensures \result == 3
#@ assigns \nothing
def fresh(s: str) -> int:
    a = list(two(s))
    b = list(two(s))
    a.append("q")
    return len(b)


if __name__ == "__main__":
    r = fresh("a")
    print("VIOLATION contract" if r != 3 else "result", r)
