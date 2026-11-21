r"""declared raises-when through a FIELD receiver under the caller's no_exception"""
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    #@ raises ValueError when v < 0
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ no_exception ValueError
    #@ ensures \result == 0
    def run(self) -> int:
        self.inner.go(-1)
        return 0


if __name__ == "__main__":
    print("CPython:", Outer().run())
