r"""Test 7041 -- route #459 (expected FAIL): red-team 36 probe c33_g007_module_try_except_bind -- `G` bound only by a `try` body that raises, the handler passes (CPython NameError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

try:
    G = 1 // 0
except ZeroDivisionError:
    pass



#@ no_exception \all
def f(n: int) -> int:
    return G + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
