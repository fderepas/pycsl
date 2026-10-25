# route #343: type(self)() constructs a new P; its __sub__ is user code
class W:
    def __sub__(self, o: object) -> int:
        return 1

    #@ ensures \result == 0
    def m(self) -> int:
        t = type(self)()
        return t - t

if __name__ == "__main__":
    assert W().m() == 0, W().m()
