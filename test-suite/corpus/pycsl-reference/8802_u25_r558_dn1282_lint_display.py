r"""Test 8802 -- route #558 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R558-BYTES-VALUE-KIND; red team 53 probe g1413/dn1282_bytes2_disp_ann.py): `xs: List[int] = [bytes(2)]; return xs[0] + 1`; CPython TypeError: can't concat int to bytes
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, t: str, ys: List[str]) -> int:
    xs: List[int] = [bytes(2)]
    x = xs[0]
    return x + 1


if __name__ == "__main__":
    try:
        r = f(1, "ab", ["a"])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
