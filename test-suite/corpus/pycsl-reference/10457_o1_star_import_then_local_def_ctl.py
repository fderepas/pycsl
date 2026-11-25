r"""Test 10457 -- run #9 u72, review rt80 O1 (PASS control). `from qa70 import *` (qa70.helper returns 1),
THEN a local `def helper` (returns 2): the local def is the later binding, CPython's `helper()` runs it.
L20 proved `g() == 2`; u70 refused it (NAME-CLASH, an introduced over-refusal). Admitted again.
"""
# pycsl-expected: PASS
from qa70 import *


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return helper()


if __name__ == "__main__":
    assert g() == 2
