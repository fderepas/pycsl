r"""Test 9712 -- lvQ open-world model (expected FAIL, refused PYCSL-R7Q-EXT-PATH-RECEIVER): the file
imports `Path`, so `n.mkdir(..)` is read as `pathlib.Path.mkdir`, but its receiver is an `int`: the
call cannot be lowered to the path model (CPython: AttributeError).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def make(n: int) -> int:
    n.mkdir(parents=True, exist_ok=True)
    return 0


if __name__ == "__main__":
    try:
        make(3)
        print("result 0")
    except AttributeError as e:
        print("VIOLATION contract", e)
