r"""G29 T2 — TUPLE-target store `self.x, self.y = k, 2` in `__init__`."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.x, self.y = k, 2


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
