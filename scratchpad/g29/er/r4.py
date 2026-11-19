r"""G29 ER4 — stores inside `try` in `__init__`, the second raising."""
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.x = 1
        try:
            self.x = 10 // k
        except ZeroDivisionError:
            self.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C(0)
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
