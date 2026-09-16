r"""G29 CL-K6 — closure / late binding (claim != truth; CPython 11)."""
_ = 0  # anchor


#@ ensures \result != 11
def probe() -> int:
    n = 1
    def bump() -> int:
        nonlocal n
        n = n + 10
        return n
    bump()
    return n


if __name__ == "__main__":
    print("CPython:", probe())
