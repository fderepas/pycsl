r"""Test 10002 -- lvT generator-as-seq (expected FAIL): a generator whose body RAISES is not
exception-free; `first("")` raises IndexError when iterated, so its `no_exception \all` claim is
false and the bounds VC of the eager lowering fails. Control: 10000.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List


#@ requires True
#@ ensures len(\result) == 1
#@ assigns \nothing
#@ no_exception \all
def first(s: str) -> Iterator[str]:
    yield s[0]


if __name__ == "__main__":
    try:
        print("result", list(first("")))
    except IndexError:
        print("VIOLATION IndexError")
