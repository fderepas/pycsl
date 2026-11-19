r"""Test 10061 -- lvU `list(<generator-as-seq call>)` (expected FAIL): the copy holds the two
yields, so `\result == 3` is false (CPython: `len(list(two("a")))` is 2). Control: 10060.
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
def count(s: str) -> int:
    r = list(two(s))
    return len(r)


if __name__ == "__main__":
    r = count("a")
    print("VIOLATION contract" if r != 3 else "result", r)
