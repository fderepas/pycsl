# route #343: s = self.me() -- method result typed W is not the erased receiver
class W:
    def __sub__(self, o: object) -> int:
        return 1

    def me(self) -> "W":
        return self

    #@ ensures \result == 0
    def m(self) -> int:
        s = self.me()
        return s - s

if __name__ == "__main__":
    assert W().m() == 0, W().m()
