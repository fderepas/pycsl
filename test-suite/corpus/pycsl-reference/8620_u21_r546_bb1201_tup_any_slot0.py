r"""Test 8620 -- route #546 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1301_bb1201_tup_any_slot0): `-> Tuple[Any, int]` returning `(1, None)`; the caller reads `t[1] + 1`; CPython f(1) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[Any, int]:
    return (1, None)


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
