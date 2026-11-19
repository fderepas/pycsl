r"""Test 4908 -- gen #37 route #365 (expected FAIL): `t: Tuple[D, int]; {t}` PROVED (CPython TypeError). REFUSED now (route #365: `Tuple[...]` arguments).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Tuple

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(t: Tuple[D, int]) -> int:
    s = {t}
    return 1

if __name__ == "__main__":
    print(g((D(1), 2)))
