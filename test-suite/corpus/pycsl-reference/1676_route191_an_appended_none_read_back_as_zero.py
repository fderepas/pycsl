r"""Test 1676 - ROUTE #191 carrier (gen #30): `xs.append(None)` stored the integer 0. The appended value reaches the TYPED `NoneExpr` arm, so the element read back `== 0` PROVED True while CPython says False. Closed by the same general repair.
"""
# pycsl-expected: FAIL
from typing import List, Optional

_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[Optional[int]] = []
    xs.append(None)
    v = xs[0]
    if v == 0:
        return 1
    return 2
