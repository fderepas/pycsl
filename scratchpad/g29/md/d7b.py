r"""G29 MD7b — a function redefined later; a caller between them."""
_ = 0  # anchor


#@ ensures \result == 1
def f() -> int:
    return 1


#@ ensures \result == 1
def probe() -> int:
    return f()


def f() -> int:  # noqa: F811
    return 2


if __name__ == "__main__":
    print("CPython:", probe())
