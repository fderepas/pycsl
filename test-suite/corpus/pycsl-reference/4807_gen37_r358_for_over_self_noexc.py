r"""Test 4807 -- gen #37 route #358 (expected FAIL): witness r07: `for z in self` (field-less `P`, no `__iter__`) under `no_exception \all`; PROVED (CPython TypeError). FAIL (PyCSL-R358 assertion before the opaque `iter_length`).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    def m(self) -> int:
        n = 0
        for z in self:
            n = n + 1
        return n


if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
