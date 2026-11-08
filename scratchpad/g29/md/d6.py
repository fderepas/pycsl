r"""G29 MD6 — module constant rebound after a function reads it at call time."""
_ = 0  # anchor
D = 1


#@ ensures \result == 1
def f() -> int:
    return D


D = 2


#@ ensures \result == 1
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
