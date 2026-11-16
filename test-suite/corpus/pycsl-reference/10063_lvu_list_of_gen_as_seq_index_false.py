r"""Test 10063 -- lvU `list(<generator-as-seq call>)` (expected FAIL): the copy has length 2, so
`r[2]` raises IndexError (CPython: `pick("a")` raises), and the read is an in-bounds obligation
that does not hold. Control: 10060.
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


#@ assigns \nothing
#@ no_exception IndexError
def pick(s: str) -> str:
    r = list(two(s))
    return r[2]


if __name__ == "__main__":
    try:
        print("result", pick("a"))
    except IndexError:
        print("VIOLATION IndexError")
