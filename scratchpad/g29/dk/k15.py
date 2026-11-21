r"""G29 K15 — collection semantics probe (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    xs = [1, 2, 2]
    return xs.count(2)


if __name__ == "__main__":
    print("CPython:", probe())
