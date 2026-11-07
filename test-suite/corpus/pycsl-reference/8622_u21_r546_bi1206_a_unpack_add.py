r"""Test 8622 -- route #546 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1308_bi1206_a_unpack_add): `-> Tuple[Any, int]` returning `(k, None)`, unpacked `a, b = g(k)`; `b + 1`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[Any, int]:
    return (k, None)


#@ no_exception \all
def f(k: int) -> int:
    a, b = g(k)
    return b + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
