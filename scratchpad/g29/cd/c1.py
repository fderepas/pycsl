r"""G29 CD11 — Liskov: Sub.val overrides a contracted Base.val with a violating body; a Base-typed caller trusts Base's contract."""
_ = 0  # anchor


class Base:
    def __init__(self) -> None:
        self.k = 0

    #@ ensures \result == 1
    def val(self) -> int:
        return 1


class Sub(Base):
    def val(self) -> int:
        return 2


#@ ensures \result == 1
def use(b: Base) -> int:
    return b.val()


#@ ensures \result == 1
def probe() -> int:
    return use(Sub())


if __name__ == "__main__":
    print("CPython:", probe())
