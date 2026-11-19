class R:
    def __init__(self, name: str) -> None:
        self.x: int = 1
        setattr(self, name, 5)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    v = f(R("k"))
    print("VIOLATION f =", v) if v != 0 else print("no violation")
