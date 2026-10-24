r"""Test 4619 -- gen #37 route #343 (expected FAIL): witness l05: `h(self)` into `n: int` (`n + 1`) under `no_exception \all`; PROVED (CPython TypeError). REFUSED (route #252: erased receiver into an `int` parameter).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def h(n: int) -> int:
    return n + 1

class P:
    #@ no_exception \all
    def m(self) -> int:
        return h(self)

if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
