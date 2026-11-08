r"""Test 4420 -- gen #37 route #334 (expected FAIL): a field initialised from a LOCAL bound to a float (`x = 2.5; self.r = x`) was carried as an int and `int(c.r) == c.r` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): a field is int only when every stored value is provably int.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        x = 2.5
        self.r = x

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()

    return int(c.r) == c.r

if __name__ == "__main__":
    assert g() == True, g()
