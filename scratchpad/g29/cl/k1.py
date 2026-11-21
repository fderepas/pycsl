r"""G29 CL-K1 — closure / late binding (claim != truth; CPython 5)."""
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    n = 1
    def inner() -> int:
        return n
    n = 5
    return inner()


if __name__ == "__main__":
    print("CPython:", probe())
