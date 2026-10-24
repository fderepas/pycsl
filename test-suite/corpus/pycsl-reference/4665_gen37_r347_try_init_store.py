r"""Test 4665 -- gen #37 route #347 (expected FAIL): (new) `self.x = int(s)` inside `try` with a swallowing handler; PROVED (CPython AttributeError). REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #347).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self, s: str) -> None:
        self.n = 0
        try:
            self.x = int(s)
        except ValueError:
            pass

#@ no_exception \all
def f(r: R) -> int:
    return r.x

if __name__ == "__main__":
    print(f(R("a")))
