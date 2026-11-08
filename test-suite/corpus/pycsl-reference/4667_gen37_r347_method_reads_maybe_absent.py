r"""Test 4667 -- gen #37 route #347 (expected FAIL): (new) `no_exception` METHOD reads `self.x` stored under `if`; PROVED (CPython AttributeError). REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #347).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self, flag: bool) -> None:
        self.n = 0
        if flag:
            self.x = 1
    #@ no_exception \all
    def get(self) -> int:
        return self.x

if __name__ == "__main__":
    print(R(False).get())
