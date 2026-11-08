r"""G29 ER3 — a `@classmethod` alternate constructor."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.x = k

    @classmethod
    def make(cls, k: int) -> "C":
        return cls(k + 1)


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C.make(1)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
