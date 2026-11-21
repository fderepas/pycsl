r"""Test 8796 -- route #558 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R558-BYTES-VALUE-KIND; red team 53 probe g1406/dg1354_bytes_call_append_join.py): `xs.append(bytes(2)); return len("-".join([xs[1]]))`; CPython TypeError: sequence item 0: expected str instance, bytes found
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, t: str, b: bytes) -> int:
    xs: List[str] = ["a"]
    xs.append(bytes(2))
    x = xs[1]
    return len("-".join([x]))


if __name__ == "__main__":
    try:
        r = f(1, "ab", b"ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
