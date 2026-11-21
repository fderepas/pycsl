# route #344: record classes; MRO-picked B defines m by class-body ASSIGNMENT (no def)
class A:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> int:
        return 1

def _bm(self: object) -> float:
    return 0.5

class B:
    def __init__(self) -> None:
        self.n = 0
    m = _bm

class C(B, A):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1

if __name__ == "__main__":
    r = g(C())
    assert r == 0, r

