r"""G29 K13 — collection semantics probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    xs = [1, 2, 3]
    xs.reverse()
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
