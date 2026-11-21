r"""Advice probe for route #471 (a valid base: `int` for `bool`), from test 7365 -- route #471 (expected FAIL): red-team 38 witness `g7_i733_class_in_function_bool_base` -- `class Z(bool)` inside the claimed def (TypeError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    class Z(int):
        pass
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
