r"""Test 10460 -- run #9 u72, review rt80 O4 (PASS control). qj72.x and qk72.y each use their OWN private
`_h` (1 and 2). L20 proved `qj72.x() + qk72.y() == 3`; u70 refused it (an introduced over-refusal). Each
`_h` keeps its own identity; admitted.
"""
# pycsl-expected: PASS
import qj72
import qk72


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return qj72.x() + qk72.y()


if __name__ == "__main__":
    assert g() == 3
