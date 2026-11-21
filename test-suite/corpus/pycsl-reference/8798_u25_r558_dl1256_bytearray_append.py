r"""Test 8798 -- route #558 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R558-BYTES-VALUE-KIND; red team 53 probe g1411/dl1256_bytearray_append_cat.py): `xs.append(bytearray(2))` into `List[str]`, then `x + "c"`; CPython TypeError: can't concat str to bytearray
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, t: str, b: bytes) -> int:
    xs: List[str] = ["a"]
    xs.append(bytearray(2))
    x = xs[1]
    return len(x + "c")


if __name__ == "__main__":
    try:
        r = f(1, "ab", b"ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
