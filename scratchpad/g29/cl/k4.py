r"""G29 CL-K4 — closure / late binding (claim != truth; CPython 4)."""
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    def mk(k: int):
        def g() -> int:
            return k
        return g
    h = mk(4)
    return h()


if __name__ == "__main__":
    print("CPython:", probe())
