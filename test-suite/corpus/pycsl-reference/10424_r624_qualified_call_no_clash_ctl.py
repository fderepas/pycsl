r"""Test 10424 -- run #9 u70, route #624 (PASS control). `qa70.val1()` with no local `val1`: the dependency
stub is injected and `g() == 1` proves; CPython agrees.
"""
# pycsl-expected: PASS
import qa70


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return qa70.val1()


if __name__ == "__main__":
    assert g() == 1
