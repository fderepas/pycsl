r"""Test 4437 -- gen #37 route #334 (expected FAIL): a field DECLARED int but SHOWN a float through a local (`x = 2.5; self.r: int = x`) was carried as an int and `c.r % 1 == 0` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): an annotation covers values of unknown type, not values shown non-int.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        x = 2.5
        self.r: int = x

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
