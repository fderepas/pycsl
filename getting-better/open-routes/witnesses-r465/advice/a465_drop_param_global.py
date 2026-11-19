r"""Advice probe for route #465 (drop the `global` of a parameter), from test 7336 -- route #465 (expected FAIL): red-team 38 witness `g1_c116_in_f_param_global` -- `global n` of the claimed def's own parameter (CPython SyntaxError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R465-COMPILE-ERROR).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
