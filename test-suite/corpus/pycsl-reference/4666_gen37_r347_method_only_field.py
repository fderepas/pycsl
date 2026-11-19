r"""Test 4666 -- gen #37 route #347 (expected FAIL): (new) field stored only by another method; FAILED at base (Why3 unbound field), REFUSED now. REFUSED (PYCSL-R347-FIELD-MAYBE-UNASSIGNED, route #347).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.n = 0
    def setup(self) -> None:
        self.x = 1

#@ no_exception \all
def f(r: R) -> int:
    return r.x

if __name__ == "__main__":
    print(f(R()))
