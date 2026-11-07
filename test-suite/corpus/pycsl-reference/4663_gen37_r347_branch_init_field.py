r"""Test 4663 -- gen #37 route #347 (expected FAIL): witness k03: `if flag: self.x = 1` in `__init__`, `no_exception \all` read of `r.x`; PROVED (CPython AttributeError). REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #347).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self, flag: bool) -> None:
        self.n = 0
        if flag:
            self.x = 1

#@ no_exception \all
def f(r: R) -> int:
    return r.x

if __name__ == "__main__":
    print(f(R(False)))
