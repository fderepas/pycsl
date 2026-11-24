r"""Test 10463 -- run #9 u72, route #629 (PASS control). One attribute base `qg72.Base` reached from one
module: X inherits qg72.Base.m (1); `g(x) == 1` for `x: X` proves, CPython agrees.
"""
# pycsl-expected: PASS
import qg72


class X(qg72.Base):
    pass


#@ ensures \result == 1
#@ assigns \nothing
def g(x: X) -> int:
    return x.m()


if __name__ == "__main__":
    assert g(X()) == 1
