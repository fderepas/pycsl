r"""Test 8797 -- route #558 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R558-BYTES-VALUE-KIND; red team 53 probe g1406/dg1367_bytes_call_display_cat.py): `xs: List[str] = [bytes(2)]; return len(xs[0] + "c")`; CPython TypeError: can't concat str to bytes
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, t: str, b: bytes) -> int:
    xs: List[str] = [bytes(2)]
    x = xs[0]
    return len(x + "c")


if __name__ == "__main__":
    try:
        r = f(1, "ab", b"ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
