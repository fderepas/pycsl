r"""Test 4664 -- gen #37 route #347 (expected FAIL): (new) early `return` before `self.x = 1`; PROVED (CPython AttributeError). REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #347).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self, flag: bool) -> None:
        self.n = 0
        if not flag:
            return
        self.x = 1

#@ no_exception \all
def f(r: R) -> int:
    return r.x

if __name__ == "__main__":
    print(f(R(False)))
