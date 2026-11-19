class R:
    def __init__(self) -> None:
        self.x: int = 1
        setattr(self, "k", 5)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    r = f(R())
    print("VIOLATION f =", r) if r != 0 else print("no violation")
