r"""G29 K7 — collection semantics probe (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    xs = [3, 1, 2]
    xs.sort()
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
