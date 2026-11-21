r"""user subclass caught by base user class"""
_ = 0  # anchor


class Base(Exception):
    pass


class Sub(Base):
    pass


#@ ensures \result == 0
def probe() -> int:
    try:
        raise Sub()
    except Base:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
