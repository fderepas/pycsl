r"""Test 9633 -- route #592 WITNESS (expected FAIL: the claim is FALSE of the program): `C.g` returns `len(d) + x`, `\result >= x` for every map; `C.h` calls `self.g(3)` omitting `d` (the opaque map `pycsl_none_map` since lvN, the `_handle_dotted_call` fill site) and claims `\result >= 3`. CPython passes `None`: `len(None)` raises TypeError, `C().h()` returns nothing. Refused PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.k: int = 0

    #@ ensures \result >= x
    #@ assigns \nothing
    def g(self, x: int, d: Optional[Dict[str, int]] = None) -> int:
        return len(d) + x

    #@ ensures \result >= 3
    #@ assigns \nothing
    def h(self) -> int:
        return self.g(3)


if __name__ == "__main__":
    print("result", C().h())   # CPython: TypeError (len of None)
