r"""G29 ER-M2 — a LOCAL computed from a parameter, then stored."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        t = k * 2
        self.x = t


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
