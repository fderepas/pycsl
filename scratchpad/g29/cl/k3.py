r"""G29 CL-K3 — closure / late binding (claim != truth; CPython 9)."""
_ = 0  # anchor


#@ ensures \result != 9
def probe() -> int:
    n = 1
    f = lambda: n
    n = 9
    return f()


if __name__ == "__main__":
    print("CPython:", probe())
