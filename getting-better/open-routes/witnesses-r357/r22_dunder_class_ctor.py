# route #343: self.__class__() constructs a W; user __sub__
class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        t = self.__class__()
        return t - t

if __name__ == "__main__":
    assert W().m() == 0, W().m()
