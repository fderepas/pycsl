# r341 residual (3): an attribute base `om.B` resolves by its tail to THIS file's B
import rt25other as om

class B:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

class S(om.B):
    pass

#@ ensures \result == 1
def g(s: S) -> int:
    return s.m()

if __name__ == "__main__":
    print(g(S()))
