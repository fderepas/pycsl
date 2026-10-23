r"""Test 1599 - ROUTE #174 (gen #29): `c: Optional[C] = None; try: v = c.x except AttributeError: return 9; return v * 0` PROVED `\result == 0` (CPython 9): AttributeError is not modelled, so the handler was dead. A handler only an unmodelled exception can reach is now refused in a claiming function.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Optional
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == 0
def probe() -> int:
    c: Optional[C] = None
    try:
        v = c.x
    except AttributeError:
        return 9
    return v * 0
