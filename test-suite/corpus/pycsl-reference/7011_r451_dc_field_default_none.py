r"""Test 7011 -- route #451 (expected FAIL): red-team 36 probe c3_d034_dataclass_default_none -- `@dataclass` field `s: str = None` (CPython AttributeError on `p.s.upper()`). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

@dataclass
class P:
    s: str = None  # type: ignore


#@ no_exception \all
def f(n: int) -> int:
    p = P()
    return len(p.s.upper())


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
