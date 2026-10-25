class R:
    k = -1
    def __init__(self) -> None:
        self.x = 1

#@ ensures \result >= 0
def f(r: R) -> int:
    return getattr(r, "k", 0)

if __name__ == "__main__":
    assert f(R()) >= 0, f(R())
