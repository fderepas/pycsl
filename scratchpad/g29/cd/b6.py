r"""G29 CD6 — isinstance of a subclass instance against the base."""
_ = 0  # anchor


class Base:
    def __init__(self) -> None:
        self.k = 0


class Sub(Base):
    pass


#@ ensures \result == False
def probe() -> bool:
    s = Sub()
    return isinstance(s, Base)


if __name__ == "__main__":
    print("CPython:", probe())
