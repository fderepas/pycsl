r"""Test 8414 -- route #527 (expected FAIL: PROVED at base, REFUSED PYCSL-R527-OPTIONAL-OPERAND; red team 49 probe ah1009): `for c in r.s` (iteration); CPython TypeError: NoneType object is not iterable
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
    t = 0
    for c in r.s:
        t += 1
    return t


if __name__ == "__main__":
    try:
        r = f(R(None, "ab"))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
