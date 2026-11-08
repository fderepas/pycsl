r"""Test 4538 -- gen #37 route #338 (expected FAIL): `c.r += 0.5` from `__main__`: PROVED before (CPython False). REFUSED now (an augmented store `0 op e`).
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
    c.r += 0.5
    assert g(c) == True
