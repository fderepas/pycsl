r"""Test 4527 -- gen #37 route #337 (expected FAIL): inside a method of `class P` (no `__lt__`), `self < self` PROVED `False` under `no_exception \all` (CPython TypeError). REFUSED (PYCSL-R337-SELF-OPERATOR).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    #@ ensures \result == False
    def m(self) -> bool:
        return self < self

if __name__ == "__main__":
    assert P().m() == False
