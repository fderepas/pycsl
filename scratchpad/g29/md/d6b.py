r"""G29 MD6b — module constant rebound after the defining function."""
_ = 0  # anchor
D = 1


#@ ensures \result == 1
def f() -> int:
    return D


D = 2


if __name__ == "__main__":
    print("CPython:", f())
