r"""G29 T1 — store through `self.__dict__["x"]` in `__init__`."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 1
        self.__dict__["x"] = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
