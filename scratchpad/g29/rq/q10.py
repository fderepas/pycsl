r"""G29 RQ10 — a violated `requires` on a staticmethod called through the class."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    @staticmethod
    #@ requires d != 0
    #@ ensures \result == 1
    def get(d: int) -> int:
        return d // d


#@ ensures \result == 5
def probe() -> int:
    C.get(0)
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
