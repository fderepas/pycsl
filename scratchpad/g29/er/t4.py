r"""G29 T4 — CHAINED store overwriting an earlier literal: `self.x = 1; self.x = self.y = k`."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.x = 1
        self.x = self.y = k


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
