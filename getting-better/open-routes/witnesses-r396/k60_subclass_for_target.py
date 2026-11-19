class R:
    def __init__(self) -> None:
        self.x: int = 1


class S(R):
    def __init__(self) -> None:
        super().__init__()
        for self.k in [5]:
            pass


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        print("result", f(S()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
