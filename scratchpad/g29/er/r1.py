r"""G29 ER1 — `__init__` with an EARLY RETURN before a top-level store; the class attribute stays."""
_ = 0  # anchor


class C:
    x = 0

    def __init__(self, k: int) -> None:
        if k < 0:
            return
        self.x = k


#@ ensures \result == -1
#@ assigns \nothing
def probe() -> int:
    c = C(-1)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
