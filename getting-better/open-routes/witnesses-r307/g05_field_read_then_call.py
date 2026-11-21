class K:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1 and \result == 0
    def bump(self) -> int:
        self.n = self.n + 1
        return 0

#@ ensures \result == 1
def f() -> int:
    k = K()
    return k.n + k.bump()

if __name__ == "__main__":
    assert f() == 1
