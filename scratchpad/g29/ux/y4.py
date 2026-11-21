r"""control: method raise caught, true claim 9"""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    #@ requires v >= 0
    #@ ensures \result == v
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


#@ ensures \result == 3 or \result == 9
def probe() -> int:
    c = C()
    try:
        r = c.go(3)
    except ValueError:
        return 9
    return 3


if __name__ == "__main__":
    print("CPython:", probe())
