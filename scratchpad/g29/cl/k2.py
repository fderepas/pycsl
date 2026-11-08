r"""G29 CL-K2 — closure / late binding (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    fs = [lambda: i for i in range(3)]
    return fs[0]()


if __name__ == "__main__":
    print("CPython:", probe())
