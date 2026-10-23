r"""G29 CO-W7 — the `(Array.make 1 0)` coercion placeholder feeding a length-preserving val (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    return len(sorted({1: 2, 3: 4}))


if __name__ == "__main__":
    print("CPython:", probe())
