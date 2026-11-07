class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        def g(w: "W" = self) -> "W":
            return w
        t = g()
        return t - t

if __name__ == "__main__":
    assert W().m() == 0, W().m()
