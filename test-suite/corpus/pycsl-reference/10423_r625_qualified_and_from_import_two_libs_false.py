r"""Test 10423 -- run #9 u70, route #625 (FAIL, PRE-EXISTING). The same collision across two resolvers:
`from qb70 import helper` (direct) and `qa70.helper()` (module-qualified). pycsl kept qb70's `helper` for
both calls, so `g() == 2 or g() == 4` PROVED at daa36070b. CPython prints "result 3".
REFUSED: PYCSL-SEM-IMPORT-FUNCTION-NAME-CLASH.
"""
# pycsl-expected: FAIL
import qa70
from qb70 import helper


#@ ensures \result == 2 or \result == 4
#@ assigns \nothing
def g() -> int:
    return qa70.helper() + helper()


if __name__ == "__main__":
    print("result", g())
