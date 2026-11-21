r"""raises-when understates the condition (method)"""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    #@ raises ValueError when x < 0
    def f(self, x: int) -> int:
        if x <= 0:
            raise ValueError()
        return x


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.f(0)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
