r"""G29 A14 — arithmetic/sequence semantics probe (false claim; CPython 6)."""
_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    xs = [1, 2, 3, 4]
    return xs[-1] + xs[1:][0]


if __name__ == "__main__":
    print("CPython:", probe())
