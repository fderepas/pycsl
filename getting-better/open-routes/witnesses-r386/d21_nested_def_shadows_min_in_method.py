class W:
    def __init__(self) -> None:
        self.a: int = 3

    #@ ensures \result <= 1
    #@ assigns \nothing
    def m(self) -> int:
        def min(x: int, y: int) -> int:
            return 100
        return min(self.a, 1)


if __name__ == "__main__":
    r = W().m()
    print("VIOLATION m() =", r) if r > 1 else print("no violation")
