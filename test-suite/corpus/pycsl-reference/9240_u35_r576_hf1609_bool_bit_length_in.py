r"""Test 9240 -- route #576 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 55 probe hf1609_bool_bit_length_in.py): `return 1 if k in t.bit_length else 0`; CPython TypeError argument of type 'builtin_function_or_method' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

SA = str


#@ no_exception \all
def f(k: int, x: float, b: bytes, t: bool, tp: Tuple[int, ...], fs: FrozenSet[int], os_: Optional[str], sa: SA) -> int:
    return 1 if k in t.bit_length else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, 1.5, b"a", True, (1,), frozenset({1}), "a", "b"))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
