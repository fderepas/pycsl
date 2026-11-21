r"""G29 RQ3 — requires on a method parameter (not self), violated."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires d != 0
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return d // d


#@ ensures \result == 1
def probe() -> int:
    c = C(3)
    return c.get(0)


if __name__ == "__main__":
    print("CPython:", probe())
