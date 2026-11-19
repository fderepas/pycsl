r"""G29 ER-M3 — the parameter is rebound by an AUGMENTED assignment before the store."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        k += 1
        self.x = k


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
