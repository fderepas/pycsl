r"""raise a user exception INSTANCE bound to a variable"""
_ = 0  # anchor


class MyErr(ValueError):
    pass


#@ ensures \result == 0
def probe() -> int:
    e = MyErr()
    try:
        raise e
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
