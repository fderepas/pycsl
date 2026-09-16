r"""G29 VA2 — `__init__(self, *args)` storing `self.x = args[0]`."""
_ = 0  # anchor


class C:
    def __init__(self, *args: int) -> None:
        self.x = args[0]


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(9)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
