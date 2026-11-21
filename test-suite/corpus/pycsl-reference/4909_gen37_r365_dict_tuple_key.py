r"""Test 4909 -- gen #37 route #365 (expected FAIL): `{(d, 1): 0}` PROVED (CPython TypeError). REFUSED now (route #365).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    m = {(d, 1): 0}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
