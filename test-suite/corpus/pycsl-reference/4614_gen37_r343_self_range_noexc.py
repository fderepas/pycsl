r"""Test 4614 -- gen #37 route #343 (expected FAIL): witness h05: `range(self)` under `no_exception \all` for `class P`; PROVED (CPython TypeError). FAIL (PyCSL-R343 assertion: a builtin applied to an erased value).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    #@ ensures \result == 0
    def m(self) -> int:
        r = range(self)
        return 0

if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
