r"""Test 10458 -- run #9 u72, review rt80 O2 (PASS control). qj72.x uses qj72's private `_h` (1); the
program defines its own `_h` (5). L20 proved `qj72.x() + _h() == 6`; u70 refused it (an introduced
over-refusal). qj72's `_h` now keeps its own identity (a fresh name); admitted.
"""
# pycsl-expected: PASS
import qj72


#@ ensures \result == 5
#@ assigns \nothing
def _h() -> int:
    return 5


#@ ensures \result == 6
#@ assigns \nothing
def g() -> int:
    return qj72.x() + _h()


if __name__ == "__main__":
    assert g() == 6
