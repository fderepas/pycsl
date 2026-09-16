r"""G29 VA4 — a constructor parameter with a default, but the field is stored from a DIFFERENT expression over it."""
_ = 0  # anchor


class C:
    def __init__(self, k: int = 4) -> None:
        self.x = k * 3


#@ ensures \result == 12
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
