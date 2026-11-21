r"""Test 8795 -- route #558 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R558-BYTES-VALUE-KIND; red team 53 probe g1400/da1296_lstr_bytes_cat.py): `xs: List[str] = ["a"]; xs.append(bytes(2)); x = xs[1]; return len(x + "c")`; CPython TypeError: can't concat str to bytes
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, s: str) -> int:
    xs: List[str] = ["a"]
    xs.append(bytes(2))
    x = xs[1]
    return len(x + "c")


if __name__ == "__main__":
    try:
        r = f(1, "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
