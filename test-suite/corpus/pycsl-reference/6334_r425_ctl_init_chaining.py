r"""Test 6334 -- route #425 (expected PASS): CONTROL: constructor chaining `super().__init__(n)` inside `__init__` (admitted by route #425), then a method read under the invariant (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ class invariant self.n >= 0
class A:
    #@ requires n >= 0
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 0
    #@ assigns \nothing
    def where(self) -> int:
        return self.n


class B(A):
    #@ requires n >= 0
    def __init__(self, n: int) -> None:
        super().__init__(n)


#@ ensures \result >= 0
def g(a: A) -> int:
    return a.where()


if __name__ == "__main__":
    print(g(B(1)))
