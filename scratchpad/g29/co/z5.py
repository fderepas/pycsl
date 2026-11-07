r"""G29 CO-Z5 — the EMPTY list literal as a value (claim != truth; CPython 0)."""
_ = 0  # anchor


#@ ensures \result != 0
def probe() -> int:
    xs = []
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
