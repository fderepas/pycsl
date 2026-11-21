r"""G29 P3 — `__init__` delegates the store to a HELPER METHOD."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 1
        self._setup()

    #@ assigns self.x
    def _setup(self) -> None:
        self.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
