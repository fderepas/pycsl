# r338 R5: override by multiple inheritance (C defines no m; MRO picks B.m -> float over A.m -> int)
class A:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> int:
        return 1

class B:
    def __init__(self) -> None:
        self.n = 0
    def m(self) -> float:
        return 0.5

class C(B, A):
    pass

#@ ensures \result == 0
def g(a: A) -> int:
    return a.m() % 1

if __name__ == "__main__":
    print(g(C()))
