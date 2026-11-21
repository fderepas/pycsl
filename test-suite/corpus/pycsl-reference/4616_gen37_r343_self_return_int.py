r"""Test 4616 -- gen #37 route #343 (expected FAIL): witness h07: `return self` through `-> int` and `self.m() + 1` under `no_exception \all`; PROVED (CPython TypeError). REFUSED (route #252: erased receiver returned through `-> int`).
"""
# pycsl-expected: FAIL
class P:
    def m(self) -> int:
        return self

    #@ no_exception \all
    def k(self) -> int:
        return self.m() + 1

if __name__ == "__main__":
    try:
        P().k()
        assert False, "expected TypeError"
    except TypeError:
        pass
