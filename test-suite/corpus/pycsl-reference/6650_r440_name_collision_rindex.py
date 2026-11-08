r"""Test 6650 -- route #440 A1 (expected FAIL): a file class `Buffer` defines `rindex`, which admitted `path.rindex(".")` on a `str` receiver by NAME under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `x001_realistic_rindex.py`); CPython raises ValueError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

class Buffer:
    def __init__(self) -> None:
        self.items: List[int] = []

    def rindex(self, v: int) -> int:
        return 0


#@ no_exception \all
def last_dot(path: str) -> int:
    return path.rindex(".")


if __name__ == "__main__":
    try:
        r = last_dot("README")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
