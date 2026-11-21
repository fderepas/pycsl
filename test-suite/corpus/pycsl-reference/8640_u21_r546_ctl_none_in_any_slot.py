r"""Test 8640 -- route #546 (control, expected PASS): `-> Tuple[Any, int]` returning `(None, k)` -- the None is in the `Any` slot; the caller reads `t[1] + 1`; CPython returns k + 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires 0 <= k <= 1000
def g(k: int) -> Tuple[Any, int]:
    return (None, k)


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return t[1] + 1


if __name__ == "__main__":
    print("result", f(3))
