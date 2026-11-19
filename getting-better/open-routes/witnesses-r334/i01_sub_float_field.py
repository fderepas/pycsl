class B:
    def __init__(self) -> None:
        self.r = 0

class S(B):
    def __init__(self) -> None:
        super().__init__()
        self.r = 0.5

#@ ensures \result == True
def g(b: B) -> bool:
    return b.r % 1 == 0

if __name__ == "__main__":
    assert g(S()) == True, g(S())
