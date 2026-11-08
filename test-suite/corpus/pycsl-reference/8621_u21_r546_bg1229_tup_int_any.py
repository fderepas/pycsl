r"""Test 8621 -- route #546 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1306_bg1229_tup_int_any): `-> Tuple[int, Any]` returning `(None, 1)`; the caller reads `t[0] + 1`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[int, Any]:
    return (None, 1)


#@ no_exception \all
def f(d: Dict[str, int], k: str) -> int:
    t = g(1)
    return t[0] + 1


if __name__ == "__main__":
    try:
        r = f({}, "a")
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
