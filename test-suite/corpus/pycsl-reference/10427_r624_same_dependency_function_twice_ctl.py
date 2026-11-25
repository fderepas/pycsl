r"""Test 10427 -- run #9 u70, route #624 (PASS control). The SAME dependency function reached twice
(`import qa70` + `qa70.val1()`, and `from qa70 import val1`): one origin, one IR, so the second injection
is the same function and is not refused; `g() == 2` proves; CPython agrees.
"""
# pycsl-expected: PASS
import qa70
from qa70 import val1


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return qa70.val1() + val1()


if __name__ == "__main__":
    assert g() == 2
