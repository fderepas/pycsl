r"""Test 1627 - ROUTE #178 (gen #29): a method reading `self.d["b"]` called as `c.get()` inside `try ... except KeyError: return 9` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
from typing import Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    def get(self) -> int:
        return self.d["b"]


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        v = c.get()
    except KeyError:
        return 9
    return v * 0
