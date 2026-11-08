r"""Test 5564 -- gen #37 route #394 (expected FAIL): class attribute through `self`: `{self.K}` with `K = D(1)` (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the value's class is derived from its source (or refused as unknown)).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


class C:
    K = D(1)

    #@ no_exception \all
    #@ assigns \nothing
    def m(self) -> int:
        s = {self.K}
        return len(s)


if __name__ == "__main__":
    try:
        print("result", C().m())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
