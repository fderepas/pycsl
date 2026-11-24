r"""Test 10426 -- run #9 u70, route #625 (PASS control). The two `helper`s of qa70 and qb70 under distinct
names (`from qa70 import helper as ha`, `from qb70 import helper`): no collision, `g() == 3` proves;
CPython agrees.
"""
# pycsl-expected: PASS
from qa70 import helper as ha
from qb70 import helper


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return ha() + helper()


if __name__ == "__main__":
    assert g() == 3
