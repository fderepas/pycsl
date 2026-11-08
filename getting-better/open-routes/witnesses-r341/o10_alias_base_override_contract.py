class B:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

Base = B

class S(Base):
    def m(self) -> int:
        return 2

#@ ensures \result == 1
def g(b: B) -> int:
    return b.m()

if __name__ == "__main__":
    assert g(S()) == 1
