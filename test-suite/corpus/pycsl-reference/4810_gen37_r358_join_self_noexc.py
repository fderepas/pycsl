r"""Test 4810 -- gen #37 route #358 (expected FAIL): witness r19: `"".join([self])` under `no_exception \all`; PROVED (CPython TypeError). FAIL (PyCSL-R358: a str method handed an erased element).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    def m(self) -> int:
        s = "".join([self])
        return 0


if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
