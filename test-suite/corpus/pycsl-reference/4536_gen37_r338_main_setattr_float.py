r"""Test 4536 -- gen #37 route #338 (expected FAIL): `setattr(d, "r", 0.25)` from `__main__` into the int-inferred field: PROVED before (CPython False). REFUSED now: `setattr` / `delattr` / `object.__setattr__` on any receiver are stores.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.r = 0

#@ ensures \result == True
def g(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    d = C()
    setattr(d, "r", 0.25)
    assert g(d) == True
