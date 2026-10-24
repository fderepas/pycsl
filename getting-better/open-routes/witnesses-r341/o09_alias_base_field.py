class B:
    def __init__(self) -> None:
        self.n = 1
    def m(self) -> int:
        return 1

Base = B

class S(Base):
    def m(self) -> float:
        return 0.5

#@ ensures \result == True
def g(b: B) -> bool:
    return b.m() % 1 == 0

if __name__ == "__main__":
    assert g(S()) == True
