r"""Test 1830 — gen #31 (expected FAIL/REFUSED): UB-7.1 inside a DUNDER is refused again.

UB-7.1 (mutation during iteration) is not a proof obligation, it is a HARD REFUSAL the UB
catalog advertises:

    [!] PIPELINE ERROR: ... UB-7.1 — the loop body mutates the iterated collection 'xs'.
        This is undefined behaviour in CPython (iterator state corruption).

The check walks `ir_data["functions"]`, which a dropped dunder never entered — so moving the
identical loop into `__enter__` produced `[+] Verification SUCCESS! All contracts formally
proven` instead. The perimeter this project advertises had a hole the width of a method
name. It is now refused here too.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    def __enter__(self) -> int:
        xs: List[int] = [1, 2, 3]
        k: int = 0
        for x in xs:
            xs.append(x)
            k = k + 1
        return k
