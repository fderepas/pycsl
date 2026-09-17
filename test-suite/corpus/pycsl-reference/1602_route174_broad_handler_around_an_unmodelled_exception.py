r"""Test 1602 - ROUTE #174 (gen #29): the None attribute read under `except Exception` PROVED `\result == 0` (CPython 9) even with routes #171/#172 (they widen only the modelled exceptions). Broad handlers are refused in a claiming function.
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
    except Exception:
        return 9
    return v * 0
