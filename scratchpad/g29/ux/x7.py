r"""exception raised in a callee, caught by base class"""
_ = 0  # anchor


class Base(Exception):
    pass


class Sub(Base):
    pass


#@ raises Sub
def boom() -> int:
    raise Sub()


#@ ensures \result == 0
def probe() -> int:
    try:
        boom()
    except Base:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
