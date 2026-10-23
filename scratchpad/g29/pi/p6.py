r"""G29 P6 — a store inside `__init__` through `setattr(self, "x", 7)`."""
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.x = 1
        setattr(self, "x", 7)


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
