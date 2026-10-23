r"""G29 FD4 — a function `bool` default True, omitted, read as a truth value."""
_ = 0  # anchor


#@ ensures (flag and \result == 1) or (not flag and \result == 0)
def f(flag: bool = True) -> int:
    if flag:
        return 1
    return 0


#@ ensures \result == 0
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
