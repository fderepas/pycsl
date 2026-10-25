# route #343: s = self.me(); s == s with a user __eq__ -> False
class W:
    def __eq__(self, o: object) -> bool:
        return False
    __hash__ = object.__hash__

    def me(self) -> "W":
        return self

    #@ ensures \result == True
    def m(self) -> bool:
        s = self.me()
        return s == s

if __name__ == "__main__":
    assert W().m() == True, W().m()
