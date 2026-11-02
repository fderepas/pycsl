r"""Test 8412 -- route #527 (expected FAIL: PROVED at base, REFUSED PYCSL-R527-OPTIONAL-OPERAND; red team 49 probe ah1003): `"a" in r.s` (the field as a membership haystack); CPython TypeError: argument of type NoneType is not a container or iterable
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
    return 1 if "a" in r.s else 0


if __name__ == "__main__":
    try:
        r = f(R(None, "ab"))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
