r"""Test 9390 -- cap-none-default-map-param (run #6 lvN, expected PASS): a call that OMITS an `Optional[Dict[str, str]] = None` argument, on a method (`self.g(3)`) and on a module function (`mg(3)`), is filled with the opaque `pycsl_none_map` (route #44's "this is None, nothing is decidable about it"), not the int witness `0`. Before the fix both call sites were ill-typed (L3-tc `int` vs `string -> option string`) and the whole file was refused; the callees never read `d`, so `\result == 3` / `\result == 4` are TRUE and now prove (CPython: 3 and 4).
"""
# pycsl-expected: PASS
from typing import Dict, Optional


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.k: int = 0

    #@ requires True
    #@ ensures \result == x
    #@ assigns \nothing
    def g(self, x: int, d: Optional[Dict[str, str]] = None) -> int:
        return x

    #@ requires True
    #@ ensures \result == 3
    #@ assigns \nothing
    def h(self) -> int:
        return self.g(3)


#@ requires True
#@ ensures \result == x + 1
#@ assigns \nothing
def mg(x: int, d: Optional[Dict[str, str]] = None) -> int:
    return x + 1


#@ requires True
#@ ensures \result == 4
#@ assigns \nothing
def mh() -> int:
    return mg(3)


if __name__ == "__main__":
    print("result", C().h(), mh())
