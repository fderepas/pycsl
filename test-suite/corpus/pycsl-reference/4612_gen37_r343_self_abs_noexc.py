r"""Test 4612 -- gen #37 route #343 (expected FAIL): witness h01: `return abs(self)` under `no_exception \all` for `class P`; PROVED (CPython TypeError). REFUSED (erased receiver into `-> int`) / FAIL (R343 builtin assertion).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    def m(self) -> int:
        return abs(self)

if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
