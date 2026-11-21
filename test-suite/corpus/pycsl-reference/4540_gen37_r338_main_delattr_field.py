r"""Test 4540 -- gen #37 route #338 (expected FAIL): `delattr(c, "r")` from `__main__` (CPython AttributeError): PROVED before. REFUSED now.
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
    delattr(c, "r")
    assert g(c) == True
