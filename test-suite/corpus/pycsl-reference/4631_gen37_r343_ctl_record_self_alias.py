r"""Test 4631 -- gen #37 route #343: CONTROL: a RECORD class's receiver is not erased: `self` passed to a function taking the record (`h(self)`) keeps the record field laws, `h(self) - self.x` PROVES `\result == 0` (CPython 0).
"""
# pycsl-expected: PASS
class R:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ ensures \result == 0
    def m(self) -> int:
        return h(self) - self.x

#@ ensures \result == r.x
def h(r: R) -> int:
    return r.x

if __name__ == "__main__":
    assert R(5).m() == 0
