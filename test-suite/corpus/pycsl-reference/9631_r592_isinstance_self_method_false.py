r"""Test 9631 -- route #592 WITNESS (expected FAIL: the claim is FALSE of the program): the `self.g(3)` twin of 9630 (the `_handle_dotted_call` fill site). `C.g`'s verified body proves `\result == 1` because `isinstance(d, dict)` is true of every map, and the omitted `d` is the opaque map `pycsl_none_map`, so `C.h`'s `\result == 1` followed. CPython passes `None`: `C().h()` returns 0. Refused PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.k: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def g(self, x: int, d: Optional[Dict[str, str]] = None) -> int:
        return 1 if isinstance(d, dict) else 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def h(self) -> int:
        return self.g(3)


if __name__ == "__main__":
    print("result", C().h())   # CPython: result 0
