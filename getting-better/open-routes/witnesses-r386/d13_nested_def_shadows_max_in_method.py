class W:
    def __init__(self) -> None:
        self.a: int = 3

    #@ ensures \result >= self.a
    #@ assigns \nothing
    def m(self) -> int:
        def max(x: int, y: int) -> int:
            return -100
        return max(self.a, 1)


if __name__ == "__main__":
    r = W().m()
    print("VIOLATION m() =", r) if r < 3 else print("no violation")
