# ROUTE #224 CARRIER (expects SUCCESS today — a declared conformance nothing checks).
#
# `C.m` ensures `\result == 1`, which does NOT refine `P.m`'s `\result == 99`. The default
# run reports "All contracts formally proven" with no warning. Under
# `--check-behavioral-subtyping` the identical file FAILS (see the control).
_ = 0  # anchor
from typing import Protocol


class P(Protocol):
    #@ ensures \result == 99
    def m(self) -> int: ...


#@ conforms_to P
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    def m(self) -> int:
        return 1
