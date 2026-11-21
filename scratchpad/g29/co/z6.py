r"""G29 CO-Z6 — the EMPTY list literal as a value (claim != truth; CPython 1)."""
_ = 0  # anchor


#@ ensures \result != 1
def probe() -> int:
    xs = []
    return 1 if all(x > 0 for x in xs) else 0


if __name__ == "__main__":
    print("CPython:", probe())
