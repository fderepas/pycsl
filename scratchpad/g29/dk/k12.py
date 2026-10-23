r"""G29 K12 — collection semantics probe (claim != truth; CPython 5)."""
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    d = {1: 2}
    e = d
    e[1] = 5
    return d[1]


if __name__ == "__main__":
    print("CPython:", probe())
