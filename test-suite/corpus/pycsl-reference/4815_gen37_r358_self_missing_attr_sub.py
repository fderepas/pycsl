r"""Test 4815 -- gen #37 route #358 (expected FAIL): witness r51: `y = self.zz; return y - y` under `no_exception \all`, `ensures \result == 0`; PROVED (CPython AttributeError). FAIL (PyCSL-R358).
"""
# pycsl-expected: FAIL
class W:
    #@ no_exception \all
    #@ ensures \result == 0
    def m(self) -> int:
        y = self.zz
        return y - y


if __name__ == "__main__":
    try:
        W().m()
        assert False, "expected AttributeError"
    except AttributeError:
        pass
