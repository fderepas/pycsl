r"""G29 K8 — collection semantics probe (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    xs = [1, 2, 3]
    xs.insert(0, 9)
    return xs[1]


if __name__ == "__main__":
    print("CPython:", probe())
