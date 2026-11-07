r"""Test 8624 -- route #546 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1317_br1206_tup_branch): `-> Tuple[Any, int]` returning `(k, None)` on one branch; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[Any, int]:
    if k > 0:
        return (k, None)
    return (k, 1)


#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return t[1] + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
