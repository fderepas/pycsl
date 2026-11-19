r"""Test 8185 -- route #512 (expected FAIL: PROVED at base `no_exception \all`, now NOT PROVED -- the count form states the Py_ssize_t bound and `requires n >= 0` does not discharge it; red team 47 probe g813/q8004_bytes_req_index0): `b = bytes(n); return b[0]` under `requires n >= 0`: the faithful `Array.make n 0` owed only n >= 0; the count form now states the Py_ssize_t bound, which does not discharge (NOT PROVED); CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    b = bytes(n)
    if n > 0:
        return b[0]
    return 0


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
