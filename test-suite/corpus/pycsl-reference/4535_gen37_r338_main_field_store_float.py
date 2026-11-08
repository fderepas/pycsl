r"""Test 4535 -- gen #37 route #338 (expected FAIL): `__main__` stores `c.r = 0.5` into the int-inferred field of `C`; #334's store census covered the class, its bases and descendants only, and `c.r % 1 == 0` PROVED (CPython False). REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK): stores from ANY code join the census.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 0

#@ ensures \result == True
def g(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    c = C()
    c.r = 0.5
    assert g(c) == True
