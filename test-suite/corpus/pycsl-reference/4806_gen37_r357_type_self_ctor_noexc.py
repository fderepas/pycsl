r"""Test 4806 -- gen #37 route #357 (expected FAIL): witness r50: `type(self)()` under `no_exception \all` where `__init__` needs an argument; PROVED (CPython TypeError). REFUSED (PYCSL-R357-DYNAMIC-CONSTRUCTOR).
"""
# pycsl-expected: FAIL
class W:
    def __init__(self, k: int) -> None:
        pass

    #@ no_exception \all
    def m(self) -> int:
        t = type(self)()
        return 0


if __name__ == "__main__":
    try:
        W(1).m()
        assert False, "expected TypeError"
    except TypeError:
        pass
