r"""G29 K9 — collection semantics probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    xs = [1, 2, 3]
    xs.remove(2)
    return xs[1]


if __name__ == "__main__":
    print("CPython:", probe())
