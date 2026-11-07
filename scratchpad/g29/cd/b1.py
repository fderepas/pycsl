r"""G29 CD1 — base method calls self.val() overridden in subclass: dynamic dispatch."""
_ = 0  # anchor


class Base:
    def __init__(self) -> None:
        self.k = 0

    #@ ensures \result == 1
    def val(self) -> int:
        return 1

    def total(self) -> int:
        return self.val()


class Sub(Base):
    def val(self) -> int:
        return 2


#@ ensures \result == 1
def probe() -> int:
    s = Sub()
    return s.total()


if __name__ == "__main__":
    print("CPython:", probe())
