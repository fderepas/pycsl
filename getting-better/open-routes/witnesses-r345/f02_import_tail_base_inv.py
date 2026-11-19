import rt25other as om

#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

class S(om.B):
    def k(self) -> int:
        return 0

#@ ensures \result == 1
def g(s: S) -> int:
    return s.m()

if __name__ == "__main__":
    print(g(S()))
