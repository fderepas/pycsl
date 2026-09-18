r"""G29 MD5 — default parameter evaluated at def time from a module variable later rebound."""
_ = 0  # anchor
D = 1


def f(x: int = D) -> int:
    return x


D = 2


#@ ensures \result == 2
def probe() -> int:
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
