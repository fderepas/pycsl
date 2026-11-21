r"""G29 CD10 — super().val() in override adds to base."""
_ = 0  # anchor


class Base:
    def __init__(self) -> None:
        self.k = 0

    def val(self) -> int:
        return 1


class Sub(Base):
    def val(self) -> int:
        return super().val() + 10


#@ ensures \result == 10
def probe() -> int:
    return Sub().val()


if __name__ == "__main__":
    print("CPython:", probe())
