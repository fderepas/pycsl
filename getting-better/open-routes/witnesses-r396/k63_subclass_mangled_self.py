class R:
    def __init__(self) -> None:
        self.x: int = 1


class S(R):
    def __init__(self) -> None:
        super().__init__()
        self.__k: int = 5


class T(R):
    #@ ensures \result == 0
    def g(self, r: R) -> int:
        return getattr(r, "_S__k", 0)


if __name__ == "__main__":
    try:
        print("result", T().g(S()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
