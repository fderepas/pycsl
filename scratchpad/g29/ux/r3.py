r"""init implicit division by zero"""
_ = 0  # anchor


class C:
    def __init__(self, v: int) -> None:
        self.v = 10 // v


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(0)
    except ZeroDivisionError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
