r"""Test 4906 -- gen #37 route #365 (expected FAIL): `{(d, 1)}` with `d` an eq-dataclass PROVED (CPython TypeError: a tuple hashes its components). REFUSED now (route #365).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {(d, 1)}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
