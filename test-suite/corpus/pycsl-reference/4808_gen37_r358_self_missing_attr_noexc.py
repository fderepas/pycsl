r"""Test 4808 -- gen #37 route #358 (expected FAIL): witness r11: `y = self.zz` on a field-less receiver under `no_exception \all`; PROVED (CPython AttributeError). FAIL (PyCSL-R358: an attribute the erased value is not known to have).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    def m(self) -> int:
        y = self.zz
        return 0


if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected AttributeError"
    except AttributeError:
        pass
