r"""requires mentions a module constant and a param with same name as a caller local"""
_ = 0  # anchor
LIMIT = 3


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires d < LIMIT
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return 10 // (LIMIT - d)


#@ ensures \result == 5
def probe() -> int:
    d = 0
    c = C(1)
    c.get(3)
    return 5 + d


if __name__ == "__main__":
    print("CPython:", probe())
