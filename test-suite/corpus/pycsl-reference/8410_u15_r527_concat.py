r"""Test 8410 -- route #527 (expected FAIL: PROVED at base, REFUSED PYCSL-R527-OPTIONAL-OPERAND; red team 49 probe ah1000): `w = r.s + "x"` on an `Optional[str]` @dataclass field; CPython f(R(None, "ab")) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Optional[str]
    t: str


#@ no_exception \all
def f(r: R) -> int:
    w = r.s + "x"
    return 1


if __name__ == "__main__":
    try:
        r = f(R(None, "ab"))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
