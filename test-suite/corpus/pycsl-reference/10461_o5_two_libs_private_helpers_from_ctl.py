r"""Test 10461 -- run #9 u72, review rt80 O5 (PASS control). As 10460, through `from ... import x` / `y`.
"""
# pycsl-expected: PASS
from qj72 import x
from qk72 import y


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return x() + y()


if __name__ == "__main__":
    assert g() == 3
