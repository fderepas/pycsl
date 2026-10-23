r"""control: user subclass caught by its own name"""
_ = 0  # anchor


class Base(Exception):
    pass


class Sub(Base):
    pass


#@ ensures \result == 9
def probe() -> int:
    try:
        raise Sub()
    except Sub:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
