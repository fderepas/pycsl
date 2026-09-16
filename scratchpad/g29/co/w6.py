r"""G29 CO-W6 — the `(Array.make 1 0)` coercion placeholder feeding a length-preserving val (claim != truth; CPython 3)."""
_ = 0  # anchor


#@ ensures \result != 3
def probe() -> int:
    return len(sorted([3, 1, 2]))


if __name__ == "__main__":
    print("CPython:", probe())
