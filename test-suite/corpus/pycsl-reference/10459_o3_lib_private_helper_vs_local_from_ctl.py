r"""Test 10459 -- run #9 u72, review rt80 O3 (PASS control). As 10458, through `from qj72 import x`.
"""
# pycsl-expected: PASS
from qj72 import x


#@ ensures \result == 5
#@ assigns \nothing
def _h() -> int:
    return 5


#@ ensures \result == 6
#@ assigns \nothing
def g() -> int:
    return x() + _h()


if __name__ == "__main__":
    assert g() == 6
