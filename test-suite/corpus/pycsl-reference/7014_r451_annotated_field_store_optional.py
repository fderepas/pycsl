r"""Test 7014 -- route #451 (expected FAIL): red-team 36 probe c11_q008_init_default_none_field_ann -- annotated store `self.s: str = s` with `s: Optional[str] = None` (CPython AttributeError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self, s: Optional[str] = None) -> None:
        self.s: str = s  # type: ignore



#@ no_exception \all
def f(n: int) -> int:
    return len(P().s.upper())


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
