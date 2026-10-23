r"""init raises via self method"""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = v
        self.check()

    def check(self) -> None:
        if self.v < 0:
            raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(-1)
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
