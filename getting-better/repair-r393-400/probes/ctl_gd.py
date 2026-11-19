class R:
    def __init__(self) -> None:
        self.x: int = 1
class S(R):
    def __init__(self) -> None:
        super().__init__()
        self.j: int = 5
#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)
if __name__ == "__main__":
    assert f(S()) == 0 and f(R()) == 0
