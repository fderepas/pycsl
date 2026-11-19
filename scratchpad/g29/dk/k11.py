r"""G29 K11 — collection semantics probe (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    xs = [1, 2, 3]
    ys = xs[:]
    ys.append(4)
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
