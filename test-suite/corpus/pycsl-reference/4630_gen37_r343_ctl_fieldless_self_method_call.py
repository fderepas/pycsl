r"""Test 4630 -- gen #37 route #343: CONTROL: in a field-less class (receiver erased since route #343) a method call on `self` keeps its callee's `-> int` contract and an identity test on `self` is Why3 `=`; PROVES (CPython 2, True).
"""
# pycsl-expected: PASS
class P:
    #@ ensures \result == 1
    def h(self) -> int:
        return 1

    #@ no_exception \all
    #@ ensures \result == 2
    def k(self) -> int:
        return self.h() + 1

    #@ ensures \result == True
    def same(self) -> bool:
        s = self
        return s is self

if __name__ == "__main__":
    assert P().k() == 2
    assert P().same() is True
