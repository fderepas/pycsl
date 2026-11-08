r"""Test 4539 -- gen #37 route #338 (expected FAIL): `del c.r` from `__main__`, then `g(c)` reads it (CPython AttributeError): PROVED before. REFUSED now (a deletion is a store of a non-int value).
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
    del c.r
    assert g(c) == True
