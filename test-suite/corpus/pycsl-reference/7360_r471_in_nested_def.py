r"""Test 7360 -- route #471 (expected FAIL): red-team 38 witness `g13_k139_in_nested_def` -- `class Z(bool)` in a nested def (TypeError). PROVED at base a9eac4a08 / daf5c3d1f under `#@ no_exception \all`; now REFUSED (PYCSL-R471-LOCAL-CLASS-RAISES).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    def g() -> int:
        class Z(bool):
            pass
        return 1
    return g() + n


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
