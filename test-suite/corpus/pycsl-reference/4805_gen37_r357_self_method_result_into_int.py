r"""Test 4805 -- gen #37 route #357 (expected FAIL): witness r41: `h(self.me())` into `n: int` under `no_exception \all`; PROVED (CPython TypeError in `n + 1`). REFUSED (route #252 flow into an `int` parameter).
"""
# pycsl-expected: FAIL
class P:
    def me(self) -> "P":
        return self

#@ no_exception \all
def h(n: int) -> int:
    return n + 1

class Q:
    def me(self) -> "Q":
        return self

    #@ no_exception \all
    def m(self) -> int:
        return h(self.me())


if __name__ == "__main__":
    try:
        Q().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
