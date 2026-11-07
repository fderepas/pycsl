# route #344: B.m defined inside a try in the class body
class A:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> int:
        return 1

class B:
    def __init__(self) -> None:
        self.n = 0
    try:
        def m(self) -> float:
            return 0.5
    except Exception:
        pass

class C(B, A):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1

if __name__ == "__main__":
    r = g(C())
    assert r == 0, r

