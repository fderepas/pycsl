r"""Test 10007 -- lvT generator-as-seq (expected FAIL): WITHOUT the `no_exception \all` claim the
generator's exception-freedom is not a proof obligation, so it is NOT lowered as a list; it stays a
generator for route #271, whose (G1) refuses its `ensures` about the eagerly-run body. CPython:
`list(first(""))` raises IndexError. Control: 10000.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List


#@ ensures len(\result) == 1
#@ assigns \nothing
def first(s: str) -> Iterator[str]:
    yield s[0]


if __name__ == "__main__":
    try:
        print("result", list(first("")))
    except IndexError:
        print("VIOLATION IndexError")
