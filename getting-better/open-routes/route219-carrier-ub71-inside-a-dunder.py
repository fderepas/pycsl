# ROUTE #219 CARRIER 2 (expects SUCCESS today — a UB REFUSAL is evaded).
#
# UB-7.1 (mutation during iteration) is a HARD REFUSAL: `bin/`'s UB catalog documents it,
# and `pycsl.py` raises `UB-7.1 — the loop body mutates the iterated collection` on the
# first violation. That check walks `ir_data["functions"]`, which a dunder never enters.
# The identical loop in a plain function IS refused (see the control).
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
