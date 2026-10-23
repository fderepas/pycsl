r"""G29 MD7 — a function redefined later in the module; the later definition wins."""
_ = 0  # anchor


#@ ensures \result == 1
def f() -> int:
    return 1


#@ ensures \result == 1
def probe() -> int:
    return f()


def f() -> int:
    return 2


if __name__ == "__main__":
    print("CPython:", probe())
