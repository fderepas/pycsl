r"""Test 4611 -- gen #37 route #343 (expected FAIL): witness b04: `s = self; return s < s` under `no_exception \all` for `class P` (no `__lt__`); PROVED `False` (CPython TypeError). FAIL (route #252 assertion on the erased ordering).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    #@ ensures \result == False
    def m(self) -> bool:
        s = self
        return s < s

if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
