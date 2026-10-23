r"""G29 K2 — collection semantics probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    d = {1: 2, 1: 3}
    return d[1]


if __name__ == "__main__":
    print("CPython:", probe())
