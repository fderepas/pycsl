r"""G29 CO-W5 — the `(Array.make 1 0)` coercion placeholder feeding a length-preserving val (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    xs = sorted(x * 2 for x in range(3))
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
