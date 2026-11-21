# route #344 residual: MRO class outside the file (imported Bf.m -> float)
class A:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> int:
        return 1

from rt26other import Bf as B

class C(B, A):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1

if __name__ == "__main__":
    r = g(C())
    assert r == 0, r

