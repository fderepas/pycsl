r"""Test 8642 -- route #546 (control, expected PASS): `-> Tuple[Any, Optional[int]]` returning `(k, None)`; the caller unpacks `a, v = g(k)` and narrows `if v is None: return 0`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires 0 <= k <= 1000
def g(k: int) -> Tuple[Any, Optional[int]]:
    return (k, None)


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    a, v = g(k)
    if v is None:
        return 0
    return v + 1


if __name__ == "__main__":
    print("result", f(3))
