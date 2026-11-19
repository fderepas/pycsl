r"""G29 CO-W8 — the `(Array.make 1 0)` coercion placeholder feeding a length-preserving val (claim != truth; CPython 4)."""
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    return len(list(range(4)))


if __name__ == "__main__":
    print("CPython:", probe())
