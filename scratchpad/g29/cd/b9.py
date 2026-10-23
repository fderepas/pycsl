r"""G29 CD9 — instance attribute shadows class attribute; class attribute unchanged."""
_ = 0  # anchor


class A:
    x = 1

    def __init__(self) -> None:
        self.y = 0


#@ ensures \result == 5
def probe() -> int:
    a = A()
    a.x = 5
    return A.x


if __name__ == "__main__":
    print("CPython:", probe())
