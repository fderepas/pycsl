r"""Test 10060 -- lvU `list(<generator-as-seq call>)` CONTROL (expected PASS): `two` is a pure,
terminating, exception-free generator (lvT §7.323 (1)), lowered as the list of its yields, and
`list(two(s))` is a FRESH list holding exactly them (CPython drains the generator into a new list),
so its length is 2. Twins (must FAIL): 10061-10063.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import Iterator, List


#@ ensures len(\result) == 2
#@ assigns \nothing
#@ no_exception \all
def two(s: str) -> Iterator[str]:
    yield s
    yield "x"


#@ ensures \result == 2
#@ assigns \nothing
def count(s: str) -> int:
    r = list(two(s))
    return len(r)


if __name__ == "__main__":
    for s in ["", "a", "bc"]:
        r = count(s)
        print("VIOLATION contract" if r != 2 else "result", r)
