r"""Test 7013 -- route #451 (expected FAIL): red-team 36 probe c11_q005_dc_default_none_index -- `@dataclass` field `d: Dict[int, int] = None` (CPython AttributeError on `.get`). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

@dataclass
class P:
    d: Dict[int, int] = None  # type: ignore



#@ no_exception \all
def f(k: int) -> int:
    return P().d.get(k, 0)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
