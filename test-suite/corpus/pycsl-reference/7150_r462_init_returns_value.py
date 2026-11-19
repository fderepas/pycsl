r"""Test 7150 -- route #462 (expected FAIL): red-team 37 witness `e3_k014_init_returns_value` -- `__init__` ends with `return n`, so the claimed `f`'s `C(n)` raises TypeError. PROVED at base 370db7dc2 under `#@ no_exception \all`; now REFUSED (PYCSL-R462-INIT-RETURNS-VALUE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> int:
        self.n = n
        return n



#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
