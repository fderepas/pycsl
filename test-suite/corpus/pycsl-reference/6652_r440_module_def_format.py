r"""Test 6652 -- route #440 A1 (expected FAIL): a module function named `format` admitted `"{} {}".format(n)` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `r002_mod_format.py`); CPython raises IndexError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

def format(a0: int) -> int:
    return 0


#@ no_exception \all
def f(n: int) -> int:
    return len("{} {}".format(n))


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
