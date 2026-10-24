r"""Test 4621 -- gen #37 route #343 (expected FAIL): witness l08: `return max(self, 0)` under `no_exception \all`; PROVED (CPython TypeError). REFUSED (erased value into `-> int`).
"""
# pycsl-expected: FAIL
class P:
    #@ no_exception \all
    def m(self) -> int:
        return max(self, 0)

if __name__ == "__main__":
    try:
        P().m()
        assert False, "expected TypeError"
    except TypeError:
        pass
