r"""Test 6659 -- route #440 A1 (expected FAIL): a file name `rsplit` admitted `s.rsplit("")` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `n026_str_rsplit_empty.py`); CPython raises ValueError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

class K:
    def rsplit(self, a0: int) -> int:
        return 0


#@ no_exception \all
def f(s: str, t: str) -> int:
    return len(s.rsplit(t))


if __name__ == "__main__":
    try:
        r = f("a", "")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
