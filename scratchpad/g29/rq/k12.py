r"""two params swapped args"""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires a > b
    #@ ensures \result == 1
    def get(self, a: int, b: int) -> int:
        return 10 // (a - b) * 0 + 1


#@ ensures \result == 5
def probe() -> int:
    a = 1
    b = 2
    c = C(1)
    c.get(b, a)
    c.get(a, b)
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
