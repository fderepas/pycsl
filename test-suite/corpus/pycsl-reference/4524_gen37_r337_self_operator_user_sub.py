r"""Test 4524 -- gen #37 route #337 (expected FAIL): inside a method of a field-less class (`type w = int`), `self - self == 0` PROVED although the class's own `__sub__` returns 1 (CPython 1). REFUSED (PYCSL-R337-SELF-OPERATOR).
"""
# pycsl-expected: FAIL
class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        return self - self

if __name__ == "__main__":
    assert W().m() == 0, W().m()
