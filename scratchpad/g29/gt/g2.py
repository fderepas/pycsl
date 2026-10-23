r"""G29 GT2 — unbounded recursion (RecursionError) with a false ensures."""
_ = 0  # anchor


#@ ensures \result == 5
def f(x: int) -> int:
    return f(x)


#@ ensures \result == 5
def probe() -> int:
    return f(0)


if __name__ == "__main__":
    print("CPython:", probe())
