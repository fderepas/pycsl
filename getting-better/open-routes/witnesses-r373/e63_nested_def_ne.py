class W:
    def __ne__(self, o: object) -> bool:
        return True

    #@ ensures \result == 0
    def m(self) -> int:
        def g() -> "W":
            return self
        t = g()
        return 1 if t != t else 0

if __name__ == "__main__":
    assert W().m() == 0, W().m()
