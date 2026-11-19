r"""Test 8956 -- route #546 residual (control, expected PASS; u27 d02_union_none_first_any_slot1): `-> Union[None, Tuple[int, Any]]` returning `(k, None)`; the caller reads `x = t[0]; x + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


#@ requires 0 <= k <= 1000
def g(k: int) -> Union[None, Tuple[int, Any]]:
    return (k, None)


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    if t is not None:
        x = t[0]
        return x + 1
    return 0


if __name__ == "__main__":
    print("result", f(3))
