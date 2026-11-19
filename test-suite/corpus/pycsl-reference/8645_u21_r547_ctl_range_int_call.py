r"""Test 8645 -- route #547 (control, expected PASS): `range(g(k))` of a file function `-> int` that never returns None
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires 0 <= k <= 10
#@ ensures \result == k
def g(k: int) -> int:
    return k


#@ requires 0 <= k <= 10
#@ no_exception \all
def f(k: int) -> int:
    n = 0
    for i in range(g(k)):
        n += 1
    return n


if __name__ == "__main__":
    print("result", f(3))
