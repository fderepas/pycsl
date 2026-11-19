class K:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1 and \result == self.n
    def bump(self) -> int:
        self.n = self.n + 1
        return self.n

#@ ensures \result == 1
def f() -> int:
    k = K()
    return k.bump() - k.bump()

if __name__ == "__main__":
    assert f() == 1
