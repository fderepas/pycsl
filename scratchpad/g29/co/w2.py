r"""G29 CO-W2 — the `(Array.make 1 0)` coercion placeholder feeding a length-preserving val (claim != truth; CPython 5)."""
_ = 0  # anchor


#@ ensures \result != 5
def probe() -> int:
    return len(list(x for x in range(5)))


if __name__ == "__main__":
    print("CPython:", probe())
