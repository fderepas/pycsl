r"""G29 K10 — collection semantics probe (claim != truth; CPython 4)."""
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    xs = [1, 2, 3]
    ys = xs
    ys.append(4)
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
